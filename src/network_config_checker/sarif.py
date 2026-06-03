"""SARIF 2.1.0 export for GitHub Code Scanning and GitLab SAST."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from network_config_checker.models import ComplianceResult, Severity
from network_config_checker.version import __version__

_SARIF_LEVEL = {
    Severity.CRITICAL: "error",
    Severity.HIGH: "error",
    Severity.MEDIUM: "warning",
    Severity.LOW: "note",
}


def build_sarif(results: list[ComplianceResult]) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    sarif_results: list[dict[str, Any]] = []

    for compliance in results:
        for violation in compliance.violations:
            rule_id = violation.rule_id
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": violation.rule_key,
                    "shortDescription": {"text": violation.rule_key},
                    "fullDescription": {"text": violation.message},
                    "defaultConfiguration": {"level": _SARIF_LEVEL[violation.severity]},
                }

            sarif_results.append(
                {
                    "ruleId": rule_id,
                    "level": _SARIF_LEVEL[violation.severity],
                    "message": {"text": violation.message},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": compliance.config_path},
                            }
                        }
                    ],
                    "properties": {
                        "severity": violation.severity.value,
                        "scope": violation.scope.value,
                        "target": violation.target,
                        "remediation": violation.remediation,
                        "references": list(violation.references),
                        "configSha256": compliance.config_sha256,
                    },
                }
            )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "network-config-checker",
                        "version": __version__,
                        "informationUri": "https://github.com/akintunero/network-config-checker",
                        "rules": list(rules.values()),
                    }
                },
                "results": sarif_results,
            }
        ],
    }


def write_sarif_report(results: list[ComplianceResult], path: Path) -> bool:
    path.write_text(json.dumps(build_sarif(results), indent=2), encoding="utf-8")
    return True
