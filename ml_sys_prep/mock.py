"""Mock 评分器：把 40 分 rubric 变成**机器判的门槛**，不是散文。

    python mock.py score --kind review      # 跑一次评分，存历史
    python mock.py status                   # 我现在 ready 了吗
    python mock.py followups --kind review   # 随机抽 3 个追问（答完再评分）
    python mock.py log                       # 历史记录

为什么要这个：`11_mock_interviews.md` 里那张 40 分表一直是散文，
所以从来没成为**门槛** —— 自己判会放水，而且没有历史可比。

过关判据（四条同时满足，且**连续两次**）：
    ① 总分 ≥ 32/40
    ② 无单项 < 3
    ③ 三个随机追问都没卡住
    ④ 在时限内讲完
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

LOG = Path(__file__).parent / ".mock_log.jsonl"

# ── 8 个维度 × 5 分 = 40（沿用 11_mock_interviews 的口径）
DIMS = {
    "framing": "先问清楚：澄清问题、定义成功、说明假设",
    "metrics": "指标选得对，且说清为什么不是别的",
    "data": "数据来源 / 标签可信度 / 泄漏 / split",
    "baseline": "有 baseline 阶梯，最蠢的那级也报了",
    "depth": "至少一处挖到「什么时候会咬人」+ 怎么验证",
    "priority": "分级清楚；**主动降级过一条**（含说明理由）",
    "honesty": "主动说边界；不确定处标明；不把设计说成经历",
    "delivery": "结论先行、控时、被打断能接回来",
}

KINDS = {
    "review": "陌生 repo code review（25 min）",
    "design": "ML system design（45 min）",
    "sysdesign": "非 ML 系统设计（45 min）",
    "deepdive": "项目深挖（20 min）",
    "presentation": "work trial presentation（40 min 讲 + 20 min Q&A）",
}

FOLLOWUPS = {
    "review": [
        "你说这里有泄漏 —— **影响有多大？**给个数。",
        "这条你标成 blocker，为什么不是 should fix？",
        "AI 报了这条你没采纳，为什么？",
        "如果只能改一处，你改哪个？",
        "你怎么验证你的判断是对的？现在就能验证吗？",
        "这段代码我们是故意这么写的，你怎么看？",
        "假设作者说没时间重构，你的建议会变吗？",
        "你漏了 X（面试官现场指出）—— 为什么没看到？",
    ],
    "design": [
        "为什么不用更简单的方案？",
        "数据从哪来？标签什么时候可得？",
        "这个指标被 game 了会怎样？",
        "规模乘以 100 会先在哪里坏掉？",
        "offline 提升多少你才敢上线？",
        "如果这个假设不成立，你的设计要改多少？",
        "谁会因为这个系统的错误而受损？",
    ],
    "sysdesign": [
        "写请求量再大 10 倍呢？",
        "这里为什么要强一致？最终一致行不行？",
        "某个下游挂了会怎样？",
        "怎么做灰度和回滚？",
        "为什么不用 X（一个更简单/更复杂的方案）？",
        "这个设计最贵的部分是哪里？",
    ],
    "deepdive": [
        "当时有什么替代方案？为什么否掉？",
        "你怎么知道它真的有效？对照是什么？",
        "重来一次你会怎么做？",
        "这个项目里你最大的判断失误是什么？",
        "和同事意见不一致时你怎么处理的？",
        "哪部分是你做的，哪部分是别人做的？",
    ],
    "presentation": [
        "这个数字是怎么算出来的？现在能重跑吗？",
        "你为什么先做这个而不是那个？",
        "哪里没成功？",
        "再给你两周你会做什么？",
        "这个结论在什么条件下不成立？",
    ],
}


def _load():
    if not LOG.exists():
        return []
    return [json.loads(x) for x in LOG.read_text().splitlines() if x.strip()]


def _passed(rec) -> bool:
    return (rec["total"] >= 32 and min(rec["scores"].values()) >= 3
            and rec["followups_ok"] >= 3 and rec["in_time"])


def cmd_followups(a):
    pool = FOLLOWUPS[a.kind]
    rng = random.Random(a.seed) if a.seed else random
    print(f"【{KINDS[a.kind]}】随机追问 —— 答完再去 score：\n")
    for i, q in enumerate(rng.sample(pool, min(3, len(pool))), 1):
        print(f"  {i}. {q}")
    print("\n⚠️ 卡住 / 答不出 / 开始绕 = 这一条不算过。")


def cmd_score(a):
    print(f"【{KINDS[a.kind]}】逐项打分（0–5，回车默认 3）\n")
    scores = {}
    for k, desc in DIMS.items():
        while True:
            raw = input(f"  {k:<10} {desc}\n    分数 [0-5] = ").strip()
            if raw == "":
                scores[k] = 3; break
            if raw.isdigit() and 0 <= int(raw) <= 5:
                scores[k] = int(raw); break
            print("    请输入 0–5")
    fu = input("\n  三个随机追问，答稳了几个？[0-3] = ").strip()
    it = input("  在时限内讲完了吗？[y/n] = ").strip().lower()
    note = input("  一句话记：这次最差的是什么？= ").strip()

    rec = {"ts": datetime.now().isoformat(timespec="seconds"), "kind": a.kind,
           "scores": scores, "total": sum(scores.values()),
           "followups_ok": int(fu or 0), "in_time": it.startswith("y"),
           "note": note}
    rec["passed"] = _passed(rec)
    with LOG.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\n  总分 {rec['total']}/40   最低单项 {min(scores.values())}"
          f"   追问 {rec['followups_ok']}/3   {'✅ 本次通过' if rec['passed'] else '❌ 本次不过'}")
    if not rec["passed"]:
        why = []
        if rec["total"] < 32: why.append(f"总分 {rec['total']} < 32")
        if min(scores.values()) < 3:
            why.append("单项 <3：" + "、".join(
                k for k, v in scores.items() if v < 3))
        if rec["followups_ok"] < 3: why.append(f"追问只稳了 {rec['followups_ok']}/3")
        if not rec["in_time"]: why.append("超时")
        print("  差在：" + "；".join(why))
    cmd_status(argparse.Namespace(kind=a.kind))


def cmd_status(a):
    recs = [r for r in _load() if not a.kind or r["kind"] == a.kind]
    print("\n─── ready 状态 ───")
    for kind in ([a.kind] if a.kind else KINDS):
        ks = [r for r in _load() if r["kind"] == kind]
        if not ks:
            print(f"  {kind:<14} 未练过")
            continue
        last2 = ks[-2:]
        ready = len(last2) == 2 and all(r["passed"] for r in last2)
        marks = " ".join("✅" if r["passed"] else "❌" for r in ks[-5:])
        print(f"  {kind:<14} {marks:<16} "
              f"{'🟢 READY（连续两次通过）' if ready else '🔴 未 ready'}")
    if recs:
        worst = {}
        for r in recs:
            for k, v in r["scores"].items():
                worst.setdefault(k, []).append(v)
        avg = sorted(((k, sum(v) / len(v)) for k, v in worst.items()),
                     key=lambda x: x[1])
        print("\n  最弱的三个维度（历史均分）：")
        for k, v in avg[:3]:
            print(f"    {k:<10} {v:.1f}/5   {DIMS[k]}")


def cmd_log(a):
    for r in _load():
        print(f"{r['ts']}  {r['kind']:<13} {r['total']:>2}/40  "
              f"追问{r['followups_ok']}/3  {'✅' if r['passed'] else '❌'}  {r['note']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("score", cmd_score), ("status", cmd_status),
                     ("followups", cmd_followups), ("log", cmd_log)):
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        if name in ("score", "followups", "status"):
            p.add_argument("--kind", choices=list(KINDS),
                           default=None if name == "status" else "review")
        if name == "followups":
            p.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
