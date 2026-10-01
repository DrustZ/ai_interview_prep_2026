import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "practice"
    / "anthropic"
    / "weighted_data_batcher.py"
)
SPEC = importlib.util.spec_from_file_location("weighted_data_batcher", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

DataBatcher = MODULE.DataBatcher
DatasetExhaustedError = MODULE.DatasetExhaustedError


class InfiniteRegistry:
    def __init__(self, version="registry-v1"):
        self.version = version

    def get_iterator(self, dataset_name, offset=0):
        index = offset
        while True:
            yield dataset_name, index
            index += 1


class LegacyOneArgumentRegistry:
    """Matches the minimal public conceptual interface."""

    def get_iterator(self, dataset_name):
        index = 0
        while True:
            yield dataset_name, index
            index += 1


class FiniteRegistry:
    def __init__(self, data):
        self.data = data

    def get_iterator(self, dataset_name, offset=0):
        return iter(self.data[dataset_name][offset:])


def names(batch):
    return [sample[0] for sample in batch]


class DataBatcherTests(unittest.TestCase):
    def test_part_1_exact_allocation_when_divisible(self):
        batcher = DataBatcher(
            InfiniteRegistry(), ["A", "B"], [2, 1], batch_size=3
        )

        self.assertEqual(names(next(batcher)), ["A", "A", "B"])
        self.assertEqual(names(next(batcher)), ["A", "A", "B"])

        three_sources = DataBatcher(
            InfiniteRegistry(), ["A", "B", "C"], [1, 1, 2], batch_size=4
        )
        self.assertEqual(Counter(names(next(three_sources))), {"A": 1, "B": 1, "C": 2})

    def test_part_2_offset_is_a_global_sample_offset(self):
        baseline = DataBatcher(
            InfiniteRegistry(), ["A", "B", "C"], [2, 1, 2], batch_size=1
        )
        full_stream = [next(baseline)[0] for _ in range(20)]

        resumed = DataBatcher(
            InfiniteRegistry(),
            ["A", "B", "C"],
            [2, 1, 2],
            batch_size=4,
            offset=7,
        )
        resumed_stream = next(resumed) + next(resumed)

        self.assertEqual(resumed_stream, full_stream[7:15])
        self.assertEqual(resumed.offset, 15)

    def test_save_and_json_round_trip_matches_uninterrupted_execution(self):
        registry = InfiniteRegistry()
        uninterrupted = DataBatcher(registry, ["A", "B"], [2, 1], batch_size=4)
        next(uninterrupted)
        next(uninterrupted)
        state = json.loads(json.dumps(uninterrupted.save_state()))
        expected = [next(uninterrupted) for _ in range(5)]

        restored = DataBatcher.from_state(InfiniteRegistry(), state)

        self.assertEqual([next(restored) for _ in range(5)], expected)
        self.assertEqual(restored.offset, uninterrupted.offset)

    def test_part_3_non_divisible_batches_carry_remainder_across_boundaries(self):
        batcher = DataBatcher(
            InfiniteRegistry(), ["A", "B"], [2, 1], batch_size=4
        )
        batches = [next(batcher) for _ in range(3)]
        flattened_names = [name for batch in batches for name, _ in batch]

        self.assertEqual(Counter(flattened_names), {"A": 8, "B": 4})
        self.assertNotEqual(Counter(names(batches[0])), Counter(names(batches[2])))

        one_at_a_time = DataBatcher(
            InfiniteRegistry(), ["large", "small"], [100, 1], batch_size=1
        )
        skewed = [next(one_at_a_time)[0][0] for _ in range(202)]
        self.assertEqual(Counter(skewed), {"large": 200, "small": 2})

    def test_minimal_registry_without_seek_replays_each_source(self):
        resumed = DataBatcher(
            LegacyOneArgumentRegistry(), ["A", "B"], [2, 1], batch_size=3, offset=4
        )

        self.assertEqual(next(resumed), [("A", 3), ("B", 1), ("A", 4)])

    def test_checkpoint_validation_rejects_corruption_and_version_drift(self):
        batcher = DataBatcher(
            InfiniteRegistry("v1"), ["A", "B"], [2, 1], batch_size=3
        )
        next(batcher)
        state = batcher.save_state()

        corrupted = json.loads(json.dumps(state))
        corrupted["source_offsets"]["A"] += 1
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            batcher.load_state(corrupted)

        with self.assertRaisesRegex(ValueError, "registry version changed"):
            DataBatcher.from_state(InfiniteRegistry("v2"), state)

        class RegistryWithoutVersion:
            def get_iterator(self, dataset_name, offset=0):
                return InfiniteRegistry().get_iterator(dataset_name, offset)

        with self.assertRaisesRegex(ValueError, "registry version changed"):
            DataBatcher.from_state(RegistryWithoutVersion(), state)

    def test_exhaustion_never_returns_or_commits_a_partial_batch(self):
        registry = FiniteRegistry({"A": ["a0", "a1"], "B": ["b0"]})
        batcher = DataBatcher(registry, ["A", "B"], [2, 1], batch_size=4)

        with self.assertRaises(DatasetExhaustedError):
            next(batcher)
        self.assertEqual(batcher.offset, 0)
        self.assertEqual(batcher.source_offsets, {"A": 0, "B": 0})

    def test_invalid_configuration(self):
        registry = InfiniteRegistry()
        invalid_arguments = [
            ([], [], 1),
            (["A"], [1, 2], 1),
            (["A", "A"], [1, 1], 1),
            (["A"], [0], 1),
            (["A"], [1], 0),
        ]
        for datasets, weights, batch_size in invalid_arguments:
            with self.subTest(datasets=datasets, weights=weights, batch_size=batch_size):
                with self.assertRaises(ValueError):
                    DataBatcher(registry, datasets, weights, batch_size)


if __name__ == "__main__":
    unittest.main()
