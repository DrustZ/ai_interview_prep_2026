# cr_data · Code review agent 的数据 pipeline（可跑）

配套文章：[`../../22_code_review_agent_data.md`](../../22_code_review_agent_data.md)

```bash
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V toyreview.py                    # 造语料：git 历史 + 19 条 review 评论 + ground truth
$V signals.py                      # ① 采纳信号（真 git diff）② SZZ（真 git blame）
$V gate.py                         # 过滤漏斗 + **校准自动信号**
$V pairs.py                        # 正负样本（含「未评论行」陷阱组）+ 偏好对
$V reward.py                       # 分层 reward + 精度优先 + 防 hack
$V -m pytest test_cr_data.py -q    # 20 passed
```

只依赖 numpy + pytest。**采纳信号和 SZZ 都是真的调 git 算出来的。**

| 文件 | 干什么 | 对应文章 |
|---|---|---|
| `toyreview.py` | 语料：6 个 commit + 19 条评论（8 条真信号、11 条五类噪声）+ ground truth | §2 |
| `signals.py` | **制造可验证性**：采纳信号 + SZZ 回溯 | §3 |
| `gate.py` | 过滤（bot/nit/夸奖/提问/重复）+ **校准**（precision/recall vs 人工标注） | §4 |
| `pairs.py` | 三类正样本（按证据强度）+ 四类负样本 + 一个陷阱组 | §5 |
| `reward.py` | 三层 reward、两段式精度优先、hack 监控 | §6 |

## 跑出来的四个关键结果

**① 采纳信号能算，但有 30% 假阳性**
```
precision 70%  recall 88%  TP=7 FP=3 FN=1 TN=8
假阳性：cm07(夸奖) cm14(nit) cm17(事实错误的安全评论)
假阴性：cm03（说得对、当时没采纳，三周后变成真 bug）
```

**② SZZ 真的回溯到了引入 bug 的 commit**
```
bug-fix 5023e36 → git blame → 由 5be7388 引入  ✅ 命中期望
可验证正样本：shop/orders.py:21 `if code == "SAVE10":`
```

**③ 词袋去重抓不到改写**
```
阈值 0.35 → 0 条    阈值 0.10 → cm18≈cm11、cm19≈cm01
```

**④ F1 最优阈值不随误报代价变化，产品最优会变**
```
信任衰减 0.95 → 产品最优 0.075（比 F1 宽 0.60）
信任衰减 0.75 → 恰好重合（巧合）
信任衰减 0.45 → 产品最优 0.825（比 F1 严 0.15）
F1 最优永远是 0.675
```

## 三个测试专门守着这个领域最容易犯的错

- `test_unreviewed_lines_are_kept_separate` —— 把「没人评论的行」当负样本
- `test_an_unreviewed_line_actually_contained_a_real_bug` —— 证明上一条不是洁癖
- `test_f1_optimum_ignores_false_positive_cost` —— F1 不知道误报值多少钱
