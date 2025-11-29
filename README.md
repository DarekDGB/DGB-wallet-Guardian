# 🛡 DigiByte Wallet Guardian v2

Status: **v2 reference implementation – experimental**  
Layer: **4 — Wallet Behaviour & Withdrawal Protection**

---

## 1. Project Intent

DigiByte Wallet Guardian v2 (**DWG v2**) is **not** a wallet, key manager, or signing engine.  
It never holds private keys, never signs transactions, and does not modify DigiByte consensus.

Instead, it is a **behavioural firewall** that sits *next to* wallet infrastructure and node software.  
Its job is to monitor **withdrawal patterns** and apply **defensive policies** such as:

- per-transaction limits  
- rolling 24h limits  
- cooldowns between withdrawals  
- emergency freeze under elevated risk  
- escalation signals to higher-level security / monitoring layers

In the full DigiByte 5-layer shield, Wallet Guardian v2 is **Layer 4**, connected to:

- **Layer 3 – ADN v2 (Autonomous Defense Node):** provides node / network risk state  
- **Adaptive Core (future):** receives behaviour fingerprints & events for long-term learning

---

## 2. What Wallet Guardian v2 *is not*

To avoid confusion:

- ❌ does **not** generate or store keys  
- ❌ does **not** sign or broadcast transactions  
- ❌ does **not** change DigiByte’s consensus rules or cryptography  
- ❌ does **not** offer financial, custodial, or regulatory guarantees

It is a **policy + decision engine** focused purely on *behaviour*:

> “Given this risk level and this withdrawal history, should this withdrawal be  
> ALLOWed, DELAYed, FREEZE the wallet, or REJECTed?”

---

## 3. Core Capabilities

At a high level DWG v2 can:

1. **Track withdrawal history**
2. **Apply configurable policies**
3. **Ingest external risk signals**
4. **Emit structured decisions**
5. **Export events to Adaptive Core**

(Full explanations remain same as previous version.)

---

## 4. Architecture Overview

```
src/dgb_wallet_guardian/
    __init__.py
    adaptive_bridge.py
    client.py
    config.py
    decisions.py
    guardian_engine.py
    models.py
    policies.py
```

(Section retained as in previous version.)

---

## 5. Tests

Tests live under:

```
tests/
    test_decisions.py
    test_imports.py
    test_models.py
    test_policies.py
    test_smoke.py
```

Additional end‑to‑end tests will be added for full shield bundle validation.

---

## 6. Virtual Attack / Simulation Scenarios

Simulation / analysis of behaviour is documented in:

```
docs/reports/guardian_wallet_attack_scenario_1.md
```

Scenario **GW-SIM-001** demonstrates full LOW → MEDIUM → HIGH risk behaviour.

---

## 7. Intended Testnet Usage

When DigiByte testnet evaluation begins, DWG v2 can run in:

- fully sandboxed mode  
- real testnet wallet event mode  
- linked mode with Sentinel, DQSN, ADN, and Adaptive Core  

It adds **behavioural guard rails** without touching protocol rules.

---

## 8. Security & Safety Notes

- DWG v2 is experimental.  
- Only run in testnet / sandbox until fully reviewed.  
- Does not replace key security or multi‑sig.  
- All limits must be tuned for the environment.

---

## 9. Roadmap

1. More simulation scenarios  
2. Integration tests with ADN v2  
3. Export to Adaptive Core v1  
4. Inclusion in the **DigiByte Shield Testnet Bundle**  

---

## 📄 License

This project is released under the **MIT License**.

```
MIT License

Copyright (c) 2025 DarekDGB

Permission is hereby granted, free of charge, to any person obtaining a copy...
(standard MIT text)
```

---

## 👤 Author

**Created by:**  
🛡 **DarekDGB** — DigiByte Community Builder & Quantum Shield Architect  

All code, architecture, documentation and simulations authored with the intention  
to strengthen DigiByte for the coming decade and beyond.

