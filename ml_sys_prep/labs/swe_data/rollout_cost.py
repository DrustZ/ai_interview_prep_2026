"""SWE agent rollout 的推理成本：**prefix cache 是不是开着，差 20 倍。**

    python rollout_cost.py

造 SWE 训练数据时，真正的瓶颈不是 GPU 算力，是**你有没有把多轮对话的
prefix cache 用对**。这个文件把账算出来。

核心事实：agent loop 每一轮都要**重发整段历史**。
    第 t 轮的 prompt 长度 ≈ base + Σ(前 t-1 轮的所有内容)
    → 不缓存时 prefill 总量是 **O(T²)**
    → 完美缓存时只有新增部分要算，**O(T)**

40 轮的 SWE 任务上，这个差是 20 倍以上。而缓存**极其容易被无意中打掉**。
"""
from __future__ import annotations

# ── 一个典型的 SWE agent rollout（数量级取自真实 harness）
SYS_TOOLS = 3_000        # system prompt + 工具 schema（**稳定**，最该被缓存的部分）
REPO_CTX = 6_000         # 仓库结构 / 相关文件摘要（每个任务固定）
AGENT_OUT = 300          # 每轮 agent 输出（thinking + tool call）
TOOL_OUT = 800           # 每轮工具返回（文件内容、测试输出）
TURNS = 40
PER_TURN = AGENT_OUT + TOOL_OUT


def prefill_no_cache(turns=TURNS) -> int:
    """每轮从头 prefill 整段历史。Σ(base + t·per_turn) —— **二次增长**。"""
    base = SYS_TOOLS + REPO_CTX
    return sum(base + t * PER_TURN for t in range(turns))


def prefill_perfect_cache(turns=TURNS) -> int:
    """只有**新增的 token** 需要 prefill。base 只算一次。

    注意是 `turns - 1`：最后一轮的 agent 输出不会再被 prefill 了
    （它是生成出来的，不需要再喂回去）。第一版写成 `turns` 导致
    「从不失效」和「完美缓存」对不上一个 PER_TURN —— 口径不一致的经典表现。
    """
    return SYS_TOOLS + REPO_CTX + (turns - 1) * PER_TURN


def prefill_with_invalidations(turns=TURNS, break_at=()) -> int:
    """`break_at` 里的轮次缓存失效 —— 那一轮要把**当时的整段 prompt** 重算。

    正确性检查（写在这里是因为我第一版算错过）：
      break_at = 全部轮次  →  必须**恰好等于** prefill_no_cache（缓存永不命中 = 没缓存）
      break_at = ()        →  必须等于 prefill_perfect_cache
    第一版每轮既加了 `live` 又加了 `PER_TURN`，把新增 token 重复计了一次，
    结果「每轮失效」比「不开缓存」还贵 —— 那在物理上不可能。
    """
    total, live = 0, 0                   # live = 已在缓存里的前缀长度
    prompt = SYS_TOOLS + REPO_CTX
    for t in range(turns):
        if live == 0 or t in break_at:
            total += prompt              # 整段 prefill
        else:
            total += prompt - live       # 只算新增
        live = prompt
        prompt += PER_TURN
    return total


def prefill_sticky(turns=TURNS, replicas=8) -> int:
    """**没有 cache-aware 路由**时，同一会话的下一轮落到别的副本上，缓存全丢。

    命中概率 ≈ 1/replicas（round-robin）。llm-d 实测：8 pods / 16 H100 上，
    prefix-cache-aware 路由 vs round-robin，**TTFT 快 57×、吞吐 2×**。
    SGLang RadixAttention + sticky 把命中率从 18% 拉到 71%。
    """
    p_hit = 1.0 / replicas
    total, live = 0.0, 0
    prompt = SYS_TOOLS + REPO_CTX
    for _ in range(turns):
        if live == 0:
            total += prompt
        else:                            # 期望：命中只算新增，未命中整段重算
            total += p_hit * (prompt - live) + (1 - p_hit) * prompt
        live = prompt
        prompt += PER_TURN
    return int(total)


def trace(turns=12, break_at=(), width=58):
    """**逐轮打印**：这一轮的 prompt 有多长、其中多少是缓存里已有的、
    真正要 prefill 多少。O(T²) 这件事光看公式没感觉，看这张表就有了。"""
    print("轮次   prompt长度   缓存命中     实际prefill   累计prefill")
    print("─" * width)
    total, live = 0, 0
    prompt = SYS_TOOLS + REPO_CTX
    for t in range(turns):
        miss = (live == 0) or (t in break_at)
        this = prompt if miss else prompt - live
        total += this
        flag = ""
        if t in break_at:
            flag = "  ← 缓存失效，整段重算"
        elif live == 0:
            flag = "  ← 第一轮，本来就要全算"
        print("{:>3}   {:>9,}   {:>9,}   {:>11,}   {:>11,}{}".format(
            t, prompt, 0 if miss else live, this, total, flag))
        live = prompt
        prompt += PER_TURN
    print("─" * width)
    print(f"      最终 prompt {prompt - PER_TURN:,} tokens，"
          f"累计 prefill {total:,}")
    return total


def fmt(n) -> str:
    return f"{n/1e6:.2f}M" if n >= 1e6 else f"{n/1e3:.0f}k"


def main():
    import sys as _s
    if "--trace" in _s.argv:
        print("═══ 有缓存：每轮只 prefill 新增的 1,100 token ═══\n")
        a = trace(12)
        print("\n═══ 无缓存（比如 system prompt 里有时间戳）═══\n")
        b = trace(12, break_at=tuple(range(12)))
        print(f"\n12 轮就差了 {b/a:.1f} 倍；40 轮差 {prefill_no_cache()/prefill_perfect_cache():.1f} 倍。")
        print("**注意增长形状**：有缓存那列是常数 1,100；无缓存那列每轮多 1,100。")
        return

    base = prefill_no_cache()
    best = prefill_perfect_cache()

    print("═══ 一个 40 轮 SWE rollout 的 prefill token 量 ═══\n")
    rows = [
        ("① 不开 prefix cache", base),
        ("② 完美 prefix cache", best),
        ("③ 完美缓存 + 中途 compact 一次（第 25 轮）",
         prefill_with_invalidations(break_at=(25,))),
        ("④ 完美缓存 + compact 三次（10/20/30）",
         prefill_with_invalidations(break_at=(10, 20, 30))),
        ("⑤ system prompt 里有时间戳（**每轮都失效**）",
         prefill_with_invalidations(break_at=tuple(range(TURNS)))),
        ("⑥ 开了缓存但**没有 sticky 路由**（8 副本 round-robin）",
         prefill_sticky()),
    ]
    print("{:<44} {:>9} {:>10}".format("配置", "prefill", "vs 最优"))
    print("─" * 66)
    for name, v in rows:
        print("{:<44} {:>9} {:>9.1f}×".format(name, fmt(v), v / best))

    print(f"\n⭐ 开不开缓存差 **{base/best:.0f} 倍**。")
    print("   而 ⑤ 说明：**system prompt 里一个时间戳，就能让缓存完全失效**")
    print(f"   （{fmt(prefill_with_invalidations(break_at=tuple(range(TURNS))))} "
          f"≈ 不开缓存的 {prefill_with_invalidations(break_at=tuple(range(TURNS)))/base:.1f} 倍）。")
    print("   ⑥ 说明：**开了缓存不等于用上了缓存** —— 没有 cache-aware 路由，")
    print("   多副本部署下命中率约 1/N。llm-d 实测 sticky 路由 TTFT 快 57×。")

    # ── n 个样本共享前缀
    print("\n═══ RL rollout：每个任务采 n 个样本 ═══\n")
    n = 8
    sep = n * best
    shared = best + (n - 1) * (TURNS * PER_TURN)   # 只有分叉之后的部分要重算
    print(f"  n={n} 个独立请求      {fmt(sep):>8}")
    print(f"  n={n} 共享 base 前缀  {fmt(shared):>8}   省 {(1-shared/sep):.0%}")
    print("  → 用引擎的 `n=8` 参数（或 SGLang 的 fork），别发 8 个独立请求。")
    print(f"  ⚠️ **但这只值 {(1-shared/sep):.0%}，不是大头** —— n 个样本在第一轮就分叉了，")
    print("     之后什么都不共享。真正的 23× 来自**单条轨迹内跨轮次**的缓存。")
    print("     别把 n-sharing 当成主要优化。")

    # ── 真正被忽略的大头：跨任务共享仓库上下文
    print("\n═══ 跨任务：**按仓库分组调度** ═══\n")
    tasks_per_repo = 40
    print(f"  同一个仓库的 {tasks_per_repo} 个任务共享 {fmt(REPO_CTX)} 的仓库上下文")
    print(f"    随机打散调度：每个任务各自 prefill 一次 → "
          f"{fmt(tasks_per_repo * REPO_CTX)}")
    print(f"    按仓库分组：  只 prefill 一次              → {fmt(REPO_CTX)}")
    print(f"  ⭐ **调度顺序本身就是一个优化项。** 任务列表按 repo 排序再发，")
    print("     配合 cache-aware 路由（同 repo 打到同一副本），这部分几乎归零。")

    # ── 规模：一次数据生成 campaign
    print("\n═══ 一次数据生成 campaign 的账 ═══\n")
    n_tasks, n_samp = 5_000, 8
    for label, per in (("不开缓存", base), ("完美缓存", best),
                       ("缓存+sticky+n 共享", shared / n_samp)):
        tot = n_tasks * n_samp * per
        # H100 prefill 粗估：~10k tok/s/卡（长上下文、含 attention 二次项）
        gpu_h = tot / 10_000 / 3600
        print(f"  {label:<20} {tot/1e9:>7.1f}B tokens   ≈ {gpu_h:>7.0f} GPU-小时"
              f"   ≈ ${gpu_h*2.5:>8,.0f}（按 $2.5/H100-h）")
    print("\n  → **同一批数据，缓存用对与否差两个数量级的钱。**")
    print("    这就是为什么『造 SWE 数据』本质上是个推理工程问题，不是训练问题。")


if __name__ == "__main__":
    main()
