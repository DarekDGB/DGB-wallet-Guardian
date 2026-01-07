# 🛡️ DGB Wallet Guardian

[![CI](https://github.com/DarekDGB/DGB-Wallet-Guardian/actions/workflows/test.yml/badge.svg)](https://github.com/DarekDGB/DGB-Wallet-Guardian/actions)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Shield Contract](https://img.shields.io/badge/Shield%20Contract-v3-critical)](#shield-contract-v3)
[![Security](https://img.shields.io/badge/security-fail--closed-red)](#security-model)

---

## Overview

**DGB Wallet Guardian** is the **user‑side protection layer** of the DigiByte Quantum Shield.
It enforces **policy‑driven, fail‑closed, deterministic protections** at the wallet boundary.

Guardian Wallet is **not a UI feature** and **not a heuristic monitor**.
It is a **contract‑enforced security engine** designed to prevent irreversible user‑side losses
even when upstream layers behave unexpectedly.

---

## Shield Contract v3

Wallet Guardian **v3** is the only authoritative version.

**Guarantees**
- Deterministic decisions
- Explicit reason codes
- Fail‑closed by default
- Glass‑box contract surface
- CI‑enforced invariants

📌 v3 docs → `docs/v3/`  
📦 Legacy v2 docs → `docs/v2/` (archived, non‑authoritative)

---

## Architecture Role

Guardian Wallet sits **between user intent and execution**.

It evaluates:
- Shield context hashes
- Wallet‑local policies
- User risk posture

It outputs:
- `ALLOW` · `WARN` · `DELAY` · `BLOCK`
- Stable `reason_codes`
- Deterministic contract envelopes

Guardian **never signs transactions** and **never mutates state**.

---

## Security Model

Hard rules:

- ❌ No silent allow
- ❌ No heuristic guessing
- ❌ No mutable outcomes
- ❌ No hidden authority
- ✅ Deterministic inputs → deterministic outputs
- ✅ Explicit failure reasons
- ✅ Fail‑closed on ambiguity

If Guardian cannot prove safety, **it blocks**.

---

## Documentation Index

### v3 (Current)
- `docs/v3/GUARDIAN_V3.md`
- `docs/v3/technical-spec-guardian-v3.md`
- `docs/v3/guardian_attack_scenarios_v3.md`

### v2 (Archived)
- `docs/v2/`

---

## Development Discipline

All changes must:
- Preserve determinism
- Preserve fail‑closed behavior
- Include tests
- Update docs **after** tests pass

---

## License

MIT

---

**Author:** DarekDGB  
**Part of:** DigiByte Quantum Shield
