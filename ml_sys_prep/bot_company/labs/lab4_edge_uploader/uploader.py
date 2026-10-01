"""Edge upload queue for a home-robot fleet (Playbook A, bandwidth-starved collection).

Models the on-device uploader of a home robot that must ship event clips to the
cloud over a residential WiFi uplink with a hard daily quota. Design invariants:

  1. Priority order: INTERVENTION > FAILURE > NOVELTY (embedding-distance proxy)
     > ROUTINE. Interventions are teleop takeovers -- the highest-value training
     data -- and are never dropped, ever.
  2. Two-level, privacy-by-design upload: a tiny metadata record (task id,
     outcome, novelty score -- no pixels) always uploads BEFORE any video bytes
     of the same event. Video is level 2 and competes under the quota. The
     cloud therefore has full fleet visibility even when video is triaged out,
     and can decide which video to pull. This is enforced structurally:
     ``_video_candidates`` refuses events whose metadata is not yet uploaded.
  3. Daily bandwidth budget is a hard cap: a chunk is only sent if it fits in
     the remaining budget, so the quota can never be exceeded.
  4. Large files upload in fixed-size chunks; completed chunks survive network
     outages and process restarts (resume = continue from ``chunks_done``).
  5. Transfer failures back off exponentially (base * 2^(attempts-1), capped).
  6. Aging: non-intervention events gain priority as they wait, so ROUTINE
     clips cannot starve forever behind a steady FAILURE stream. Aging is
     capped below the INTERVENTION floor: seniority never outranks a takeover.
  7. Ring buffer: when local storage is full, evict the lowest-effective-
     priority non-intervention video first (in practice: youngest ROUTINE).
     Evicting a video keeps its metadata queued -- the cloud still learns the
     clip existed. Interventions are never evicted; if only interventions
     remain, an incoming intervention is admitted over capacity (logged), and
     an incoming non-intervention is rejected instead.

Pure standard library, Python 3.9 compatible, fully deterministic (any
randomness is injected by the caller through ``failure_model``).
"""

import enum
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("edge_uploader")

MiB = 1024 * 1024


class EventType(enum.Enum):
    """Trigger classes, ordered by training value (see 06 Playbook A)."""

    INTERVENTION = "intervention"  # teleop takeover: labelled correction
    FAILURE = "failure"            # task retry / timeout / abort
    NOVELTY = "novelty"            # scene embedding far from fleet distribution
    ROUTINE = "routine"            # uniform random sample (anti selection-bias)


#: Base priority per class. INTERVENTION sits above the non-intervention
#: ceiling (see UploaderConfig) so no amount of aging or novelty bonus can
#: outrank it.
BASE_PRIORITY = {
    EventType.INTERVENTION: 100.0,
    EventType.FAILURE: 80.0,
    EventType.NOVELTY: 50.0,
    EventType.ROUTINE: 30.0,
}

# FailureModel(event, attempts_so_far, tick) -> True if this chunk send fails.
FailureModel = Callable[["Event", int, int], bool]


@dataclass(frozen=True)
class UploaderConfig:
    """Tuning knobs. Defaults model one robot on a home broadband uplink."""

    ticks_per_day: int = 24                       # 1 tick = 1 hour
    chunk_bytes: int = 4 * MiB                    # resumable-upload chunk size
    link_bytes_per_tick: int = 128 * MiB          # physical uplink per tick
    daily_budget_bytes: int = 1536 * MiB          # WiFi upload quota per day
    buffer_capacity_bytes: int = 6144 * MiB       # local NVMe ring buffer
    aging_per_tick: float = 0.5                   # priority points per waiting tick
    aging_cap: float = 55.0                       # max seniority bonus
    non_intervention_ceiling: float = 95.0        # aging can never cross this
    novelty_bonus_max: float = 15.0               # scales with embedding distance
    backoff_base_ticks: int = 2                   # first retry delay
    backoff_cap_ticks: int = 16                   # max retry delay

    def __post_init__(self) -> None:
        if self.chunk_bytes <= 0 or self.daily_budget_bytes <= 0:
            raise ValueError("chunk_bytes and daily_budget_bytes must be positive")
        if self.chunk_bytes > self.daily_budget_bytes:
            raise ValueError("a single chunk must fit inside the daily budget")
        if self.chunk_bytes > self.link_bytes_per_tick:
            raise ValueError("a single chunk must fit inside one tick of link capacity")
        if self.non_intervention_ceiling >= BASE_PRIORITY[EventType.INTERVENTION]:
            raise ValueError("ceiling must stay below the INTERVENTION floor")
        if self.aging_per_tick < 0 or self.aging_cap < 0:
            raise ValueError("aging parameters must be non-negative")
        if self.backoff_base_ticks < 1 or self.backoff_cap_ticks < self.backoff_base_ticks:
            raise ValueError("invalid backoff configuration")


@dataclass
class Event:
    """One triggered clip: a small metadata record plus a chunked video blob."""

    event_id: int
    etype: EventType
    created_tick: int
    video_bytes: int
    metadata_bytes: int = 2048
    novelty: float = 0.0            # embedding-distance proxy in [0, 1]

    # -- mutable upload state -------------------------------------------------
    chunks_done: int = 0
    metadata_done: bool = False
    video_dropped: bool = False     # evicted from ring buffer (metadata kept)
    attempts: int = 0               # consecutive failed chunk sends
    next_retry_tick: int = 0        # earliest tick the next send may happen
    bytes_sent: int = 0             # exact bytes shipped (proves no re-upload)

    def __post_init__(self) -> None:
        if self.video_bytes < 0 or self.metadata_bytes <= 0:
            raise ValueError("invalid event sizes")
        if not 0.0 <= self.novelty <= 1.0:
            raise ValueError("novelty must be in [0, 1]")

    def total_chunks(self, chunk_bytes: int) -> int:
        return (self.video_bytes + chunk_bytes - 1) // chunk_bytes

    def video_done(self, chunk_bytes: int) -> bool:
        return self.chunks_done >= self.total_chunks(chunk_bytes)

    def next_chunk_size(self, chunk_bytes: int) -> int:
        remaining = self.video_bytes - self.chunks_done * chunk_bytes
        return min(chunk_bytes, remaining)


def _type_counter() -> Dict[EventType, int]:
    return {etype: 0 for etype in EventType}


@dataclass
class DayStats:
    """Per-day accounting; the budget invariant is checked against this."""

    day: int
    bytes_uploaded: int = 0
    bytes_by_type: Dict[EventType, int] = field(default_factory=_type_counter)
    metadata_uploaded: int = 0
    video_completed: Dict[EventType, int] = field(default_factory=_type_counter)
    video_dropped: Dict[EventType, int] = field(default_factory=_type_counter)
    chunk_failures: int = 0
    overflow_admits: int = 0


class EdgeUploader:
    """Priority upload queue with quota, resume, backoff, aging and eviction.

    Usage: ``offer()`` events as triggers fire, then call ``run_tick()`` once
    per tick with the current link state. All scheduling decisions are made
    with an O(n) scan over pending events -- deliberate: n is bounded by the
    ring buffer, and aging makes priorities time-varying, which would leave a
    heap permanently stale.
    """

    def __init__(
        self,
        config: Optional[UploaderConfig] = None,
        failure_model: Optional[FailureModel] = None,
    ) -> None:
        self.config = config if config is not None else UploaderConfig()
        self._failure_model: FailureModel = (
            failure_model if failure_model is not None else (lambda _e, _a, _t: False)
        )
        self.now: int = 0
        self._events: List[Event] = []
        self._day_stats: Dict[int, DayStats] = {}
        self.completed: List[Event] = []
        self._seen_ids: set = set()

    # ------------------------------------------------------------------ admit

    def offer(self, event: Event) -> bool:
        """Admit an event, evicting lower-priority video if the buffer is full.

        Returns True if the event's *video* was admitted. The metadata record
        is queued unconditionally (it is ~5 orders of magnitude smaller than
        video and is the level-1 privacy artifact the cloud triages with).
        """
        if event.event_id in self._seen_ids:
            raise ValueError("duplicate event_id %d" % event.event_id)
        self._seen_ids.add(event.event_id)
        day = self._stats_for(self.now)

        admitted = self._make_room(event, day)
        if not admitted:
            event.video_dropped = True
            day.video_dropped[event.etype] += 1
            logger.info("buffer full: rejected video of %s #%d (metadata kept)",
                        event.etype.value, event.event_id)
        self._events.append(event)
        return admitted

    def _make_room(self, incoming: Event, day: DayStats) -> bool:
        """Ring-buffer eviction. Never touches INTERVENTION video."""
        needed = incoming.video_bytes
        if self.buffer_used + needed <= self.config.buffer_capacity_bytes:
            return True

        incoming_prio = self.effective_priority(incoming)
        victims = [
            e for e in self._events
            if e.etype is not EventType.INTERVENTION
            and not e.video_dropped
            and not e.video_done(self.config.chunk_bytes)
            and self.effective_priority(e) < incoming_prio
        ]
        # Evict cheapest-to-lose first: lowest effective priority, then newest.
        victims.sort(key=lambda e: (self.effective_priority(e), -e.created_tick,
                                    -e.event_id))
        freed = 0
        chosen: List[Event] = []
        for victim in victims:
            if self.buffer_used - freed + needed <= self.config.buffer_capacity_bytes:
                break
            chosen.append(victim)
            freed += victim.video_bytes

        if self.buffer_used - freed + needed <= self.config.buffer_capacity_bytes:
            for victim in chosen:
                self._evict_video(victim, day)
            return True

        if incoming.etype is EventType.INTERVENTION:
            # Nothing evictable is enough: admit over capacity rather than
            # ever losing a takeover. Bounded in practice (interventions are
            # rare); the overflow is surfaced in stats for fleet monitoring.
            for victim in chosen:
                self._evict_video(victim, day)
            day.overflow_admits += 1
            logger.warning("buffer overflow-admit for intervention #%d",
                           incoming.event_id)
            return True
        return False

    def _evict_video(self, event: Event, day: DayStats) -> None:
        event.video_dropped = True
        day.video_dropped[event.etype] += 1
        logger.info("evicted video of %s #%d (metadata kept)",
                    event.etype.value, event.event_id)

    # -------------------------------------------------------------- scheduling

    def effective_priority(self, event: Event, now: Optional[int] = None) -> float:
        """Base priority + novelty bonus + capped seniority (aging)."""
        tick = self.now if now is None else now
        base = BASE_PRIORITY[event.etype]
        if event.etype is EventType.INTERVENTION:
            return base  # never modified, never outranked
        if event.etype is EventType.NOVELTY:
            base += self.config.novelty_bonus_max * event.novelty
        age = max(0, tick - event.created_tick)
        aging = min(age * self.config.aging_per_tick, self.config.aging_cap)
        return min(base + aging, self.config.non_intervention_ceiling)

    def run_tick(self, network_up: bool = True) -> None:
        """Advance one tick; upload as much as quota/link/network allow."""
        day = self._stats_for(self.now)
        if network_up:
            self._upload_pass(day)
        self.now += 1

    def _upload_pass(self, day: DayStats) -> None:
        budget_left = self.config.daily_budget_bytes - day.bytes_uploaded
        link_left = self.config.link_bytes_per_tick

        # Level 1: metadata-first (privacy-by-design). Tiny, drains before any
        # video byte moves, still charged against the quota (honest accounting).
        pending_meta = sorted(
            (e for e in self._events if not e.metadata_done),
            key=lambda e: (-self.effective_priority(e), e.created_tick, e.event_id),
        )
        for event in pending_meta:
            cost = event.metadata_bytes
            if cost > budget_left or cost > link_left:
                break
            event.metadata_done = True
            event.bytes_sent += cost
            day.bytes_uploaded += cost
            day.bytes_by_type[event.etype] += cost
            day.metadata_uploaded += 1
            budget_left -= cost
            link_left -= cost
            self._maybe_finish(event, day)

        # Level 2: video chunks, strict priority. If the top candidate's chunk
        # does not fit the remaining quota we stop rather than bypass it with a
        # smaller low-priority file -- bypass would reintroduce starvation.
        while True:
            candidate = self._top_video_candidate()
            if candidate is None:
                break
            chunk = candidate.next_chunk_size(self.config.chunk_bytes)
            if chunk > budget_left or chunk > link_left:
                break
            if self._failure_model(candidate, candidate.attempts, self.now):
                candidate.attempts += 1
                delay = min(
                    self.config.backoff_base_ticks * (2 ** (candidate.attempts - 1)),
                    self.config.backoff_cap_ticks,
                )
                candidate.next_retry_tick = self.now + delay
                day.chunk_failures += 1
                logger.info("chunk send failed for #%d, retry in %d ticks",
                            candidate.event_id, delay)
                continue  # backoff excludes it; scan for the next candidate
            candidate.chunks_done += 1
            candidate.attempts = 0  # success resets backoff
            candidate.bytes_sent += chunk
            day.bytes_uploaded += chunk
            day.bytes_by_type[candidate.etype] += chunk
            budget_left -= chunk
            link_left -= chunk
            if candidate.video_done(self.config.chunk_bytes):
                day.video_completed[candidate.etype] += 1
            self._maybe_finish(candidate, day)

    def _top_video_candidate(self) -> Optional[Event]:
        best: Optional[Event] = None
        best_key = None
        for event in self._events:
            if event.video_dropped or event.video_done(self.config.chunk_bytes):
                continue
            if not event.metadata_done:  # level 2 never precedes level 1
                continue
            if event.next_retry_tick > self.now:  # still backing off
                continue
            key = (self.effective_priority(event), -event.created_tick, -event.event_id)
            if best_key is None or key > best_key:
                best, best_key = event, key
        return best

    def _maybe_finish(self, event: Event, day: DayStats) -> None:
        video_settled = event.video_dropped or event.video_done(self.config.chunk_bytes)
        if event.metadata_done and video_settled:
            self._events.remove(event)
            if not event.video_dropped:
                self.completed.append(event)

    # ------------------------------------------------------------------ stats

    @property
    def buffer_used(self) -> int:
        return sum(
            e.video_bytes for e in self._events
            if not e.video_dropped and not e.video_done(self.config.chunk_bytes)
        )

    def _stats_for(self, tick: int) -> DayStats:
        day = tick // self.config.ticks_per_day
        if day not in self._day_stats:
            self._day_stats[day] = DayStats(day=day)
        return self._day_stats[day]

    def day_stats(self, day: int) -> DayStats:
        if day not in self._day_stats:
            self._day_stats[day] = DayStats(day=day)
        return self._day_stats[day]

    @property
    def days(self) -> List[DayStats]:
        return [self._day_stats[d] for d in sorted(self._day_stats)]

    def dropped_total(self, etype: EventType) -> int:
        return sum(stats.video_dropped[etype] for stats in self._day_stats.values())

    def completed_total(self, etype: EventType) -> int:
        return sum(1 for e in self.completed if e.etype is etype)

    def pending_events(self) -> List[Event]:
        return list(self._events)
