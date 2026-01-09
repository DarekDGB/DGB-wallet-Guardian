import pytest

from dgb_wallet_guardian.contracts.v3_types import GWv3Request


def test_from_dict_rejects_non_dict():
    with pytest.raises(ValueError) as e:
        GWv3Request.from_dict("nope")  # type: ignore[arg-type]
    assert str(e.value) == "GW_ERROR_INVALID_REQUEST"


def test_from_dict_rejects_unknown_top_level_key():
    raw = {
        "contract_version": 3,
        "component": "sentinel",  # value doesn't matter for this test
        "request_id": "r1",
        "wallet_ctx": {},
        "tx_ctx": {},
        "extra_signals": {},
        "evil": True,
    }
    with pytest.raises(ValueError) as e:
        GWv3Request.from_dict(raw)
    assert str(e.value) == "GW_ERROR_UNKNOWN_TOP_LEVEL_KEY"


@pytest.mark.parametrize(
    "raw",
    [
        # missing required core fields -> invalid
        {"component": "guardian", "request_id": "r1"},
        {"contract_version": 3, "request_id": "r1"},
        {"contract_version": 3, "component": "guardian"},
        # wrong types
        {"contract_version": "3", "component": "guardian", "request_id": "r1"},
        {"contract_version": 3, "component": 123, "request_id": "r1"},
        {"contract_version": 3, "component": "guardian", "request_id": 5},
        {"contract_version": 3, "component": "guardian", "request_id": "r1", "wallet_ctx": []},
        {"contract_version": 3, "component": "guardian", "request_id": "r1", "tx_ctx": []},
        {"contract_version": 3, "component": "guardian", "request_id": "r1", "extra_signals": []},
        # empty/whitespace-only strings
        {"contract_version": 3, "component": "", "request_id": "r1"},
        {"contract_version": 3, "component": "guardian", "request_id": ""},
        {"contract_version": 3, "component": "   ", "request_id": "r1"},
        {"contract_version": 3, "component": "guardian", "request_id": "   "},
    ],
)
def test_from_dict_invalid_requests_raise(raw):
    with pytest.raises(ValueError) as e:
        GWv3Request.from_dict(raw)
    assert str(e.value) == "GW_ERROR_INVALID_REQUEST"


def test_from_dict_defaults_optional_dicts_and_strips_strings():
    raw = {
        "contract_version": 3,
        "component": "  guardian_wallet  ",
        "request_id": "  r1  ",
        # omit wallet_ctx/tx_ctx/extra_signals: should default to {}
    }
    out = GWv3Request.from_dict(raw)

    assert out.contract_version == 3
    assert out.component == "guardian_wallet"
    assert out.request_id == "r1"
    assert out.wallet_ctx == {}
    assert out.tx_ctx == {}
    assert out.extra_signals == {}


def test_from_dict_preserves_dict_objects_as_given():
    wallet_ctx = {"balance": 1, "known_addresses": ["A"]}
    tx_ctx = {"amount": 0.5, "to_address": "B"}
    extra = {"sentinel_status": "HIGH"}

    raw = {
        "contract_version": 3,
        "component": "guardian_wallet",
        "request_id": "r2",
        "wallet_ctx": wallet_ctx,
        "tx_ctx": tx_ctx,
        "extra_signals": extra,
    }
    out = GWv3Request.from_dict(raw)

    assert out.wallet_ctx is wallet_ctx
    assert out.tx_ctx is tx_ctx
    assert out.extra_signals is extra
