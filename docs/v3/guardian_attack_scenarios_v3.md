# Guardian Wallet v3 — Attack Scenarios & Fail‑Closed Analysis

**Status:** v3 (normative-aligned)  
**Scope:** Guardian Wallet (Layer: User Protection)  
**Audience:** Auditors, security reviewers, integrators

---

## Purpose

This document enumerates **explicit attack scenarios** against Guardian Wallet v3 and
documents the **fail‑closed behavior** enforced by the v3 contract and tests.

> **Rule:** If behavior is ambiguous, malformed, or unverifiable — **execution must not proceed**.

This document is **non‑normative**. The **normative source of truth** is `docs/v3/GUARDIAN_V3.md`.
If a conflict exists, **GUARDIAN_V3.md wins**.

---

## Threat Model Summary

Guardian Wallet v3 defends against:
- Malformed requests attempting to bypass checks
- Policy downgrades via partial data
- Replay and order‑based manipulation
- UI‑level coercion (confirmation fatigue)
- Maintainer / integrator misuse
- Time‑based nondeterminism
- Silent fallback behavior

It does **not**:
- Replace key custody or signing logic
- Override EQC / WSQK authority
- Perform network consensus or chain validation

---

## Attack Scenarios

### A1 — Malformed Request Injection

**Vector:**  
Attacker submits a request with missing or extra top‑level fields.

**Example:**
```json
{
  "contract_version": 3,
  "component": "guardian",
  "request_id": "x",
  "unexpected": true
}
```

**Defense:**
- Strict schema parsing
- Unknown keys → **ERROR**
- `fail_closed = true`

**Expected Outcome:**  
`decision = ERROR`  
`reason_code = GW_ERROR_UNKNOWN_TOP_LEVEL_KEY`

---

### A2 — Contract Version Downgrade

**Vector:**  
Caller submits `contract_version != 3`.

**Defense:**
- Hard version gate
- No backward compatibility inside v3 path

**Expected Outcome:**  
`decision = ERROR`  
`reason_code = GW_ERROR_SCHEMA_VERSION`

---

### A3 — Decision Bypass Attempt

**Vector:**  
Caller attempts to directly mark a transaction as `ALLOW`
without satisfying Guardian rules.

**Defense:**
- Guardian v3 does not accept external decisions
- Decisions are derived internally only

**Expected Outcome:**  
`decision = ERROR`  
`reason_code = GW_ERROR_INVALID_REQUEST`

---

### A4 — Confirmation Fatigue Abuse

**Vector:**  
Repeated `WARN`‑level actions intended to desensitize the user.

**Defense:**
- Escalation rules
- Cooldown enforcement
- Deterministic evaluation (no time drift)

**Expected Outcome:**  
Escalation → `BLOCK` or `REQUIRE_EXTRA_AUTH`

---

### A5 — Order‑Dependent Manipulation

**Vector:**  
Reordering inputs to influence outcome.

**Defense:**
- Canonical sorting before hashing
- Order‑independent aggregation

**Expected Outcome:**  
Same input set → **identical output**

---

### A6 — Replay Attack

**Vector:**  
Resubmitting a previously approved request.

**Defense:**
- Context hash includes request + policy fingerprint
- Upstream layers (EQC/WSQK) enforce nonce / scope

**Expected Outcome:**  
Replay detected upstream or escalated

---

### A7 — Oversized Payload (DoS Attempt)

**Vector:**  
Inflated metadata or evidence blob.

**Defense:**
- Strict byte caps
- Deterministic size checks

**Expected Outcome:**  
`decision = ERROR`  
`reason_code = GW_ERROR_OVERSIZE`

---

### A8 — Reason Code Pollution

**Vector:**  
Injecting unknown or malformed reason codes.

**Defense:**
- Reason codes validated against enum
- Unknown → fail‑closed

**Expected Outcome:**  
`decision = ERROR`  
`reason_code = GW_ERROR_INVALID_REASON_CODE`

---

### A9 — Silent Fallback Attempt

**Vector:**  
Triggering an exception hoping for default allow.

**Defense:**
- No silent fallback
- All exceptions map to explicit ERROR response

**Expected Outcome:**  
`decision = ERROR`  
`fail_closed = true`

---

### A10 — Maintainer Abuse

**Vector:**  
Maintainer attempts to weaken rules in code without tests.

**Defense:**
- CI requires deterministic + negative tests
- No merge without failing‑case coverage

**Expected Outcome:**  
Change rejected at CI

---

## Invariants (Non‑Negotiable)

- **Fail‑Closed Always**
- **No Silent Defaults**
- **Deterministic Output**
- **Explicit Reason Codes**
- **No Bypass Paths**
- **Tests > Docs**
- **Contract Before Features**

---

## Relationship to Other Layers

- **EQC:** Decides *whether* execution may proceed
- **Guardian Wallet:** Protects the *user*
- **WSQK:** Enforces scoped execution
- **ADN / Sentinel / DQSN:** Supply risk signals only

Guardian Wallet **cannot override** EQC or WSQK.

---

## Auditor Checklist

- [ ] Unknown keys rejected
- [ ] Invalid version rejected
- [ ] Oversize payload rejected
- [ ] Order independence proven
- [ ] Deterministic hashing
- [ ] No silent fallback
- [ ] Reason codes enumerated
- [ ] Tests cover all above

---

## Status

This document reflects **current Guardian Wallet v3 behavior**.
Any change to behavior **requires test changes first**.

