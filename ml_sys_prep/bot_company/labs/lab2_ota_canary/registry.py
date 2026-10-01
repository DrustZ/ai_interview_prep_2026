"""Minimal model registry with JSONL event-sourced persistence.

Responsibilities
----------------
1. Track every model version with full lineage: which training-data manifest
   produced it and which parent version it was fine-tuned from. Any production
   model must be able to answer "what data, what parent" (blast-radius analysis
   when a bad data batch is discovered).
2. Enforce the rollout state machine:

       staged -> canary_1pct -> canary_10pct -> fleet
                     |               |            |
                     +---------------+------------+--> rolled_back

   Promotion only moves one step forward along the path. Rollback is only
   legal from an in-flight or fully deployed stage (never from ``staged``,
   which has nothing running, and never twice). Every illegal transition
   raises :class:`IllegalTransitionError` -- the registry is the last line of
   defence against a buggy rollout controller.
3. Persist as an append-only JSONL event log. State is rebuilt by replaying
   the log, so the file is also a complete audit trail (who promoted what,
   when, and why).

Deliberate simplifications (call these out in an interview):
- No auth / no concurrent-writer locking (single-writer assumption).
- Promoting a new version to ``fleet`` does not auto-deprecate the previous
  fleet version; ``current_fleet_version`` simply returns the most recent one.
"""

import enum
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class Stage(enum.Enum):
    """Lifecycle stage of a model version."""

    STAGED = "staged"
    CANARY_1PCT = "canary_1pct"
    CANARY_10PCT = "canary_10pct"
    FLEET = "fleet"
    ROLLED_BACK = "rolled_back"


#: The only legal forward path. promote() moves exactly one step to the right.
PROMOTION_PATH: List[Stage] = [
    Stage.STAGED,
    Stage.CANARY_1PCT,
    Stage.CANARY_10PCT,
    Stage.FLEET,
]

#: Stages from which a rollback is legal (something is actually running).
ROLLBACK_SOURCES = frozenset(
    [Stage.CANARY_1PCT, Stage.CANARY_10PCT, Stage.FLEET]
)


class RegistryError(Exception):
    """Base class for all registry errors."""


class IllegalTransitionError(RegistryError):
    """Raised when a state transition violates the rollout state machine."""


class UnknownVersionError(RegistryError):
    """Raised when an operation references a version that was never registered."""


class DuplicateVersionError(RegistryError):
    """Raised when registering a version_id that already exists."""


@dataclass
class ModelVersion:
    """A single model version and its lineage.

    Attributes:
        version_id: Unique id, e.g. ``policy-2026-08-08-a``.
        train_manifest_id: Content-addressed id of the dataset manifest the
            model was trained on (episode-id list + processing-code hash).
        parent_version: Version this one was fine-tuned from, or ``None`` for
            a from-scratch train.
        stage: Current lifecycle stage.
        created_at: Unix timestamp of registration.
        history: Ordered transition records
            (``{"from": ..., "to": ..., "reason": ..., "ts": ...}``).
    """

    version_id: str
    train_manifest_id: str
    parent_version: Optional[str]
    stage: Stage = Stage.STAGED
    created_at: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)


class ModelRegistry:
    """JSONL-backed model registry.

    The on-disk format is one JSON event per line:

        {"event": "register",   "version_id": ..., "train_manifest_id": ...,
         "parent_version": ..., "ts": ...}
        {"event": "transition", "version_id": ..., "from": ..., "to": ...,
         "reason": ..., "ts": ...}

    Loading replays the log through the same validation code as live calls,
    so a corrupted/hand-edited log that encodes an illegal transition fails
    loudly at load time instead of silently poisoning state.
    """

    def __init__(self, path: str) -> None:
        """Open (or create) the registry backed by the JSONL file at ``path``."""
        self._path = path
        self._versions: Dict[str, ModelVersion] = {}
        if os.path.exists(path):
            self._replay()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        version_id: str,
        train_manifest_id: str,
        parent_version: Optional[str] = None,
    ) -> ModelVersion:
        """Register a new version in ``staged``. Lineage fields are mandatory.

        Raises:
            DuplicateVersionError: ``version_id`` already exists.
            UnknownVersionError: ``parent_version`` given but never registered.
            ValueError: empty ``version_id`` or ``train_manifest_id``.
        """
        if not version_id or not train_manifest_id:
            raise ValueError("version_id and train_manifest_id must be non-empty")
        if version_id in self._versions:
            raise DuplicateVersionError("version already registered: %s" % version_id)
        if parent_version is not None and parent_version not in self._versions:
            raise UnknownVersionError("unknown parent version: %s" % parent_version)
        event = {
            "event": "register",
            "version_id": version_id,
            "train_manifest_id": train_manifest_id,
            "parent_version": parent_version,
            "ts": time.time(),
        }
        self._apply(event)
        self._append(event)
        return self._versions[version_id]

    def promote(self, version_id: str, reason: str = "") -> Stage:
        """Advance ``version_id`` exactly one step along the promotion path.

        Returns the new stage.

        Raises:
            UnknownVersionError: version was never registered.
            IllegalTransitionError: version is at ``fleet`` (nothing above it)
                or ``rolled_back`` (dead versions never come back -- retrain
                and re-register instead).
        """
        version = self._get_or_raise(version_id)
        if version.stage not in PROMOTION_PATH or version.stage == Stage.FLEET:
            raise IllegalTransitionError(
                "cannot promote %s from stage %s"
                % (version_id, version.stage.value)
            )
        next_stage = PROMOTION_PATH[PROMOTION_PATH.index(version.stage) + 1]
        return self._transition(version, next_stage, reason)

    def rollback(self, version_id: str, reason: str) -> Stage:
        """Move ``version_id`` to ``rolled_back``.

        A reason is required: rollbacks are incidents and must be auditable.

        Raises:
            UnknownVersionError: version was never registered.
            IllegalTransitionError: version is ``staged`` (nothing deployed)
                or already ``rolled_back``.
            ValueError: empty reason.
        """
        if not reason:
            raise ValueError("rollback requires a non-empty reason")
        version = self._get_or_raise(version_id)
        if version.stage not in ROLLBACK_SOURCES:
            raise IllegalTransitionError(
                "cannot roll back %s from stage %s"
                % (version_id, version.stage.value)
            )
        return self._transition(version, Stage.ROLLED_BACK, reason)

    def get(self, version_id: str) -> ModelVersion:
        """Return the :class:`ModelVersion` for ``version_id``."""
        return self._get_or_raise(version_id)

    def lineage(self, version_id: str) -> List[str]:
        """Return ``[version, parent, grandparent, ...]`` following parents."""
        chain: List[str] = []
        cursor: Optional[str] = version_id
        while cursor is not None:
            version = self._get_or_raise(cursor)
            chain.append(version.version_id)
            cursor = version.parent_version
        return chain

    def current_fleet_version(self) -> Optional[str]:
        """Most recently promoted version currently at ``fleet``, if any."""
        best_id: Optional[str] = None
        best_ts = float("-inf")
        for version in self._versions.values():
            if version.stage is not Stage.FLEET:
                continue
            ts = version.history[-1]["ts"] if version.history else version.created_at
            if ts >= best_ts:
                best_ts = ts
                best_id = version.version_id
        return best_id

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get_or_raise(self, version_id: str) -> ModelVersion:
        try:
            return self._versions[version_id]
        except KeyError:
            raise UnknownVersionError("unknown version: %s" % version_id)

    def _transition(self, version: ModelVersion, to: Stage, reason: str) -> Stage:
        event = {
            "event": "transition",
            "version_id": version.version_id,
            "from": version.stage.value,
            "to": to.value,
            "reason": reason,
            "ts": time.time(),
        }
        self._apply(event)
        self._append(event)
        return to

    def _apply(self, event: Dict[str, Any]) -> None:
        """Mutate in-memory state from a (pre-validated) event."""
        if event["event"] == "register":
            self._versions[event["version_id"]] = ModelVersion(
                version_id=event["version_id"],
                train_manifest_id=event["train_manifest_id"],
                parent_version=event["parent_version"],
                stage=Stage.STAGED,
                created_at=event["ts"],
            )
        elif event["event"] == "transition":
            version = self._versions[event["version_id"]]
            version.stage = Stage(event["to"])
            version.history.append(
                {
                    "from": event["from"],
                    "to": event["to"],
                    "reason": event["reason"],
                    "ts": event["ts"],
                }
            )
        else:
            raise RegistryError("unknown event type: %r" % event.get("event"))

    def _append(self, event: Dict[str, Any]) -> None:
        with open(self._path, "a") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
            handle.flush()

    def _replay(self) -> None:
        """Rebuild state by replaying the JSONL log through validation."""
        with open(self._path, "r") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    raise RegistryError(
                        "corrupt registry log %s at line %d" % (self._path, line_no)
                    )
                self._validate_replayed(event, line_no)
                self._apply(event)

    def _validate_replayed(self, event: Dict[str, Any], line_no: int) -> None:
        kind = event.get("event")
        if kind == "register":
            if event["version_id"] in self._versions:
                raise RegistryError(
                    "duplicate register in log at line %d" % line_no
                )
        elif kind == "transition":
            version = self._versions.get(event["version_id"])
            if version is None:
                raise RegistryError(
                    "transition for unknown version at line %d" % line_no
                )
            to = Stage(event["to"])
            legal_promote = (
                version.stage in PROMOTION_PATH
                and version.stage is not Stage.FLEET
                and PROMOTION_PATH[PROMOTION_PATH.index(version.stage) + 1] is to
            )
            legal_rollback = (
                to is Stage.ROLLED_BACK and version.stage in ROLLBACK_SOURCES
            )
            if not (legal_promote or legal_rollback):
                raise RegistryError(
                    "illegal transition %s->%s in log at line %d"
                    % (version.stage.value, to.value, line_no)
                )
        else:
            raise RegistryError("unknown event type at line %d" % line_no)
