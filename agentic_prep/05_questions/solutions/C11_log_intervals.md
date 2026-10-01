# [C11] Sierra——日志时间区间合并 + overlap/gap 检测 · 参考实现

⏱ 读完 12 min ｜ 建议先限时 25 min 盲写一遍（merge + 两个 bool），再对照本文补 follow-up。题库原文见 [../C_live_ai_coding.md](../C_live_ai_coding.md#c11)。

## 题目还原 + 验收标准

**题面**：n 个 debug 日志段 `(start, end, text)`，**半开区间 `[start, end)`**，n ≤ 200,000。
- **Task 1**：合并重叠区间为 `[min_start, max_end)`，text 按时间顺序空格拼接，按 start 升序返回。
  例：`[(0,5,"A"),(3,10,"B"),(12,15,"C")] -> [(0,10,"A B"),(12,15,"C")]`
- **Task 2**：返回两个 bool——(a) 是否存在任意一对区间交集非空；(b) 最早 start 与最晚 end 之间是否存在 gap。同例输出 `(True, True)`。
- 扩展交付（面试官常加）：具体的**重叠对列表**和**间隙列表**。

**验收标准**（写码前口头列出）：
1. 半开区间语义正确：`[1,4)` 与 `[4,6)` **既不算 overlap 也不算 gap**（这是本题最大的坑，开场就说）。
2. 复杂度 O(n log n)：n=200k 不允许 O(n²) 两两比较。
3. text 拼接顺序确定：sort key 用 `(start, end, 原始下标)`，稳定可复述。
4. 空输入返回 `([], False, False)`；单区间 `(merged=自身, False, False)`。
5. overlap/gap 判定与 merge 共用一遍扫描，不写三个独立循环。

## 解题主线（25 min 时间分配）

- **0–4 min 澄清**（见下），当场把"相邻不算 overlap 也不算 gap"确认掉。
- **4–14 min**：写 `merge_coverage`——sort + 单遍扫描，一个函数同时产出 merged、has_overlap、has_gap。先写函数签名和 docstring 再填 body。
- **14–18 min**：跑 4 个测试（题面例、touching、包含关系、空输入）。
- **18–25 min**：加 `gaps()` 和 `overlapping_pairs()`（扩展交付），口头讲流式/时钟偏移 follow-up。
- **可以砍**：`overlapping_pairs` 可以只讲思路不写码；`Segment` dataclass 可换成 tuple。

**开场澄清 4 问**：
1. 相邻段 `[1,4)`+`[4,6)` 在 Task 1 里要不要**合成一个覆盖块**？——半开区间下覆盖是连续的，我默认合并（debug view 展示连续日志更合理）；若只合"真重叠"，改一个 `<=` 为 `<` 即可。
2. start 相同的两段，text 谁在前？——用 `(start, end, 原始下标)` 定序。
3. `start >= end` 的非法/零长段怎么处理？——我默认 raise，也可选择 drop。
4. gap 只看 `[min_start, max_end)` 内部，还是给定观察窗口 `[T0, T1)`？——默认前者，窗口版只需在首尾各补一次比较。

## 参考实现

```python
import heapq
from dataclasses import dataclass


@dataclass(frozen=True)
class Segment:
    start: int  # inclusive
    end: int    # exclusive —— 半开区间 [start, end)
    text: str = ""


def merge_coverage(segments, merge_touching=True):
    """单遍扫描同时完成 Task 1 + Task 2。O(n log n) 排序 + O(n) 扫描。

    返回 (merged, has_overlap, has_gap):
      merged      : list[Segment]，覆盖块，text 按时间顺序空格拼接
      has_overlap : 存在一对区间交集非空（半开区间: prev_end > cur_start）
      has_gap     : [min_start, max_end) 内部存在未覆盖空隙
    merge_touching=True 时相邻块（prev_end == cur_start）合成一个覆盖块，
    但既不计 overlap 也不计 gap —— 半开区间语义。
    """
    for s in segments:
        if s.start >= s.end:
            raise ValueError(f"invalid segment [{s.start}, {s.end})")
    # 原始下标作最终 tie-break：同 (start, end) 时拼接顺序确定
    segs = sorted(segments, key=lambda s: (s.start, s.end))
    if not segs:
        return [], False, False

    merged, has_overlap, has_gap = [], False, False
    cur_start, cur_end, texts = segs[0].start, segs[0].end, [segs[0].text]
    for s in segs[1:]:
        # cur_end 是当前块内的 running max end；排序保证 s.start >= 块内所有 start，
        # 所以 s.start < cur_end 等价于 s 与"取得 max end 的那一段"真相交
        if s.start < cur_end:
            has_overlap = True
        elif s.start > cur_end:
            has_gap = True
        joinable = (s.start <= cur_end) if merge_touching else (s.start < cur_end)
        if joinable:
            cur_end = max(cur_end, s.end)
            texts.append(s.text)
        else:
            merged.append(Segment(cur_start, cur_end, " ".join(t for t in texts if t)))
            cur_start, cur_end, texts = s.start, s.end, [s.text]
    merged.append(Segment(cur_start, cur_end, " ".join(t for t in texts if t)))
    return merged, has_overlap, has_gap


def gaps(merged):
    """间隙列表：相邻覆盖块之间的未覆盖半开区间 [prev.end, cur.start)。"""
    return [(p.end, c.start) for p, c in zip(merged, merged[1:]) if c.start > p.end]


def overlapping_pairs(segments):
    """所有交集非空的原始下标对。O(n log n + K)，K 为答案数。
    注意最坏 K = O(n^2)（全部互相重叠）——输出本身就是瓶颈，先口头说明。"""
    order = sorted(range(len(segments)), key=lambda i: (segments[i].start, segments[i].end))
    active = []  # min-heap of (end, idx)：所有 end > 当前 start 的"仍在延续"的段
    for i in order:
        s = segments[i]
        while active and active[0][0] <= s.start:  # end <= start：半开语义下不相交
            heapq.heappop(active)
        for _end, j in active:  # 留在堆里的每一段都与 s 相交
            yield (j, i)
        heapq.heappush(active, (s.end, i))


if __name__ == "__main__":
    segs = [Segment(0, 5, "A"), Segment(3, 10, "B"), Segment(12, 15, "C")]
    merged, ov, gp = merge_coverage(segs)
    assert [(m.start, m.end, m.text) for m in merged] == [(0, 10, "A B"), (12, 15, "C")]
    assert (ov, gp) == (True, True)
    assert gaps(merged) == [(10, 12)]
    assert sorted(overlapping_pairs(segs)) == [(0, 1)]
    # 相邻：不算 overlap 不算 gap；覆盖块默认合并
    merged, ov, gp = merge_coverage([Segment(1, 4, "x"), Segment(4, 6, "y")])
    assert [(m.start, m.end, m.text) for m in merged] == [(1, 6, "x y")]
    assert (ov, gp) == (False, False)
    # 包含关系：[2,3) 完全在 [0,10) 内 —— overlap 但无 gap，end 不回退
    merged, ov, gp = merge_coverage([Segment(0, 10, "A"), Segment(2, 3, "B")])
    assert (ov, gp) == (True, False) and merged[0].end == 10
    assert merge_coverage([]) == ([], False, False)
    print("all tests passed")
```

## 边界与测试要点

必须口头提或写进 test：
- **相邻段**：`[1,4)`+`[4,6)` → 不 overlap、不 gap、覆盖块合并（三件事分开说）。
- **包含关系**：`[0,10)` 包住 `[2,3)`——`cur_end = max(cur_end, s.end)` 防止 end 回退；漏写 `max` 是本题最常见 bug。
- **同 start**：`(start, end, 原始下标)` 排序，拼接顺序确定。
- **空输入 / 单区间**：`([], False, False)`；单区间无 overlap 无 gap。
- **零长/非法段** `start >= end`：raise（或与面试官约定 drop）。
- **全部互相重叠**：`overlapping_pairs` 输出 O(n²)——如果只要"是否存在"，用 `merge_coverage` 的单遍扫描 O(n log n) 就够，不要真的枚举对。

## 高频 follow-up 与应对

**1. start 相同时 text 拼接定序？**（题库原追问）
完整答法："我排序 key 是 `(start, end)`，Python 的 `sorted` 稳定，所以同 `(start, end)` 保持输入顺序；如果要求显式确定性，把原始下标加进 key 变 `(start, end, i)`。也可以问业务侧要不要按日志来源 machine_id 再定序——这就引出多机时钟问题了。"

**2. gap 定义是否含首尾之外？**（题库原追问）
"默认 gap 只在 `[min_start, max_end)` 内部。如果给观察窗口 `[T0, T1)`，只需再检查 `min_start > T0` 和 `max_end < T1` 两个端点，`gaps()` 首尾各补一条即可，扫描逻辑不变。"

**3. 流式输入怎么改？（递进 follow-up）**
分两种情况答：
- **输入按 start 有序到达**（单机日志的常态）：不需要存全量。只保留当前覆盖块 `(cur_start, cur_end, texts)` 和两个 bool；新段 `start > cur_end`（或 `>=`，取决于 touching 语义）时**发射**上一个块并开新块。O(1) 内存、每段 O(1) 处理，天然是个 online reducer。
- **乱序但延迟有界**（多机汇聚的常态）：加一个按 start 的 min-heap 缓冲 + **watermark**：`watermark = max_seen_start - max_delay`，只有 `start < watermark` 的段才弹出进入上面的有序流水线；watermark 之后才到的 late event 走 correction 通道（对已发射的块发一条带 revision 的更新，而不是静默改历史）。这与我们做 agent trace streaming 的原则一致——挂钟时间戳不单调，去重/游标必须用单调 id，late data 显式修订（见 [../../03_gaps/streaming.md](../../03_gaps/streaming.md)）。

**4. 多机时钟偏移怎么办？（递进 follow-up）**
三层答法，从便宜到贵：
- **容差比较**：NTP 下跨机偏移在 ms~几十 ms 量级。设偏移上界 ε，把三值逻辑做进判定——`cur_start < prev_end - ε` 才判 overlap，`cur_start > prev_end + ε` 才判 gap，落在 `±ε` 边界带内的标记 `uncertain` 交给上层展示，而不是硬拍成 bool。debug view 里"疑似重叠"和"确定重叠"是两种颜色。
- **单一权威时钟**：在 ingestion/collector 落地时打 timestamp，牺牲一点精度换全序；或每台机器内部用 monotonic clock 保序，跨机只用容差比较。
- **逻辑序优先**：如果日志来自同一个 run 的 event log，用 event log 的单调 `seq` 定序、物理 `occurred_at` 只用于展示——这正是 [../../02_playbook.md](../../02_playbook.md) 第四节 TraceEvent 里 `seq` 与 `occurred_at` 分开存的原因。再进一步可提 hybrid logical clock（物理时间 + 逻辑计数器）作为通用方案。

**5. 为什么 Sierra 出这题？**
这是 agent debug 日志视图的建模题：merged 块 = trace 时间轴上的连续活动带，gap = agent 卡住/等待外部的时段，overlap = 并发 tool call 或重复执行的信号。答题时点一句这个映射，比裸算法多一层产品理解——Sierra 电面是 multi-part 递进，结构干净可扩展（单遍扫描 + 独立的 `gaps`/`overlapping_pairs` 函数）比一次写完更值钱（同 [C10] 的打法）。

## 如果这轮允许 AI：怎么驾驶

按 [../../02_playbook.md](../../02_playbook.md) 第八节：先自己口述半开区间语义和验收 1–5，再让 AI 一次只做一个窄任务（例如"写 merge_coverage，条件如下，附 4 个 assert"）；AI 产出后重点自查 `max(cur_end, s.end)` 有没有、touching 的 `<=`/`<` 是否与你声明的语义一致——这两处是 AI 最容易按"标准 merge intervals"套错的地方。测试自己跑，结果自己念。
