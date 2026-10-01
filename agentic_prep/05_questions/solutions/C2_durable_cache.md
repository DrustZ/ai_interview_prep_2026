# [C2] Anthropic：Durable Function Call Cache · 参考实现

⏱ 读完 12 min ｜ 建议先盲写 60 分钟（按下面时间盒）再对照——盲看解答记不住。题面原文见 [../C_live_ai_coding.md](../C_live_ai_coding.md#c2)，完整 rubric 见 [../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-anthropic-durable-cache`。

## 题目还原 + 验收标准

给部分实现的 Python `FunctionCallCache`（LRU 已写好）。**Part 1** `create_cache_key`：为任意函数调用生成确定、可哈希的 key，等价的 positional/keyword/default 调用必须命中同一 key。**Part 2**：cache 操作写 append-only WAL，重启 replay 同时恢复 value 和 LRU recency；尾部记录可能截断/损坏，不能让启动失败。rubric 权重：key 等价性 25%、LRU 语义 25%、durability/recovery 25%、安全与版本 15%、测试 10%。

验收标准（写代码前口头列给面试官）：
1. `f(1, 2)`、`f(1, b=2)`、`f(a=1, b=2)`、省略默认参数 → 同一 key
2. 不支持的参数类型显式 `TypeError`，绝不静默 `str(obj)`（那会把不同对象撞成同一 key）
3. 重启后 value **和** recency 顺序都恢复；hit（touch）也影响恢复后的顺序
4. 尾部截断/损坏：replay 在第一条坏记录停止，启动成功，坏尾被截掉
5. crash 发生在"intent 已写、result 未写"之间 → 该 key 进 `unknown_at_recovery`，不进 cache
6. 并发调用同一 key：函数只执行一次（single-flight dedup）

## 解题主线（60 分钟时间盒）

- **0–7 澄清语义**：支持哪些参数类型？函数 identity 算不算 key 的一部分？hit 要不要持久化 recency（要，否则恢复后顺序错）？遇到第一条坏记录后是停止还是跳过继续（停止——坏记录之后的偏移量已不可信）？value 是否保证 JSON-serializable？
- **7–14 记录格式与数据结构**：先在注释里写死 WAL 记录格式（`crc32 + 空格 + JSON body + \n`）和三张内存表（`OrderedDict` 存数据、`_inflight` 做并发 dedup、`unknown_at_recovery`），再动手。
- **14–38 核心实现**：Part 1 → `_append`/`_replay` → `get_or_call`。先跑通 happy path 再加 dedup。
- **38–48 崩溃与损坏**：写坏尾测试、intent-without-result 测试。
- **48–55 测试**：跑 `__main__` 里的 assert，口头补充没写的 case。
- **55–60 安全与演进**：pickle、KEY_VERSION、compaction（见 follow-up 节）。

来不及时的砍法（口述代替实现）：single-flight → abort 记录 → 恢复时 truncate 坏尾 → set/bytes 类型支持。**不能砍**：apply_defaults、checksum、delete-and-reinsert。

## 参考实现

```python
import inspect, json, os, threading, zlib
from collections import OrderedDict

KEY_VERSION = 1  # key encoding 演进: bump 后旧条目自然全 miss, 不会静默错误命中

# ---------------- Part 1: 确定性 cache key ----------------

def _canon(v):
    """带类型标签的规范形式; 等价值 -> 同一结构; 不支持的类型显式报错."""
    if v is None: return ["null"]
    if isinstance(v, bool): return ["bool", v]          # bool 必须在 int 之前判断
    if isinstance(v, int): return ["int", v]
    if isinstance(v, float): return ["float", repr(v)]  # repr 保精度, 区分 1 和 1.0
    if isinstance(v, str): return ["str", v]
    if isinstance(v, bytes): return ["bytes", v.hex()]
    if isinstance(v, (list, tuple)): return ["list", [_canon(x) for x in v]]
    if isinstance(v, (set, frozenset)):
        return ["set", sorted((_canon(x) for x in v), key=json.dumps)]
    if isinstance(v, dict):
        return ["dict", sorted(([_canon(k), _canon(x)] for k, x in v.items()),
                               key=json.dumps)]
    raise TypeError(f"un-cacheable argument type: {type(v).__name__}")

def create_cache_key(func, args=(), kwargs=None):
    bound = inspect.signature(func).bind(*args, **(kwargs or {}))
    bound.apply_defaults()  # positional/keyword/default 等价调用 -> 同一 arguments
    canon = ["k", KEY_VERSION, f"{func.__module__}.{func.__qualname__}",
             _canon(dict(bound.arguments))]
    return json.dumps(canon, separators=(",", ":"))  # 确定性字符串, 可哈希可入 WAL

# ------------- Part 2: WAL + durable LRU + single-flight -------------

def _frame(rec):
    body = json.dumps(rec, separators=(",", ":")).encode()
    return b"%08x %s\n" % (zlib.crc32(body), body)   # checksum + body = 一条记录

class DurableFunctionCache:
    def __init__(self, path, capacity=128):
        self.path, self.capacity = path, capacity
        self._lock = threading.Lock()
        self._data = OrderedDict()      # key -> value; 末尾 = most-recent
        self._inflight = {}             # key -> (Event, box), 并发 dedup
        self.unknown_at_recovery = []   # intent 有、result/abort 无 -> 结局未知
        self._replay()
        self._f = open(self.path, "ab")

    def _append(self, op, key, payload=None):   # 调用方必须持有 _lock
        self._f.write(_frame({"v": 1, "op": op, "key": key, "p": payload}))
        self._f.flush()
        os.fsync(self._f.fileno())      # fsync 返回后, 这条操作才算真正"发生过"

    def _replay(self):
        pending, good_end = {}, 0
        if not os.path.exists(self.path):
            return
        with open(self.path, "rb") as f:
            for line in f:
                try:
                    if not line.endswith(b"\n"):
                        break                           # 尾部截断的半条记录
                    crc, body = line[:-1].split(b" ", 1)
                    if int(crc, 16) != zlib.crc32(body):
                        break                           # 尾部损坏: checksum 不符
                    rec = json.loads(body)
                except ValueError:
                    break                               # 畸形记录: 停止重放
                good_end += len(line)
                op, key = rec["op"], rec["key"]
                if op == "intent":
                    pending[key] = True
                elif op == "abort":
                    pending.pop(key, None)
                elif op == "result":
                    pending.pop(key, None)
                    self._data.pop(key, None)   # 已存在必须 delete-and-reinsert,
                    self._data[key] = rec["p"]  # 否则 recency 不更新 (标准 replay 漏点)
                elif op == "touch" and key in self._data:
                    self._data.move_to_end(key)
        while len(self._data) > self.capacity:
            self._data.popitem(last=False)      # 重放完成后再按容量收敛
        self.unknown_at_recovery = list(pending)
        os.truncate(self.path, good_end)  # 砍掉坏尾: 新记录不能 append 在垃圾后面

    def get_or_call(self, func, *args, **kwargs):
        key = create_cache_key(func, args, kwargs)
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
                self._append("touch", key)  # hit 也写 WAL, 否则恢复后 recency 缺失
                return self._data[key]
            waiter = self._inflight.get(key)
            if waiter is None:
                event, box = threading.Event(), {}
                self._inflight[key] = (event, box)
        if waiter is not None:              # 别的线程正在算同一个 key: 锁外等
            waiter[0].wait()
            if "error" in waiter[1]:
                raise waiter[1]["error"]
            return waiter[1]["value"]
        try:
            with self._lock:
                self._append("intent", key)  # 1. 先落盘"我要执行"
            value = func(*args, **kwargs)    # 2. 再执行 (可能有副作用, 可能 crash)
            with self._lock:
                self._append("result", key, value)  # 3. 结果落盘后才进内存
                self._data.pop(key, None)
                self._data[key] = value
                if len(self._data) > self.capacity:
                    self._data.popitem(last=False)
            box["value"] = value
            return value
        except Exception as e:
            with self._lock:
                self._append("abort", key, type(e).__name__)  # 失败闭环, 不留 unknown
            box["error"] = e
            raise
        finally:
            with self._lock:
                self._inflight.pop(key, None)
            event.set()
```

intent→执行→result 的两阶段写法就是 [../../../agentic/labs/03_durable_harness/README.md](../../../agentic/labs/03_durable_harness/README.md) 里"最关键的 crash window"的单机版：崩溃后 intent 无 result 的 key 只能标 **unknown**——纯函数直接重算即可；有副作用的调用必须像 lab 03 那样靠外部 idempotency key 重放拿回同一结果，本地日志自己保证不了 exactly-once。这句话主动说出来是本题最大的加分点。

## 边界与测试要点

```python
if __name__ == "__main__":
    import tempfile
    def f(a, b=2, *, c=3): return a + b + c
    assert create_cache_key(f, (1, 2), {"c": 3}) \
        == create_cache_key(f, (), {"a": 1}) \
        == create_cache_key(f, (1,), {"b": 2})        # 等价调用同一 key
    path = tempfile.mktemp(); calls = []
    def slow(x): calls.append(x); return x * 10
    c1 = DurableFunctionCache(path, capacity=2)
    assert c1.get_or_call(slow, 1) == 10 and c1.get_or_call(slow, 1) == 10
    assert calls == [1]                                # 第二次是 hit
    c1.get_or_call(slow, 2); c1.get_or_call(slow, 1)   # touch 1 -> 2 变最旧
    with open(path, "ab") as g: g.write(b"\xffgarbage-no-newline")  # 模拟坏尾
    c2 = DurableFunctionCache(path, capacity=2)        # "重启"
    assert c2.get_or_call(slow, 1) == 10 and calls == [1, 2]  # 值+recency 都恢复
    print("ok, unknown =", c2.unknown_at_recovery)
```

必须口头点到（没时间写的话）：`True` vs `1` 不同 key（bool 判断在 int 前）；`float("nan")` 会命中同一 key（repr 相等），按业务决定是否拒绝；空文件/全坏文件启动成功且 cache 为空；capacity=1 时 replay 收敛正确；坏尾之后 append 的新记录能被下次 replay 读到（靠 truncate）；并发 100 线程同 key 只执行一次；executor 抛异常后 waiter 收到同一异常且下次调用可重试。

## 高频 follow-up 与应对

- **pickle 为什么不适合不可信文件？** `pickle.load` 反序列化时会执行 `__reduce__` 里的任意可调用对象——一个被篡改的 WAL 文件等于任意代码执行。JSON 只产生数据不执行代码，坏记录最多 parse 失败被 checksum/异常挡下。这也是为什么参数类型要白名单：不做"任意对象都能序列化"的承诺。
- **如何演进 key encoding 而不静默错误命中？** `KEY_VERSION` 直接编进 key 字符串：改编码规则时 bump 版本，所有旧条目自然 miss、被 LRU 逐出，绝不会出现"新规则算出的 key 撞上旧规则的值"。WAL 记录里的 `"v"` 字段独立演进记录格式：replay 遇到不认识的版本记 warning 跳过或停止，而不是按错误的字段含义解析。
- **函数签名/源码变了怎么失效？** 现在 key 只含 `module.qualname`，改实现不改名会命中陈旧结果。答法：key 里加 `hashlib.sha256(inspect.getsource(func))` 或 `func.__code__.co_code` 的哈希——部署新代码等于整体失效；或按函数注册显式 `version` 参数，语义不变的重构不清缓存。
- **不可 JSON 序列化的参数（自定义类）？** 不猜。提供注册协议：`register_codec(cls, to_canonical)`，由类作者给出确定性表示（如 `["User", user.id]`）；未注册的类型保持 `TypeError`。用 `id(obj)` 或默认 `repr` 都是错——进程重启后不稳定。
- **序列化字符串 vs 值元组做 key？** 元组（把 `_canon` 输出转嵌套 tuple）：不丢类型、可直接 hash、内存 dict 里更快；字符串：可写进 WAL/跨进程传输/做外部索引。本实现选字符串因为 Part 2 要落盘；两者答出 trade-off 即可。
- **多进程并发？** append-only 文件多写者会交错损坏。选项：(1) 单 writer 进程 + IPC；(2) `fcntl.flock` 串行化 append，replay 逻辑不变；(3) 直接换 SQLite（WAL mode 自带原子提交与并发读），代价是失去"纯 append 文件好 debug"。跨机器则是另一道题：中心化 Redis/DB + 每机 L1。
- **批量写降 I/O + checkpoint 加速恢复 + compaction？** fsync 是主要成本（每条一次）。批量：攒 N 条或 T 毫秒组提交，一次 fsync——代价是崩溃丢最后一批（touch 丢了只是 recency 略旧，result 丢了退化为重算，都可接受）。恢复加速：定期把整个 `OrderedDict` snapshot 写临时文件 + fsync + **原子 rename**，然后轮换 WAL；启动 = 读 snapshot + replay 短 WAL。compaction 顺带完成：旧 WAL 里被覆盖/逐出的 key 不进 snapshot。
- **线程安全的代价？** 单锁下 fsync 在临界区内，写吞吐受限。答法：锁只保护内存表和"分配 WAL 位置"，fsync 移出锁做组提交；或每条记录带单调 seq，允许乱序落盘、按 seq replay。

<details><summary>加分项：把它接回 agent 场景（面试官若问"这东西在 agent 系统里干嘛用"）</summary>

这就是 tool-call result cache / idempotency 层：key = tool name + canonical args（对应 [../../02_playbook.md](../../02_playbook.md) 第四节 ActionProposal 的 `canonical_args_hash`），intent/result 两阶段对应 durable harness 的 start intent + external idempotency key。只读工具可以直接 cache；有副作用的工具 cache 的意义是 crash 重放时不重复执行，而不是省钱。

</details>

## 如果这轮允许 AI：怎么驾驶

按 [../../02_playbook.md](../../02_playbook.md) 第八节：先自己写验收标准 1–6 和 WAL 记录格式（这是你的设计判断，不外包），再让 AI 一次一个窄任务："实现 `_replay`，遇到第一条 checksum 不符或截断的记录停止并 truncate，附坏尾测试"。review 时专查三处：bool/int 顺序、delete-and-reinsert、fsync 是否真调了 `os.fsync` 而不是只 `flush`——这三处正是 AI 最常写错、也正是 rubric 给分的地方。
