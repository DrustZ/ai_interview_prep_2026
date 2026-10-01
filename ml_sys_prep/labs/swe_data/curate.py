"""挖出来之后：**去重 → 去污染 → 难度分层 → 配比**。

这一步是 math/STEM 数据 curation 的经验**直接可以迁移**的部分，
但有三个 SWE 特有的坑：

  1. **去重的单位不是文本，是「改动的语义」。** 同一个仓库里
     「给 N 个函数各加一个 None 检查」的 PR 可能有几十个，patch 文本高度相似 ——
     它们对模型是同一道题。要在 patch 的归一化形式上做近重复检测。
  2. **去污染要按仓库 + 时间双维度。** 只查 instance_id 不够：
     SWE-bench 的 12 个测试仓库**整个仓库**都要排除（SWE-smith 就是这么做的），
     因为同一个仓库的其他 PR 会泄漏代码库结构和风格。
  3. **难度必须用「当前模型的可解率」来定，不是用 patch 行数。**
     行数只是一个 proxy，而且和难度的相关性没你以为的高。

    python curate.py
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


# ─────────────────────────────────────────── 归一化 + 近重复
def normalize_patch(patch: str) -> str:
    """只保留**增删的代码行**，去掉 hunk 头、行号、路径、空白和注释。
    目的：让「同一种改动作用在不同文件上」被认成近重复。"""
    lines = []
    for ln in patch.splitlines():
        if ln.startswith(("+++", "---", "diff ", "index ", "@@")):
            continue
        if ln[:1] not in "+-":
            continue
        body = ln[1:].strip()
        body = re.sub(r"#.*$", "", body)          # 去注释
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            lines.append(body)
    return "\n".join(lines)


def assert_is_diff(patch: str, who: str = ""):
    """**护栏**：归一化后为空 = 这不是 diff，或者 schema 变了。
    没有这一行，dedup 会把所有实例判成重复而且一声不吭。"""
    if not normalize_patch(patch).strip():
        raise ValueError(f"归一化后为空，{who} 传进来的多半不是 unified diff")


def shingles(text: str, k: int = 5) -> set:
    toks = re.findall(r"[A-Za-z_]\w*|\S", text)
    return {" ".join(toks[i:i + k]) for i in range(max(1, len(toks) - k + 1))}


def minhash(s: set, n: int = 64) -> tuple:
    """n 个哈希函数各取最小值。**手写是因为要说清它在算什么** ——
    两个集合的 MinHash 签名相同位数的比例，是 Jaccard 的无偏估计。"""
    if not s:
        return tuple([0] * n)
    sig = []
    for i in range(n):
        sig.append(min(int(hashlib.md5(f"{i}|{x}".encode()).hexdigest()[:8], 16)
                       for x in s))
    return tuple(sig)


def jaccard_est(a: tuple, b: tuple) -> float:
    return sum(x == y for x, y in zip(a, b)) / len(a)


def dedup(instances: list, thr: float = 0.7) -> tuple:
    """贪心近重复去除。返回 (保留, 丢弃原因列表)。
    真实规模要用 LSH 分桶，不能 O(n²)。"""
    kept, sigs, dropped = [], [], []
    for inst in instances:
        raw = inst.get("patch", "") or inst.get("bug_patch", "")
        assert_is_diff(raw, inst.get("instance_id", "?"))
        sig = minhash(shingles(normalize_patch(raw)))
        dup_of = next((kept[i]["instance_id"] for i, s in enumerate(sigs)
                       if jaccard_est(sig, s) >= thr), None)
        if dup_of:
            dropped.append((inst["instance_id"], f"≈{dup_of}"))
        else:
            kept.append(inst); sigs.append(sig)
    return kept, dropped


# ─────────────────────────────────────────── 去污染
SWEBENCH_TEST_REPOS = {          # SWE-bench 的 12 个测试仓库，整仓排除
    "astropy/astropy", "django/django", "matplotlib/matplotlib", "mwaskom/seaborn",
    "pallets/flask", "psf/requests", "pydata/xarray", "pylint-dev/pylint",
    "pytest-dev/pytest", "scikit-learn/scikit-learn", "sphinx-doc/sphinx",
    "sympy/sympy",
}


def decontaminate(instances: list, bench_repos=SWEBENCH_TEST_REPOS,
                  bench_patches: list = None) -> tuple:
    """三层：① 整仓排除 ② instance_id 精确匹配 ③ patch 近重复。

    ⚠️ **只做 ①② 是不够的**：同一个 bug 可能在 fork 里、在别的仓库的
    vendored 副本里再出现一次。③ 才能抓到。"""
    bench_sigs = [minhash(shingles(normalize_patch(p))) for p in (bench_patches or [])]
    kept, removed = [], []
    for inst in instances:
        if inst.get("repo") in bench_repos:
            removed.append((inst["instance_id"], "① 属于 benchmark 测试仓库")); continue
        sig = minhash(shingles(normalize_patch(inst.get("patch", ""))))
        if any(jaccard_est(sig, b) >= 0.8 for b in bench_sigs):
            removed.append((inst["instance_id"], "③ patch 与 benchmark 近重复")); continue
        kept.append(inst)
    return kept, removed


# ─────────────────────────────────────────── 难度
def static_difficulty(inst: dict) -> str:
    """**便宜但不可靠的 proxy。** 只用来做初筛和分桶，不能当结论。"""
    n_lines = inst.get("meta", {}).get("patch_lines", 0)
    n_files = inst.get("meta", {}).get("n_code_files", 1)
    n_f2p = len(inst.get("FAIL_TO_PASS", []))
    score = n_lines / 20 + (n_files - 1) * 1.5 + max(0, n_f2p - 1) * 0.5
    return "easy" if score < 1 else ("medium" if score < 3 else "hard")


def empirical_difficulty(inst: dict, rollout_results: list) -> dict:
    """**正确的做法**：用当前策略跑 k 次 rollout，用通过率定难度。

    这直接接你在 math/STEM 上做的自适应难度筛选 —— 同一个思路：
      * pass@k = 0   → 无梯度信号，**这一组 rollout 白跑**（GRPO 组内优势全 0）
      * pass@k = 1   → 太简单，同样无信号
      * 0 < p < 1    → 有区分度，**这才是该留的**
    """
    k = len(rollout_results)
    p = sum(rollout_results) / k if k else 0.0
    return {"pass_rate": p, "k": k,
            "keep_for_rl": 0 < p < 1,
            "bucket": "unsolvable" if p == 0 else
                      ("trivial" if p == 1 else
                       ("hard" if p <= 0.25 else ("medium" if p <= 0.6 else "easy")))}


# ─────────────────────────────────────────── 配比
def stratify(instances: list, quota: dict = None) -> list:
    """按难度桶配比。默认偏向中等难度 —— RL 的信号密度在那里最高。"""
    quota = quota or {"easy": 0.2, "medium": 0.5, "hard": 0.3}
    buckets = {}
    for i in instances:
        buckets.setdefault(static_difficulty(i), []).append(i)
    n = len(instances)
    out = []
    for b, frac in quota.items():
        out += buckets.get(b, [])[: max(1, int(n * frac))]
    return out


def report(instances: list, title: str):
    print(f"\n{title}：{len(instances)} 条")
    for k, v in Counter(static_difficulty(i) for i in instances).most_common():
        print(f"    {k:<8} {v}")


if __name__ == "__main__":
    import mine, synth, toyrepo
    root = toyrepo.build()
    mined = mine.run(root)
    synthed = synth.synthesize(root, verbose=False)
    for s in synthed:                     # 统一 schema
        s["patch"] = s["bug_patch"]
        s.setdefault("meta", {
            "patch_lines": sum(1 for ln in s["bug_patch"].splitlines()
                               if ln[:1] in "+-" and ln[:3] not in ("+++", "---")),
            "n_code_files": 1})
    pool = mined + synthed
    report(pool, "原始池")

    kept, dropped = dedup(pool)
    print(f"\n近重复去除：丢 {len(dropped)} 条")
    for i, why in dropped[:5]:
        print(f"    {i}  {why}")

    kept2, removed = decontaminate(
        kept, bench_patches=[mined[0]["patch"]] if mined else [])
    print(f"\n去污染：丢 {len(removed)} 条")
    for i, why in removed[:5]:
        print(f"    {i}  {why}")

    report(kept2, "最终")
    print("\n⚠️ static_difficulty 只是 proxy。上 RL 前必须用 empirical_difficulty")
    print("   跑一遍 rollout，把 pass@k ∈ {0, 1} 的题**先扔掉** —— 它们没有梯度。")
    demo = empirical_difficulty(kept2[0], [0, 1, 0, 0, 1, 0, 0, 0])
    print(f"   例：{kept2[0]['instance_id']} → {demo}")
