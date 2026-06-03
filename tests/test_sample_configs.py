from pathlib import Path

import pytest

from network_config_checker.policy import load_policies
from network_config_checker.scanner import scan_file, should_fail
from network_config_checker.models import Severity

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_production_config_passes_all_builtin_packs() -> None:
    pack = load_policies(REPO_ROOT / "policies" / "builtin")
    result = scan_file(REPO_ROOT / "configs" / "production" / "edge-sw-01.cfg", pack)
    assert result.summary["total_violations"] == 0
    assert not should_fail([result], Severity.HIGH)
