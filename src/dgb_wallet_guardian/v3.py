from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .client import WalletGuardian
from .models import RiskLevel
from .contracts.v3_hash import canonical_sha256
from .contracts.v3_reason_codes import ReasonCode
from .contracts.v3_types import GWv3Request


@dataclass(frozen=True)
class GuardianWalletV3:
    """
    Guardian Wallet v3 Contract Gate (Layer-4).

    Goals:
    - strict schema, deny unknown keys
    - fail-closed semantics
    - deterministic output + deterministic meta
    - stable reason_codes (no magic strings)
    - calls v2 engine for behavior (no authority expansion)
    """

    COMPONENT: str = "guardian_wallet"
    CONTRACT_VERSION: int = 3

    # Abuse caps
    MAX_PAYLOAD_BYTES: int = 128_000  # 128KB

    # Strict allowlists for nested dicts (glass-box)
    WALLET_KEYS = {"balance", "typical_amount", "wallet_age_days", "tx_count_24h"}
    TX_KEYS = {"to_address", "amount", "fee", "memo", "asset_id"}
    SIGNAL_KEYS = {"device_fingerprint", "sentinel_status", "geo_ip", "session", "trusted_device"}

    def evaluate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        latency_ms = 0  # deterministic contract envelope

        try:
            req = GWv3Request.from_dict(request)
        except ValueError as e:
            code = str(e) or ReasonCode.GW_ERROR_INVALID_REQUEST.value
            return self._error(request_id=self._safe_request_id(request), reason_code=code, latency_ms=latency_ms)
        except Exception:
            return self._error(request_id=self._safe_request_id(request), reason_code=ReasonCode.GW_ERROR_INVALID_REQUEST.value, latency_ms=latency_ms)

        if req.contract_version != self.CONTRACT_VERSION:
            return self._error(request_id=req.request_id, reason_code=ReasonCode.GW_ERROR_SCHEMA_VERSION.value, latency_ms=latency_ms)

        if req.component != self.COMPONENT:
            return self._error(request_id=req.request_id, reason_code=ReasonCode.GW_ERROR_INVALID_REQUEST.value, latency_ms=latency_ms)

        # Oversize protection (deterministic)
        if self._encoded_size_bytes(request) > self.MAX_PAYLOAD_BYTES:
            return self._error(request_id=req.request_id, reason_code=ReasonCode.GW_ERROR_OVERSIZE.value, latency_ms=latency_ms)

        # Strict nested key checks
        if set(req.wallet_ctx.keys()) - self.WALLET_KEYS:
            return self._error(request_id=req.request_id, reason_code=ReasonCode.GW_ERROR_UNKNOWN_WALLET_KEY.value, latency_ms=latency_ms)
        if set(req.tx_ctx.keys()) - self.TX_KEYS:
            return self._error(request_id=req.request_id, reason_code=ReasonCode.GW_ERROR_UNKNOWN_TX_KEY.value, latency_ms=latency_ms)
        if set(req.extra_signals.keys()) - self.SIGNAL_KEYS:
            return self._error(request_id=req.request_id, reason_code=ReasonCode.GW_ERROR_UNKNOWN_SIGNAL_KEY.value, latency_ms=latency_ms)

        # Bad number checks (NaN/Inf) on numeric fields we care about
        if not self._numbers_ok(req.wallet_ctx, req.tx_ctx):
            return self._error(request_id=req.request_id, reason_code=ReasonCode.GW_ERROR_BAD_NUMBER.value, latency_ms=latency_ms)

        # Run existing v2 engine via client wrapper (authoritative behavior)
        guardian = WalletGuardian()
        decision = guardian.evaluate_transaction(req.wallet_ctx, req.tx_ctx, req.extra_signals)

        outcome = self._map_outcome(decision.level)
        reason_codes = self._extract_reason_codes(decision.reasons, decision.level)

        # Deterministic context hash for orchestrator audit
        v3_context = {
            "component": self.COMPONENT,
            "contract_version": self.CONTRACT_VERSION,
            "request_id": req.request_id,
            "wallet_ctx": self._stable_wallet(req.wallet_ctx),
            "tx_ctx": self._stable_tx(req.tx_ctx),
            "extra_signals": self._stable_signals(req.extra_signals),
            "outcome": outcome,
            "risk_level": decision.level.value,
            "reason_codes": reason_codes,
        }
        context_hash = canonical_sha256(v3_context)

        return {
            "contract_version": self.CONTRACT_VERSION,
            "component": self.COMPONENT,
            "request_id": req.request_id,
            "context_hash": context_hash,
            "outcome": outcome,  # allow | deny | escalate
            "risk": {
                "level": decision.level.value,
                "score": float(decision.score),
            },
            "reason_codes": reason_codes,
            "evidence": {
                "actions": list(decision.actions),
                "reasons": list(decision.reasons),
            },
            "meta": {
                "latency_ms": latency_ms,
                "fail_closed": True,
            },
        }

    # ----------------------------
    # Deterministic helpers
    # ----------------------------

    @staticmethod
    def _safe_request_id(request: Any) -> str:
        if isinstance(request, dict):
            rid = request.get("request_id", "unknown")
            return str(rid) if rid is not None else "unknown"
        return "unknown"

    @staticmethod
    def _encoded_size_bytes(obj: Any) -> int:
        try:
            return len(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        except Exception:
            # If it can't be encoded deterministically, fail closed at parse stage
            return 10**9

    @staticmethod
    def _is_finite_number(x: Any) -> bool:
        if isinstance(x, bool):
            return True
        if isinstance(x, (int, float)):
            f = float(x)
            return math.isfinite(f)
        return True

    def _numbers_ok(self, wallet_ctx: Dict[str, Any], tx_ctx: Dict[str, Any]) -> bool:
        # Only validate known numeric fields; reject NaN/Inf
        numeric_fields = [
            wallet_ctx.get("balance"),
            wallet_ctx.get("typical_amount"),
            wallet_ctx.get("wallet_age_days"),
            wallet_ctx.get("tx_count_24h"),
            tx_ctx.get("amount"),
            tx_ctx.get("fee"),
        ]
        return all(self._is_finite_number(v) for v in numeric_fields if v is not None)

    @staticmethod
    def _stable_wallet(w: Dict[str, Any]) -> Dict[str, Any]:
        # Stable casting (avoid int/float drift)
        out: Dict[str, Any] = dict(w)
        if "balance" in out:
            out["balance"] = float(out["balance"])
        if "typical_amount" in out:
            out["typical_amount"] = float(out["typical_amount"])
        if "wallet_age_days" in out and out["wallet_age_days"] is not None:
            out["wallet_age_days"] = int(out["wallet_age_days"])
        if "tx_count_24h" in out and out["tx_count_24h"] is not None:
            out["tx_count_24h"] = int(out["tx_count_24h"])
        return out

    @staticmethod
    def _stable_tx(t: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = dict(t)
        if "amount" in out:
            out["amount"] = float(out["amount"])
        if "fee" in out and out["fee"] is not None:
            out["fee"] = float(out["fee"])
        # strings remain strings; optional keys remain present only if provided
        return out

    @staticmethod
    def _stable_signals(s: Dict[str, Any]) -> Dict[str, Any]:
        # Keep signals stable and JSON-serializable
        out: Dict[str, Any] = dict(s)
        if "trusted_device" in out:
            out["trusted_device"] = bool(out["trusted_device"])
        return out

    @staticmethod
    def _map_outcome(level: RiskLevel) -> str:
        if level == RiskLevel.NORMAL:
            return "allow"
        if level == RiskLevel.ELEVATED:
            return "escalate"
        # HIGH/CRITICAL are blocking
        return "deny"

    def _extract_reason_codes(self, reasons: List[str], level: RiskLevel) -> List[str]:
        # reasons are like: "RULE_ID: description"
        rule_ids: List[str] = []
        for r in reasons:
            if isinstance(r, str) and ":" in r:
                rid = r.split(":", 1)[0].strip()
                if rid:
                    rule_ids.append(rid)

        # Deterministic dedup + sorted
        rule_ids = sorted(set(rule_ids))

        # Outcome code always included (stable)
        if level == RiskLevel.NORMAL:
            base = [ReasonCode.GW_OK_HEALTHY_ALLOW.value]
        elif level == RiskLevel.ELEVATED:
            base = [ReasonCode.GW_ESCALATE_ELEVATED.value]
        else:
            base = [ReasonCode.GW_DENY_HIGH_OR_CRITICAL.value]

        return base + rule_ids

    def _error(self, request_id: str, reason_code: str, latency_ms: int) -> Dict[str, Any]:
        context_hash = canonical_sha256(
            {
                "component": self.COMPONENT,
                "contract_version": self.CONTRACT_VERSION,
                "request_id": str(request_id),
                "reason_code": reason_code,
            }
        )
        return {
            "contract_version": self.CONTRACT_VERSION,
            "component": self.COMPONENT,
            "request_id": str(request_id),
            "context_hash": context_hash,
            "outcome": "deny",
            "risk": {"level": "unknown", "score": 1.0},
            "reason_codes": [str(reason_code)],
            "evidence": {"details": {"error": str(reason_code)}},
            "meta": {"latency_ms": int(latency_ms), "fail_closed": True},
        }
