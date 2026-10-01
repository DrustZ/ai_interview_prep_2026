"""Executable invariants for the edge upload queue. Plain asserts, no pytest.

Run:  /usr/bin/python3 test_uploader.py

Each test states the fleet-learning invariant it encodes:
  1. priority + two-level upload   metadata (level 1) always precedes video
  2. intervention zero loss        never evicted, even when the buffer is full
  3. drop order                    routine -> novelty -> failure, never intervention
  4. budget never exceeded         hard daily WiFi quota (scripted + 7-day sim)
  5. resume after outage           completed chunks survive, no byte re-sent
  6. exponential backoff           retry gaps double: 2, 4, 8, then cap at 16
  7. storm squeezes routine        routine video yields, routine metadata flows
  8. aging beats starvation        an old routine clip overtakes fresh failures
  9. 7-day sim invariants          everything above holds end-to-end + determinism
"""

import logging
from typing import List

from uploader import (
    BASE_PRIORITY,
    EdgeUploader,
    Event,
    EventType,
    MiB,
    UploaderConfig,
)
from simulate import OUTAGE_DAY, STORM_DAY, run_simulation

KB = 1024


def _cfg(**overrides) -> UploaderConfig:
    """Small deterministic config for scripted tests."""
    base = dict(
        ticks_per_day=24,
        chunk_bytes=4 * MiB,
        link_bytes_per_tick=50 * MiB,
        daily_budget_bytes=10240 * MiB,
        buffer_capacity_bytes=10240 * MiB,
        aging_per_tick=0.0,          # aging off unless a test opts in
        aging_cap=55.0,
        backoff_base_ticks=2,
        backoff_cap_ticks=16,
    )
    base.update(overrides)
    return UploaderConfig(**base)


def _event(event_id: int, etype: EventType, video_mib: int,
           tick: int = 0, novelty: float = 0.0) -> Event:
    return Event(event_id=event_id, etype=etype, created_tick=tick,
                 video_bytes=video_mib * MiB, novelty=novelty)


# ---------------------------------------------------------------------- 1
def test_priority_order_and_two_level_upload() -> None:
    up = EdgeUploader(config=_cfg(link_bytes_per_tick=12 * MiB))
    up.offer(_event(0, EventType.ROUTINE, 8))
    up.offer(_event(1, EventType.NOVELTY, 8, novelty=0.9))
    up.offer(_event(2, EventType.FAILURE, 8))
    up.offer(_event(3, EventType.INTERVENTION, 8))

    up.run_tick()
    # Level 1 drained for *all* events before level 2 got a third chunk.
    assert all(e.metadata_done for e in up.pending_events() + up.completed), \
        "metadata of every event must upload before video saturates the tick"
    # Highest priority video went first.
    assert up.completed and up.completed[0].etype is EventType.INTERVENTION

    for _ in range(8):
        up.run_tick()
    order = [e.etype for e in up.completed]
    assert order == [EventType.INTERVENTION, EventType.FAILURE,
                     EventType.NOVELTY, EventType.ROUTINE], order
    print("PASS 1: priority order + metadata-first two-level upload")


# ---------------------------------------------------------------------- 2
def test_intervention_never_dropped() -> None:
    cfg = _cfg(buffer_capacity_bytes=100 * MiB)
    up = EdgeUploader(config=cfg)
    for i in range(5):
        assert up.offer(_event(i, EventType.ROUTINE, 20))
    assert up.buffer_used == 100 * MiB

    # Intervention evicts exactly enough routine video.
    assert up.offer(_event(10, EventType.INTERVENTION, 60))
    assert up.dropped_total(EventType.ROUTINE) == 3
    assert up.dropped_total(EventType.INTERVENTION) == 0

    # Buffer now: 2 routine (40) + 1 intervention (60). Two more interventions:
    # the first (40) evicts the remaining routines and fits exactly, the
    # second (60) finds nothing evictable and is admitted OVER capacity --
    # never lost, surfaced as an overflow in stats.
    assert up.offer(_event(11, EventType.INTERVENTION, 40))
    assert up.dropped_total(EventType.ROUTINE) == 5
    assert up.day_stats(0).overflow_admits == 0
    assert up.offer(_event(12, EventType.INTERVENTION, 60))
    assert up.dropped_total(EventType.INTERVENTION) == 0
    assert up.day_stats(0).overflow_admits == 1
    assert up.buffer_used > cfg.buffer_capacity_bytes  # logged overflow

    # Incoming routine while the buffer holds only interventions: the incoming
    # video is rejected (metadata still queued), interventions untouched.
    admitted = up.offer(_event(13, EventType.ROUTINE, 20))
    assert not admitted
    assert up.dropped_total(EventType.ROUTINE) == 6  # 3 + 2 evicted + 1 rejected
    assert up.dropped_total(EventType.INTERVENTION) == 0
    rejected = [e for e in up.pending_events() if e.event_id == 13][0]
    assert rejected.video_dropped and not rejected.metadata_done
    print("PASS 2: intervention video is never dropped (overflow-admit path incl.)")


# ---------------------------------------------------------------------- 3
def test_drop_order_routine_then_novelty_then_failure() -> None:
    up = EdgeUploader(config=_cfg(buffer_capacity_bytes=100 * MiB))
    up.offer(_event(0, EventType.ROUTINE, 30))
    up.offer(_event(1, EventType.NOVELTY, 30, novelty=0.5))
    up.offer(_event(2, EventType.FAILURE, 30))

    up.offer(_event(3, EventType.INTERVENTION, 40))  # needs 30 MiB freed
    assert up.dropped_total(EventType.ROUTINE) == 1, "routine must go first"
    assert up.dropped_total(EventType.NOVELTY) == 0
    assert up.dropped_total(EventType.FAILURE) == 0

    up.offer(_event(4, EventType.INTERVENTION, 60))  # needs 60 MiB freed
    assert up.dropped_total(EventType.NOVELTY) == 1, "novelty before failure"
    assert up.dropped_total(EventType.FAILURE) == 1, "failure only as last resort"
    assert up.dropped_total(EventType.INTERVENTION) == 0
    print("PASS 3: eviction order routine -> novelty -> failure, never intervention")


# ---------------------------------------------------------------------- 4
def test_budget_never_exceeded_scripted() -> None:
    cfg = _cfg(daily_budget_bytes=10 * MiB, chunk_bytes=4 * MiB,
               link_bytes_per_tick=50 * MiB)
    up = EdgeUploader(config=cfg)
    up.offer(_event(0, EventType.FAILURE, 40))  # 10 chunks, needs 4+ days
    for _ in range(5 * cfg.ticks_per_day):
        up.run_tick()
    for stats in up.days:
        assert stats.bytes_uploaded <= cfg.daily_budget_bytes, \
            "day %d used %d > budget" % (stats.day, stats.bytes_uploaded)
    # Quota really bites: exactly 2 chunks/day fit next to the metadata.
    assert up.days[0].bytes_uploaded == 2 * cfg.chunk_bytes + 2 * KB
    assert up.completed_total(EventType.FAILURE) == 1
    print("PASS 4: daily budget is a hard cap (chunk denied when it would overshoot)")


# ---------------------------------------------------------------------- 5
def test_resume_after_network_outage() -> None:
    cfg = _cfg(link_bytes_per_tick=8 * MiB + 8 * KB)
    up = EdgeUploader(config=cfg)
    event = _event(0, EventType.FAILURE, 40)  # 10 chunks of 4 MiB
    up.offer(event)

    for _ in range(3):                # tick 0: meta+1 chunk; ticks 1-2: 2 chunks
        up.run_tick(network_up=True)
    chunks_before_outage = event.chunks_done
    assert 0 < chunks_before_outage < event.total_chunks(cfg.chunk_bytes)

    for _ in range(4):                # WiFi down: state must be preserved
        up.run_tick(network_up=False)
    assert event.chunks_done == chunks_before_outage
    assert event.bytes_sent == chunks_before_outage * cfg.chunk_bytes + 2 * KB

    for _ in range(10):               # link back: finish from where we stopped
        up.run_tick(network_up=True)
    assert event.video_done(cfg.chunk_bytes)
    assert up.completed == [event]
    # THE resume invariant: exactly file size + metadata crossed the wire.
    assert event.bytes_sent == 40 * MiB + 2 * KB, \
        "re-uploaded bytes detected: %d" % event.bytes_sent
    print("PASS 5: chunked upload resumes after outage, zero bytes re-sent")


# ---------------------------------------------------------------------- 6
def test_exponential_backoff() -> None:
    failure_ticks: List[int] = []

    def flaky(_event: Event, attempts: int, tick: int) -> bool:
        if attempts < 4:              # first 4 sends fail, 5th succeeds
            failure_ticks.append(tick)
            return True
        return False

    cfg = _cfg()
    up = EdgeUploader(config=cfg, failure_model=flaky)
    event = _event(0, EventType.FAILURE, 4)   # single chunk
    up.offer(event)
    for _ in range(40):
        up.run_tick()

    # Retry schedule: fail@0 -> +2 -> fail@2 -> +4 -> fail@6 -> +8 ->
    # fail@14 -> +16 (capped) -> success@30.
    assert failure_ticks == [0, 2, 6, 14], failure_ticks
    gaps = [b - a for a, b in zip(failure_ticks, failure_ticks[1:])]
    assert gaps == [2, 4, 8], "retry gaps must double: %s" % gaps
    assert up.completed == [event]
    assert event.attempts == 0, "success must reset the backoff counter"
    assert event.bytes_sent == 4 * MiB + 2 * KB
    print("PASS 6: exponential backoff 2/4/8 then cap, state resets on success")


# ---------------------------------------------------------------------- 7
def test_storm_squeezes_routine_video_not_metadata() -> None:
    cfg = _cfg(daily_budget_bytes=200 * MiB, aging_per_tick=0.5)
    up = EdgeUploader(config=cfg)
    eid = 0
    for _ in range(5):
        up.offer(_event(eid, EventType.ROUTINE, 20)); eid += 1
    for _ in range(20):               # OTA incident: failure storm
        up.offer(_event(eid, EventType.FAILURE, 40)); eid += 1
    for _ in range(2):
        up.offer(_event(eid, EventType.INTERVENTION, 40)); eid += 1

    for _ in range(cfg.ticks_per_day):
        up.run_tick()
    day = up.day_stats(0)
    # Routine shipped ONLY its level-1 metadata; every video byte of the quota
    # went to interventions and failures.
    assert day.bytes_by_type[EventType.ROUTINE] == 5 * 2 * KB, \
        "routine video should be fully squeezed out on storm day"
    assert day.metadata_uploaded == 27, "cloud must still see all 27 events"
    assert day.video_completed[EventType.INTERVENTION] == 2
    assert day.bytes_uploaded <= cfg.daily_budget_bytes
    print("PASS 7: storm day squeezes routine video out; metadata still flows")


# ---------------------------------------------------------------------- 8
def test_aging_prevents_starvation() -> None:
    def run(aging_per_tick: float, horizon: int) -> EdgeUploader:
        cfg = _cfg(aging_per_tick=aging_per_tick,
                   link_bytes_per_tick=9 * MiB,
                   chunk_bytes=4 * MiB)
        up = EdgeUploader(config=cfg)
        up.offer(_event(0, EventType.ROUTINE, 8))     # the clip at risk
        for tick in range(horizon):                   # endless fresh failures
            up.offer(_event(1 + tick, EventType.FAILURE, 8, tick=tick))
            up.run_tick()
        return up

    # Control: no aging -> the routine clip starves forever.
    control = run(aging_per_tick=0.0, horizon=60)
    assert control.completed_total(EventType.ROUTINE) == 0, \
        "without aging the routine clip should starve (control)"

    # With aging 2.0/tick the routine clip overtakes fresh failures
    # (30 + 55 cap = 85 > 80) at ~tick 28 and completes.
    aged = run(aging_per_tick=2.0, horizon=60)
    assert aged.completed_total(EventType.ROUTINE) == 1, \
        "aging must eventually push the routine clip through"
    routine_done_index = next(i for i, e in enumerate(aged.completed)
                              if e.etype is EventType.ROUTINE)
    assert routine_done_index > 0, "routine must NOT jump the queue immediately"

    # Aging never crosses the intervention floor.
    old_routine = Event(event_id=999, etype=EventType.ROUTINE,
                        created_tick=0, video_bytes=MiB)
    assert aged.effective_priority(old_routine, now=10_000) < \
        BASE_PRIORITY[EventType.INTERVENTION]
    print("PASS 8: aging rescues routine from starvation, control run starves")


# ---------------------------------------------------------------------- 9
def test_seven_day_simulation_invariants() -> None:
    result = run_simulation(seed=42)
    up = result.uploader
    cfg = up.config

    # (a) intervention: zero loss, all videos fully delivered.
    assert up.dropped_total(EventType.INTERVENTION) == 0
    assert up.completed_total(EventType.INTERVENTION) == \
        result.generated[EventType.INTERVENTION]

    # (b) hard quota, every single day.
    for stats in up.days:
        assert stats.bytes_uploaded <= cfg.daily_budget_bytes, \
            "day %d over budget" % stats.day

    # (c) outage day uploads less; backlog carried over and resumed without
    #     re-sending: every completed event shipped exactly its size once.
    assert up.day_stats(OUTAGE_DAY).bytes_uploaded < \
        up.day_stats(0).bytes_uploaded
    for e in up.completed:
        assert e.bytes_sent == e.metadata_bytes + e.video_bytes, \
            "event %d re-uploaded bytes" % e.event_id

    # (d) storm day: routine video evicted (never intervention/failure here),
    #     intervention took the lion's share of the quota.
    storm = up.day_stats(STORM_DAY)
    assert storm.video_dropped[EventType.ROUTINE] > 0
    assert storm.video_dropped[EventType.INTERVENTION] == 0
    assert storm.bytes_by_type[EventType.INTERVENTION] > \
        storm.bytes_by_type[EventType.ROUTINE]
    assert storm.bytes_by_type[EventType.ROUTINE] < 0.25 * cfg.daily_budget_bytes

    # (e) privacy-by-design: level-1 metadata reached the cloud for EVERY
    #     generated event, including all dropped-video clips.
    meta_total = sum(s.metadata_uploaded for s in up.days)
    assert meta_total == sum(result.generated.values())

    # (f) backoff was actually exercised by the flaky link.
    assert sum(s.chunk_failures for s in up.days) > 0

    # (g) determinism: identical rerun.
    rerun = run_simulation(seed=42)
    assert [s.bytes_uploaded for s in rerun.uploader.days] == \
        [s.bytes_uploaded for s in up.days]
    print("PASS 9: 7-day sim -- zero intervention loss, quota held, resume exact,"
          " storm triage correct, deterministic")


def main() -> None:
    # The overflow-admit path in test 2 intentionally triggers a WARNING log;
    # keep the assertion output clean.
    logging.disable(logging.WARNING)
    test_priority_order_and_two_level_upload()
    test_intervention_never_dropped()
    test_drop_order_routine_then_novelty_then_failure()
    test_budget_never_exceeded_scripted()
    test_resume_after_network_outage()
    test_exponential_backoff()
    test_storm_squeezes_routine_video_not_metadata()
    test_aging_prevents_starvation()
    test_seven_day_simulation_invariants()
    print("\nALL 9 TESTS PASSED")


if __name__ == "__main__":
    main()
