"""Deterministic weighted DataBatcher with exact checkpoint/resume.

This solves the publicly described three-part interview variant:

1. Mix named dataset iterators using positive integer weights.
2. Resume from a global sample ``offset`` and from serialized state.
3. Keep the long-run ratio when ``batch_size`` does not divide the sum of
   weights.

The important modeling choice is to define one infinite, deterministic sample
stream first and only then cut it into batches.  For datasets A/B with weights
2/1, the stream is A, A, B, A, A, B, ... .  Batch boundaries never reset that
stream, so remainders are naturally carried into later batches.

The provided DataRegistry may expose either ``get_iterator(name)`` or the more
efficient ``get_iterator(name, offset=...)``.  The latter permits fast resume;
with the one-argument interface, this implementation must replay each source
iterator to its saved per-source offset.
"""

from __future__ import annotations

import bisect
import inspect
from typing import Any, Dict, Generic, Iterator, List, Mapping, Optional, Protocol
from typing import Sequence, Tuple, TypeVar


SampleT = TypeVar("SampleT")


class DataRegistry(Protocol[SampleT]):
    """Conceptual interface supplied by the interview environment."""

    def get_iterator(self, dataset_name: str, offset: int = 0) -> Iterator[SampleT]:
        ...


class DatasetExhaustedError(RuntimeError):
    """Raised instead of returning a partial batch."""

    def __init__(self, dataset_name: str, source_offset: int) -> None:
        super().__init__(
            f"dataset {dataset_name!r} ended at source offset {source_offset}"
        )
        self.dataset_name = dataset_name
        self.source_offset = source_offset


class DataBatcher(Generic[SampleT], Iterator[List[SampleT]]):
    """Mix registry iterators into deterministic fixed-size batches.

    ``offset`` is measured in *samples in the global mixed stream*, not in
    batches.  Consequently, changing ``batch_size`` only changes grouping; it
    does not change the underlying sample sequence.

    Exact resume assumes that a registry iterator is deterministic for a fixed
    dataset name and source offset.  A production registry should also expose
    an immutable ``version`` attribute so a checkpoint can reject changed data.
    """

    STATE_VERSION = 1
    ALGORITHM = "contiguous-weighted-cycle-v1"

    def __init__(
        self,
        registry: DataRegistry[SampleT],
        datasets: Sequence[str],
        weights: Sequence[int],
        batch_size: int,
        *,
        offset: int = 0,
        registry_version: Optional[str] = None,
    ) -> None:
        self._validate_configuration(datasets, weights, batch_size, offset)

        self._registry = registry
        self._datasets: Tuple[str, ...] = tuple(datasets)
        self._weights: Tuple[int, ...] = tuple(weights)
        self._batch_size = batch_size
        self._total_weight = sum(self._weights)

        running = 0
        cumulative_weights: List[int] = []
        for weight in self._weights:
            running += weight
            cumulative_weights.append(running)
        self._cumulative_weights = tuple(cumulative_weights)

        detected_version = getattr(registry, "version", None)
        self._registry_version = (
            registry_version if registry_version is not None else detected_version
        )
        if self._registry_version is not None:
            self._registry_version = str(self._registry_version)

        self._position = offset
        self._source_offsets = self._source_offsets_at(offset)
        self._iterators = self._build_iterators(self._source_offsets)

    def __iter__(self) -> "DataBatcher[SampleT]":
        return self

    def __next__(self) -> List[SampleT]:
        return self.next_batch()

    @property
    def offset(self) -> int:
        """Global offset of the next sample that will be returned."""

        return self._position

    @property
    def source_offsets(self) -> Dict[str, int]:
        """Number of samples already consumed from every source."""

        return dict(zip(self._datasets, self._source_offsets))

    def next_batch(self) -> List[SampleT]:
        """Return exactly ``batch_size`` samples.

        For a deterministic, restartable registry this operation is atomic: if
        a source ends or raises while the batch is being assembled, iterator
        positions are rebuilt to their values before the call and no partial
        batch is returned.
        """

        old_position = self._position
        old_source_offsets = list(self._source_offsets)

        try:
            return [self._next_sample() for _ in range(self._batch_size)]
        except Exception:
            # Iterator objects cannot be rewound.  Recreate them from the
            # registry, which is also exactly what checkpoint restore does.
            restored = self._build_iterators(old_source_offsets)
            self._position = old_position
            self._source_offsets = old_source_offsets
            self._iterators = restored
            raise

    def save_state(self) -> Dict[str, Any]:
        """Return a JSON-serializable checkpoint for the next sample."""

        return {
            "state_version": self.STATE_VERSION,
            "algorithm": self.ALGORITHM,
            "datasets": list(self._datasets),
            "weights": list(self._weights),
            "batch_size": self._batch_size,
            "next_offset": self._position,
            "source_offsets": self.source_offsets,
            "registry_version": self._registry_version,
        }

    def load_state(self, state: Mapping[str, Any]) -> None:
        """Restore this instance after validating configuration and data."""

        if not isinstance(state, Mapping):
            raise TypeError("state must be a mapping")
        if state.get("state_version") != self.STATE_VERSION:
            raise ValueError("unsupported checkpoint state_version")
        if state.get("algorithm") != self.ALGORITHM:
            raise ValueError("checkpoint uses a different scheduling algorithm")
        if tuple(state.get("datasets", ())) != self._datasets:
            raise ValueError("checkpoint datasets do not match this batcher")
        if tuple(state.get("weights", ())) != self._weights:
            raise ValueError("checkpoint weights do not match this batcher")
        if state.get("batch_size") != self._batch_size:
            raise ValueError("checkpoint batch_size does not match this batcher")

        checkpoint_registry_version = state.get("registry_version")
        normalized_checkpoint_version = (
            None
            if checkpoint_registry_version is None
            else str(checkpoint_registry_version)
        )
        if normalized_checkpoint_version != self._registry_version:
            raise ValueError("registry version changed since the checkpoint")

        next_offset = state.get("next_offset")
        if (
            isinstance(next_offset, bool)
            or not isinstance(next_offset, int)
            or next_offset < 0
        ):
            raise ValueError("checkpoint next_offset must be a non-negative integer")

        expected_offsets = self._source_offsets_at(next_offset)
        raw_offsets = state.get("source_offsets")
        if not isinstance(raw_offsets, Mapping):
            raise ValueError("checkpoint source_offsets must be a mapping")
        try:
            saved_offsets = [raw_offsets[name] for name in self._datasets]
        except KeyError as exc:
            raise ValueError(f"checkpoint is missing source offset {exc.args[0]!r}") from exc
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in saved_offsets
        ):
            raise ValueError("checkpoint source offsets must be non-negative integers")
        if saved_offsets != expected_offsets:
            raise ValueError("checkpoint source offsets are inconsistent with next_offset")

        # Do not mutate the live instance until every iterator is restorable.
        restored = self._build_iterators(saved_offsets)
        self._position = next_offset
        self._source_offsets = saved_offsets
        self._iterators = restored

    @classmethod
    def from_state(
        cls,
        registry: DataRegistry[SampleT],
        state: Mapping[str, Any],
        *,
        registry_version: Optional[str] = None,
    ) -> "DataBatcher[SampleT]":
        """Construct and restore a batcher from serialized state."""

        try:
            datasets = state["datasets"]
            weights = state["weights"]
            batch_size = state["batch_size"]
        except (KeyError, TypeError) as exc:
            raise ValueError("checkpoint is missing batcher configuration") from exc

        batcher = cls(
            registry,
            datasets,
            weights,
            batch_size,
            registry_version=registry_version,
        )
        batcher.load_state(state)
        return batcher

    def _next_sample(self) -> SampleT:
        cycle_position = self._position % self._total_weight
        source_index = bisect.bisect_right(
            self._cumulative_weights, cycle_position
        )
        source_offset = self._source_offsets[source_index]
        try:
            sample = next(self._iterators[source_index])
        except StopIteration as exc:
            raise DatasetExhaustedError(
                self._datasets[source_index], source_offset
            ) from exc

        self._position += 1
        self._source_offsets[source_index] += 1
        return sample

    def _source_offsets_at(self, global_offset: int) -> List[int]:
        """Compute source consumption counts without replaying the schedule."""

        complete_cycles, remainder = divmod(global_offset, self._total_weight)
        offsets: List[int] = []
        cycle_start = 0
        for weight in self._weights:
            from_partial_cycle = min(max(remainder - cycle_start, 0), weight)
            offsets.append(complete_cycles * weight + from_partial_cycle)
            cycle_start += weight
        return offsets

    def _build_iterators(self, source_offsets: Sequence[int]) -> List[Iterator[SampleT]]:
        return [
            self._iterator_at(dataset_name, source_offset)
            for dataset_name, source_offset in zip(self._datasets, source_offsets)
        ]

    def _iterator_at(self, dataset_name: str, source_offset: int) -> Iterator[SampleT]:
        method = getattr(self._registry, "get_iterator", None)
        if method is None or not callable(method):
            raise TypeError("registry must provide get_iterator(dataset_name)")

        # Prefer the offset-aware form without catching a TypeError raised from
        # inside the registry implementation itself.
        signature = None
        try:
            signature = inspect.signature(method)
        except (TypeError, ValueError):
            pass

        if signature is not None:
            try:
                signature.bind(dataset_name, offset=source_offset)
            except TypeError:
                try:
                    signature.bind(dataset_name, source_offset)
                except TypeError:
                    iterator = iter(method(dataset_name))
                    self._replay(iterator, dataset_name, source_offset)
                    return iterator
                return iter(method(dataset_name, source_offset))
            return iter(method(dataset_name, offset=source_offset))

        # Some extension methods do not expose a signature.  The conceptual
        # interview interface is the one-argument form, so use the safe fallback.
        iterator = iter(method(dataset_name))
        self._replay(iterator, dataset_name, source_offset)
        return iterator

    @staticmethod
    def _replay(
        iterator: Iterator[SampleT], dataset_name: str, source_offset: int
    ) -> None:
        for consumed in range(source_offset):
            try:
                next(iterator)
            except StopIteration as exc:
                raise DatasetExhaustedError(dataset_name, consumed) from exc

    @staticmethod
    def _validate_configuration(
        datasets: Sequence[str],
        weights: Sequence[int],
        batch_size: int,
        offset: int,
    ) -> None:
        if not datasets:
            raise ValueError("at least one dataset is required")
        if len(datasets) != len(weights):
            raise ValueError("datasets and weights must have the same length")
        if len(set(datasets)) != len(datasets):
            raise ValueError("dataset names must be unique")
        if any(not isinstance(name, str) or not name for name in datasets):
            raise ValueError("dataset names must be non-empty strings")
        if any(
            isinstance(weight, bool) or not isinstance(weight, int) or weight <= 0
            for weight in weights
        ):
            raise ValueError("weights must be positive integers")
        if (
            isinstance(batch_size, bool)
            or not isinstance(batch_size, int)
            or batch_size <= 0
        ):
            raise ValueError("batch_size must be a positive integer")
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be a non-negative integer")
