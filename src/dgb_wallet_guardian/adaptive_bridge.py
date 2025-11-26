from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional

GW_LAYER_NAME = "GuardianWallet_v2"


@dataclass
class AdaptiveEvent:
    """
    Standardized adaptive event emitted by Guardian Wallet v2.

    Compatible with:
      - Sentinel AI v2
      - DQSN
      - ADN v2
      - DigiByte Quantum Adaptive Core
    """

    event_id: str
    layer: str
    action: str
    severity: float
    fingerprint: str
    created_at: datetime
    feedback: str = "unknown"
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d


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
    if user_id:
        meta["user_id"] = user_id
    if extra_meta:
        meta.update(extra_meta)

    return AdaptiveEvent(
        event_id=event_id,
        layer=GW_LAYER_NAME,
        action=action,
        severity=max(0.0, min(1.0, float(severity))),
        fingerprint=fingerprint,
        created_at=datetime.utcnow(),
        metadata=meta,
    )


def emit_adaptive_event(
    sink, *,
    event_id: str,
    action: str,
    severity: float,
    fingerprint: str,
    user_id: Optional[str] = None,
    extra_meta: Optional[Dict[str, Any]] = None,
):
    """
    Guardian Wallet convenience wrapper to send an event into
    the Quantum Adaptive Core (if sink is provided).
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

    sink(event)
    return event
