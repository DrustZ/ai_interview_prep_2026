"""合成路线：**环境优先，再造 bug**（SWE-smith 的思路）。

挖 PR 的路线有个硬上限：一个仓库里「同时改了代码和测试、且能跑通」的 PR
就那么多。SWE-bench 从 12 个仓库只挖出 2,294 个实例；SWE-Gym 11 个仓库 2,438 个。

SWE-smith 把顺序**倒过来**：先把仓库的执行环境搭好（这才是真正贵的部分），
然后在环境里**批量制造** bug。同样 128 个仓库产出 5 万个实例，
平均每仓库 381 个，pandas 一个仓库就 2,277 个。

它用四种造 bug 的策略（我们这里实现最便宜的第 2 种）：
  1. **LM Modify / LM Rewrite** —— 让模型改坏一个函数，或只给签名+docstring 让它重写
  2. **Procedural Modification** —— 改 AST（删条件/删循环/换运算符/…共 13 种）← 本文件
  3. **Combine Bugs** —— 把同文件/同模块的多个 bug 合成一个更难的任务
  4. **Invert PR（PR Mirroring）** —— 让模型把一个真 PR 的改动「撤销」回去

**关键洞察**（论文原话的意思）：执行验证不只能验证解法，
**它也能筛出「哪些改动是真 bug」** —— 造一堆候选，只留下真的弄挂测试的那些。

    python synth.py
"""
from __future__ import annotations

import ast
import difflib
import json
import random
from pathlib import Path

import mine
import toyrepo
from toyrepo import sh


# ─────────────────────────────────────────── AST 变换（procedural）
class _Mutator(ast.NodeTransformer):
    """13 种里选 6 种代表性的。**每次只改一处** —— 多处一起改会让任务
    难度不可控，而且定位不到「这个 bug 到底是什么」。"""

    KINDS = ("flip_compare", "off_by_one", "drop_if", "drop_loop",
             "swap_binop", "return_none")

    def __init__(self, kind: str, rng: random.Random):
        self.kind, self.rng, self.done = kind, rng, False

    def _fire(self) -> bool:
        if self.done or self.rng.random() < 0.5:
            return False
        self.done = True
        return True

    def visit_Compare(self, node):
        self.generic_visit(node)
        flip = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE,
                ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
        if self.kind == "flip_compare" and type(node.ops[0]) in flip and self._fire():
            node.ops = [flip[type(node.ops[0])]()]
        return node

    def visit_Constant(self, node):
        if (self.kind == "off_by_one" and isinstance(node.value, int)
                and not isinstance(node.value, bool) and self._fire()):
            return ast.copy_location(
                ast.Constant(value=node.value + self.rng.choice([-1, 1])), node)
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if self.kind == "drop_if" and node.body and self._fire():
            return node.body            # 把 if 拆掉，body 无条件执行
        return node

    def visit_For(self, node):
        self.generic_visit(node)
        if self.kind == "drop_loop" and self._fire():
            return ast.copy_location(ast.Pass(), node)
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        swap = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div,
                ast.Div: ast.Mult, ast.FloorDiv: ast.Div}
        if self.kind == "swap_binop" and type(node.op) in swap and self._fire():
            node.op = swap[type(node.op)]()
        return node

    def visit_Return(self, node):
        self.generic_visit(node)
        if self.kind == "return_none" and node.value is not None and self._fire():
            return ast.copy_location(ast.Return(value=ast.Constant(None)), node)
        return node


def mutate(src: str, kind: str, seed: int):
    """返回改坏后的源码；没改动则返回 None。"""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    m = _Mutator(kind, random.Random(seed))
    new = m.visit(tree)
    if not m.done:
        return None
    ast.fix_missing_locations(new)
    try:
        out = ast.unparse(new)                # py3.9+
    except Exception:
        return None
    return out if out.strip() != src.strip() else None


# ─────────────────────────────────────────── 生成 + 执行验证
def synthesize(root: Path, targets=("calc/stats.py", "calc/text.py"),
               per_file: int = 12, verbose: bool = True) -> list:
    sh("git checkout -q -f main && git clean -qfdx", root)
    base_tests = mine.run_tests(root)
    assert base_tests and all(v == "passed" for v in base_tests.values()), \
        "环境必须先是干净的 —— 这是 SWE-smith 第一步「建环境」的验收标准"
    if verbose:
        print(f"基线：{len(base_tests)} 个测试全过\n")

    kept, tried = [], 0
    for rel in targets:
        orig = (root / rel).read_text()
        for i in range(per_file):
            kind = _Mutator.KINDS[i % len(_Mutator.KINDS)]
            bugged = mutate(orig, kind, seed=i)
            tried += 1
            if bugged is None:
                continue
            (root / rel).write_text(bugged)
            res = mine.run_tests(root)
            (root / rel).write_text(orig)                    # 立刻还原

            broke = sorted(t for t, s in res.items() if s != "passed")
            still = sorted(t for t, s in res.items() if s == "passed")
            if not res:
                continue                                      # 语法/导入直接崩，丢弃
            if not broke:
                continue                                      # 没弄挂任何测试 → 不是 bug
            if len(broke) == len(res):
                continue                                      # 全挂了 → 多半是导入炸了，太粗暴
            kept.append({
                "instance_id": f"synth__calc-{rel.split('/')[-1][:-3]}-{kind}-{i}",
                "repo": "toy/calc", "strategy": f"procedural:{kind}",
                "bugged_file": rel,
                # 存**统一 diff** 而不是整份文件。第一版我存了整份源码，
                # 结果 curate 里的 normalize_patch（只保留 +/- 行）返回空串，
                # 所有实例的 MinHash 签名一模一样 → 去重把它们全判成重复。
                # **两个数据源 schema 不一致，会让下游过滤静默失效。**
                "bug_patch": "".join(difflib.unified_diff(
                    orig.splitlines(keepends=True), bugged.splitlines(keepends=True),
                    fromfile=f"a/{rel}", tofile=f"b/{rel}")),
                "FAIL_TO_PASS": broke, "PASS_TO_PASS": still,
                "problem_statement": None,          # 下一步由 LM 生成 issue 文本
            })
    sh("git checkout -q -f main && git clean -qfdx", root)
    if verbose:
        print(f"尝试 {tried} 次变异 → **{len(kept)} 个有效 bug**（产出率 {len(kept)/tried:.0%}）")
        from collections import Counter
        for k, v in Counter(x["strategy"] for x in kept).most_common():
            print(f"  {k:<28} {v}")
    return kept


def draft_issue(inst: dict) -> str:
    """真实做法（SWE-smith §D）：把 `.diff`、一个随机 F2P 测试的源码、
    以及带 bug 跑测试的输出一起喂给 LM，让它写成 GitHub issue 风格，
    **并且包含基于 F2P 测试的复现代码**。成本约 2.54 美分一条。

    这里给一个不调模型的占位版本，说明需要哪些字段。"""
    t = inst["FAIL_TO_PASS"][0]
    return (f"### Unexpected behaviour in `{inst['bugged_file']}`\n\n"
            f"After upgrading, `{t.split('::')[-1]}` no longer behaves as documented.\n\n"
            f"**To reproduce**\n```bash\npytest {t}\n```\n\n"
            f"**Expected**: the assertion holds.  **Actual**: it fails.")


if __name__ == "__main__":
    root = toyrepo.build()
    out = synthesize(root)
    for o in out:
        o["problem_statement"] = draft_issue(o)
    Path("/tmp/swe_synth.json").write_text(json.dumps(out, indent=2))
    print(f"\n对比：挖 PR 只得到 5 个实例；同一个仓库合成得到 {len(out)} 个。")
    print("这就是 SWE-smith 「128 个仓库 → 5 万实例」的机制。")
    if out:
        e = out[0]
        print(f"\n样例：{e['instance_id']}\n  策略 {e['strategy']}"
              f"\n  F2P {e['FAIL_TO_PASS']}\n  P2P {len(e['PASS_TO_PASS'])} 个")
