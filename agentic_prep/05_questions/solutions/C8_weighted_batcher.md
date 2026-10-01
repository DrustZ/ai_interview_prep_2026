# [C8] Anthropic：Weighted DataBatcher with Deterministic Checkpointing · 参考实现

⏱ 读完 12 min ｜ 建议先按 55 分钟时间盒盲写一遍再对照（盲看解答记不住）。题面原文见 [../C_live_ai_coding.md](../C_live_ai_coding.md#c8)，完整 rubric 见 [../../../agentic/data/questions.json](../../../agentic/data/questions.json) → `q-anthropic-weighted-batcher`。

## 题目还原 + 验收标准

实现 `DataBatcher(registry, weights, seed)`：`next_batch(k)` 按权重选数据源并取样；`checkpoint()` 返回**可序列化** state；新实例 `resume(state)` 后必须产生与未中断运行**完全相同**的后续样本流。说明动态增删数据源和 multi-worker 语义。rubric 权重：确定性语义 30%、状态模型 25%、sampling 正确性 20%、edge cases 15%、测试 10%。

验收标准（写代码前口头列给面试官）：
1. **split-run 等价**：跑 5 个 batch → checkpoint → 新实例 resume → 再跑 7 个，拼接结果 == 一口气跑 12 个
2. checkpoint 必须过 `json.loads(json.dumps(state))` round-trip（"可序列化"要真测，不是口头承诺）
3. 跨源按权重**有放回**采样；单源内每 epoch 洗牌**无放回**遍历，epoch 边界自动重洗（标准 data-loading 语义，0–6 min 先跟面试官确认）
4. resume 时 registry 与 checkpoint 指纹不符 → 显式拒绝，绝不静默错位
5. 空 source、非正权重、registry/weights key 不一致 → 构造时报错
6. resume 是 fixed point：resume 后立刻 checkpoint 得到等价 state

## 解题主线（55 分钟时间盒，rubric pacing）

- **0–6 锁定语义**：四个澄清问题——有放回还是按 source epoch 循环？offset 是全局随机步还是每源游标（答：都要——全局 RNG state + 每源 cursor/epoch）？恢复时 registry snapshot 是否保证不变？多 worker 要无重复还是只要可复现？
- **6–12 状态模型**（本题 55% 的分在这，先讲再写）：把确定性拆成三个来源分开管理——(a) **选源随机流** = 有状态的 `random.Random(seed)`，`getstate()` 进 checkpoint；(b) **每源 epoch 洗牌** = 纯函数 `Random(f"{seed}:{source}:{epoch}")`，无状态可丢，resume 后重算；(c) **游标** = 每源 `{cursor, epoch}` 两个整数。checkpoint 只存**不可重建的最小状态**：rng state + cursors + registry fingerprint + 原始 weights；洗牌结果是派生状态，不进 checkpoint。
- **12–35 核心实现**：`_fingerprint` → `__init__`（归一化 + cumsum）→ `_draw_source`（bisect）→ `_draw_item`（epoch 边界）→ `next_batch` → `checkpoint`/`resume`。
- **35–45 恢复与动态数据源**：fingerprint 拒绝策略 + migration policy（见 follow-up）。
- **45–51 等价序列测试**：先写 split-run 测试——这是本题唯一"必须写出来跑"的测试。
- **51–55 复杂度总结**：采样 O(log S) per sample（S=源数），checkpoint O(S + RNG state)，resume O(S)。

来不及的砍法（口述代替实现）：内容哈希 fingerprint 降级为 `(name, len)`；perm 缓存（先每次重算，说明是 O(n) 待优化）。**不能砍**：rng state 序列化、`sorted(registry)` 消除 dict 序依赖、split-run 测试。

## 参考实现

```python
import bisect, hashlib, itertools, json, random

def _fingerprint(registry):
    """registry 的确定性内容指纹; resume 时校验数据没被动过."""
    h = hashlib.sha256()
    for name in sorted(registry):
        h.update(name.encode())
        h.update(json.dumps(registry[name], separators=(",", ":")).encode())
    return h.hexdigest()

def _epoch_perm(seed, source, epoch, n):
    """每 (seed, source, epoch) 的确定性洗牌 —— 纯函数, 无状态可丢."""
    r = random.Random(f"{seed}:{source}:{epoch}")  # str seeding 走 sha512, 跨平台确定
    perm = list(range(n))
    r.shuffle(perm)
    return perm

class DataBatcher:
    def __init__(self, registry, weights, seed):
        if set(registry) != set(weights):
            raise ValueError("registry and weights must cover the same sources")
        self.sources = sorted(registry)          # 确定性顺序, 不依赖 dict 插入序
        for s in self.sources:
            if not registry[s]:
                raise ValueError(f"empty source: {s}")
            if weights[s] <= 0:
                raise ValueError(f"non-positive weight for {s}")
        self.registry = registry
        self._orig_weights = {s: weights[s] for s in self.sources}
        total = float(sum(self._orig_weights.values()))
        self.probs = [self._orig_weights[s] / total for s in self.sources]
        self.cum = list(itertools.accumulate(self.probs))
        self.seed = seed
        self._rng = random.Random(seed)          # 唯一有状态的随机流: 选源
        self._pos = {s: {"cursor": 0, "epoch": 0} for s in self.sources}
        self._perm = {}                          # 派生状态缓存, 不进 checkpoint
        self._fp = _fingerprint(registry)

    def _draw_source(self):
        i = bisect.bisect_right(self.cum, self._rng.random())
        return self.sources[min(i, len(self.sources) - 1)]  # min 防浮点边界越界

    def _draw_item(self, s):
        data, pos = self.registry[s], self._pos[s]
        if pos["cursor"] >= len(data):           # epoch 边界: 重洗进入下一 epoch
            pos["cursor"], pos["epoch"] = 0, pos["epoch"] + 1
            self._perm.pop(s, None)
        if s not in self._perm:
            self._perm[s] = _epoch_perm(self.seed, s, pos["epoch"], len(data))
        item = data[self._perm[s][pos["cursor"]]]
        pos["cursor"] += 1                       # 每次 draw 后状态自洽 (可随时快照)
        return item

    def next_batch(self, k):
        return [self._draw_item(self._draw_source()) for _ in range(k)]

    def checkpoint(self):
        st = self._rng.getstate()                # (version, 625 个 int 的 tuple, gauss)
        return {
            "fingerprint": self._fp,
            "seed": self.seed,
            "weights": self._orig_weights,       # 存原始值, 不存归一化后的 (见下)
            "rng": [st[0], list(st[1]), st[2]],  # tuple -> list, 才能 JSON 序列化
            "pos": self._pos,
        }

    @classmethod
    def resume(cls, registry, state):
        if _fingerprint(registry) != state["fingerprint"]:
            raise ValueError("registry changed since checkpoint; refusing to resume")
        b = cls(registry, state["weights"], state["seed"])   # 归一化走同一条代码路径
        b._rng.setstate((state["rng"][0], tuple(state["rng"][1]), state["rng"][2]))
        b._pos = {s: dict(p) for s, p in state["pos"].items()}
        return b
```

两处最容易被追问的设计判断，主动讲：
- **浮点坑**：checkpoint 存**原始** weights 而非归一化后的。归一化后的 probs 和 ≈1.0 但不精确，若 resume 时再除一次这个和，cum 数组会逐位漂移，`bisect` 在边界上可能选到不同的源——确定性悄悄碎掉。存原始值 + resume 走与 `__init__` 完全相同的归一化路径 → cum 逐位相同。
- **为什么不 pickle 整个对象**：checkpoint 应只含状态不含数据（registry 可能几百 GB）；pickle 反序列化执行任意代码，训练集群里 checkpoint 常跨信任边界传输；JSON state + 显式字段还能做版本演进。跨 Python 版本风险主动点一句：Mersenne Twister 算法和 str-seeding（sha512）都稳定，谨慎起见可在 state 里记 `sys.version` 拒绝跨大版本恢复。

## 边界与测试要点

```python
if __name__ == "__main__":
    registry = {"web": [f"w{i}" for i in range(7)],
                "code": [f"c{i}" for i in range(3)],
                "math": [f"m{i}" for i in range(5)]}
    weights = {"web": 5.0, "code": 1.0, "math": 2.0}

    # 核心测试: checkpoint 前后拼接 == 不中断序列 (面试必写)
    b1 = DataBatcher(registry, weights, seed=42)
    full = [b1.next_batch(4) for _ in range(12)]
    b2 = DataBatcher(registry, weights, seed=42)
    head = [b2.next_batch(4) for _ in range(5)]
    state = json.loads(json.dumps(b2.checkpoint()))   # 真过一遍序列化
    b3 = DataBatcher.resume(registry, state)
    tail = [b3.next_batch(4) for _ in range(7)]
    assert head + tail == full, "split-run must equal uninterrupted run"

    # 每源每 epoch 是一个 permutation (无放回语义)
    flat = [x for batch in full for x in batch]
    for s, items in registry.items():
        seen = [x for x in flat if x in items]; n = len(items)
        for e in range(len(seen) // n):
            assert sorted(seen[e*n:(e+1)*n]) == sorted(items)

    # registry 变了 -> 拒绝恢复
    changed = dict(registry); changed["web"] = registry["web"] + ["w_new"]
    try: DataBatcher.resume(changed, state); assert False
    except ValueError: pass

    # resume 是 fixed point: resume 后立刻 checkpoint == 原 state
    b5 = DataBatcher.resume(registry, state)
    assert json.loads(json.dumps(b5.checkpoint())) == state
    print("all tests pass")
```

没时间写就口头点到：`k=0` 返回空 batch；k 大于最小源的大小时一个 batch 内跨 epoch（`code` 只有 3 条，batch=4 就会触发）；单一源（权重退化为 1.0）；weights 全相等时退化为均匀采样；两个不同 seed 的实例序列不同（防止 seed 根本没接进去的低级 bug）；checkpoint 在任意 batch 边界做、任意次做，结果都一致。

## 高频 follow-up 与应对

- **checkpoint 正好发生在 batch 一半怎么办？** 分两层答。API 层：`next_batch` 是原子单位，单线程 iterator 契约下 `checkpoint()` 只会在两次 `next_batch` 之间被调用，state 永远一致。crash 层：磁盘上的 checkpoint 停留在"上一个已 commit 的 batch 之后"，resume 会**完整重发**未 checkpoint 的 batch——语义是重发而不是跳过；训练端必须把 batcher state 和 model weights **原子地**存进同一个 checkpoint（同一文件 / 先写临时文件再 rename），否则会出现"权重是 step 100 的、数据流是 step 95 的"这种静默污染。真要 mid-batch 快照（超大 batch streaming 场景）：本实现每次 `_draw_item` 后状态已自洽，把 `next_batch` 改成 generator、state 里加一个 `batch_offset` 即可。
- **百万数据源如何高效 weighted choice？** 现在是 cumsum + bisect：采样 O(log S)，但权重更新要重建 O(S)。静态权重 → **alias table**：O(S) 构建、O(1) 采样；确定性不受影响，因为构建算法确定、每个样本固定消耗两次 rng draw（draw 次数固定 → 随机流可精确续上）。动态权重 → **Fenwick/segment tree** 存前缀和：采样和更新都 O(log S)。同时指出 checkpoint 里的 per-source cursor 表变成 O(S)，要分片存储或换成"只存被采过的源"的稀疏表示。
- **worker 扩缩容如何保持 shard 稳定？** 先澄清语义：只要可复现，还是要全局无重复？标准答案是 **virtual shards**：固定 V 个虚拟分片（V >> 最大 worker 数），每片一个独立 DataBatcher——`seed = f"{seed}:vshard:{v}"`，registry 按 `hash(item_id) % V` 切分；worker 只是被分配若干 virtual shards 的执行者。扩缩容 = 重新映射 virtual→physical，每个 virtual shard 的样本流和 checkpoint 完全不动。这和 counter-based RNG 是同一个思想：把随机性绑定到稳定的逻辑标识（shard id / step counter）上，而不是绑到易变的物理执行者上。
- **动态增删数据源？** 默认拒绝（fingerprint mismatch 就是干这个的）。要支持就做**显式 migration**：`migrate(state, new_registry, policy)`——幸存源保留 cursor/epoch，新源从 `{cursor:0, epoch:0}` 起步，权重重新归一化，选源随机流从派生 seed 分叉（`f"{seed}:migration:{n}"`），state 里记录 migration lineage。必须主动说清：migration 之后的序列与"从头用新 registry 跑"**不等价**，这是有意的语义选择——目标是"迁移点之后自身确定可复现"，不是全局回放等价。
- **weights 想按 curriculum 随训练进度变？** 把 weights 变成 `f(step)` 的纯函数并把 step 计数进 state，或者每次显式 `set_weights()` 都作为一条记录写进 checkpoint lineage——两种都保住确定性；绝不允许外部代码直接改 `self.probs`。

## 如果这轮允许 AI：怎么驾驶

题库注明 Anthropic 这轮**全程可查文档、禁 AI**——按禁 AI 准备，把 `getstate/setstate` 的 tuple↔list 转换写成肌肉记忆。若真的允许，按 [../../02_playbook.md](../../02_playbook.md) 第八节：验收标准 1–6 和三层状态模型（有状态 rng / 纯函数洗牌 / 游标）是你的设计判断，先自己写在注释里，再让 AI 一次一个窄任务（"实现 resume，含 fingerprint 校验和 rng setstate，附 split-run 等价测试"）。review 专查三处：weights 存的是不是原始值、`sorted(registry)` 有没有丢、JSON round-trip 是不是真的测了——这三处正是 AI 最常偷懒、也正是确定性 30% 分数所在。
