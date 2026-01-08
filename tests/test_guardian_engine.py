from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dgb_wallet_guardian.guardian_engine import GuardianEngine
from dgb_wallet_guardian.models import RiskLevel


@dataclass
class W:
    # WalletContext minimal stub (runtime: only attributes used by GuardianEngine matter)
    balance: float
    typical_amount: Optional[float]
    known_addresses: set[str]
    recent_send_count: int
    recent_window_seconds: int
    typical_fee: Optional[float]
    wallet_id: str = "w1"


@dataclass
class T:
    # TransactionContext minimal stub
    amount: float
    to_address: str
    fee: Optional[float] = None
    destination_risk_score: Optional[float] = None
    tx_id: str = "tx1"


def test_engine_initial_state_getters():
    eng = GuardianEngine()
    assert eng.get_last_decision() is None
    assert list(eng.get_last_matches()) == []


def test_normal_tx_no_matches_and_no_adaptive_event():
    eng = GuardianEngine()
    called: List[Any] = []

    def sink(ev: Any) -> None:
        called.append(ev)

    wallet = W(
        balance=1000.0,
        typical_amount=10.0,
        known_addresses={"DGB_KNOWN"},
        recent_send_count=0,
        recent_window_seconds=10,
        typical_fee=0.1,
        wallet_id="wallet_norm",
    )
    tx = T(
        amount=1.0,
        to_address="DGB_KNOWN",
        fee=0.1,
        destination_risk_score=None,
        tx_id="tx_norm",
    )

    decision = eng.evaluate_transaction(
        wallet_ctx=wallet, tx_ctx=tx, extra_signals={"adaptive_sink": sink}
    )

    assert decision.level is RiskLevel.NORMAL
    assert decision.actions == ["ALLOW"]
    assert decision.reasons == []
    assert decision.score == 0.0

    # Adaptive hook must NOT fire for NORMAL
    assert called == []

    # State stored
    assert eng.get_last_decision() == decision
    assert list(eng.get_last_matches()) == []


def test_rules_trigger_and_actions_escalate():
    eng = GuardianEngine()

    # Force multiple rules to trigger:
    # - Full wipe (2.5)
    # - Unusual size vs typical (1.5)
    # - New destination (1.0)
    # - High-risk destination (2.0)
    # - Rate spike (1.5)
    # - Unusually high fee (1.0)
    wallet = W(
        balance=100.0,
        typical_amount=1.0,
        known_addresses=set(),  # new dest triggers
        recent_send_count=eng.config.max_sends_per_window,
        recent_window_seconds=eng.config.send_window_seconds,
        typical_fee=1.0,
        wallet_id="wallet_risky",
    )
    tx = T(
        amount=100.0,  # full wipe trigger
        to_address="DGB_NEW",
        fee=eng.config.fee_multiplier_high * wallet.typical_fee,  # fee trigger
        destination_risk_score=eng.config.high_risk_destination,  # high-risk trigger
        tx_id="tx_risky",
    )

    decision = eng.evaluate_transaction(wallet, tx, extra_signals={"sentinel_status": "HIGH"})

    # Must not be NORMAL
    assert decision.level in {RiskLevel.ELEVATED, RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert decision.score > 0.0
    assert len(decision.reasons) >= 4

    # Actions must correspond to level
    if decision.level is RiskLevel.ELEVATED:
        assert "WARN_USER" in decision.actions
    elif decision.level is RiskLevel.HIGH:
        assert "REQUIRE_EXTRA_CONFIRMATION" in decision.actions
        assert "LOG_EVENT" in decision.actions
    else:
        assert "BLOCK_SIGNING" in decision.actions
        assert "NOTIFY_ADN" in decision.actions

    # State stored
    assert eng.get_last_decision() == decision
    assert len(list(eng.get_last_matches())) == len(decision.reasons)


def test_external_signals_device_mismatch_and_sentinel_critical_weight():
    eng = GuardianEngine()
    wallet = W(
        balance=1000.0,
        typical_amount=None,
        known_addresses={"A"},
        recent_send_count=0,
        recent_window_seconds=9999,
        typical_fee=None,
        wallet_id="wallet_sig",
    )
    tx = T(amount=1.0, to_address="A", tx_id="tx_sig")

    decision = eng.evaluate_transaction(
        wallet, tx, extra_signals={"sentinel_status": "CRITICAL", "device_mismatch": True}
    )

    # Both rules should fire => non-NORMAL
    assert decision.level is not RiskLevel.NORMAL
    assert any("SENTINEL_ALERT" in r for r in decision.reasons)
    assert any("DEVICE_MISMATCH" in r for r in decision.reasons)


def test_adaptive_sink_emits_event_only_when_not_normal_and_severity_band_matches_level():
    eng = GuardianEngine()
    seen: List[Any] = []

    def sink(ev: Any) -> None:
        seen.append(ev)

    # Force ELEVATED with one moderate rule (new destination = 1.0)
    # To avoid guessing thresholds, we compute current thresholds and ensure we cross elevated.
    wallet = W(
        balance=1000.0,
        typical_amount=None,
        known_addresses={"KNOWN"},
        recent_send_count=0,
        recent_window_seconds=9999,
        typical_fee=None,
        wallet_id="wallet_emit",
    )
    tx = T(amount=1.0, to_address="NEW_ADDR", tx_id="tx_emit")

    decision = eng.evaluate_transaction(
        wallet,
        tx,
        extra_signals={
            "adaptive_sink": sink,
            "wallet_fingerprint": "fp_wallet",
            "user_id": "user123",
        },
    )

    assert decision.level is not RiskLevel.NORMAL
    assert len(seen) == 1

    ev = seen[0]
    # event is an AdaptiveEvent-like object; check fields defensively
    assert getattr(ev, "layer") == "guardian_wallet"
    assert getattr(ev, "anomaly_type") == "wallet_risk_decision"
    assert getattr(ev, "event_id") == "tx_emit"
    assert getattr(ev, "fingerprint") == "fp_wallet"
    assert getattr(ev, "user_id") == "user123"

    # severity mapping bands
    sev = float(getattr(ev, "severity"))
    if decision.level is RiskLevel.ELEVATED:
        assert sev == 0.45
    elif decision.level is RiskLevel.HIGH:
        assert sev == 0.7
    else:
        assert sev == 0.9

    meta: Dict[str, Any] = getattr(ev, "metadata")
    assert meta["destination"] == "NEW_ADDR"
    assert meta["amount"] == 1.0
    assert meta["score"] == decision.score
    assert "actions" in meta
