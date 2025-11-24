from dgb_wallet_guardian.policies import GuardianPolicy


def test_policy_defaults():
    p = GuardianPolicy()
    assert p.block_full_balance_tx is True
    assert p.max_tx_ratio == 0.5
    assert p.max_daily_amount == 50_000.0
    assert p.threshold_extra_auth == 10_000.0
