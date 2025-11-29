# 🛡 DigiByte Wallet Guardian v2 — Technical Specification  
### Layer‑4 Behavioural Withdrawal Firewall  
**Version:** 2.0  
**Author:** DarekDGB  
**Engineering:** Angel (AI Assistant)  

---

# 1. Purpose of This Document  
This technical specification describes **exactly how Wallet Guardian v2 works**,  
matching the real code structure in your repository:

```
src/dgb_wallet_guardian/
docs/
tests/
simulate_guardian_wallet_scenario_1.py
```

It is written for DigiByte Core developers, security researchers, and testnet operators.

---

# 2. High-Level Function  

Wallet Guardian v2 is a **policy-driven, risk-aware withdrawal decision engine**.

It takes in:

- wallet ID  
- withdrawal amount  
- timestamp  
- ADN risk level  

And outputs one of:

```
ALLOW
DELAY
FREEZE
REJECT
```

This engine **never touches private keys**, **never signs**, and **never broadcasts** transactions.

It is completely external and safe for testnet integration.

---

# 3. Data Flow Overview  

```
Wallet → Guardian Client → GuardianEngine
        ↓ policies.py
        ↓ decisions.py
        ↓ models.py
ADN risk feed → GuardianEngine
Adaptive Core ← adaptive_bridge
```

Sequence:

1. Wallet component sends withdrawal request to Guardian.  
2. GuardianEngine loads config values.  
3. GuardianEngine loads withdrawal history for the wallet.  
4. GuardianEngine evaluates policies.  
5. Risk state from **ADN v2** modifies the strictness.  
6. Decision is returned.  
7. High‑risk events go to Adaptive Core.

---

# 4. Code Structure (Accurate to Repository)

```
src/dgb_wallet_guardian/
│
├── __init__.py
├── adaptive_bridge.py
├── client.py
├── config.py
├── decisions.py
├── guardian_engine.py
├── models.py
└── policies.py
```

---

# 5. Module-by-Module Specification  

## 5.1 `models.py`
Defines core structured models:

- `WithdrawalEvent`
- `PolicyResult`
- `Decision`
- Historical buckets / time windows

Example fields:

```
wallet_id: str
amount_dgb: float
timestamp: datetime
```

---

## 5.2 `decisions.py`

Defines:

```
DecisionType:
    ALLOW
    DELAY
    FREEZE
    REJECT
```

A Decision object includes:

```
decision_type
reason
metadata (optional)
```

Purpose:  
Standardise decisions across all tests, simulations, and future integrations.

---

## 5.3 `policies.py`

Implements **behaviour rules**:

### • Amount-based policy  
Reject or freeze if amounts exceed thresholds.

### • Daily volume policy  
Tracks rolling 24h volume across multiple requests.

### • Cooldown policy  
Minimum minutes between withdrawals.

### • Escalation under MEDIUM/HIGH ADN risk  
Policies become stricter automatically.

Output structure:

```
PolicyResult:
    allowed: bool
    delay: bool
    freeze: bool
    reason: str
```

---

## 5.4 `config.py`

Provides configuration values:

```
MAX_WITHDRAWAL_PER_TX
MAX_WITHDRAWAL_24H
COOLDOWN_MINUTES
RULES_FOR_MEDIUM
RULES_FOR_HIGH
```

Developers can tune these for testnet.

---

## 5.5 `guardian_engine.py` (Core Brain)

Responsible for:

- loading history  
- evaluating all policies  
- combining results  
- applying risk‑based multipliers  
- generating final Decision object  
- exporting high-risk events to Adaptive Core  

Critical functions normally include:

```
evaluate_withdrawal(...)
load_wallet_history(...)
combine_policy_results(...)
export_to_adaptive(...)
```

### Decision Logic (Simplified):

```
If ADN risk == HIGH:
    freeze or reject suspicious withdrawals

If cooldown violated:
    DELAY

If daily volume exceeded:
    FREEZE

If wallet frozen and attempts continue:
    REJECT

Else:
    ALLOW
```

---

## 5.6 `client.py`

Thin wrapper for wallets:

- prepares WithdrawalEvent  
- passes it to GuardianEngine  
- receives decision  

Allows any wallet implementation to integrate Guardian instantly.

---

## 5.7 `adaptive_bridge.py`

Exports structured events:

```
WALLET_FROZEN
PERSISTENT_ATTEMPTS
ABNORMAL_PATTERN
```

These are consumed by the **Adaptive Core (immune system)** during learning.

---

# 6. Test Structure  

```
tests/
│
├── test_imports.py
├── test_decisions.py
├── test_models.py
├── test_policies.py
└── test_smoke.py
```

### Purpose of Each:

- **test_imports.py**  
  Ensures all modules import correctly.

- **test_decisions.py**  
  Validates Decision object behaviour.

- **test_models.py**  
  Validates the data structures.

- **test_policies.py**  
  Ensures each policy triggers correctly.

- **test_smoke.py**  
  Runs a minimal GuardianEngine instantiation.

---

# 7. Simulation Script  

Included in repo:

```
simulate_guardian_wallet_scenario_1.py
```

Runs the official GW‑SIM‑001 sequence:

```
ALLOW
DELAY
FREEZE
REJECT
```

Produces logs in:

```
logs/guardian_wallet_scenario_1.log
```

This allows developers to verify behaviour without real wallets.

---

# 8. Official Attack Scenario GW‑SIM‑001  

Documented in:

```
docs/guardian_wallet_attack_scenario_1.md
```

Simulates:

- multiple sequential withdrawals  
- cooldown breaches  
- 24h volume spike  
- rising ADN risk (LOW → MEDIUM → HIGH)  
- final freeze + reject sequence  

This is used during DigiByte testnet evaluation.

---

# 9. Integration With Other Layers  

Wallet Guardian v2 expects two external signals:

### 9.1 From ADN v2  
Real‑time risk levels:

```
LOW
MEDIUM
HIGH
CRITICAL
```

### 9.2 To Adaptive Core  
Exports behavioural fingerprints for immune system learning.

---

# 10. Security Guarantees  

Wallet Guardian v2 provides:

- deterministic decisions  
- transparent logic  
- no key exposure  
- no blockchain modification  
- safe testnet integration  
- immutable behaviour once parameters are set  

Guardian logic is **pure Python**, safe, sandboxed, and side‑effect limited.

---

# 11. License  

This specification and implementation are open-source under **MIT License**.

---

# 12. Author  

🛡 **DarekDGB**  
Creator of the DigiByte 5‑Layer Quantum Shield  
Visionary & Community Builder

