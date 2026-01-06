from dgb_wallet_guardian.v3 import GuardianWalletV3


def test_v3_invalid_version_fails_closed():
    v3 = GuardianWalletV3()
    req = {
        "contract_version": 2,
        "component": "guardian_wallet",
        "request_id": "bad-version",
        "wallet_ctx": {},
        "tx_ctx": {},
        "extra_signals": {},
    }
    resp = v3.evaluate(req)
    assert resp["outcome"] == "deny"
    assert resp["meta"]["fail_closed"] is True
