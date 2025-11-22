from __future__ import annotations

from typing import Any, Dict, Optional

from .config import GuardianConfig
from .guardian_engine import GuardianEngine
from .models import WalletContext, TransactionContext, GuardianDecision, RiskLevel


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

        `wallet_ctx` example:
            {"balance": 100.0, "typical_amount": 5.0, ...}

        `tx_ctx` example:
            {"to_address": "...", "amount": 95.0, "fee": 0.1}
        """
        wallet = WalletContext(**wallet_ctx)
        tx = TransactionContext(**tx_ctx)

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
