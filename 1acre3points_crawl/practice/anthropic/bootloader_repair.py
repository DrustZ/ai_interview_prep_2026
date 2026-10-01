"""Simple LeetCode-style O(n) solution for the Bootloader problem."""

from typing import List, Optional, Tuple


class Solution:
    def firstRepeatedIndex(self, instructions: List[str]) -> int:
        """Part 1: first instruction executed twice; -1 if execution exits."""
        program = self._parse(instructions)
        n = len(program)
        seen = set()
        pc = 0

        while 0 <= pc < n and pc not in seen:
            seen.add(pc)
            pc = self._next(program, pc)

        return pc if 0 <= pc < n else -1

    def fixBootloader(self, instructions: List[str]) -> int:
        """Part 2: swap one jump/next and return the final accumulator."""
        program = self._parse(instructions)
        n = len(program)

        # good[i] means the unmodified program starting at i reaches n.
        reverse = [[] for _ in range(n + 1)]
        for i in range(n):
            nxt = self._next(program, i)
            if 0 <= nxt <= n:
                reverse[nxt].append(i)

        good = [False] * (n + 1)
        good[n] = True
        stack = [n]
        while stack:
            node = stack.pop()
            for previous in reverse[node]:
                if not good[previous]:
                    good[previous] = True
                    stack.append(previous)

        # The public illustration already terminates without changing its
        # executed path, so return that result directly.
        terminated, accumulator = self._run(program)
        if terminated:
            return accumulator

        # A useful swap must occur on the original execution path.  If its
        # alternate edge enters `good`, the rest of the program reaches n.
        seen = set()
        pc = 0
        while 0 <= pc < n and pc not in seen:
            seen.add(pc)
            operation, value = program[pc]

            alternate: Optional[int] = None
            if operation == "jump":
                alternate = pc + 1
            elif operation == "next":
                alternate = pc + value

            if alternate is not None and 0 <= alternate <= n and good[alternate]:
                terminated, accumulator = self._run(program, swap_index=pc)
                if terminated:
                    return accumulator

            pc = self._next(program, pc)

        raise ValueError("no single jump/next swap terminates the program")

    def _run(
        self,
        program: List[Tuple[str, int]],
        swap_index: int = -1,
    ) -> Tuple[bool, int]:
        n = len(program)
        seen = set()
        pc = 0
        accumulator = 0

        while 0 <= pc < n and pc not in seen:
            seen.add(pc)
            operation, value = program[pc]

            if operation == "plus":
                accumulator += value
                pc += 1
            elif operation == "next":
                pc += value if pc == swap_index else 1
            else:  # jump
                pc += 1 if pc == swap_index else value

        return pc == n, accumulator

    @staticmethod
    def _next(program: List[Tuple[str, int]], pc: int) -> int:
        operation, value = program[pc]
        return pc + value if operation == "jump" else pc + 1

    @staticmethod
    def _parse(instructions: List[str]) -> List[Tuple[str, int]]:
        program = []
        for instruction in instructions:
            operation, value = instruction.split()
            if operation not in {"plus", "next", "jump"}:
                raise ValueError(f"unknown operation: {operation}")
            program.append((operation, int(value)))
        return program
