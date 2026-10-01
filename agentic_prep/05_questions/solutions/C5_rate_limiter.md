# [C5] Anthropic——线程安全 rate limiter for tool-calling agent API · 参考实现

⏱ 读完 15 min ｜ 建议先限时 30 min 盲写单机版（TokenBucket + 多租户 + 并发测试），再对照本文补分布式/滑窗/降载三段口头答案。题库原文见 [../C_live_ai_coding.md](../C_live_ai_coding.md#c5)。

## 题目还原 + 验收标准

**题面**：实现 rate limiter（场景：agent 并发高频调外部 API），follow-up 递进：(1) 线程安全 → (2) 多机分布式 → (3) sliding window → (4) load shedding。Anthropic coding 风格是 "software development assignment with a bit of leetcode baked in"——评的是工程完成度，不是算法炫技。

**验收标准**（写码前口头列出）：
1. token bucket 语义正确：`capacity` = burst 上限，`refill_rate` = 长期平均速率；**lazy refill**（按 elapsed 补发），不开后台线程。
2. thread-safe 且**不超卖**：冻结时钟下 8 线程抢 5 个 token，恰好 5 个通过——这个测试要主动写。
3. 锁粒度：per-bucket lock + registry lock 两级；"一把全局锁包住整个 dict" 是低分答案，要说得出为什么。
4. 多租户：per-key bucket 按需创建、互相隔离、支持 per-tenant 配额覆盖。
5. 拒绝时返回精确 `retry_after`，可直接映射 429 + `Retry-After` header。
6. 用 `time.monotonic` 且时钟可注入（测试确定性 + 免疫 wall-clock 回拨）。

## 解题主线（35–40 min 分配）

- **0–4 min 澄清**（见下）——当场确认"拒绝 vs 阻塞""限 requests 还是 tokens"。
- **4–16 min**：`TokenBucket.try_acquire`——先写签名和 docstring，refill 公式一次写对：`tokens = min(capacity, tokens + elapsed * rate)`。
- **16–24 min**：`RateLimiter` 多租户 + 两级锁 + double-checked 创建。
- **24–30 min**：跑测试，重点演示"冻结时钟并发不超卖"。
- **30–40 min**：follow-up 口头递进（分布式 Lua → 滑窗 → 降载）。
- **可以砍**：blocking 版 `acquire()`（口头讲 Condition + 唤醒即可）；闲置 bucket 淘汰（口头讲 TTL/LRU）；`handle_request` 中间件可最后补。

**开场澄清 5 问**：
1. 限流对象是 requests/sec 还是 tokens/sec？——LLM API 现实是 RPM + TPM 双限；我给 `try_acquire(cost)` 带 cost 参数，两者同一套代码。
2. 超限行为：立即拒绝返回 retry_after（server 端标准），还是阻塞等待（client 端 self-throttle）？默认前者。
3. key 维度：per API key？还有 per-tenant 全局？——默认 per-key，多维 = 多个 limiter 串联都过才放行。
4. burst 允许多少？——capacity 就是这个业务参数，冷启动满桶还是空桶要问（我默认满桶）。
5. 先单机做对，分布式作为 follow-up 讲？——确认递进顺序，避免一上来写 Redis。

## 参考实现（已运行验证通过）

```python
import math
import threading
import time


class TokenBucket:
    """单 key 令牌桶。capacity 决定 burst 上限，refill_rate 决定平均速率。
    Lazy refill：没有后台线程，每次请求时按流逝时间补发令牌。"""

    __slots__ = ("capacity", "refill_rate", "tokens", "last_refill", "lock", "clock")

    def __init__(self, capacity: float, refill_rate: float, clock=time.monotonic):
        assert capacity > 0 and refill_rate > 0
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)   # tokens / second
        self.tokens = float(capacity)           # 满桶启动：允许冷启动 burst
        self.clock = clock                      # 时钟可注入：测试冻结时间
        self.last_refill = clock()
        self.lock = threading.Lock()

    def _refill(self, now: float) -> None:
        elapsed = max(0.0, now - self.last_refill)  # monotonic 恒 >=0，防御 wall clock 回拨
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

    def try_acquire(self, cost: float = 1.0) -> tuple[bool, float]:
        """非阻塞。返回 (allowed, retry_after_seconds)。cost>1 支持按 token 计费的 TPM 限流。"""
        if cost > self.capacity:
            raise ValueError(f"cost {cost} > capacity {self.capacity}: never satisfiable")
        with self.lock:                          # 临界区只有算术：无 I/O、无嵌套锁
            now = self.clock()
            self._refill(now)
            if self.tokens >= cost:
                self.tokens -= cost
                return True, 0.0
            return False, (cost - self.tokens) / self.refill_rate


class RateLimiter:
    """多租户限流器：每个 key 一个 bucket。锁分两级——
    registry 锁只护 dict 结构（创建，短临界区），计数走 per-bucket 锁：
    不同 key 互不阻塞，热点争用被隔离在单个 key 内。"""

    def __init__(self, capacity: float = 10, rate: float = 5.0, clock=time.monotonic):
        self._defaults = (capacity, rate)
        self._clock = clock
        self._buckets: dict[str, TokenBucket] = {}
        self._overrides: dict[str, tuple[float, float]] = {}  # per-tenant 配额
        self._registry_lock = threading.Lock()

    def set_quota(self, key: str, capacity: float, rate: float) -> None:
        with self._registry_lock:
            self._overrides[key] = (capacity, rate)
            self._buckets.pop(key, None)         # 下次请求按新配额重建

    def _get_bucket(self, key: str) -> TokenBucket:
        bucket = self._buckets.get(key)          # fast path：CPython dict 读原子，无锁
        if bucket is None:
            with self._registry_lock:
                bucket = self._buckets.get(key)  # double-check：防两线程同时 miss 建两个桶
                if bucket is None:
                    cap, rate = self._overrides.get(key, self._defaults)
                    bucket = self._buckets[key] = TokenBucket(cap, rate, self._clock)
        return bucket

    def allow(self, key: str, cost: float = 1.0) -> tuple[bool, float]:
        return self._get_bucket(key).try_acquire(cost)


def handle_request(limiter: RateLimiter, api_key: str, cost: float = 1.0):
    """HTTP 中间件形态：拒绝 = 429 + Retry-After header + 结构化 error body。"""
    allowed, retry_after = limiter.allow(api_key, cost)
    if allowed:
        return 200, {}, None
    body = {"error": {"code": "rate_limit_exceeded", "retryable": True,
                      "retry_after": retry_after}}
    return 429, {"Retry-After": str(math.ceil(retry_after))}, body


if __name__ == "__main__":
    t = [0.0]
    clock = lambda: t[0]                         # 冻结时钟：测试确定性

    rl = RateLimiter(capacity=5, rate=2.0, clock=clock)
    # 1) 冷启动 burst：满桶连过 5 个，第 6 个拒绝且 retry_after 精确
    assert all(rl.allow("A")[0] for _ in range(5))
    ok, ra = rl.allow("A")
    assert not ok and abs(ra - 0.5) < 1e-9       # 缺 1 token / 2 per s = 0.5s
    # 2) 租户隔离：A 打空不影响 B
    assert rl.allow("B")[0]
    # 3) refill 按 elapsed 补发
    t[0] += 1.0                                  # +2 tokens
    assert rl.allow("A")[0] and rl.allow("A")[0] and not rl.allow("A")[0]
    # 4) capacity 封顶：闲置 1 小时也只攒 5 个
    t[0] += 3600.0
    assert sum(1 for _ in range(10) if rl.allow("A")[0]) == 5
    # 5) 并发不超卖：冻结时钟（无 refill），8 线程抢同一 key 的 5 个 token
    rl2 = RateLimiter(capacity=5, rate=1.0, clock=clock)
    counts = [0] * 8
    def worker(i):
        for _ in range(50):
            if rl2.allow("hot-key")[0]:
                counts[i] += 1
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for th in threads: th.start()
    for th in threads: th.join()
    assert sum(counts) == 5, counts
    # 6) 429 语义
    status, headers, body = handle_request(rl2, "hot-key")
    assert status == 429 and int(headers["Retry-After"]) >= 1
    assert body["error"]["retryable"] is True
    print("all tests passed")
```

## 边界与测试要点

必须口头提或写进 test：
- **不超卖**：并发测试冻结时钟（rate 再高也不 refill），否则断言不稳定——这个测试设计本身就是加分点。
- **capacity 封顶**：闲置很久 tokens 不能超过 capacity——漏 `min(capacity, ...)` 是本题最常见 bug。
- **`cost > capacity`**：永远无法满足，raise 而不是让调用方无限等一个不可能的 retry_after。
- **时钟回拨**：`time.time` 会被 NTP 回拨成负 elapsed；用 `monotonic` 根治 + `max(0.0, ·)` 防御。
- **浮点累积误差**：长期运行 tokens 有 float 漂移；要求严格时用整数微令牌（token * 1e6）。
- **闲置 bucket 泄漏**：百万个一次性 key 会撑爆 dict——bucket 记 `last_refill`，后台定期回收 `now - last_refill > TTL` 且满桶的（满桶 = 删了重建语义等价，无损）。

## 高频 follow-up 与应对

**1. 为什么两级锁？全局一把锁不行吗？**（follow-up 1：线程安全）
"全局锁下所有租户串行，一个热点 key 拖慢所有人；per-bucket 锁把争用隔离在同 key 内，registry 锁只在首次创建时拿（double-check 防止两线程同时 miss 各建一个桶、丢掉计数）。临界区里只有算术没有 I/O，持锁时间纳秒级。再往下是 lock-free：把 (tokens, last_refill) 打包做 CAS 循环（Go/Java 的 atomic），Python 有 GIL 用 Lock 已够。asyncio 版本单事件循环内本来就无并发，只要保证临界区内没有 await 点——本实现直接满足。"

**2. 突发流量 vs 平均速率怎么同时限？**（题库原追问）
"token bucket 天生同时表达两者：capacity 是 burst 预算，rate 是长期平均。若要求'平均 100 QPS 且任意 1 秒不超 20'：**串联两个桶**，大桶 (capacity=200, rate=100) 管平均，小桶 (capacity=20, rate=20) 管瞬时，都通过才放行。实现要点：两桶要么按固定顺序 check-then-commit（先都判断再都扣），要么第一桶扣了第二桶拒时把 token 还回去，否则会凭空烧配额。LLM API 现实就是 RPM + TPM + 并发数三个独立 limiter 串联。"

**3. 多机分布式怎么做？**（follow-up 2）
"状态收敛到 Redis，判定逻辑放进 Lua 脚本——Redis 单线程执行脚本，整段 read-modify-write 原子，无竞态：

```lua
-- KEYS[1]=bucket key; ARGV = capacity, rate, cost, ttl
local now = redis.call('TIME')               -- 用 Redis 自己的时钟：单一时钟源
local now_s = now[1] + now[2] / 1e6
local d = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens = math.min(tonumber(ARGV[1]),
    (tonumber(d[1]) or tonumber(ARGV[1])) + (now_s - (tonumber(d[2]) or now_s)) * tonumber(ARGV[2]))
local allowed = tokens >= tonumber(ARGV[3])
if allowed then tokens = tokens - tonumber(ARGV[3]) end
redis.call('HMSET', KEYS[1], 'tokens', tokens, 'ts', now_s)
redis.call('EXPIRE', KEYS[1], ARGV[4])       -- 闲置 key 自动回收
return {allowed and 1 or 0, tostring((tonumber(ARGV[3]) - tokens) / tonumber(ARGV[2]))}
```

代价是每请求一次 RTT。降 RTT：**本地配额预取**——每节点先向 Redis 批量领一块配额在本地内存扣，用完再领，牺牲精度换延迟。备选架构：一致性哈希把 key 固定路由到某台 limiter 节点做纯内存桶（无共享存储，但节点挂了该分片限流失效）。这引出 **fail-open vs fail-closed**：Redis 不可用时，保护下游脆弱服务选 fail-closed（拒绝），面向用户的 API 通常 fail-open + 降级到本地保守限额 + 告警。"

**4. sliding window 实现与 trade-off？**（follow-up 3）
"先说 fixed window 的缺陷：窗口边界两侧可各打满 → 瞬时 2x 突破。两种滑窗修复：
- **sliding window log**：每请求 timestamp 存 Redis ZSET，`ZREMRANGEBYSCORE` 清过期 + `ZCARD` 计数。**精确**，但内存 O(窗口内请求数)，高 QPS 不可承受。适合低频高价值操作（登录尝试、密码重置）。
- **sliding window counter**：只存当前/上一窗口两个计数，`count = prev × (窗口剩余占比) + cur` 线性加权。**O(1) 内存**，误差来自'假设上窗口内请求均匀分布'（Cloudflare 生产用的就是这个近似）。适合高频 API。
和 token bucket 怎么选：bucket 表达 burst 语义更自然（capacity 就是产品参数），滑窗表达'每分钟最多 N 次'的合规/计费语义更直白。"

**5. load shedding 怎么做？**（follow-up 4）
"rate limiting 是 per-key 公平，load shedding 是全局过载自保，两层都要。(a) **优先级分层**：interactive > batch > retry 流量，过载从低优先级开始丢；(b) 429 必带 Retry-After 把重试错峰，client 侧要求 jitter，否则全体同步重试 → retry storm；(c) **拒绝优于无界排队**：bounded queue + 排队 deadline，超时直接 429——排队把延迟传染给所有人，比拒绝更伤；(d) agent 场景特有：一个 agent run 放大成几十个 tool call，shed 要按 **run 级别**暂停整个 run，而不是随机丢单个请求让 run 半死不活地烧预算。"

**6. 429 之后 client（agent）侧怎么配合？**
"server 端返回结构化 error：`code/message/retryable/retry_after`——这是 [../../01_core/01_loop_and_tools.md](../../01_core/01_loop_and_tools.md) 好工具 checklist 的原文要求。agent 侧按同文件的 retry matrix 走：read + transient 429/5xx → bounded exponential backoff + jitter，且有 `Retry-After` 时把它当 backoff 下限尊重，不要自作聪明地更早重试；write 且 provider 无幂等 → timeout 后进 unknown，不自动重复。关键一句：**429 应该在 tool executor 层消化（sleep + 同 key retry），不要原样回传模型让它'决定要不要重试'**——烧 token、更慢，模型也没有比 deterministic backoff 更好的策略；只有 retry 预算耗尽才把结构化错误交给模型/用户去改变计划。"

**7. 时钟漂移对分布式窗口的影响？**（题库原追问）
"单机：`time.time` 会被 NTP 回拨，refill 算出负 elapsed——`monotonic` 根治。分布式：绝不让各节点用本地时钟写共享状态，上面 Lua 用 `redis.call('TIME')` 让所有时间读数来自同一时钟源，节点间漂移就无关紧要了。如果是各节点本地滑窗再聚合的架构，漂移会让窗口边界错位、计数漏算/重算——这正是把状态和时钟一起收敛到 Redis 的理由。跨机时间语义再深入：单调 seq 与物理时间分开存的原则同 [../../02_playbook.md](../../02_playbook.md) 第四节 TraceEvent。"

## 如果这轮允许 AI：怎么驾驶

按 [../../02_playbook.md](../../02_playbook.md) 第八节：先自己口述验收 1–6（尤其"冻结时钟不超卖"这条测试设计），再让 AI 一次只做一个窄任务（"写 TokenBucket.try_acquire，语义如下，附 assert"）。AI 产出重点自查三处：refill 有没有 `min(capacity, ·)` 封顶、用的是 `monotonic` 还是 `time.time`、锁是不是退化成了全局一把——这三处是 AI 按"教科书 rate limiter"套错的高发点。并发测试自己跑，结果自己念。
