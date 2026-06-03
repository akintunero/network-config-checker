import json
from pathlib import Path

import pytest

from network_config_checker.cli import main
from network_config_checker.exit_codes import EXIT_SUCCESS, EXIT_VIOLATIONS

pytestmark = pytest.mark.integration


def test_cli_scan_compliant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, sample_config_path) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "network-config-checker",
            "scan",
            "-c",
            str(sample_config_path),
            "-p",
            "builtin/cisco_ios_baseline",
            "-o",
            str(tmp_path / "reports"),
            "--format",
            "json",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == EXIT_SUCCESS
    payload = json.loads((tmp_path / "reports" / "compliance_report.json").read_text(encoding="utf-8"))
    assert payload["metadata"]["contact"] == "akintunero101@gmail.com"


def test_cli_scan_noncompliant_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    noncompliant_config_path: Path,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "network-config-checker",
            "scan",
            "-c",
            str(noncompliant_config_path),
            "-p",
            "builtin/cisco_ios_baseline",
            "-o",
            str(tmp_path / "reports"),
            "--format",
            "json",
            "--fail-on",
            "high",
        ],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == EXIT_VIOLATIONS
