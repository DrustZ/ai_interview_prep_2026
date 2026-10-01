# swe_data · SWE agent 训练数据 pipeline（可跑）

配套文章：[`../../21_swe_agent_data.md`](../../21_swe_agent_data.md)

```bash
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V toyrepo.py                     # 造玩具仓库（9 个 commit，真 git 历史）
$V github.py                      # 仓库筛选打分 + issue 链接解析
$V mine.py                        # 挖候选 + 真跑 pytest 做 F2P/P2P 三步验证
$V synth.py                       # SWE-smith 式 AST 造 bug + 执行验证
$V curate.py                      # 去重 / 去污染 / 难度分层（跑完整条链）
$V -m pytest test_swe_data.py -q  # 26 passed（约 30 秒）
```

**无网络、无 Docker、无 API key。F2P/P2P 是真跑测试跑出来的，不是模拟。**

| 文件 | 干什么 | 对应文章 |
|---|---|---|
| `toyrepo.py` | 造一个带真实 git 历史的仓库：5 个合格候选 + 3 个该被过滤 | §3 |
| `github.py` | 仓库筛选阈值（SWE-smith / SWE-rebench V2 的实际数字）+ issue 链接正则 | §2 |
| `mine.py` | PR→实例：劈 patch、便宜过滤、**三步执行验证** | §3, §5 |
| `synth.py` | 环境优先造 bug：6 种 AST 变换 + 执行筛选 | §6 |
| `curate.py` | MinHash 近重复、三层去污染、pass@k 难度 | §7 |

## 为什么用玩具仓库而不是 clone 真仓库

1. 真仓库要装依赖、跑几分钟、要网络 —— 学 pipeline 时这些全是噪声
2. **玩具仓库里我知道正确答案**（哪 5 个 commit 该被挖出来），所以能写断言
3. 它刻意埋了三种「不合格」commit：只改文档 / 只改测试 / 改代码但没加测试

`toyrepo.EXPECTED_VALID = 5` 就是 ground truth。**没有 ground truth 的 pipeline 没法调试。**

## 跑出来长什么样

```
挖到 8 个 commit（不含 initial）
  便宜过滤后剩 5 个进入执行验证
  ✅ 0f2d65e fix: mean() crashes with ZeroDivisionError    F2P=1 P2P=1
  ...
  ❌ 63ff97d chore: clarify mean() docstring   没有测试改动 → 无法自动验证
最终 5 个可用实例（产出率 62%）

基线：7 个测试全过
尝试 24 次变异 → 7 个有效 bug（产出率 29%）

近重复去除：丢 4 条   去污染：丢 1 条   最终：7 条
```

## 三个测试专门守着容易踩的坑

- `test_solution_patch_never_touches_test_files` —— gold patch 混进测试文件 = 答案泄漏
- `test_anchored_regex_beats_the_papers_substring_match` —— 论文那条无锚定正则会把
  `contest.py` 判成测试文件
- `test_empty_normalization_raises_instead_of_silently_deduping` —— schema 不一致
  会让去重静默把所有实例判成重复（我这次真踩了）
