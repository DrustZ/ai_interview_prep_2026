"""7-day simulation of one home robot's edge upload queue.

Day schedule (1 tick = 1 hour, 24 ticks/day):
  * days 0-2, 5-6 : normal load, slightly oversubscribed vs. the daily quota
                    (so a small routine backlog builds up and aging matters);
  * day 3         : network outage 04:00-20:00 (home WiFi down) -- proves
                    chunked resume: files interrupted mid-upload finish later
                    without re-sending completed chunks;
  * day 4         : event storm -- a bad OTA push spikes FAILURE (and teleop
                    INTERVENTION) volume; ROUTINE video gets squeezed out of
                    the quota and partly evicted from the ring buffer, while
                    ROUTINE *metadata* still reaches the cloud (level 1).

Novelty is an embedding-distance proxy: each event carries an 8-dim scene
embedding; novelty = d / (1 + d) where d is the distance to the running
centroid of everything seen so far. Storm-day scenes are shifted, so they
score higher. Pure stdlib, deterministic under a fixed seed.

Run:  /usr/bin/python3 simulate.py
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from uploader import (
    EdgeUploader,
    Event,
    EventType,
    MiB,
    UploaderConfig,
)

DAYS = 7
OUTAGE_DAY = 3
OUTAGE_TICKS = range(4, 20)     # 16 hours of dead uplink
STORM_DAY = 4
EMBED_DIM = 8

VIDEO_BYTES = {
    EventType.INTERVENTION: 128 * MiB,  # teleop takeover: all cams + actions
    EventType.FAILURE: 96 * MiB,
    EventType.NOVELTY: 64 * MiB,
    EventType.ROUTINE: 48 * MiB,
}

NORMAL_COUNTS = {
    EventType.ROUTINE: 22,
    EventType.NOVELTY: 4,
    EventType.FAILURE: 2,
    EventType.INTERVENTION: 1,
}

STORM_COUNTS = {
    EventType.ROUTINE: 22,
    EventType.NOVELTY: 4,
    EventType.FAILURE: 60,      # OTA regression: retry/timeout storm
    EventType.INTERVENTION: 8,  # operators taking over the failing robots
}


class NoveltyScorer:
    """Embedding-distance proxy: distance of a scene to the running centroid."""

    def __init__(self) -> None:
        self._centroid = [0.0] * EMBED_DIM
        self._count = 0

    def score(self, embedding: List[float]) -> float:
        if self._count == 0:
            distance = 0.0
        else:
            distance = math.sqrt(sum(
                (e - c) ** 2 for e, c in zip(embedding, self._centroid)
            ))
        self._count += 1
        alpha = 1.0 / self._count
        self._centroid = [
            (1 - alpha) * c + alpha * e for c, e in zip(self._centroid, embedding)
        ]
        return distance / (1.0 + distance)


@dataclass
class SimResult:
    uploader: EdgeUploader
    generated: Dict[EventType, int]
    day_kinds: List[str] = field(default_factory=list)
    backlog_bytes_eod: List[int] = field(default_factory=list)


def _make_embedding(rng: random.Random, day: int) -> List[float]:
    # Storm-day scenes come from a shifted distribution (robot stuck in
    # unfamiliar states after the bad OTA) -> larger centroid distance.
    shift = 3.0 if day == STORM_DAY else 0.0
    return [rng.gauss(shift, 1.0) for _ in range(EMBED_DIM)]


def _events_for_day(
    day: int,
    rng: random.Random,
    scorer: NoveltyScorer,
    next_id: int,
    ticks_per_day: int,
) -> Tuple[Dict[int, List[Event]], int]:
    """Return {tick_in_day: [events]} for one day, plus the next free id."""
    counts = STORM_COUNTS if day == STORM_DAY else NORMAL_COUNTS
    by_tick: Dict[int, List[Event]] = {}
    for etype, n in counts.items():
        for _ in range(n):
            if day == STORM_DAY and etype in (EventType.FAILURE,
                                              EventType.INTERVENTION):
                tick_in_day = rng.randrange(2, 9)   # burst right after the OTA
            else:
                tick_in_day = rng.randrange(ticks_per_day)
            novelty = 0.0
            if etype is EventType.NOVELTY:
                novelty = scorer.score(_make_embedding(rng, day))
            event = Event(
                event_id=next_id,
                etype=etype,
                created_tick=day * ticks_per_day + tick_in_day,
                video_bytes=VIDEO_BYTES[etype],
                novelty=novelty,
            )
            by_tick.setdefault(tick_in_day, []).append(event)
            next_id += 1
    for events in by_tick.values():
        events.sort(key=lambda e: e.event_id)   # deterministic offer order
    return by_tick, next_id


def run_simulation(
    seed: int = 42,
    config: Optional[UploaderConfig] = None,
    days: int = DAYS,
) -> SimResult:
    cfg = config if config is not None else UploaderConfig()
    gen_rng = random.Random(seed)
    net_rng = random.Random(seed + 1)
    # Flaky residential uplink: 3% of chunk sends fail -> exercises backoff.
    uploader = EdgeUploader(
        config=cfg,
        failure_model=lambda _e, _a, _t: net_rng.random() < 0.03,
    )
    scorer = NoveltyScorer()
    generated = {etype: 0 for etype in EventType}
    day_kinds: List[str] = []
    backlog_eod: List[int] = []
    next_id = 0

    for day in range(days):
        if day == OUTAGE_DAY:
            day_kinds.append("outage")
        elif day == STORM_DAY:
            day_kinds.append("storm")
        else:
            day_kinds.append("normal")
        by_tick, next_id = _events_for_day(day, gen_rng, scorer, next_id,
                                           cfg.ticks_per_day)
        for tick_in_day in range(cfg.ticks_per_day):
            for event in by_tick.get(tick_in_day, []):
                uploader.offer(event)
                generated[event.etype] += 1
            network_up = not (day == OUTAGE_DAY and tick_in_day in OUTAGE_TICKS)
            uploader.run_tick(network_up=network_up)
        backlog_eod.append(uploader.buffer_used)

    return SimResult(uploader=uploader, generated=generated,
                     day_kinds=day_kinds, backlog_bytes_eod=backlog_eod)


def _fmt_mb(n_bytes: int) -> str:
    return "%7.1f" % (n_bytes / MiB)


def print_report(result: SimResult) -> None:
    up = result.uploader
    cfg = up.config
    header = ("day  kind      up_MB  budget%  meta  done(i/f/n/r)  "
              "drop(r/n/f)  backlog_MB")
    print(header)
    print("-" * len(header))
    for day in range(len(result.day_kinds)):
        stats = up.day_stats(day)
        done = stats.video_completed
        drop = stats.video_dropped
        pct = 100.0 * stats.bytes_uploaded / cfg.daily_budget_bytes
        print("%3d  %-6s %s   %5.1f%%  %4d   %2d/%2d/%2d/%2d      %2d/%2d/%2d  %s" % (
            day, result.day_kinds[day], _fmt_mb(stats.bytes_uploaded), pct,
            stats.metadata_uploaded,
            done[EventType.INTERVENTION], done[EventType.FAILURE],
            done[EventType.NOVELTY], done[EventType.ROUTINE],
            drop[EventType.ROUTINE], drop[EventType.NOVELTY],
            drop[EventType.FAILURE],
            _fmt_mb(result.backlog_bytes_eod[day]),
        ))

    print()
    print("== 7-day summary ==")
    for etype in EventType:
        print("  %-13s generated=%3d  video_completed=%3d  video_dropped=%3d" % (
            etype.value, result.generated[etype],
            up.completed_total(etype), up.dropped_total(etype)))
    over_budget = [
        s.day for s in up.days if s.bytes_uploaded > cfg.daily_budget_bytes
    ]
    print("  days over budget      : %s" % (over_budget or "none"))
    print("  intervention video lost: %d (invariant: must be 0)"
          % up.dropped_total(EventType.INTERVENTION))
    failures = sum(s.chunk_failures for s in up.days)
    print("  chunk send failures    : %d (all retried with exponential backoff)"
          % failures)
    exact = all(
        e.bytes_sent == e.metadata_bytes + e.video_bytes for e in up.completed
    )
    print("  resume exactness       : every completed event shipped exactly "
          "its size once -> %s" % exact)
    print()
    print("privacy-by-design: level-1 metadata (no pixels) reached the cloud for")
    meta_total = sum(s.metadata_uploaded for s in up.days)
    total_events = sum(result.generated.values())
    print("  %d/%d events, including every clip whose video was dropped -- the"
          % (meta_total, total_events))
    print("  cloud keeps full fleet visibility and pulls video on demand.")


def main() -> None:
    result = run_simulation(seed=42)
    print_report(result)


if __name__ == "__main__":
    main()
