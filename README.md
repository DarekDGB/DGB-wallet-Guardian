# DGB-Wallet-Guardian – Layer-4 DigiByte Wallet Protection

**DGB-Wallet-Guardian** is the new **Layer-4 protection module** designed to sit on top of:

> **DQSN → Sentinel AI v2 → ADN → (NEW) Wallet Guardian**

Its purpose is simple:

### **Protect DigiByte users directly at the wallet level.**  
A final shield that watches for theft, quantum threats, phishing attempts, behavioural anomalies, and transaction manipulation.

---

## 🚀 Why Layer-4?

The DigiByte security stack is expanding:

1. **DQSN** – entropy, nonce, difficulty & chain-level anomaly sensing  
2. **Sentinel AI v2** – multi-signal threat detection, quantum anomaly prediction  
3. **ADN v1/v2** – automated network-level defense actions  
4. **Wallet Guardian (this repo)** – **user-level protection**

This turns DigiByte into the first blockchain ecosystem with a **4-layer self-healing security architecture**.

---

## 🔐 What Wallet Guardian Will Protect

### **1. Outgoing Transaction Protection**
- abnormal sending patterns  
- unusual amounts compared to wallet history  
- sudden full balance wipes  
- suspicious fee manipulation  
- AI-flagged “panic send” behaviour  
- destination wallet risk scoring (optional)

### **2. Quantum Threat Alerts**
- signing attempts from weak / legacy keys  
- preimage vulnerability warnings  
- Shor/Grover risk scoring from Sentinel AI v2  
- forced PQC mode activation via ADN

### **3. Device Behaviour Monitoring**
- mismatched device fingerprints  
- changes in OS, browser, session entropy  
- sudden automation-like behaviour  
- clipboard hijacking detection  
- malware-style transaction substitution patterns

### **4. Social Engineering / Phishing Detection**
- AI-driven message & link scoring  
- QR code anomaly detection  
- malformed address alerts  
- “look-alike address” similarity checks

### **5. Emergency Wallet Lockdown**
If high risk is detected:
- temporary signing freeze  
- 2FA / multi-step confirmation  
- delayed-sending mode  
- ADN “hardened wallet mode” activation  

---

## 🧠 How It Works With Sentinel AI v2

Wallet Guardian continuously streams minimal telemetry to Sentinel:

- signing entropy  
- behaviour patterns  
- device fingerprints  
- transaction intent  
- timestamp anomalies  

Sentinel AI v2 returns:  
**NORMAL → ELEVATED → HIGH → CRITICAL**

Wallet Guardian reacts instantly:

| Sentinel Status | Wallet Guardian Action |
|-----------------|------------------------|
| NORMAL | smooth operation |
| ELEVATED | extra warnings |
| HIGH | multi-step confirmation |
| CRITICAL | *lock wallet + block signing + notify ADN* |

---

## 📁 Repository Layout (initial)

```
DGB-wallet-Guardian/
├─ README.md
├─ LICENSE
└─ src/
   └─ dgb_wallet_guardian/
      ├─ __init__.py
      ├─ rules/
      ├─ behavioural_model/
      ├─ transaction_filters/
      ├─ device_fingerprint/
      ├─ guardian_engine.py
      └─ api.py
```

---

## 🛠️ Early Development Goal

The first milestone:

### **Guardian Engine v0.1**
- simple rules (balance wipe detection, address mismatch alerts)
- device fingerprint baseline
- behaviour scoring stub
- API endpoints for testing with Sentinel v2 + ADN

---

## 📜 License (MIT)

```
MIT License

Copyright (c) 2025 
Darek (@Darek_DGB)
```

---

## 🌟 Vision

DigiByte becomes the first chain where:

**The chain protects you.  
The AI protects you.  
The defense node protects you.  
And now — your wallet protects you.**

The 4-layer shield is how we take DigiByte safely into the quantum era.

