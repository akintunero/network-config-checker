from pathlib import Path

import pytest

from network_config_checker.policy import load_policies, resolve_policy_path
from network_config_checker.scanner import scan_paths, should_fail
from network_config_checker.models import Severity

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIGS_DIR = REPO_ROOT / "configs"
BUILTIN_DIR = REPO_ROOT / "policies" / "builtin"


def test_configs_directory_passes_all_builtin_packs() -> None:
    pack = load_policies(BUILTIN_DIR)
    assert "require_hostname" in pack.rules
    assert "require_enable_secret" in pack.rules
    results = scan_paths(CONFIGS_DIR, pack)
    assert len(results) == 2
    assert all(r.summary["total_violations"] == 0 for r in results)
    assert not should_fail(results, Severity.HIGH)


def test_management_hardening_pack_loads() -> None:
    pack = load_policies(resolve_policy_path("builtin/cisco_ios_management_hardening"))
    assert pack.name == "cisco_ios_management_hardening"
    assert pack.rules["forbid_snmp_public_community"].severity.value == "critical"


def test_inventory_scan() -> None:
    pack = load_policies(BUILTIN_DIR)
    inventory = REPO_ROOT / "configs" / "inventory.csv"
    results = scan_paths(REPO_ROOT, pack, inventory_path=inventory)
    hostnames = {r.config_path for r in results}
    assert "edge-sw-01" in hostnames
    assert "core-sw-01" in hostnames
