from __future__ import annotations

from dataclasses import fields
from typing import Any, Dict, Optional

from .config import GuardianConfig
from .guardian_engine import GuardianEngine
from .models import WalletContext, TransactionContext, GuardianDecision, RiskLevel


def _filter_to_model_fields(model_type: type, raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter an input dict down to only the keyword fields accepted by a dataclass model.

    This prevents adapter crashes when newer contract layers (v3) include
    additional allowed context keys not used by the v2 model.
    """
    allowed = {f.name for f in fields(model_type)}
    return {k: v for k, v in raw.items() if k in allowed}


class WalletGuardian:
    """
    High-level convenience wrapper for DGB Wallet Guardian.

    This is what wallet developers will usually integrate with.

    Example usage:

        guardian = WalletGuardian()
        decision = guardian.evaluate_transaction(
            wallet_ctx={"balance": 100.0},
            tx_ctx={
                "to_address": "...",
                "amount": 95.0,
            },
            extra_signals={"sentinel_status": "ELEVATED"},
        )
    """

    def __init__(self, config: Optional[GuardianConfig] = None) -> None:
        self.config = config or GuardianConfig()
        self.engine = GuardianEngine(config=self.config)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def evaluate_transaction(
        self,
        wallet_ctx: Dict[str, Any],
        tx_ctx: Dict[str, Any],
        extra_signals: Optional[Dict[str, Any]] = None,
    ) -> GuardianDecision:
        """
        Convert raw dictionaries into typed models and run the engine.

        NOTE:
        - v3 contract may provide additional allowed keys (e.g., wallet_age_days, tx_count_24h).
        - This adapter filters inputs to the actual WalletContext / TransactionContext fields
          to preserve backward compatibility and avoid TypeError crashes.
        """
        safe_wallet_ctx = _filter_to_model_fields(WalletContext, wallet_ctx)
        safe_tx_ctx = _filter_to_model_fields(TransactionContext, tx_ctx)

        wallet = WalletContext(**safe_wallet_ctx)
        tx = TransactionContext(**safe_tx_ctx)

        return self.engine.evaluate_transaction(
            wallet_ctx=wallet,
            tx_ctx=tx,
            extra_signals=extra_signals or {},
        )

    def is_safe_to_send(
        self,
        wallet_ctx: Dict[str, Any],
        tx_ctx: Dict[str, Any],
        extra_signals: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Convenience helper: return True if transaction should be allowed
        without blocking (NORMAL or ELEVATED).
        """
        decision = self.evaluate_transaction(wallet_ctx, tx_ctx, extra_signals)
        return decision.level in {RiskLevel.NORMAL, RiskLevel.ELEVATED}
