import pytest

from network_config_checker.policy import PolicyValidationError, explain_rule, load_policies, resolve_policy_path

pytestmark = pytest.mark.unit


def test_load_builtin_policy(builtin_policy: str) -> None:
    pack = load_policies(resolve_policy_path(builtin_policy))
    assert pack.name == "cisco_ios_baseline"
    assert "require_hostname" in pack.rules


def test_explain_rule(builtin_policy: str) -> None:
    pack = load_policies(resolve_policy_path(builtin_policy))
    text = explain_rule(pack, "NCC-REQUIRE_HOSTNAME")
    assert "NCC-REQUIRE_HOSTNAME" in text
    assert "global" in text


def test_invalid_severity_rejected() -> None:
    from network_config_checker.policy import _parse_rule

    with pytest.raises(PolicyValidationError):
        _parse_rule(
            "bad",
            {
                "description": "Invalid severity example",
                "severity": "urgent",
                "scope": "global",
                "conditions": ["hostname"],
            },
        )
