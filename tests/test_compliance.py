from pathlib import Path

import pytest

from network_config_checker.compliance import ComplianceEngine, violations_at_or_above
from network_config_checker.models import Severity
from network_config_checker.parser import ConfigParser
from network_config_checker.policy import load_policies, resolve_policy_path
from network_config_checker.scanner import scan_file, should_fail

pytestmark = pytest.mark.unit


def test_compliant_sample(sample_config_path, builtin_policy: str) -> None:
    pack = load_policies(resolve_policy_path(builtin_policy))
    result = scan_file(sample_config_path, pack)
    assert result.summary["total_violations"] == 0


def test_noncompliant_sample_detects_critical(noncompliant_config_path: Path) -> None:
    pack = load_policies(resolve_policy_path("builtin/cisco_ios_baseline"))
    result = scan_file(noncompliant_config_path, pack)
    assert result.summary["total_violations"] > 0
    critical = violations_at_or_above(result.violations, Severity.CRITICAL)
    assert any(v.rule_id == "NCC-FORBID_TELNET_TRANSPORT" for v in critical)


def test_should_fail_on_high(
    builtin_policy: str,
    noncompliant_config_path: Path,
) -> None:
    pack = load_policies(resolve_policy_path(builtin_policy))
    bad = scan_file(noncompliant_config_path, pack)
    assert should_fail([bad], Severity.HIGH)


def test_interface_rule_application() -> None:
    pack = load_policies(resolve_policy_path("builtin/cisco_ios_baseline"))
    parser = ConfigParser("interface GigabitEthernet0/1\n ip address 10.0.0.1 255.255.255.0\n!")
    engine = ComplianceEngine(parser, pack)
    result = engine.check(config_path="inline")
    rule_result = result.detailed_results["require_interface_description"]
    assert rule_result.status == "non_compliant"
