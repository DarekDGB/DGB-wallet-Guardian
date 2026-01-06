from dgb_wallet_guardian.v3 import GuardianWalletV3


def test_v3_unknown_top_level_key_fails_closed():
    v3 = GuardianWalletV3()
    req = {
        "contract_version": 3,
        "component": "guardian_wallet",
        "request_id": "unknown-key",
        "wallet_ctx": {},
        "tx_ctx": {},
        "extra_signals": {},
        "unexpected": "nope",
    }
    resp = v3.evaluate(req)
    assert resp["outcome"] == "deny"
    assert resp["meta"]["fail_closed"] is True
