# labs · 三个可跑实验

⏱ 每个 40–45 分钟，砍时版 10 分钟 ｜ 纯标准库，无任何依赖，`python3` 直接跑

## 为什么要动手

面试里说「我会做 hard negative mining」「我会加 length penalty 防刷量」是**空话**，谁都会说。跑完这三个 lab 之后，你能说的是具体的失效机理和它的修法——那才是 senior 信号。

每个 lab 的 README 里都写了「这个 lab 让你在面试里能说出哪句话」。

## 一键校验

```bash
python3 run_all.py
```

## 三个 lab

| Lab | 主题 | 日程 | 对口 | 面试里能说出的那句话 |
|---|---|---|---|---|
| [lab01_dedup_quality](lab01_dedup_quality/) | MinHash/LSH 去重 + 质量分类器偏见 | Day 2 上午 | [07](../07_pretraining_data.md) §六/§七，OpenAI pretraining | LSH 阈值 ≈ `(1/b)^(1/r)`；阈值压到 0.5 就把「样板相同、规格不同」的商品页当重复删了，删的是长尾事实 |
| [lab02_reward_design](lab02_reward_design/) | code review reward + reward hacking | Day 1 晚 | [04](../04_case_code_review_llm.md) §7–§8 | 刷量的根因不是缺 length penalty，是 reward **没有按缺陷去重**；precision 的分子必须是「独立真缺陷数」 |
| [lab03_retrieval_negatives](lab03_retrieval_negatives/) | InfoNCE + 假负例 + Matryoshka 级联 | Day 2 下午 | [06](../06_search_post_training.md) §五/§六，Exa | hard negative 的 top-k 里混着未标注的相关文档，直接当负例会把自己的正例训练成负例 |

## 每个 lab 的结构

```
README.md          实测结论 + 追问预演（先读这个）
solution.py        参考实现，直接 python3 跑，输出即结论
test_solution.py   把结论变成可执行断言
starter.py         （仅 lab02）自己写一遍的 TODO 版
```

## 建议用法

1. **先跑 `solution.py` 看输出**——每个 lab 的输出本身就是一段可以复述的论证；
2. 读 README 的「实测结论」，对照输出确认自己看懂了失效机理；
3. 时间够的话跑 `test_solution.py`，读断言——断言写的是「什么必须成立」，比读实现更快抓住重点；
4. lab02 有 `starter.py`，值得真的自己写一遍（限时 30 min），因为 reward 设计是你已经被问过、还会再被问的题。

## 诚实性提醒

这些是**教学用的最小复现**，不是 production 系统，也不是你的项目经历。面试里正确的说法是：

> 为了补这块知识，我写了一个小规模可复现的实验，验证的是 ___；它不能证明 ___（真实规模下的表现），下一步要做的是 ___。

见 [12_personal_bridge.md](../12_personal_bridge.md) §6。
