from __future__ import annotations

from typing import List

from .config import GuardianConfig
from .models import WalletContext, TxProposal, EvaluationResult


class GuardianEngine:
    """
    Core risk evaluation engine for DGB Wallet Guardian.

    v0.1 is intentionally simple and transparent:
    - looks at balance vs amount
    - reacts to Sentinel status (NORMAL/ELEVATED/HIGH/CRITICAL)
    - returns SAFE / WARNING / BLOCK with reasons
    """

    def __init__(self, config: GuardianConfig) -> None:
        self._config = config

    def evaluate(self, ctx: WalletContext, tx: TxProposal) -> EvaluationResult:
        reasons: List[str] = []
        score = 0.0

        # 1) Baseline: Sentinel / ADN risk state
        sentinel = ctx.sentinel_status.upper().strip()

        if sentinel == "CRITICAL":
            score = max(score, 0.95)
            reasons.append("CHAIN_RISK_CRITICAL")
        elif sentinel == "HIGH":
            score = max(score, 0.75)
            reasons.append("CHAIN_RISK_HIGH")
        elif sentinel == "ELEVATED":
            score = max(score, 0.4)
            reasons.append("CHAIN_RISK_ELEVATED")

        # 2) Amount vs balance heuristics
        if ctx.balance > 0:
            ratio = tx.amount / ctx.balance

            if ratio > self._config.large_send_warning_ratio:
                score = max(score, 0.8)
                reasons.append("AMOUNT_NEAR_FULL_BALANCE")

            elif ratio > self._config.max_normal_send_ratio:
                score = max(score, 0.5)
                reasons.append("LARGE_RELATIVE_SEND")

        # 3) First-time recipient heuristic
        if ctx.known_addresses and tx.to_address not in ctx.known_addresses:
            score = max(score, 0.5)
            reasons.append("NEW_RECIPIENT_ADDRESS")

        # 4) Map score → status
        if score >= 0.9:
            status = "BLOCK"
        elif score >= 0.5:
            status = "WARNING"
        else:
            status = "SAFE"

        return EvaluationResult(status=status, score=score, reasons=reasons)
