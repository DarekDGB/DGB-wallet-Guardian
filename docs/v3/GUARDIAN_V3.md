# Guardian Wallet v3 — Shield Contract v3

**Status:** Active • Contract-Locked • CI-Enforced  
**Component:** `guardian_wallet`  
**Contract Version:** `3`

Guardian Wallet v3 is the **user-side protection gate** for DigiByte wallets.
It evaluates a wallet's outgoing intent (transaction context + wallet context + signals)
and returns a **deterministic, fail-closed verdict envelope**.

This module **does not sign, broadcast, or mutate state**. It only evaluates and reports.

---

## Core Guarantees

1. **Fail‑Closed Semantics**
   - Any malformed, incomplete, oversized, or invalid request returns `outcome="deny"`.
   - Errors are reported via stable `reason_codes`.

2. **Deterministic Output**
   - Identical valid inputs produce identical outputs, including `context_hash`.
   - No time, randomness, environment, or global state may influence results.

3. **Strict Contract Parsing**
   - Unknown **top-level** keys are rejected.
   - Unknown **nested** keys in `wallet_ctx`, `tx_ctx`, or `extra_signals` are rejected.

4. **Stable Reason Codes**
   - Error and outcome codes come from a single enum source.
   - Rule IDs extracted from v2 engine reasons are deterministic, de-duplicated, and sorted.

5. **No Hidden Authority**
   - Guardian Wallet cannot sign, mint, broadcast, or alter wallet state.
   - It only evaluates and returns a verdict envelope.

---

## Non‑Goals

Guardian Wallet v3 does **not**:

- Hold, derive, or access private keys
- Sign transactions
- Broadcast transactions
- Perform network I/O
- Modify wallet balances or state
- Replace runtime enforcement (EQC / WSQK / Orchestrator)

---

## Request Schema (v3)

All requests **must** be a JSON object with only these top-level keys:

| Field | Type | Required | Notes |
|---|---|---:|---|
| `contract_version` | int | ✅ | Must be `3` |
| `component` | string | ✅ | Must be `guardian_wallet` |
| `request_id` | string | ✅ | Caller-defined identifier |
| `wallet_ctx` | object | ⛔ default `{}` | Strict allowlist (see below) |
| `tx_ctx` | object | ⛔ default `{}` | Strict allowlist (see below) |
| `extra_signals` | object | ⛔ default `{}` | Strict allowlist (see below) |

### Nested allowlists (strict)

`wallet_ctx` allowed keys:
- `balance`
- `typical_amount`
- `wallet_age_days`
- `tx_count_24h`

`tx_ctx` allowed keys:
- `to_address`
- `amount`
- `fee`
- `memo`
- `asset_id`

`extra_signals` allowed keys:
- `device_fingerprint`
- `sentinel_status`
- `geo_ip`
- `session`
- `trusted_device`

**Any unknown key** at any level fails closed with `outcome="deny"`.

### Abuse caps

- Requests larger than **128KB** (deterministic encoded size) are rejected.

### Bad number rules

Numeric fields used by the gate must be **finite**:
- rejects `NaN`, `+Inf`, `-Inf`

---

## Response Envelope (v3)

Guardian Wallet returns the following response:

| Field | Description |
|---|---|
| `contract_version` | Always `3` |
| `component` | Always `guardian_wallet` |
| `request_id` | Echoed from request |
| `context_hash` | Deterministic SHA‑256 over the contract-defined context (see below) |
| `outcome` | `"allow"` \| `"escalate"` \| `"deny"` |
| `risk.level` | One of model levels (e.g. `NORMAL`, `ELEVATED`, `HIGH`, `CRITICAL`) |
| `risk.score` | Float score from the engine |
| `reason_codes` | Stable codes + extracted rule IDs (sorted / deduped) |
| `evidence.actions` | Engine suggested actions |
| `evidence.reasons` | Engine reasons (human-readable) |
| `meta.fail_closed` | Always `true` |
| `meta.latency_ms` | Deterministic `0` in reference implementation |

### Outcome mapping

- `RiskLevel.NORMAL` → `outcome="allow"`
- `RiskLevel.ELEVATED` → `outcome="escalate"`
- `RiskLevel.HIGH` / `RiskLevel.CRITICAL` → `outcome="deny"`

---

## Context Hash (Deterministic)

`context_hash` is computed using canonical JSON + SHA‑256.

### SUCCESS / ESCALATE / DENY (non-error path)

Hash input is the canonical JSON of:

```json
{
  "component": "guardian_wallet",
  "contract_version": 3,
  "request_id": "<string>",
  "wallet_ctx": { ... },
  "tx_ctx": { ... },
  "extra_signals": { ... },
  "outcome": "<allow|escalate|deny>",
  "risk_level": "<NORMAL|ELEVATED|HIGH|CRITICAL>",
  "reason_codes": ["<code>", "..."]
}
```

### ERROR (fail-closed path)

Hash input is the canonical JSON of:

```json
{
  "component": "guardian_wallet",
  "contract_version": 3,
  "request_id": "<string>",
  "reason_code": "<error_code>"
}
```

---

## Invariants (Audit IDs)

- **GW_V3_INV_001** — Unknown keys rejected (top-level and nested)
- **GW_V3_INV_002** — Deterministic output for identical input
- **GW_V3_INV_003** — Fail‑closed on schema violation / oversize / bad numbers
- **GW_V3_INV_004** — No time or randomness dependency
- **GW_V3_INV_005** — Reason codes stable and enum-backed
- **GW_V3_INV_006** — Order‑independent canonical hashing

Each invariant is enforced by regression tests in CI.

---

## Integration Rules

- Consumers MUST call the **v3 public entrypoint** (`GuardianWalletV3.evaluate`).
- Consumers MUST treat `outcome="deny"` as **BLOCK**.
- Consumers MUST NOT call internal engine methods directly.

---

## Status

Guardian Wallet v3 is **locked**.

Changes require:
- Contract discipline (semantic changes → bump version)
- Regression tests
- CI proof
