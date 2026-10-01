#!/usr/bin/env python3
"""跑四个 Exa drill 的参考实现（全部自带断言）。

用法:  python3 run_all.py

会优先用 interview/.venv 的 python(带 torch);找不到就用当前解释器,
此时 drill C 会被跳过并提示。
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = "/Users/mingrui/Documents/codes/interview/.venv/bin/python"

DRILLS = [
    ("A · 检索评测指标", "drill_a_retrieval_metrics.py", False),
    ("B · 向量检索 / Matryoshka", "drill_b_vector_search.py", False),
    ("C · PyTorch InfoNCE", "drill_c_infonce_pytorch.py", True),   # 需要 torch
    ("D · Judge 一致率", "drill_d_judge_agreement.py", False),
    ("E · 流式分位数 / DDSketch", "drill_e_streaming_quantile.py", False),
]


def has_torch(python: str) -> bool:
    return subprocess.run([python, "-c", "import torch"],
                          capture_output=True).returncode == 0


def main() -> int:
    python = VENV if os.path.exists(VENV) else sys.executable
    torch_ok = has_torch(python)
    print("解释器: {}\ntorch: {}\n".format(python, "可用" if torch_ok else "不可用"))

    failed, skipped = [], []
    for title, script, needs_torch in DRILLS:
        if needs_torch and not torch_ok:
            skipped.append(title)
            continue
        print("=" * 70)
        print(title)
        print("=" * 70)
        proc = subprocess.run([python, script], cwd=HERE,
                              capture_output=True, text=True)
        # 只打印断言结果那几行,不刷屏追问预演
        for line in proc.stdout.splitlines():
            if "面试追问预演" in line:
                break
            print(line)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)
            failed.append(title)
        print()

    print("=" * 70)
    if skipped:
        print("跳过(缺 torch): " + ", ".join(skipped))
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1
    print("{} 个 drill 全部通过".format(len(DRILLS) - len(skipped)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
