#!/usr/bin/env python3
"""一键跑三个 lab 的全部测试。

用法:  python3 run_all.py          # 只跑测试
       python3 run_all.py --demo   # 顺带跑每个 lab 的 solution.py 演示
"""

import os
import subprocess
import sys

LABS = [
    "lab01_dedup_quality",
    "lab02_reward_design",
    "lab03_retrieval_negatives",
]
HERE = os.path.dirname(os.path.abspath(__file__))


def run(lab: str, script: str) -> int:
    path = os.path.join(HERE, lab)
    proc = subprocess.run([sys.executable, script], cwd=path,
                          capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
    return proc.returncode


def main() -> int:
    demo = "--demo" in sys.argv
    failed = []
    for lab in LABS:
        print("\n" + "#" * 78)
        print("# " + lab)
        print("#" * 78)
        if demo:
            run(lab, "solution.py")
            print("-" * 78)
        if run(lab, "test_solution.py") != 0:
            failed.append(lab)

    print("\n" + "=" * 78)
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1
    print("全部 {} 个 lab 测试通过".format(len(LABS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
