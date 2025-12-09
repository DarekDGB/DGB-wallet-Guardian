# 🛡️ Guardian Wallet  
### *User Protection Layer • Human-Centric Defence • Secure Transaction UX*  
**Architecture by @DarekDGB — MIT Licensed**

---

## 🚀 Purpose

**Guardian Wallet** is the *user-facing protection layer* of the DigiByte Quantum Shield.

Where:

- **DQSN v2** reads network health  
- **Sentinel AI v2** detects anomalies  
- **ADN v2** produces defensive playbooks  
- **QWG** evaluates and guards transactions  

**Guardian Wallet is where all that intelligence meets the user.**

Its job is to:

- explain threats clearly  
- ask for confirmations  
- warn when danger is detected  
- block behaviour that is unsafe  
- ensure humans understand risks before sending funds  
- act as the *communication layer* between the wallet and the shield  

Guardian Wallet protects users from mistakes, malware, deception, and network attacks  
by translating complex shield signals into *simple, actionable guidance*.

---

# 🧱 Position in the DigiByte Quantum Shield (5-Layer Model)

```
 ┌───────────────────────────────────────────────┐
 │              Guardian Wallet                  │
 │   User UX • Confirmations • Warnings          │
 └───────────────────────────────────────────────┘
                     ▲
                     │  (structured prompts)
 ┌───────────────────────────────────────────────┐
 │       QWG — Quantum Wallet Guard              │
 │ Runtime Guard • PQC Verify • Behaviour Check  │
 └───────────────────────────────────────────────┘
                     ▲
                     │  (playbook outputs)
 ┌───────────────────────────────────────────────┐
 │                ADN v2                         │
 │ Tactical Defence • Attack Response Routing    │
 └───────────────────────────────────────────────┘
                     ▲
                     │  (threat signals)
 ┌───────────────────────────────────────────────┐
 │             Sentinel AI v2                    │
 │ Telemetry & Anomaly Detection                 │
 └───────────────────────────────────────────────┘
                     ▲
                     │  (network metrics)
 ┌───────────────────────────────────────────────┐
 │                  DQSN v2                      │
 │ Entropy • Node Health • Chain Condition       │
 └───────────────────────────────────────────────┘
```

Guardians sits at the **final human checkpoint**.  
Its purpose: **“Make sure the user acts safely.”**

---

# 🎯 Core Mission

### ✓ Turn technical defence signals into human understanding  
Guardian converts:

- QWG behavioural alerts  
- ADN threat warnings  
- Sentinel anomaly signals  

into human-friendly language users can act on.

### ✓ Protect against human mistakes  
Such as:

- sending to the wrong address  
- unusually large transfers  
- high-fee scams  
- risky timing (e.g., during reorg danger)  

### ✓ Block dangerous actions  
When appropriate, Guardian Wallet may:

- refuse the send  
- ask for multi-step confirmation  
- recommend waiting  
- warn of suspected malware behaviour  

### ✓ Provide transparent, educational feedback  
Users learn *why* an action is unsafe — enabling smarter future decisions.

### ✓ Serve as the UX face of the entire Quantum Shield  
Guardian is the interface between:

- Shield intelligence  
- Wallet user  
- Wallet transaction flow  

---

# 🧠 Threat Model (User-Centric)

Guardian Wallet protects against:

## **1. Human Errors**
- wrong address  
- incorrect amounts  
- dangerous copy/paste behaviour  
- sending funds during known network risks  

## **2. Social Engineering**
- fake “urgent payment” scams  
- misleading DMs or phishing messages  
- manipulated addresses  

## **3. Malware Behaviour**
- replaced addresses via clipboard hijacking  
- bot-like automated withdrawals  
- suspicious rapid-fire sends  

## **4. Network-Level Risks (via ADN/QWG)**
- reorg warnings  
- eclipse or partition detection  
- mempool flooding  
- dangerous block timing  

## **5. Quantum Threat Evolution**
- hybrid signature transitions  
- PQC-driven warning logic  

Guardian Wallet ensures the *user decides safely*.

---

# 🧩 Internal Architecture (Reference)

```
guardian_wallet/
│
├── prompts/
│     ├── warning_prompts.py     # human-friendly alert messages
│     ├── confirmation_flows.py  # multi-step verification flows
│     └── risk_categories.py     # mapping threat → explanation
│
├── integration/
│     ├── qwg_bridge.py          # receives behavioural signals
│     ├── adn_bridge.py          # receives defence playbook outputs
│     └── shield_context.py      # unified threat context
│
├── flows/
│     ├── send_flow.py           # pre-send safety checks
│     ├── receive_flow.py        # safe incoming logic
│     ├── fee_validation.py      # prevents exploitative fees
│     └── safety_modes.py        # safe mode / heightened alert mode
│
├── ui_logic/
│     ├── decision_engine.py     # decides which prompt to show
│     └── hold_and_review.py     # temporarily blocks suspicious actions
│
└── utils/
      ├── types.py
      ├── config.py
      └── logging.py
```

This structure is intentionally simple:  
Guardian Wallet is **logic + prompts**, not UI visuals.

---

# 📡 Data Flow Overview

```
         [Shield Intelligence]
              ▲        ▲
              │        │
      [ADN Signals]  [QWG Alerts]
              │        │
              └───► [Guardian Context]
                       │
                       ▼
         ┌──────────────────────────┐
         │  Decision Engine         │
         └──────────────────────────┘
                       │
   ┌───────────────┬───────────────┬───────────────┐
   ▼               ▼               ▼               ▼
[Warn User]   [Block Send]   [Require Review]   [Proceed Safely]
```

Guardian Wallet **never acts silently** — the user is always involved.

---

# 🛡️ Security & UX Design Principles

1. **Explain everything**  
   A warning must *always* include a reason.

2. **User empowerment**  
   Users make better decisions when they understand risks.

3. **Fail-safe behaviour**  
   If unsure → ask, block, or delay.

4. **Never confuse the user**  
   Messages must be simple, direct, human.

5. **Never duplicate QWG logic**  
   Guardian interprets, it does not detect.

6. **Non-technical clarity**  
   “Block reorg risk detected” → becomes  
   **“The DigiByte network is unstable right now. It is safer to wait.”**

---

# ⚙️ Code Status

Guardian Wallet provides:

- complete defence flow scaffolding  
- prompt templates  
- shield integration points  
- safe send-flow design  
- deterministic rule logic  
- stable CI tests  

It is **architecture-complete**, ready for expansion by DigiByte community contributors.

---

# 🧪 Tests

Tests validate:

- prompt logic  
- decision engine behaviour  
- correct mapping of QWG & ADN signals  
- safe-mode transitions  
- no regressions in safety flows  

---

# 🤝 Contribution Policy

See `CONTRIBUTING.md`.

Summary:

- improvements welcome  
- clarity upgrades encouraged  
- no removal of safety  
- no consensus or detection logic  
- no UI visuals here — only logic  

---

# 📜 License

MIT License  
© 2025 **DarekDGB**

This architecture is free to use with mandatory attribution.
