"""锁住整条 pipeline 的关键不变量。`pytest test_swe_data.py -q`"""
from __future__ import annotations

import pytest

import curate
import github
import mine
import synth
import toyrepo

ROOT = toyrepo.build()
INSTANCES = mine.run(ROOT)


# ───────────────────────────── 挖掘 + 执行验证
def test_yield_matches_ground_truth():
    """玩具仓库里我知道正确答案 —— 5 个合格、3 个该被过滤。"""
    assert len(INSTANCES) == toyrepo.EXPECTED_VALID


def test_every_instance_has_f2p_and_p2p():
    """没有 F2P 就没有 reward；没有 P2P 就没有防回归护栏。"""
    for i in INSTANCES:
        assert i["FAIL_TO_PASS"], i["instance_id"]
        assert isinstance(i["PASS_TO_PASS"], list)
        assert not set(i["FAIL_TO_PASS"]) & set(i["PASS_TO_PASS"])


def test_docs_only_and_test_only_commits_are_rejected():
    ids = {i["instance_id"] for i in INSTANCES}
    msgs = {i["problem_statement"] for i in INSTANCES}
    assert not any(m.startswith(("docs:", "test:", "chore:")) for m in msgs)
    assert len(ids) == len(INSTANCES)


def test_solution_patch_never_touches_test_files():
    """**gold patch 里混进测试文件 = 答案泄漏。** 训练时模型能直接看到断言。"""
    for i in INSTANCES:
        for line in i["patch"].splitlines():
            if line.startswith("+++ b/"):
                assert not mine.is_test_file(line[6:]), i["instance_id"]


def test_test_patch_only_touches_test_files():
    for i in INSTANCES:
        for line in i["test_patch"].splitlines():
            if line.startswith("+++ b/"):
                assert mine.is_test_file(line[6:]), i["instance_id"]


@pytest.mark.parametrize("path,expected", [
    ("tests/test_a.py", True), ("src/test_utils.py", True),
    ("pkg/foo_test.py", True), ("testing/conftest.py", True),
    ("src/core.py", False), ("docs/index.md", False),
])
def test_test_file_regex(path, expected):
    assert mine.is_test_file(path) is expected


@pytest.mark.parametrize("path", ["src/contest.py", "build/latest/x.py",
                                  "app/protests/views.py"])
def test_anchored_regex_beats_the_papers_substring_match(path):
    """SWE-rebench V2 用的是无锚定子串匹配 `(?i)(test(?:ing|s)?|e2e)`，
    这三个路径会被它误判成测试文件 —— 后果是这些文件的改动被当成 test_patch，
    **真正的 solution patch 变空，实例被静默丢弃**。加路径段边界就好了。"""
    assert mine.NAIVE_TEST_RE.search(path), "论文那条确实会误判"
    assert mine.is_test_file(path) is False, "加了锚定之后不该误判"


# ───────────────────────────── 合成
def test_synth_yields_more_than_mining():
    """合成路线的全部意义：同一个仓库产出更多实例。"""
    s = synth.synthesize(ROOT, verbose=False)
    assert len(s) >= len(INSTANCES)


def test_every_synth_bug_actually_breaks_a_test():
    """**执行验证不只验证解法，也用来筛「哪些改动是真 bug」。**"""
    for s in synth.synthesize(ROOT, verbose=False):
        assert s["FAIL_TO_PASS"] and s["PASS_TO_PASS"]


def test_mutation_is_deterministic():
    src = "def f(x):\n    return x + 1\n"
    a = synth.mutate(src, "swap_binop", 0)
    b = synth.mutate(src, "swap_binop", 0)
    assert a == b


def test_synth_patch_is_a_real_diff():
    """schema 护栏：存整份源码会让下游去重静默失效（我踩过）。"""
    for s in synth.synthesize(ROOT, verbose=False):
        curate.assert_is_diff(s["bug_patch"], s["instance_id"])


# ───────────────────────────── curate
def test_dedup_catches_identical_patches():
    a = dict(INSTANCES[0])
    b = dict(INSTANCES[0]); b["instance_id"] = "clone"
    kept, dropped = curate.dedup([a, b])
    assert len(kept) == 1 and len(dropped) == 1


def test_dedup_keeps_genuinely_different_patches():
    kept, _ = curate.dedup(INSTANCES)
    assert len(kept) >= len(INSTANCES) - 1


def test_empty_normalization_raises_instead_of_silently_deduping():
    with pytest.raises(ValueError):
        curate.assert_is_diff("def f():\n    return 1\n", "not-a-diff")


def test_decontamination_removes_benchmark_repos():
    fake = dict(INSTANCES[0]); fake["repo"] = "django/django"
    kept, removed = curate.decontaminate([fake])
    assert not kept and "benchmark" in removed[0][1]


def test_decontamination_catches_near_duplicate_patch():
    kept, removed = curate.decontaminate(
        [INSTANCES[0]], bench_repos=frozenset(),
        bench_patches=[INSTANCES[0]["patch"]])
    assert not kept


def test_empirical_difficulty_drops_zero_and_one():
    """pass@k ∈ {0,1} 的题在 GRPO 里组内优势全为 0 —— 白烧算力。"""
    assert curate.empirical_difficulty({}, [0] * 8)["keep_for_rl"] is False
    assert curate.empirical_difficulty({}, [1] * 8)["keep_for_rl"] is False
    assert curate.empirical_difficulty({}, [0, 1, 0, 0])["keep_for_rl"] is True


# ───────────────────────────── 仓库筛选
def test_repo_filter_excludes_benchmark_and_forks():
    by = {r["repo"]: r for r in map(github.score_repo, github.SAMPLE)}
    assert not by["pallets/flask"]["keep"]        # benchmark 测试仓库
    assert not by["acme/fastapi-clone"]["keep"]   # fork
    assert not by["corp/internal-tool"]["keep"]   # 非宽松 license
    assert by["tqdm/tqdm"]["keep"]


def test_linked_issue_requires_resolving_verb():
    assert github.linked_issue_numbers("Fixes #1, closes #2") == [1, 2]
    assert github.linked_issue_numbers("related to #3") == []
