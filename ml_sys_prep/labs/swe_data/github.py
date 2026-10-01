"""从 GitHub 拿数据的三条路，以及**选仓库**的打分。

    python github.py            # 离线示例，不需要 token
    GITHUB_TOKEN=xxx python github.py --live pallets/flask

三条路，按规模和成本排序：

| 路 | 怎么拿 | 速率限制 | 适合 |
|---|---|---|---|
| **REST/GraphQL API** | `api.github.com` | 认证后 5000 req/h | 几百个仓库、要最新状态 |
| **GH Archive** | BigQuery / 下载每小时的 `.json.gz` | 无 | **全量 PR/issue 元数据**，SWE-rebench V2 用这个 |
| **本地 clone + git log** | `git clone --filter=blob:none` | 无 | 拿 patch 内容。**别用 API 逐个拉 diff** |

**SWE-rebench V2 的做法值得抄**：用 GH Archive 拿元数据（issue/PR/commit SHA/license），
然后**分布式 map-reduce 克隆仓库、从本地 git 历史取 patch**，
完全绕开 API 速率限制。他们这样处理出 21,000 个仓库 / 58 万个候选实例。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from dataclasses import dataclass

API = "https://api.github.com"


# ─────────────────────────────────────────── 仓库筛选标准
@dataclass
class RepoFilters:
    """各家的实际阈值（可引用）：

    * **SWE-smith**：PyPI 下载量前 5000 的包 → 按 star 排序 → **剔除 <1000 star**
      → 再剔除 SWE-bench 的 12 个测试仓库。最终 128 个仓库。
    * **SWE-rebench V2**：高资源语言（Python/Java/Go）**≥25 star 且 ≥15 个 closed issue**；
      长尾语言放宽到 **≥10 star、≥1 个 closed issue**。
      他们量化过：**这个阈值保留约 20% 的仓库，却覆盖约 80% 的任务** ——
      需要做环境搭建的仓库数直接降为 1/5。这是整条 pipeline 里性价比最高的一刀。
    """
    min_stars: int = 25
    min_closed_issues: int = 15
    require_permissive_license: bool = True
    exclude_repos: frozenset = frozenset({
        "astropy/astropy", "django/django", "matplotlib/matplotlib",
        "mwaskom/seaborn", "pallets/flask", "psf/requests", "pydata/xarray",
        "pylint-dev/pylint", "pytest-dev/pytest", "scikit-learn/scikit-learn",
        "sphinx-doc/sphinx", "sympy/sympy",           # SWE-bench 测试集，整仓排除
    })
    languages: frozenset = frozenset({"Python"})


PERMISSIVE = {"mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause", "isc", "unlicense"}


def score_repo(meta: dict, f: RepoFilters = RepoFilters()) -> dict:
    """返回 {keep, reasons, yield_score}。

    `yield_score` 是「这个仓库大概能产出多少可用实例」的先验估计。
    **任务产出高度长尾** —— 少数核心仓库贡献大部分实例，
    所以按它排序、优先给高分仓库搭环境，是对的。
    """
    full = meta.get("full_name", "")
    reasons = []
    if full in f.exclude_repos:
        reasons.append("在 benchmark 测试集里（整仓排除）")
    if meta.get("stargazers_count", 0) < f.min_stars:
        reasons.append(f"star {meta.get('stargazers_count')} < {f.min_stars}")
    if meta.get("closed_issues", 0) < f.min_closed_issues:
        reasons.append(f"closed issue {meta.get('closed_issues')} < {f.min_closed_issues}")
    if f.languages and meta.get("language") not in f.languages:
        reasons.append(f"语言 {meta.get('language')} 不在目标内")
    lic = (meta.get("license") or {}).get("key", "")
    if f.require_permissive_license and lic not in PERMISSIVE:
        reasons.append(f"license `{lic or 'none'}` 非宽松许可")
    if meta.get("archived"):
        reasons.append("已归档")
    if meta.get("fork"):
        reasons.append("是 fork（会和上游重复）")

    # 有测试目录 + issue 活跃 + PR 多 → 产出高
    ys = (min(meta.get("closed_issues", 0), 2000) / 2000 * 3
          + min(meta.get("stargazers_count", 0), 20000) / 20000 * 2
          + (2 if meta.get("has_tests") else 0))
    return {"repo": full, "keep": not reasons, "reasons": reasons,
            "yield_score": round(ys, 2)}


# ─────────────────────────────────────────── 真实 API（需 token）
def _get(url: str, token: str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "swe-data-lab"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_repo(full_name: str, token: str) -> dict:
    m = _get(f"{API}/repos/{full_name}", token)
    # closed issue 数要单独查：repo 的 open_issues_count 含 PR，且只算 open
    s = _get(f"{API}/search/issues?q=repo:{full_name}+type:issue+state:closed&per_page=1",
             token)
    tree = _get(f"{API}/repos/{full_name}/contents", token)
    m["closed_issues"] = s.get("total_count", 0)
    m["has_tests"] = any(e["name"] in ("tests", "test", "testing") for e in tree)
    return m


def linked_issue_numbers(pr_body: str) -> list:
    """PR 正文里 `Fixes #123` / `Closes #45` 这类引用。
    **issue 链接是 SWE-bench 系的关键**：problem_statement 用的是 issue 正文，
    不是 PR 描述 —— 因为 PR 描述常常已经把解法说出来了（**答案泄漏**）。
    拿不到 issue 时 SWE-rebench V2 才退而用 PR 描述，并单独打标记。"""
    import re
    return sorted({int(n) for n in re.findall(
        r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s*#(\d+)", pr_body or "", re.I)})


# ─────────────────────────────────────────── 离线示例
SAMPLE = [
    {"full_name": "pallets/flask", "stargazers_count": 68000, "closed_issues": 2600,
     "language": "Python", "license": {"key": "bsd-3-clause"}, "has_tests": True},
    {"full_name": "tqdm/tqdm", "stargazers_count": 29000, "closed_issues": 1100,
     "language": "Python", "license": {"key": "mit"}, "has_tests": True},
    {"full_name": "someone/tiny-utils", "stargazers_count": 12, "closed_issues": 3,
     "language": "Python", "license": {"key": "mit"}, "has_tests": False},
    {"full_name": "corp/internal-tool", "stargazers_count": 900, "closed_issues": 80,
     "language": "Python", "license": {"key": "gpl-3.0"}, "has_tests": True},
    {"full_name": "acme/fastapi-clone", "stargazers_count": 400, "closed_issues": 60,
     "language": "Python", "license": {"key": "mit"}, "has_tests": True, "fork": True},
    {"full_name": "vuejs/core", "stargazers_count": 47000, "closed_issues": 5000,
     "language": "TypeScript", "license": {"key": "mit"}, "has_tests": True},
]


def main():
    if "--live" in sys.argv:
        tok = os.environ.get("GITHUB_TOKEN")
        if not tok:
            sys.exit("需要 GITHUB_TOKEN")
        name = sys.argv[sys.argv.index("--live") + 1]
        meta = fetch_repo(name, tok)
        print(json.dumps(score_repo(meta), ensure_ascii=False, indent=2))
        return

    print("仓库筛选（离线示例）\n")
    rows = [score_repo(m) for m in SAMPLE]
    for r in sorted(rows, key=lambda x: -x["yield_score"]):
        tag = "✅" if r["keep"] else "❌"
        why = "" if r["keep"] else "  ← " + "；".join(r["reasons"])
        print(f"  {tag} {r['repo']:<24} yield={r['yield_score']:<5}{why}")
    kept = sum(r["keep"] for r in rows)
    print(f"\n保留 {kept}/{len(rows)}。**先给 yield_score 高的搭环境** —— "
          f"任务产出是长尾的，\n  SWE-rebench V2 量过：20% 的仓库覆盖 80% 的任务。")

    print("\nPR 正文里的 issue 链接：")
    for body in ["Fixes #123 and closes #456.", "See #99 for context (not a fix)",
                 "resolve: #7"]:
        print(f"  {body!r:<42} → {linked_issue_numbers(body)}")
    print("  ⚠️ 只提到 #99 不算 —— 必须是 close/fix/resolve 这类**解决**语义。")


if __name__ == "__main__":
    main()
