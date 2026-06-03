"""JUnit XML export for Jenkins, GitLab CI, and Azure DevOps."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

from network_config_checker.models import ComplianceResult


def write_junit_report(results: list[ComplianceResult], path: Path) -> bool:
    total_tests = 0
    total_failures = 0
    suites = ET.Element("testsuites")

    for compliance in results:
        suite = ET.SubElement(suites, "testsuite", name=compliance.config_path)
        for violation in compliance.violations:
            total_tests += 1
            case = ET.SubElement(
                suite,
                "testcase",
                classname=compliance.config_path,
                name=violation.rule_id,
            )
            ET.SubElement(
                case,
                "failure",
                message=violation.message,
                type=violation.severity.value,
            ).text = violation.remediation or violation.message
            total_failures += 1

        if not compliance.violations:
            total_tests += 1
            ET.SubElement(
                suite,
                "testcase",
                classname=compliance.config_path,
                name="compliance-summary",
            )

    suites.set("tests", str(total_tests))
    suites.set("failures", str(total_failures))

    rough = ET.tostring(suites, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")
    path.write_text(pretty, encoding="utf-8")
    return True
