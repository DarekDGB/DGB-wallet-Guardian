# Guardian Wallet v3 — Attack Scenarios & Fail‑Closed Analysis

**Status:** v3 authoritative • Regression‑locked  
**Component:** `guardian_wallet`  
**Contract Version:** `3`

This document enumerates realistic abuse/attack scenarios against the **Guardian Wallet v3
contract gate** and the **fail‑closed defenses** implemented in code + tests.

Guardian Wallet v3 is an **evaluator**. It never signs, broadcasts, or mutates state.
Its job is to return a deterministic envelope that upstream systems can treat as:
- `outcome="allow"` → proceed
- `outcome="escalate"` → require extra confirmation / user action
- `outcome="deny"` → block

---

## Contract safety rules (baseline)

Guardian Wallet v3 is hardened by these contract invariants:

- **Strict top‑level schema** (`GWv3Request.from_dict` rejects unknown keys)
- **Strict nested allowlists** for `wallet_ctx`, `tx_ctx`, `extra_signals`
- **Oversize cap** (128KB deterministic encoded size)
- **Bad number rejection** (NaN/±Inf fail closed)
- **Deterministic context_hash** (canonical JSON + SHA‑256)
- **Fail‑closed envelope**: any contract error returns `outcome="deny"` and stable `reason_codes`

---

## Scenario group A — Schema / parsing abuse

### A1 — Unknown top‑level key injection

**Vector:**  
Caller adds an unexpected top‑level field to probe parser weaknesses, smuggle authority, or bypass validation.

**Example:**
```json
{
  "contract_version": 3,
  "component": "guardian_wallet",
  "request_id": "r1",
  "wallet_ctx": {},
  "tx_ctx": {},
  "extra_signals": {},
  "unexpected": true
}
```

**Defense (fail‑closed):**
- Unknown top‑level keys are rejected by `GWv3Request.from_dict`.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_UNKNOWN_TOP_LEVEL_KEY"`
- `meta.fail_closed = true`

---

### A2 — Wrong contract version

**Vector:**  
Caller submits any `contract_version` other than `3` (downgrade / confusion attack).

**Defense (fail‑closed):**
- `contract_version` is checked before any behavioral evaluation.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_SCHEMA_VERSION"`

---

### A3 — Wrong component name

**Vector:**  
Caller sends a request for another component (or a typo) to try to reuse the gate as a permissive validator.

**Defense (fail‑closed):**
- `component` must equal `guardian_wallet`.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_INVALID_REQUEST"`

---

## Scenario group B — Nested key smuggling

### B1 — wallet_ctx key smuggling

**Vector:**  
Caller attempts to add hidden parameters inside `wallet_ctx` that could affect evaluation or later layers.

**Defense (fail‑closed):**
- `wallet_ctx` is strict‑allowlisted.
- Any unknown wallet key fails closed.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_UNKNOWN_WALLET_KEY"`

---

### B2 — tx_ctx key smuggling

**Vector:**  
Caller injects unknown fields into `tx_ctx` (e.g., internal flags, bypass bits).

**Defense (fail‑closed):**
- `tx_ctx` is strict‑allowlisted.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_UNKNOWN_TX_KEY"`

---

### B3 — extra_signals key smuggling

**Vector:**  
Caller injects unknown `extra_signals` fields to fake trust or introduce unvalidated structures.

**Defense (fail‑closed):**
- `extra_signals` is strict‑allowlisted.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_UNKNOWN_SIGNAL_KEY"`

---

## Scenario group C — Resource exhaustion / payload abuse

### C1 — Oversize payload (128KB+)

**Vector:**  
Caller submits a huge payload (e.g., massive memo/session blob) to waste resources or trigger inconsistent parsing.

**Defense (fail‑closed):**
- Deterministic encoded size check blocks requests over `MAX_PAYLOAD_BYTES`.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_OVERSIZE"`

---

## Scenario group D — Numeric edge cases

### D1 — NaN / Infinity injection

**Vector:**  
Caller sends NaN/±Inf in numeric fields to break comparisons or create non‑deterministic serialization/hashing.

**Defense (fail‑closed):**
- Known numeric fields are validated to be finite.

**Expected result:**
- `outcome="deny"`
- `reason_codes[0] = "GW_ERROR_BAD_NUMBER"`

---

## Scenario group E — Decision tampering / authority injection

### E1 — Caller attempts to force allow

**Vector:**  
Caller tries to include fields like `decision="ALLOW"` or similar to bypass evaluation.

**Defense (fail‑closed):**
- Such fields are not part of the contract and are rejected as unknown keys.
- GuardianWalletV3 computes outcome from the engine risk level only.

**Expected result:**
- If injected at top-level → `GW_ERROR_UNKNOWN_TOP_LEVEL_KEY`
- Otherwise (if nested) → corresponding unknown nested key error

---

### E2 — “Partial data downgrade” (missing signals)

**Vector:**  
Caller omits signals hoping the system will “assume safe”.

**Defense (safe behavior):**
- Missing optional dicts default to `{}` (deterministic).
- v3 contract remains strict on unknown keys, but does not require optional context.

**Expected result:**
- Deterministic evaluation using available context.
- If risk remains low → `outcome="allow"` with `GW_OK_HEALTHY_ALLOW`
- Otherwise → `outcome="escalate"` / `outcome="deny"` based on the engine

---

## Scenario group F — Adapter safety (v3 → v2 engine)

### F1 — v3‑allowed keys not present in v2 dataclasses

**Vector:**  
v3 allows `wallet_age_days` / `tx_count_24h`, but older v2 dataclasses may not accept them.
This can become a crash vector if not handled.

**Defense (hard):**
- The v2 adapter layer filters `wallet_ctx` / `tx_ctx` to the **actual** model fields before construction.

**Expected result:**
- No TypeError / crash.
- Deterministic evaluation continues.
- Contract envelope remains stable.

---

## Scenario group G — Determinism / replay safety

### G1 — Same input, different output attempt

**Vector:**  
Attacker tries to exploit time/randomness/global state to produce different verdicts for identical inputs.

**Defense (hard):**
- Contract envelope uses deterministic fields only.
- `latency_ms` is pinned to 0 in reference implementation.
- `context_hash` is computed from canonical JSON.

**Expected result:**
- Identical input → identical `context_hash`, `outcome`, `reason_codes`.

---

## What “fail‑closed” means here

Guardian Wallet v3 **never** returns “ERROR” as a mode that upstream systems might accidentally treat as permissive.
Instead, any contract failure is represented as:

- `outcome="deny"`
- `meta.fail_closed=true`
- `reason_codes` explaining the exact failure

Upstream systems must treat `deny` as **BLOCK**.

---

## Regression‑locked truth

This document is only authoritative if it matches:
- the implementation (`src/dgb_wallet_guardian/v3.py`, `contracts/v3_types.py`)
- the regression tests (`tests/test_v3_contract_gate.py`, etc.)

Any behavior change must:
1) change tests first
2) then change code
3) then update docs
