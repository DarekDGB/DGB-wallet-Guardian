from dgb_wallet_guardian.guardian_core import GuardianCore

def test_smoke():
    g = GuardianCore()
    assert g is not None
