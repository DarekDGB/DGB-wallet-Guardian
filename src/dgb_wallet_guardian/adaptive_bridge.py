from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Stable, v3-facing layer identifier (used by GuardianEngine + integration tests)
GW_LAYER_NAME = "guardian_wallet"


@dataclass
class AdaptiveEvent:
    """
    Standardized adaptive event emitted by Guardian Wallet.

    Compatible with:
      - Sentinel AI / DQSN / ADN signal pipelines
      - DigiByte Quantum Adaptive Core (sink-provided)

    NOTE:
      Guardian Wallet does NOT depend on Adaptive Core.
      The caller provides a sink callable if they want events.
    """

    event_id: str
    layer: str
    action: str
    severity: float
    fingerprint: str
    created_at: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_wallet_adaptive_event(
    *,
    event_id: str,
    action: str,
    severity: float,
    fingerprint: str,
    user_id: Optional[str] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
) -> AdaptiveEvent:
    meta: Dict[str, Any] = {}
    if extra_meta:
        meta.update(extra_meta)

    # Clamp severity deterministically to [0.0, 1.0]
    sev = max(0.0, min(1.0, float(severity)))

    return AdaptiveEvent(
        event_id=str(event_id),
        layer=GW_LAYER_NAME,
        action=str(action),
        severity=sev,
        fingerprint=str(fingerprint),
        created_at=datetime.now(timezone.utc).isoformat(),
        user_id=str(user_id) if user_id is not None else None,
        metadata=meta,
    )


def emit_adaptive_event(
    sink,
    *,
    event_id: str,
    action: str,
    severity: float,
    fingerprint: str,
    user_id: Optional[str] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
):
    """
    Guardian Wallet convenience wrapper to send an event into Adaptive Core
    (if a sink is provided).

    Contract rule:
      - If sink is None -> return None
      - If sink raises -> swallow (do not affect Guardian decision) and return None
      - Otherwise -> return the emitted event
    """
    if sink is None:
        return None

    event = build_wallet_adaptive_event(
        event_id=event_id,
        action=action,
        severity=severity,
        fingerprint=fingerprint,
        user_id=user_id,
        extra_meta=extra_meta,
    )

    try:
        sink(event)
    except Exception:
        # Integration must never affect Guardian outcomes; swallow sink errors.
        return None

    return event
