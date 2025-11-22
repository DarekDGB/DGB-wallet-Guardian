from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .config import GuardianConfig
from .models import (
    RiskLevel,
    WalletContext,
    TransactionContext,
    GuardianDecision,
)


@dataclass
class RuleMatch:
    """Internal helper – describes a single triggered rule."""
    rule_id: str
    description: str
    weight: float


class GuardianEngine:
    """
    Core rule engine for DGB Wallet Guardian.

    This is a **reference implementation**:
    - simple, auditable rules
    - no external dependencies
    - safe to run in test environments

    Future versions can extend this with ML models and Sentinel AI v2
    integration without breaking the public API.
    """

    def __init__(self, config: Optional[GuardianConfig] = None) -> None:
        self.config = config or GuardianConfig()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def evaluate_transaction(
        self,
        wallet_ctx: WalletContext,
        tx_ctx: TransactionContext,
        extra_signals: Optional[Dict[str, Any]] = None,
    ) -> GuardianDecision:
        """
        Evaluate a single outgoing transaction and return a GuardianDecision.

        `extra_signals` can contain:
        - device_fingerprint
        - sentinel_status (NORMAL/ELEVATED/HIGH/CRITICAL)
        - geo_ip / session info
        - any other wallet-side signals
        """
        extra_signals = extra_signals or {}

        rule_matches: List[RuleMatch] = []
        self._apply_balance_rules(wallet_ctx, tx_ctx, rule_matches)
        self._apply_destination_rules(wallet_ctx, tx_ctx, rule_matches)
        self._apply_behavior_rules(wallet_ctx, tx_ctx, rule_matches)
        self._apply_external_signals(extra_signals, rule_matches)

        score = sum(r.weight for r in rule_matches)
        level = self._map_score_to_level(score)

        actions = self._suggest_actions(level)

        return GuardianDecision(
            level=level,
            score=score,
            actions=actions,
            reasons=[f"{r.rule_id}: {r.description}" for r in rule_matches],
        )

    # ------------------------------------------------------------------ #
    # Rule groups
    # ------------------------------------------------------------------ #

    def _apply_balance_rules(
        self,
        wallet_ctx: WalletContext,
        tx_ctx: TransactionContext,
        matches: List[RuleMatch],
    ) -> None:
        balance = wallet_ctx.balance
        amount = tx_ctx.amount

        # Rule: full-balance wipe
        if balance > 0 and amount >= balance * self.config.full_wipe_ratio:
            matches.append(
                RuleMatch(
                    rule_id="BALANCE_FULL_WIPE",
                    description=(
                        f"Transaction spends {amount} out of {balance} DGB "
                        f"(≥ {self.config.full_wipe_ratio:.0%} of balance)"
                    ),
                    weight=2.5,
                )
            )

        # Rule: unusually large send vs typical_amount
        if (
            wallet_ctx.typical_amount is not None
            and amount >= wallet_ctx.typical_amount * self.config.large_tx_multiplier
        ):
            matches.append(
                RuleMatch(
                    rule_id="BALANCE_UNUSUAL_SIZE",
                    description=(
                        f"Amount {amount} DGB is much larger than typical "
                        f"{wallet_ctx.typical_amount} DGB"
                    ),
                    weight=1.5,
                )
            )

    def _apply_destination_rules(
        self,
        wallet_ctx: WalletContext,
        tx_ctx: TransactionContext,
        matches: List[RuleMatch],
    ) -> None:
        dest = tx_ctx.to_address

        # Rule: new destination never seen before
        if dest not in wallet_ctx.known_addresses:
            matches.append(
                RuleMatch(
                    rule_id="DEST_NEW_ADDRESS",
                    description="Destination address not seen before in this wallet.",
                    weight=1.0,
                )
            )

        # Rule: address flagged as risky by external systems
        if tx_ctx.destination_risk_score is not None:
            if tx_ctx.destination_risk_score >= self.config.high_risk_destination:
                matches.append(
                    RuleMatch(
                        rule_id="DEST_HIGH_RISK",
                        description=(
                            f"Destination risk score {tx_ctx.destination_risk_score} "
                            f"is above high-risk threshold."
                        ),
                        weight=2.0,
                    )
                )

    def _apply_behavior_rules(
        self,
        wallet_ctx: WalletContext,
        tx_ctx: TransactionContext,
        matches: List[RuleMatch],
    ) -> None:
        # Rule: too many sends in a short period
        if (
            wallet_ctx.recent_send_count >= self.config.max_sends_per_window
            and wallet_ctx.recent_window_seconds <= self.config.send_window_seconds
        ):
            matches.append(
                RuleMatch(
                    rule_id="BEHAV_RATE_SPIKE",
                    description=(
                        f"{wallet_ctx.recent_send_count} sends in "
                        f"{wallet_ctx.recent_window_seconds}s window."
                    ),
                    weight=1.5,
                )
            )

        # Rule: fee looks manipulated (too high)
        if tx_ctx.fee is not None and wallet_ctx.typical_fee is not None:
            if tx_ctx.fee >= wallet_ctx.typical_fee * self.config.fee_multiplier_high:
                matches.append(
                    RuleMatch(
                        rule_id="FEE_UNUSUALLY_HIGH",
                        description=(
                            f"Fee {tx_ctx.fee} is much higher than typical "
                            f"{wallet_ctx.typical_fee}"
                        ),
                        weight=1.0,
                    )
                )

    def _apply_external_signals(
        self,
        extra_signals: Dict[str, Any],
        matches: List[RuleMatch],
    ) -> None:
        sentinel_status = extra_signals.get("sentinel_status")
        if sentinel_status in {"HIGH", "CRITICAL"}:
            matches.append(
                RuleMatch(
                    rule_id="SENTINEL_ALERT",
                    description=f"Sentinel AI v2 status is {sentinel_status}.",
                    weight=2.5 if sentinel_status == "CRITICAL" else 1.5,
                )
            )

        # Placeholder: device / session anomalies
        if extra_signals.get("device_mismatch"):
            matches.append(
                RuleMatch(
                    rule_id="DEVICE_MISMATCH",
                    description="Current device fingerprint differs from baseline.",
                    weight=1.5,
                )
            )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _map_score_to_level(self, score: float) -> RiskLevel:
        if score >= self.config.threshold_critical:
            return RiskLevel.CRITICAL
        if score >= self.config.threshold_high:
            return RiskLevel.HIGH
        if score >= self.config.threshold_elevated:
            return RiskLevel.ELEVATED
        return RiskLevel.NORMAL

    def _suggest_actions(self, level: RiskLevel) -> List[str]:
        if level is RiskLevel.NORMAL:
            return ["ALLOW"]
        if level is RiskLevel.ELEVATED:
            return ["WARN_USER", "SHOW_DETAILS"]
        if level is RiskLevel.HIGH:
            return ["REQUIRE_EXTRA_CONFIRMATION", "WARN_USER", "LOG_EVENT"]
        # CRITICAL
        return [
            "BLOCK_SIGNING",
            "LOCK_WALLET_TEMPORARILY",
            "NOTIFY_USER",
            "NOTIFY_ADN",
        ]
