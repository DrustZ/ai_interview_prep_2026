"""Employee Management System — 四级 OA 题目与 Python 解法。

题目说明
========
实现一个员工管理系统。输入是一系列按顺序执行的操作，所有返回值在
``solution(queries)`` 中转换为字符串。工作时间和查询区间都按照半开区间
``[start, end)`` 处理。

Level 1：添加员工与打卡
-----------------------

``ADD_WORKER worker_id position compensation``
    添加员工并保存职位和单位时间工资。
    员工 ID 已存在时返回 ``"false"``，否则返回 ``"true"``。

``REGISTER worker_id timestamp``
    同一个操作交替表示进入和离开办公室：

    * 员工当前不在办公室：本次是 clock-in；
    * 员工当前在办公室：本次是 clock-out，并形成一个完成的工作区间；
    * 员工不存在：返回 ``"invalid_request"``；
    * 成功：返回 ``"registered"``。

``GET worker_id``
    返回该员工所有已完成工作区间的总时长。尚未 clock-out 的区间不计算。
    员工不存在时返回 ``"-1"``。

Level 2：按职位查询 Top N
-------------------------

``TOP_N_WORKERS n position``
    只选择当前职位等于 ``position`` 且至少打过一次卡的员工，按照：

    1. 已完成的总工作时长降序；
    2. ``worker_id`` 字典序升序；

    返回 ``"worker_id(total), worker_id(total)"``。没有匹配员工时返回空串。
    Promotion 生效后，员工归入新职位；排名时间仍是其所有已完成区间的总和。

Level 3：延迟 Promotion 与工资计算
----------------------------------

``PROMOTE worker_id new_position new_compensation start_timestamp``
    安排一次晋升。它不会立刻生效，而是在 ``start_timestamp`` 到达后，该员工
    下一次进入办公室时生效。已经有未生效 promotion 或员工不存在时返回
    ``"invalid_request"``，否则返回 ``"success"``。

``CALC_SALARY worker_id start end``
    计算查询区间 ``[start, end)`` 内的工资。只计算已完成的工作区间，并使用
    每次 clock-in 时生效的工资率。因此每个工作区间必须保存当时的 rate，不能
    只读取员工当前 rate。员工不存在时返回空串。

    对工作区间 ``[a, b)``，实际计薪长度为：
    ``max(0, min(b, end) - max(a, start))``。

Level 4：双倍工资区间
---------------------

``SET_DOUBLE_PAID start end``
    增加一个全体员工的双倍工资区间 ``[start, end)``，返回 ``"success"``。

    多个 double-pay 区间可能重叠，必须先取并集。重叠部分仍然只支付 2 倍，
    不能叠加成 3 倍或 4 倍。最终工资可以写成：

    ``普通覆盖时长 * rate + bonus 并集覆盖时长 * rate``。

例子
====
员工 A 的 rate 是 10，工作区间为 ``[0, 40)``，double-pay 区间分别为
``[5, 25)`` 和 ``[20, 35)``。两个 bonus 区间合并为 ``[5, 35)``，因此：

``40 * 10 + 30 * 10 = 700``。

本题面根据本地保存的同题资料整理，不是会员页面的逐字复制。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Worker:
    position: str
    rate: int
    entered_at: Optional[int] = None
    entry_rate: int = 0
    sessions: List[Tuple[int, int, int]] = field(default_factory=list)
    total_time: int = 0
    has_registered: bool = False
    # (new_position, new_rate, effective_timestamp)
    pending_promotion: Optional[Tuple[str, int, int]] = None


class EmployeeManagement:
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        # Sorted, non-overlapping double-pay intervals.
        self.double_paid: List[Tuple[int, int]] = []

    def add_worker(self, worker_id: str, position: str, rate: int) -> str:
        if worker_id in self.workers:
            return "false"
        self.workers[worker_id] = Worker(position, rate)
        return "true"

    def register(self, worker_id: str, timestamp: int) -> str:
        if worker_id not in self.workers:
            return "invalid_request"

        worker = self.workers[worker_id]

        if worker.entered_at is None:  # clock in
            promotion = worker.pending_promotion
            if promotion and timestamp >= promotion[2]:
                worker.position, worker.rate, _ = promotion
                worker.pending_promotion = None

            worker.entered_at = timestamp
            worker.entry_rate = worker.rate
            worker.has_registered = True
        else:  # clock out
            start = worker.entered_at
            worker.sessions.append((start, timestamp, worker.entry_rate))
            worker.total_time += timestamp - start
            worker.entered_at = None

        return "registered"

    def get(self, worker_id: str) -> str:
        worker = self.workers.get(worker_id)
        return "-1" if worker is None else str(worker.total_time)

    def top_n_workers(self, n: int, position: str) -> str:
        ranking = [
            (worker.total_time, worker_id)
            for worker_id, worker in self.workers.items()
            if worker.position == position and worker.has_registered
        ]
        ranking.sort(key=lambda item: (-item[0], item[1]))
        return ", ".join(
            f"{worker_id}({total})" for total, worker_id in ranking[:n]
        )

    def promote(
        self,
        worker_id: str,
        new_position: str,
        new_rate: int,
        start_timestamp: int,
    ) -> str:
        worker = self.workers.get(worker_id)
        if worker is None or worker.pending_promotion is not None:
            return "invalid_request"

        worker.pending_promotion = (new_position, new_rate, start_timestamp)
        return "success"

    def set_double_paid(self, start: int, end: int) -> str:
        self.double_paid.append((start, end))
        self.double_paid.sort()

        merged: List[Tuple[int, int]] = []
        for left, right in self.double_paid:
            if not merged or left > merged[-1][1]:
                merged.append((left, right))
            else:
                old_left, old_right = merged[-1]
                merged[-1] = (old_left, max(old_right, right))

        self.double_paid = merged
        return "success"

    def calc_salary(self, worker_id: str, start: int, end: int) -> str:
        worker = self.workers.get(worker_id)
        if worker is None:
            return ""

        salary = 0
        for clock_in, clock_out, rate in worker.sessions:
            left = max(start, clock_in)
            right = min(end, clock_out)
            if left >= right:
                continue

            # Everyone receives the normal rate once.
            salary += (right - left) * rate

            # A double-pay interval contributes one additional normal rate.
            for bonus_start, bonus_end in self.double_paid:
                if bonus_end <= left:
                    continue
                if bonus_start >= right:
                    break
                overlap = min(right, bonus_end) - max(left, bonus_start)
                salary += overlap * rate

        return str(salary)

    def command(self, *query: str) -> str:
        op = query[0]
        if op == "ADD_WORKER":
            return self.add_worker(query[1], query[2], int(query[3]))
        if op == "REGISTER":
            return self.register(query[1], int(query[2]))
        if op == "GET":
            return self.get(query[1])
        if op == "TOP_N_WORKERS":
            return self.top_n_workers(int(query[1]), query[2])
        if op == "PROMOTE":
            return self.promote(query[1], query[2], int(query[3]), int(query[4]))
        if op == "CALC_SALARY":
            return self.calc_salary(query[1], int(query[2]), int(query[3]))
        if op == "SET_DOUBLE_PAID":
            return self.set_double_paid(int(query[1]), int(query[2]))
        return ""


def solution(queries: List[List[str]]) -> List[str]:
    office = EmployeeManagement()
    return [office.command(*query) for query in queries]
