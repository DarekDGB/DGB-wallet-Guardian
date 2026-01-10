from __future__ import annotations

from dgb_wallet_guardian.adaptive_bridge import (
    AdaptiveEvent,
    GW_LAYER_NAME,
    build_wallet_adaptive_event,
    emit_adaptive_event,
)


def test_build_wallet_adaptive_event_clamps_severity_and_sets_layer_and_meta():
    e = build_wallet_adaptive_event(
        event_id="e1",
        action="tx_blocked",
        severity=1.5,  # should clamp to 1.0
        fingerprint="fp",
        user_id="u1",
        extra_meta={"k": "v"},
    )

    assert isinstance(e, AdaptiveEvent)
    assert e.event_id == "e1"
    assert e.layer == GW_LAYER_NAME
    assert e.action == "tx_blocked"
    assert e.severity == 1.0
    assert e.fingerprint == "fp"

    # user_id is a first-class field (not in metadata)
    assert e.user_id == "u1"

    # extra_meta stays in metadata
    assert e.metadata["k"] == "v"

    # created_at is an ISO8601 string (UTC)
    assert isinstance(e.created_at, str)
    assert e.created_at  # non-empty


def test_build_wallet_adaptive_event_clamps_low_and_casts_float():
    e = build_wallet_adaptive_event(
        event_id="e2",
        action="warn",
        severity="-0.25",  # should cast and clamp to 0.0
        fingerprint="fp2",
    )
    assert e.severity == 0.0
    assert e.user_id is None
    assert e.metadata == {}


def test_adaptive_event_to_dict_serializes_created_at_string():
    e = build_wallet_adaptive_event(
        event_id="e3",
        action="info",
        severity=0.2,
        fingerprint="fp3",
        extra_meta={"a": 1},
    )
    d = e.to_dict()
    assert d["event_id"] == "e3"
    assert d["layer"] == GW_LAYER_NAME

    # created_at remains exactly the string stored on the object
    assert d["created_at"] == e.created_at
    assert d["metadata"]["a"] == 1


def test_emit_adaptive_event_returns_none_when_no_sink():
    out = emit_adaptive_event(
        None,
        event_id="e4",
        action="noop",
        severity=0.5,
        fingerprint="fp4",
    )
    assert out is None


def test_emit_adaptive_event_calls_sink_and_returns_event():
    seen: list[AdaptiveEvent] = []

    def sink(ev: AdaptiveEvent) -> None:
        seen.append(ev)

    out = emit_adaptive_event(
        sink,
        event_id="e5",
        action="sent",
        severity=0.7,
        fingerprint="fp5",
        user_id="u5",
        extra_meta={"x": "y"},
    )

    assert isinstance(out, AdaptiveEvent)
    assert len(seen) == 1
    assert seen[0] is out

    assert out.user_id == "u5"
    assert out.metadata["x"] == "y"


def test_emit_adaptive_event_swallows_sink_exception():
    def sink(_ev: AdaptiveEvent) -> None:
        raise RuntimeError("boom")

    out = emit_adaptive_event(
        sink,
        event_id="e6",
        action="sent",
        severity=0.4,
        fingerprint="fp6",
    )

    # Sink failure must be swallowed and must not leak exceptions.
    assert out is None
