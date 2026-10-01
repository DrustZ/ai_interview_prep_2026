"""Drill E · 流式分位数:桶压缩、相对误差、可合并 sketch

⏱ timebox 25 分钟  ｜  概率评级:★★★★★(**这题 Exa 真考过**)

为什么是这道题:2026-07-28 Exa 第一轮技术面的实际题目——
「给一个 stream,怎么返回任意 percentile」。
推导路线:全排序 -> 压缩空间 -> 分桶 -> 引入误差容忍 -> **log 分桶**。
这就是 DDSketch。

搜索系统里到处都是这个东西:p50/p99 延迟监控、召回分数分布、
每查询成本分布。而且 agent 会连着搜 5~30 次,尾延迟被放大
(单次 p99=1% -> 30 次里至少撞一次的概率 1-0.99^30 ≈ 26%),
所以「分位数怎么算」在 agentic search 里不是运维小事。

冷写协议:
    cp drill_e_streaming_quantile.py scratch.py  -> 删实现体 -> 计时 25 分钟

面试时必须能顺口说出来的四句:
    1. 延迟跨几个数量级,所以要的是**相对误差**(p99 误差 1%)而不是
       绝对误差(误差 1ms)。-> 桶宽随值指数增长 -> log 分桶
    2. 桶索引就是 i = ceil( log(x) / log(gamma) ),gamma = (1+a)/(1-a)
    3. 桶数 = ln(max/min) / ln(gamma)。a=1%、值域 1ms~100s -> **约 575 个桶**
       (不到 5KB) 就能覆盖全部延迟,这就是「压缩空间」的答案
    4. **必须可合并(mergeable)**:每台机器一个 sketch,中心节点相加。
       百分位数本身不能跨机平均,sketch 可以。分布式监控里这是硬需求
"""

import math
import random

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def exact_quantile(values, q: float) -> float:
    """参考实现:全排序取第 ceil(q*(n-1)) 个(0-indexed,nearest-rank 风格)。

    O(n) 空间、O(n log n) 时间 —— 面试里先写这个,再说为什么不够。
    """
    if not values:
        raise ValueError("空流没有分位数")
    s = sorted(values)
    rank = math.ceil(q * (len(s) - 1))
    return s[rank]


class FixedBucketSketch:
    """固定宽度分桶 —— 「压缩空间」的第一版,也是用来暴露问题的对照组。

    桶数 = 值域 / 宽度。想在 1ms 处也有 1ms 精度,又要覆盖到 100s,
    就需要 100_000 个桶。**绝对误差恒定 = 小值处相对误差爆炸**。
    """

    def __init__(self, width: float):
        self.width = width
        self.buckets = {}
        self.count = 0

    def add(self, x: float) -> None:
        i = int(x // self.width)
        self.buckets[i] = self.buckets.get(i, 0) + 1
        self.count += 1

    def quantile(self, q: float) -> float:
        rank = math.ceil(q * (self.count - 1))
        cum = 0
        for i in sorted(self.buckets):
            cum += self.buckets[i]
            if cum > rank:
                return (i + 0.5) * self.width     # 桶中点
        raise ValueError("不该到这里")

    def n_buckets(self) -> int:
        return len(self.buckets)


class DDSketch:
    """log 分桶,保证**相对误差** <= alpha,且可合并。

    桶 i 覆盖区间 (gamma^(i-1), gamma^i],代表值取 2*gamma^i / (gamma+1)。
    这个代表值让区间两端的相对误差相等,都正好是 alpha:
        右端 x=gamma^i    : 1 - 2/(gamma+1)     = (gamma-1)/(gamma+1) = alpha
        左端 x=gamma^(i-1): 2*gamma/(gamma+1)-1 = (gamma-1)/(gamma+1) = alpha
    所以 gamma = (1+alpha)/(1-alpha) 不是凑出来的,是解出来的。
    """

    def __init__(self, alpha: float = 0.01):
        if not 0 < alpha < 1:
            raise ValueError("alpha 必须在 (0,1)")
        self.alpha = alpha
        self.gamma = (1 + alpha) / (1 - alpha)
        self.log_gamma = math.log(self.gamma)
        self.buckets = {}        # 桶索引 -> 计数
        self.zero_count = 0      # 0 不能取 log,单独记
        self.count = 0

    # ---- 写入 ----------------------------------------------------------
    def _index(self, x: float) -> int:
        return math.ceil(math.log(x) / self.log_gamma)

    def add(self, x: float) -> None:
        if x < 0:
            # 负值要用一组镜像桶。延迟/分数都非负,面试里说明这个假设即可。
            raise ValueError("这一版只处理非负值")
        self.count += 1
        if x == 0.0:
            self.zero_count += 1
            return
        i = self._index(x)
        self.buckets[i] = self.buckets.get(i, 0) + 1

    # ---- 查询 ----------------------------------------------------------
    def _value(self, i: int) -> float:
        return 2.0 * self.gamma ** i / (self.gamma + 1.0)

    def quantile(self, q: float) -> float:
        """返回 x~,保证 |x~ - x_q| <= alpha * x_q,x_q 是真实的第 q 分位元素。

        桶内计数是精确的,所以「累计计数跨过 rank 的那个桶」
        **就是**真实第 q 分位元素所在的桶 —— 误差只来自桶内取代表值。
        """
        if self.count == 0:
            raise ValueError("空 sketch")
        rank = math.ceil(q * (self.count - 1))
        if rank < self.zero_count:
            return 0.0
        cum = self.zero_count
        for i in sorted(self.buckets):
            cum += self.buckets[i]
            if cum > rank:
                return self._value(i)
        return self._value(max(self.buckets))

    # ---- 合并 ----------------------------------------------------------
    def merge(self, other: "DDSketch") -> "DDSketch":
        """桶索引只由 (alpha, x) 决定,与插入顺序和数据划分无关
        -> 同 alpha 的两个 sketch 直接逐桶相加。这是分布式聚合的全部秘密。"""
        if abs(other.alpha - self.alpha) > 1e-12:
            raise ValueError("alpha 不同的 sketch 不能合并")
        out = DDSketch(self.alpha)
        out.buckets = dict(self.buckets)
        for i, c in other.buckets.items():
            out.buckets[i] = out.buckets.get(i, 0) + c
        out.zero_count = self.zero_count + other.zero_count
        out.count = self.count + other.count
        return out

    # ---- 空间 ----------------------------------------------------------
    def n_buckets(self) -> int:
        return len(self.buckets) + (1 if self.zero_count else 0)

    def bucket_bound(self, lo: float, hi: float) -> int:
        """理论桶数上界:覆盖 [lo, hi] 需要 ln(hi/lo) / ln(gamma) 个桶。
        **这是「压缩空间」那一问的定量答案。**"""
        return math.ceil(math.log(hi / lo) / self.log_gamma)


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _latency_stream(n: int, seed: int = 0):
    """模拟真实延迟:对数正态主体 + 1% 的长尾。跨约 4 个数量级。"""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        if rng.random() < 0.01:
            out.append(rng.lognormvariate(math.log(2000), 0.8))   # 尾:~2s
        else:
            out.append(rng.lognormvariate(math.log(30), 0.7))     # 主体:~30ms
    return out


def _check():
    N = 200_000
    xs = _latency_stream(N)
    qs = [0.5, 0.9, 0.99, 0.999]

    # ---- 1. DDSketch 的相对误差保证 ----
    alpha = 0.01
    dd = DDSketch(alpha)
    for x in xs:
        dd.add(x)

    print("q       exact       DDSketch    相对误差")
    for q in qs:
        e = exact_quantile(xs, q)
        a = dd.quantile(q)
        rel = abs(a - e) / e
        print("{:<7} {:>10.3f}  {:>10.3f}  {:>8.4%}".format(q, e, a, rel))
        # 1.001 的余量给浮点 log 在桶边界上的抖动
        assert rel <= alpha * 1.001, "q={} 相对误差 {:.4%} 超过 alpha".format(q, rel)

    # ---- 2. 空间:log 桶 vs 固定桶 ----
    fixed = FixedBucketSketch(width=1.0)       # 1ms 宽,才能在小值处有精度
    for x in xs:
        fixed.add(x)
    print("\n空间对比({} 个样本,值域 {:.1f} ~ {:.1f} ms)".format(
        N, min(xs), max(xs)))
    print("  全排序               : {:>7} 个数".format(N))
    print("  固定桶(1ms,实际占用) : {:>7} 个桶".format(fixed.n_buckets()))
    print("  DDSketch(1%,实际占用): {:>7} 个桶".format(dd.n_buckets()))
    print("  —— 最坏情况(覆盖 1ms~100s 全值域,不靠数据稀疏)——")
    print("  固定桶(1ms)          : {:>7} 个桶".format(100_000))
    print("  DDSketch(1%)         : {:>7} 个桶".format(
        dd.bucket_bound(1.0, 100_000.0)))
    # 注意:两者都用 dict 稀疏存储,所以实测差距(~4x)远小于最坏情况差距(~170x)。
    # 真正的结论是**最坏情况有界**:固定桶的桶数随值域线性增长、无上界可言,
    # log 桶随值域**对数**增长。稀疏性只是掩盖了这一点。
    assert dd.n_buckets() < fixed.n_buckets(), "占用桶数 log 桶也应更少"
    assert dd.bucket_bound(1.0, 100_000.0) < 100_000 / 100, \
        "最坏情况下 log 桶应该省两个数量级"

    # ---- 3. 固定桶在小值处相对误差爆炸(这是它被淘汰的原因) ----
    tiny = [0.08, 0.12, 0.2, 0.35, 0.6]        # 亚毫秒:全落进固定桶的第 0 桶
    f2 = FixedBucketSketch(width=1.0)
    d2 = DDSketch(alpha)
    for x in tiny:
        f2.add(x)
        d2.add(x)
    ex = exact_quantile(tiny, 0.5)
    rel_fixed = abs(f2.quantile(0.5) - ex) / ex
    rel_dd = abs(d2.quantile(0.5) - ex) / ex
    print("\n亚毫秒区间的 p50(exact={:.2f})".format(ex))
    print("  固定桶相对误差: {:.1%}".format(rel_fixed))
    print("  DDSketch      : {:.3%}".format(rel_dd))
    assert rel_fixed > 0.1 and rel_dd <= alpha * 1.001

    # ---- 4. 可合并:分片后合并 == 一次性灌入 ----
    shards = [DDSketch(alpha) for _ in range(4)]
    for j, x in enumerate(xs):
        shards[j % 4].add(x)
    merged = shards[0]
    for s in shards[1:]:
        merged = merged.merge(s)
    assert merged.count == dd.count
    for q in qs:
        assert merged.quantile(q) == dd.quantile(q), "合并必须与整体一致"
    print("\n4 分片合并 == 单机整体:全部分位数逐一相等 ✓")

    # ---- 5. 平均值不能替代分位数(顺带反驳一个常见提议) ----
    shard_p99 = [s.quantile(0.99) for s in shards]
    avg_of_p99 = sum(shard_p99) / len(shard_p99)
    true_p99 = exact_quantile(xs, 0.99)
    print("\n把各分片 p99 直接平均 = {:.1f},真 p99 = {:.1f},偏差 {:.1%}"
          .format(avg_of_p99, true_p99, abs(avg_of_p99 - true_p99) / true_p99))
    print("(这里分片是随机均分所以还算接近;按机器/地域分片时会差很多"
          " —— 所以要合并 sketch,不是平均分位数)")

    print("\nDrill E 全部断言通过")


if __name__ == "__main__":
    _check()
    print("""
================ 面试追问预演 ================
Q: 为什么不用 reservoir sampling?
A: 可以,而且实现更简单、支持任意分位数和其他统计量。但它的误差是**采样误差**,
   在 p99.9 这种极尾部,样本里可能只有几个点 -> 方差极大。
   DDSketch 对每个分位数都给**确定性**的相对误差上界,尾部同样成立。
   要 p999 的稳定值就用 sketch,要灵活的探索性分析就用 reservoir。

Q: t-digest 呢?
A: 同类工具。t-digest 用可变大小的质心,**尾部精度高、中位数附近相对松**,
   而且误差是经验性的、没有 DDSketch 那样的严格相对误差保证。
   合并 t-digest 还需要重新压缩质心,不是简单相加。
   选型:要严格 SLO 保证 -> DDSketch;要固定内存上限 -> t-digest。

Q: 桶会无限增长吗?
A: 理论上界是 ln(max/min)/ln(gamma),对延迟这种有物理上下界的量是有界的
   (1%误差、1ms~100s 只要约 575 个桶)。真要硬上限,就设 max_bins,
   超了把最小的几个桶折叠进一个「下溢桶」—— 牺牲小值精度换固定内存,
   对延迟监控完全可接受,因为你关心的是尾部。

Q: 怎么做滑动窗口(只要最近 5 分钟)?
A: 分桶时间片:每分钟一个 sketch,查询时合并最近 5 个,过期的丢掉。
   **可合并性在这里第二次救场** —— 这就是为什么 mergeable 是硬需求而不是加分项。

Q: 并发写怎么办?
A: 每线程一个 sketch,查询时合并(第三次)。桶是纯计数,无锁累加也行。
   这比对一个共享结构加锁快得多,也是 sketch 相对「保留全部样本」的
   另一个工程优势。

Q: 这跟 Exa 有什么关系?
A: ① 搜索的 SLO 是 p99 不是均值,agent 连搜 30 次会把尾延迟放大到 26% 的
     任务受影响;② 多路索引赛跑 = hedged request,是用算力换 p99,
     要不要 hedge 得先能准确量 p99;③ 相同的结构也用来监控召回分数分布和
     每查询成本分布的漂移。
""")
