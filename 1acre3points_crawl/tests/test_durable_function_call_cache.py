import tempfile
import unittest
from pathlib import Path

from practice.anthropic.durable_function_call_cache import (
    DurableFunctionCallCache,
    FunctionCallCache,
)


def describe(a, b=0, *, options=None):
    return a, b, options


def increment(value):
    return value + 1


class FunctionCallCacheTests(unittest.TestCase):
    def test_equivalent_calls_have_the_same_key(self):
        cached = FunctionCallCache(describe, 3)

        key1 = cached.create_cache_key(
            1, b=2, options={"outer": {"x": 1, "y": 2}}
        )
        key2 = cached.create_cache_key(
            a=1, options={"outer": {"y": 2, "x": 1}}, b=2
        )

        self.assertEqual(key1, key2)
        self.assertIsInstance(key1, str)
        hash(key1)

    def test_default_arguments_and_lru_eviction(self):
        calls = []

        def square(value, scale=1):
            calls.append(value)
            return value * value * scale

        cached = FunctionCallCache(square, 2)
        self.assertEqual(cached(2), 4)
        self.assertEqual(cached(value=2, scale=1), 4)  # same bound call
        self.assertEqual(cached(3), 9)
        self.assertEqual(cached(2), 4)  # 2 becomes MRU
        self.assertEqual(cached(4), 16)  # evicts 3
        self.assertEqual(cached(3), 9)  # recomputed

        self.assertEqual(calls, [2, 3, 4, 3])
        self.assertEqual(cached.hits, 2)
        self.assertEqual(cached.misses, 4)

    def test_non_json_argument_is_rejected_clearly(self):
        cached = FunctionCallCache(lambda value: value, 2)
        with self.assertRaises(TypeError):
            cached.create_cache_key({1, 2, 3})

    def test_wal_recovers_values_and_lru_order(self):
        calls = []

        def compute(value):
            calls.append(value)
            return {"answer": value * 10}

        with tempfile.TemporaryDirectory() as directory:
            log_path = str(Path(directory) / "cache.wal")

            first = DurableFunctionCallCache(compute, 2, log_path, fsync=False)
            first(1)
            first(2)
            first(1)  # LRU order is now 2, 1 and must survive restart.
            self.assertEqual(calls, [1, 2])

            recovered = DurableFunctionCallCache(compute, 2, log_path, fsync=False)
            self.assertEqual(recovered(1), {"answer": 10})
            self.assertEqual(calls, [1, 2])

            recovered(3)  # 2 is LRU and is evicted.
            recovered(2)
            self.assertEqual(calls, [1, 2, 3, 2])

    def test_recovery_ignores_corrupted_tail(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "cache.wal"
            cached = DurableFunctionCallCache(increment, 2, str(log_path), fsync=False)
            self.assertEqual(cached(5), 6)

            with log_path.open("ab") as log:
                log.write(b"truncated-crash-record")

            recovered = DurableFunctionCallCache(
                increment, 2, str(log_path), fsync=False
            )
            self.assertEqual(recovered(5), 6)
            self.assertEqual(len(recovered.cache), 1)

    def test_recovery_never_skips_over_a_corrupted_record(self):
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "cache.wal"
            cached = DurableFunctionCallCache(increment, 3, str(log_path), fsync=False)
            cached(1)

            with log_path.open("ab") as log:
                log.write(b"bad-checksum bad-payload\n")

            # This valid record is physically after the broken WAL prefix and
            # therefore must not be replayed after a restart.
            cached(2)
            recovered = DurableFunctionCallCache(increment, 3, str(log_path), fsync=False)
            self.assertEqual(len(recovered.cache), 1)


if __name__ == "__main__":
    unittest.main()
