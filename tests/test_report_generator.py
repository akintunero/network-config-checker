import pytest
import json
from src.report_generator import ReportGenerator

def test_generate_json_report(tmp_path):
    compliance_results = {"IP Addressing": "Compliant"}
    report_file = tmp_path / "report.json"

    generator = ReportGenerator(compliance_results)
    generator.generate_json_report(report_file)

    with open(report_file, "r") as file:
        data = json.load(file)

    assert "IP Addressing" in data
    assert data["IP Addressing"] == "Compliant"
