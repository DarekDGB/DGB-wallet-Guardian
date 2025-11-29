# Guardian Wallet v2 — Simulation Script (Scenario GW-SIM-001)

Save the following code as **`simulate_guardian_wallet_scenario_1.py`** in the root of your  
**DGB-wallet-guardian-v2** repository (next to `README.md`, `src/`, `tests/`, etc.).

You can run it with:

```bash
python simulate_guardian_wallet_scenario_1.py
```

> 🔐 This script is **testnet/simulation-only**.  
> It does **not** connect to real wallets or keys.  
> It just feeds a sequence of synthetic withdrawals into the Guardian engine.

```python
# Standard library
import datetime
from dataclasses import dataclass
from typing import List

# Import the guardian engine and any needed config helpers.
# If your actual module / class names differ slightly, adjust these imports.
try:
    from dgb_wallet_guardian.guardian_engine import GuardianEngine
    from dgb_wallet_guardian.config import get_default_config  # or similar helper
except ImportError as e:
    raise SystemExit(
        "Import error: please verify the import paths for GuardianEngine and config.\n"
        "Adjust the imports at the top of simulate_guardian_wallet_scenario_1.py "
        "to match your code structure.\n"
        f"Original error: {e}"
    )


@dataclass
class SimulatedWithdrawal:
    step: int
    minutes_from_start: int
    wallet_id: str
    amount_dgb: float
    adn_risk: str  # "LOW", "MEDIUM", "HIGH"


def build_scenario() -> List[SimulatedWithdrawal]:
    # Scenario GW-SIM-001: LOW -> MEDIUM -> HIGH risk with limits & cooldowns.
    # Matches the behaviour described in docs/guardian_wallet_attack_scenario_1.md
    # for a single wallet that becomes increasingly suspicious.
    return [
        SimulatedWithdrawal(step=1, minutes_from_start=0, wallet_id="WALLET_X", amount_dgb=3000, adn_risk="LOW"),     # allow
        SimulatedWithdrawal(step=2, minutes_from_start=3, wallet_id="WALLET_X", amount_dgb=4000, adn_risk="LOW"),    # cooldown breach -> DELAY
        SimulatedWithdrawal(step=3, minutes_from_start=8, wallet_id="WALLET_X", amount_dgb=5000, adn_risk="MEDIUM"), # daily limit + MEDIUM -> FREEZE/HARD_DELAY
        SimulatedWithdrawal(step=4, minutes_from_start=15, wallet_id="WALLET_X", amount_dgb=2500, adn_risk="HIGH"),  # frozen + HIGH -> REJECT
        SimulatedWithdrawal(step=5, minutes_from_start=25, wallet_id="WALLET_X", amount_dgb=1000, adn_risk="HIGH"),  # persistent attempts -> REJECT
    ]


def main() -> None:
    # Initialise GuardianEngine with default configuration.
    config = get_default_config()
    guardian = GuardianEngine(config=config)

    start_time = datetime.datetime.utcnow()
    scenario = build_scenario()

    # Optional: open a simple log file under ./logs/
    log_path = "logs/guardian_wallet_scenario_1.log"
    try:
        log_file = open(log_path, "w", encoding="utf-8")
    except FileNotFoundError:
        # If logs/ doesn't exist yet, create it.
        import os

        os.makedirs("logs", exist_ok=True)
        log_file = open(log_path, "w", encoding="utf-8")

    header = (
        "Step | t(min) | Wallet       | Amount (DGB) | ADN Risk | Decision | Reason\n"
        + "-" * 72
        + "\n"
    )
    print(header.strip())
    log_file.write(header)

    for tx in scenario:
        timestamp = start_time + datetime.timedelta(minutes=tx.minutes_from_start)

        # NOTE: Adjust this call if your GuardianEngine API uses a different signature.
        decision = guardian.evaluate_withdrawal(
            wallet_id=tx.wallet_id,
            amount_dgb=tx.amount_dgb,
            timestamp=timestamp,
            adn_risk=tx.adn_risk,
        )

        # Expecting decision object with .decision_type and .reason (adapt if different).
        decision_type = getattr(decision, "decision_type", str(decision))
        reason = getattr(decision, "reason", "n/a")

        line = f"{tx.step:>4} | {tx.minutes_from_start:>5}   | {tx.wallet_id:<11} | {tx.amount_dgb:>11.0f} | {tx.adn_risk:<7} | {decision_type:<8} | {reason}\n"
        print(line, end="")
        log_file.write(line)

    log_file.close()
    print(f"\nSimulation finished. Log written to {log_path}")


if __name__ == "__main__":
    main()
```
