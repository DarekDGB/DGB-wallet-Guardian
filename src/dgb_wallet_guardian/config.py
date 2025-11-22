from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GuardianConfig:
    """
    Configuration object for DGB Wallet Guardian.

    Values here are **reference defaults**. In production, node operators
    and wallet devs can tune these based on real-world data.
    """

    # Balance-related thresholds
    full_wipe_ratio: float = 0.9          # ≥ 90% of balance
    large_tx_multiplier: float = 5.0      # ≥ 5x typical_amount treated as unusual

    # Behaviour rate-limiting
    max_sends_per_window: int = 5         # max sends in window
    send_window_seconds: int = 600        # 10 minutes

    # Fee anomaly thresholds
    fee_multiplier_high: float = 3.0      # ≥ 3x typical_fee is suspicious

    # Destination risk thresholds (0.0–1.0)
    high_risk_destination: float = 0.8

    # Score → RiskLevel mapping
    threshold_elevated: float = 1.0
    threshold_high: float = 2.0
    threshold_critical: float = 3.0
