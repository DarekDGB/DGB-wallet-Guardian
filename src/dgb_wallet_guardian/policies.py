from dataclasses import dataclass
from enum import Enum


class PolicyRule(str, Enum):
    LARGE_TX = "large_tx"
    FULL_BALANCE = "full_balance_tx"
    DAILY_LIMIT = "daily_limit"
    DESTINATION_RISK = "destination_risk"
    DEVICE_UNTRUSTED = "device_untrusted"


@dataclass
class GuardianPolicy:
    # Ratio of balance allowed in a single TX (0.5 = 50%)
    max_tx_ratio: float = 0.5

    # Max amount allowed per 24h window
    max_daily_amount: float = 50_000.0

    # How big a destination risk score triggers warnings
    threshold_extra_auth: float = 10_000.0

    # Whether sending full balance requires special handling
    block_full_balance_tx: bool = True
