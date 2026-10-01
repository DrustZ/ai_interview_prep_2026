"""从 git 历史挖 SWE 训练实例，并用**真实执行**验证 F2P / P2P。

这是 SWE-bench 家族的核心过程，一比一实现（只是把 GitHub PR 换成本地 commit，
因为 PR 的本质就是「一个 base commit + 一个 diff」）：

    候选 = 同时改了「代码文件」和「测试文件」的 commit
    solution_patch = diff 里的非测试文件部分
    test_patch     = diff 里的测试文件部分

    三步验证（缺一不可）：
      ① 在 parent commit 上跑测试         → 必须全过（证明环境是好的）
      ② 打上 test_patch 再跑              → 新测试必须 FAIL（证明 bug 真存在）
      ③ 再打上 solution_patch 跑          → 必须全过（证明这个 fix 真管用）

    F2P = ②失败 且 ③通过 的测试      ← 这是奖励信号
    P2P = ②通过 且 ③通过 的测试      ← 这是防回归的护栏

**为什么 P2P 不能省**：只用 F2P 当 reward，模型可以把不相关的代码删光
只要新测试过就行。P2P 是「别把别的东西弄坏」的约束。

    python mine.py
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path

import toyrepo
from toyrepo import sh

# SWE-rebench V2 论文里用的就是这一条（无锚定的子串匹配）
NAIVE_TEST_RE = re.compile(r"(?i)(test(?:ing|s)?|e2e)")
# 我们用的：要求**路径段边界**，避免 contest/latest 这类误判
TEST_RE = re.compile(r"(^|/)(tests?|testing|e2e)(/|$)|(^|/)test_[^/]*\.py$|_test\.py$",
                     re.I)
CODE_EXT = {".py"}
PYTEST = "/Users/mingrui/Documents/codes/interview/.venv/bin/python -m pytest"


def is_test_file(path: str) -> bool:
    """判定「这是测试文件吗」。看起来是小事，其实是 pipeline 里
    **最容易被忽略的正确性来源** —— 判错会让 gold patch 里混进测试文件（答案泄漏），
    或者把真正的测试改动漏掉（instance 被误判为「没有测试」而丢弃）。

    对比 SWE-rebench V2 论文用的 `(?i)(test(?:ing|s)?|e2e)`：
    那是**无锚定的子串匹配**，`src/contest.py`、`build/latest/x.py`
    都会被判成测试文件。我们加了路径段边界。
    （论文自己也说了要在 metadata 里标记「测试逻辑混在业务文件里」的情况。）
    """
    return bool(TEST_RE.search(path))


@dataclass
class Candidate:
    sha: str
    parent: str
    message: str
    code_files: list = field(default_factory=list)
    test_files: list = field(default_factory=list)
    solution_patch: str = ""
    test_patch: str = ""
    # 验证后填充
    valid: bool = False
    reject_reason: str = ""
    f2p: list = field(default_factory=list)
    p2p: list = field(default_factory=list)


# ───────────────────────────────────────────────── 第一步：挖候选
def list_commits(root: Path) -> list:
    out = sh("git log --reverse --format='%H|%P|%s'", root).stdout.strip().splitlines()
    rows = []
    for line in out:
        sha, parents, msg = line.split("|", 2)
        if not parents.strip():
            continue                                   # 跳过 initial commit
        rows.append((sha, parents.split()[0], msg))
    return rows


def split_patch(root: Path, sha: str, parent: str) -> Candidate:
    files = sh(f"git diff --name-only {parent} {sha}", root).stdout.split()
    code = [f for f in files if Path(f).suffix in CODE_EXT and not is_test_file(f)]
    tests = [f for f in files if is_test_file(f)]
    c = Candidate(sha=sha, parent=parent,
                  message=sh(f"git log -1 --format=%s {sha}", root).stdout.strip(),
                  code_files=code, test_files=tests)
    if code:
        c.solution_patch = sh(
            f"git diff {parent} {sha} -- {' '.join(code)}", root).stdout
    if tests:
        c.test_patch = sh(
            f"git diff {parent} {sha} -- {' '.join(tests)}", root).stdout
    return c


def mine(root: Path) -> list:
    return [split_patch(root, sha, par) for sha, par, _ in list_commits(root)]


# ───────────────────────────────────────────────── 第二步：便宜的启发式过滤
def cheap_filter(c: Candidate) -> Candidate:
    """**先做免费的过滤，再做贵的执行验证。** 执行一次要几分钟到几十分钟，
    而这些检查是微秒级的。真实 pipeline 里这一步能砍掉 80%+ 的候选。"""
    if not c.code_files:
        c.reject_reason = "只改了测试或文档，没有 solution patch"
    elif not c.test_files:
        c.reject_reason = "没有测试改动 → 无法自动验证"
    elif len(c.code_files) > 20:
        c.reject_reason = "改动面过大（>20 文件），多半是重构/版本升级"
    elif sum(1 for ln in c.solution_patch.splitlines()
             if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))) > 400:
        c.reject_reason = "solution patch 超过 400 行"
    return c


# ───────────────────────────────────────────────── 第三步：执行验证
def run_tests(root: Path) -> dict:
    """返回 {test_id: 'passed'|'failed'|'error'}。真实 pipeline 里要按语言
    换 runner 并优先用结构化报告（pytest 的 -q 输出、JUnit XML）。"""
    r = subprocess.run(f"{PYTEST} -q --tb=no -p no:cacheprovider",
                       cwd=str(root), shell=True, capture_output=True, text=True)
    out = {}
    for line in (r.stdout + r.stderr).splitlines():
        m = re.match(r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR)", line)
        if m:
            out[m.group(1)] = m.group(2).lower()
    if not out:                       # -q 模式不打印每条，改用 --tb=no -v 兜底
        r = subprocess.run(f"{PYTEST} -v --tb=no -p no:cacheprovider",
                           cwd=str(root), shell=True, capture_output=True, text=True)
        for line in (r.stdout + r.stderr).splitlines():
            m = re.match(r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR)", line)
            if m:
                out[m.group(1)] = m.group(2).lower()
    return out


def apply_patch(root: Path, patch: str) -> bool:
    if not patch.strip():
        return True
    p = root / ".__patch"
    p.write_text(patch)
    r = sh("git apply --whitespace=nowarn .__patch", root, check=False)
    p.unlink(missing_ok=True)
    return r.returncode == 0


def validate(root: Path, c: Candidate) -> Candidate:
    """三步验证。**每一步都真的跑测试**，不是猜。"""
    if c.reject_reason:
        return c
    # -f 强制丢弃上一轮打进去的补丁；-x 连 .pytest_cache 一起清
    sh(f"git checkout -q -f {c.parent} && git clean -qfdx", root)

    before_base = run_tests(root)                       # ① parent 上的基线
    if not before_base:
        c.reject_reason = "① parent 上收集不到测试（环境坏了）"
        return c
    if any(v != "passed" for v in before_base.values()):
        # SWE-bench 要求这里全过。有的 pipeline 放宽成「记录下来当作已知失败」
        c.reject_reason = "① parent 上就有测试不过 —— 环境或仓库状态不干净"
        return c

    if not apply_patch(root, c.test_patch):             # ② 只打测试补丁
        c.reject_reason = "② test patch 打不上"
        return c
    before = run_tests(root)

    if not apply_patch(root, c.solution_patch):         # ③ 再打代码补丁
        c.reject_reason = "③ solution patch 打不上"
        return c
    after = run_tests(root)

    c.f2p = sorted(t for t, s in after.items()
                   if s == "passed" and before.get(t) in ("failed", "error", None))
    c.p2p = sorted(t for t, s in after.items()
                   if s == "passed" and before.get(t) == "passed")
    fails = [t for t, s in after.items() if s != "passed"]

    if fails:
        c.reject_reason = f"③ 打了 fix 之后仍有 {len(fails)} 个测试不过"
    elif not c.f2p:
        c.reject_reason = "没有 F2P 测试 —— 这个改动没有可验证的行为变化"
    else:
        c.valid = True
    return c


def to_instance(root: Path, c: Candidate) -> dict:
    """落成训练实例。**注意 problem_statement 这里是 commit message** ——
    真实数据里应该用链接的 issue 正文；拿不到 issue 时
    SWE-rebench V2 的做法是用 PR description，并单独标记来源。"""
    return {
        "instance_id": f"toy__calc-{c.sha[:7]}",
        "repo": "toy/calc",
        "base_commit": c.parent,
        "problem_statement": c.message,       # ← 真实场景换成 issue body
        "patch": c.solution_patch,            # gold patch（训练时不给模型看）
        "test_patch": c.test_patch,
        "FAIL_TO_PASS": c.f2p,
        "PASS_TO_PASS": c.p2p,
        "meta": {"n_code_files": len(c.code_files),
                 "patch_lines": sum(1 for ln in c.solution_patch.splitlines()
                                    if ln[:1] in "+-" and ln[:3] not in ("+++", "---")),
                 "problem_source": "commit_message"},
    }


def run(root: Path = None) -> list:
    root = root or toyrepo.build()
    cands = [cheap_filter(c) for c in mine(root)]
    print(f"挖到 {len(cands)} 个 commit（不含 initial）")
    print(f"  便宜过滤后剩 {sum(1 for c in cands if not c.reject_reason)} 个进入执行验证")
    out = []
    for c in cands:
        validate(root, c)
        tag = "✅" if c.valid else "❌"
        detail = (f"F2P={len(c.f2p)} P2P={len(c.p2p)}" if c.valid else c.reject_reason)
        print(f"  {tag} {c.sha[:7]} {c.message[:52]:<52} {detail}")
        if c.valid:
            out.append(to_instance(root, c))
    sh("git checkout -q -f main && git clean -qfdx", root)
    print(f"\n最终 {len(out)} 个可用实例（产出率 {len(out)/len(cands):.0%}）")
    return out


if __name__ == "__main__":
    inst = run()
    Path("/tmp/swe_instances.json").write_text(json.dumps(inst, indent=2))
    print("已写入 /tmp/swe_instances.json")
    if inst:
        e = dict(inst[0]); e["patch"] = e["patch"][:200] + " ...(截断)"
        e["test_patch"] = e["test_patch"][:160] + " ...(截断)"
        print("\n样例实例：\n" + json.dumps(e, indent=2, ensure_ascii=False)[:1100])
