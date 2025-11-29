# DGB Wallet Guardian v2

DGB Wallet Guardian v2 is the wallet-side security & monitoring layer in
the **5‑Layer DigiByte Security Stack**.\
It *does not modify DigiByte protocol or cryptography*---it simply
evaluates wallet behaviour and transaction context to help users avoid
high‑risk actions.

It can **ALLOW, WARN, DELAY, BLOCK, or REQUIRE EXTRA AUTHENTICATION**
based on policy rules.

This system protects DigiByte users from: - wallet‑draining patterns\
- phishing or new‑address anomalies\
- unusual transaction behaviour\
- high‑risk external signals (Sentinel AI v2 / DQSN / ADN v2)\
- device‑level irregularities

------------------------------------------------------------------------

# 🔐 Place in the 5‑Layer DigiByte Security Stack

1.  **Sentinel AI v2** -- observes blockchain & mempool behaviour\
2.  **DQSN** -- aggregates global anomaly signals\
3.  **ADN v2** -- node-side behavioural monitoring\
4.  **🛡️ DGB Wallet Guardian v2** -- *local wallet behavioural
    analysis*\
5.  **DGB Quantum Wallet Guard** -- device + wallet + network fusion
    layer

Wallet Guardian v2 is where **local transaction‑level checks** happen
before signing.

------------------------------------------------------------------------

# ✨ Features

-   Rule‑based risk engine\
-   Full transaction evaluation\
-   Score → RiskLevel mapping\
-   Explained reasons for each triggered rule\
-   Optional Sentinel / DQSN / ADN signal integration\
-   Lightweight, auditable Python architecture\
-   GitHub Actions CI tests

------------------------------------------------------------------------

# 📦 Directory Structure

    src/dgb_wallet_guardian/
    │
    ├── models.py           # WalletState, DeviceState, TxContext, Risk models
    ├── decisions.py        # GuardianDecision + GuardianResult enums
    ├── policies.py         # Policy rules + evaluation helpers
    ├── guardian_engine.py  # Core evaluation engine
    ├── config.py           # Thresholds & tuning parameters
    └── client.py           # Optional helper for external wallet apps

------------------------------------------------------------------------

# 🚀 Quick Usage Example

``` python
from dgb_wallet_guardian.models import WalletState, TxContext
from dgb_wallet_guardian.guardian_engine import GuardianEngine
from dgb_wallet_guardian.decisions import GuardianDecision
from datetime import datetime

engine = GuardianEngine()

wallet = WalletState(
    balance=5000.0,
    daily_sent_amount=120.0
)

tx = TxContext(
    amount=2000.0,
    destination_address="dgb1qnewaddress123",
    created_at=datetime.utcnow()
)

decision = engine.evaluate(wallet, tx)

print("Decision:", decision.decision)
print("Reason:", decision.reason)
print("Cooldown:", decision.cooldown_seconds)
```

------------------------------------------------------------------------

# ⚙️ Configuration

Thresholds inside **config.py**:

-   `FULL_BALANCE_RATIO`\
-   `LARGE_TX_MULTIPLIER`\
-   `DAILY_LIMIT_MULTIPLIER`\
-   `COOLDOWN_SECONDS`\
-   `REQUIRE_2FA_THRESHOLD`

Wallet applications may override these via custom policy sets.

------------------------------------------------------------------------

# 🧪 Tests

Tests run automatically on GitHub Actions.\
Local run:

    pytest

------------------------------------------------------------------------

# 📜 License

MIT License --- free to use, modify, and distribute.

------------------------------------------------------------------------

# 👤 Author

Created and maintained by **Darek (@Darek_DGB)**\
Open‑source for DigiByte and future generations.
