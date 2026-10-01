"""造一个带**真实 git 历史**的玩具仓库，供整条 pipeline 跑在上面。

为什么要造而不是 clone 真仓库：
  * 真仓库要装依赖、跑几分钟、要网络 —— 学 pipeline 的时候这些全是噪声
  * 玩具仓库里我**知道正确答案**（哪几个 commit 该被挖出来），可以写断言
  * 它埋了真实世界会遇到的四种「不合格」commit，正好用来练过滤

产出：一个 /tmp 下的 git repo，8 个 commit：
    5 个合格候选（改代码 + 改测试，且测试真的从 fail 变 pass）
    3 个不合格（只改文档 / 只改测试 / 改代码但没加测试）
"""
from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

DEFAULT = Path("/tmp/swe_toyrepo")


def sh(cmd, cwd, check=True):
    return subprocess.run(cmd, cwd=str(cwd), shell=True, capture_output=True,
                          text=True, check=check)


def _w(root: Path, rel: str, body: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body).lstrip())


def _append(root: Path, rel: str, body: str):
    """追加时必须**单独** dedent 新块 —— 直接 read_text()+body 再整体 dedent
    会因为已有内容顶格而使公共前缀为空，新块的缩进被原样保留 → IndentationError。
    （我第一版就是这么写的，pytest 直接 collection error。）"""
    p = root / rel
    p.write_text(p.read_text().rstrip() + "\n\n" + textwrap.dedent(body).strip() + "\n")


def _commit(root: Path, msg: str, date: str):
    sh("git add -A", root)
    env = f'GIT_AUTHOR_DATE="{date}" GIT_COMMITTER_DATE="{date}"'
    sh(f'{env} git commit -q -m {msg!r}', root)


def build(root: Path = DEFAULT) -> Path:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    sh("git init -q -b main", root)
    sh('git config user.email a@b.c && git config user.name Dev', root)

    # ── c0：初始版本，四个函数各带一个 bug ───────────────────────────
    _w(root, "calc/__init__.py", "")
    _w(root, "calc/stats.py", '''
        def mean(xs):
            return sum(xs) / len(xs)                    # BUG: 空列表除零

        def median(xs):
            s = sorted(xs)
            return s[len(s) // 2]                       # BUG: 偶数长度不取平均

        def clamp(x, lo, hi):
            return max(lo, min(x, hi))
    ''')
    _w(root, "calc/text.py", '''
        def slugify(s):
            return s.lower().replace(" ", "-")          # BUG: 没去掉标点

        def truncate(s, n):
            return s[:n]                                # BUG: 没加省略号
    ''')
    _w(root, "tests/test_stats.py", '''
        from calc.stats import clamp

        def test_clamp():
            assert clamp(5, 0, 3) == 3
    ''')
    _w(root, "README.md", "# calc\n\nTiny numeric helpers.\n")
    _commit(root, "initial commit", "2025-01-06T10:00:00")

    # ── 合格候选 ×5：改代码 + 加测试 ─────────────────────────────────
    _w(root, "calc/stats.py", '''
        def mean(xs):
            if not xs:
                raise ValueError("mean() of empty sequence")
            return sum(xs) / len(xs)

        def median(xs):
            s = sorted(xs)
            return s[len(s) // 2]

        def clamp(x, lo, hi):
            return max(lo, min(x, hi))
    ''')
    _w(root, "tests/test_stats.py", '''
        import pytest
        from calc.stats import clamp, mean

        def test_clamp():
            assert clamp(5, 0, 3) == 3

        def test_mean_empty_raises():
            with pytest.raises(ValueError):
                mean([])
    ''')
    _commit(root, "fix: mean() crashes with ZeroDivisionError on empty input",
            "2025-01-09T11:00:00")

    _w(root, "calc/stats.py", (root / "calc/stats.py").read_text().replace(
        "    s = sorted(xs)\n    return s[len(s) // 2]",
        "    s = sorted(xs)\n    m = len(s) // 2\n"
        "    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2"))
    _append(root, "tests/test_stats.py", '''
        def test_median_even_length():
            from calc.stats import median
            assert median([1, 2, 3, 4]) == 2.5
    ''')
    _commit(root, "fix: median() wrong for even-length input", "2025-01-14T09:30:00")

    _w(root, "calc/text.py", '''
        import re

        def slugify(s):
            s = re.sub(r"[^\\w\\s-]", "", s.lower())
            return re.sub(r"[\\s_]+", "-", s).strip("-")

        def truncate(s, n):
            return s[:n]
    ''')
    _w(root, "tests/test_text.py", '''
        from calc.text import slugify

        def test_slugify_strips_punctuation():
            assert slugify("Hello, World!") == "hello-world"
    ''')
    _commit(root, "fix: slugify keeps punctuation in the slug", "2025-01-20T15:12:00")

    _w(root, "calc/text.py", (root / "calc/text.py").read_text().replace(
        "def truncate(s, n):\n    return s[:n]",
        'def truncate(s, n):\n'
        '    return s if len(s) <= n else s[: max(0, n - 1)] + "\\u2026"'))
    _append(root, "tests/test_text.py", '''
        def test_truncate_adds_ellipsis():
            from calc.text import truncate
            assert truncate("abcdef", 4) == "abc\\u2026"
            assert truncate("ab", 4) == "ab"
    ''')
    _commit(root, "fix: truncate() should append an ellipsis", "2025-01-27T18:03:00")

    _w(root, "calc/stats.py", (root / "calc/stats.py").read_text().replace(
        "def clamp(x, lo, hi):\n    return max(lo, min(x, hi))",
        "def clamp(x, lo, hi):\n"
        "    if lo > hi:\n"
        "        raise ValueError('lo must be <= hi')\n"
        "    return max(lo, min(x, hi))"))
    _append(root, "tests/test_stats.py", '''
        def test_clamp_rejects_inverted_bounds():
            import pytest
            from calc.stats import clamp
            with pytest.raises(ValueError):
                clamp(1, 5, 0)
    ''')
    _commit(root, "fix: clamp silently returns garbage when lo > hi",
            "2025-02-03T08:45:00")

    # ── 不合格 ×3：pipeline 必须把它们过滤掉 ──────────────────────────
    _w(root, "README.md", "# calc\n\nTiny numeric helpers.\n\n## Install\n\n`pip install -e .`\n")
    _commit(root, "docs: add install section", "2025-02-05T12:00:00")   # 只改文档

    _append(root, "tests/test_text.py", '''
        def test_slugify_idempotent():
            from calc.text import slugify
            assert slugify(slugify("A B")) == slugify("A B")
    ''')
    _commit(root, "test: add idempotence check for slugify", "2025-02-07T14:20:00")  # 只改测试

    _w(root, "calc/stats.py", (root / "calc/stats.py").read_text().replace(
        "def mean(xs):", "def mean(xs):\n    # NOTE: raises on empty input"))
    _commit(root, "chore: clarify mean() docstring", "2025-02-10T16:00:00")  # 改代码无测试

    return root


# 期望结果 —— 用来写断言。**没有 ground truth 的 pipeline 没法调试。**
EXPECTED_VALID = 5
EXPECTED_TOTAL_COMMITS = 9        # 含 initial


if __name__ == "__main__":
    r = build()
    log = sh("git log --oneline", r).stdout.strip().splitlines()
    print(f"建好了 {r}，{len(log)} 个 commit：")
    for line in reversed(log):
        print("  " + line)
