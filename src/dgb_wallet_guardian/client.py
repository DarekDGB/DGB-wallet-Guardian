from __future__ import annotations

from typing import Any, Dict

from .config import GuardianConfig, load_config
from .guardian_engine import GuardianEngine
from .models import WalletContext, TxProposal, EvaluationResult


class WalletGuardian:
    """
    High-level convenience wrapper for DGB Wallet Guardian.

    Example usage:

        guardian = WalletGuardian()
        result = guardian.evaluate_transaction(
            wallet_ctx={"balance": 100.0},
            tx={"to_address": "...", "amount": 10.0, "fee": 0.001},
        )
    """

    def __init__(self, config: GuardianConfig | None = None) -> None:
        if config is None:
            config = load_config()
        self._config = config
        self._engine = GuardianEngine(config=config)

    def evaluate_transaction(
        self,
        wallet_ctx: Dict[str, Any],
        tx: Dict[str, Any],
    ) -> EvaluationResult:
        """
        Evaluate a transaction proposal.

        `wallet_ctx` and `tx` are plain dicts so different wallets
        (mobile, desktop, hardware) can easily map their own structures.
        """
        ctx_obj = WalletContext(
            balance=float(wallet_ctx.get("balance", 0.0)),
            known_addresses=list(wallet_ctx.get("known_addresses", [])),
            device_id=wallet_ctx.get("device_id"),
            region=wallet_ctx.get("region"),
            sentinel_status=str(wallet_ctx.get("sentinel_status", "NORMAL")),
            extra=dict(wallet_ctx.get("extra", {})),
        )

        tx_obj = TxProposal(
            to_address=str(tx.get("to_address")),
            amount=float(tx.get("amount", 0.0)),
            fee=float(tx.get("fee", 0.0)),
            metadata=dict(tx.get("metadata", {})),
        )

        return self._engine.evaluate(ctx_obj, tx_obj)
