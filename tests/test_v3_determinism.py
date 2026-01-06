from dgb_wallet_guardian.v3 import GuardianWalletV3


def test_v3_determinism_same_input_same_output():
    v3 = GuardianWalletV3()
    req = {
        "contract_version": 3,
        "component": "guardian_wallet",
        "request_id": "det",
        "wallet_ctx": {"balance": 100.0, "typical_amount": 5.0},
        "tx_ctx": {"to_address": "DGB_TEST", "amount": 10.0, "fee": 0.1},
        "extra_signals": {"trusted_device": True},
    }
    r1 = v3.evaluate(req)
    r2 = v3.evaluate(req)
    assert r1 == r2
    assert r1["meta"]["latency_ms"] == 0
