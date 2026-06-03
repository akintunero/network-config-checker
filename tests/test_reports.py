from pathlib import Path

import pytest

from network_config_checker.policy import load_policies, resolve_policy_path
from network_config_checker.reports import ReportWriter
from network_config_checker.scanner import scan_file

pytestmark = pytest.mark.unit


def test_report_writer_all_formats(tmp_path: Path, sample_config_path, builtin_policy: str) -> None:
    pack = load_policies(resolve_policy_path(builtin_policy))
    results = [scan_file(sample_config_path, pack)]
    writer = ReportWriter(results)
    outcomes = writer.write_all(tmp_path, ["txt", "json", "html", "csv", "sarif", "junit"])

    assert all(outcomes.values())
    for name in (
        "compliance_report.txt",
        "compliance_report.json",
        "compliance_report.html",
        "compliance_report.csv",
        "compliance_report.sarif",
        "compliance_report.junit.xml",
    ):
        assert (tmp_path / name).is_file()
