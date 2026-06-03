"""Generate compliance reports (TXT, JSON, HTML, CSV, SARIF, JUnit)."""

from __future__ import annotations

import csv
import html
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from network_config_checker.junit_xml import write_junit_report
from network_config_checker.models import ComplianceResult
from network_config_checker.sarif import write_sarif_report
from network_config_checker.version import __version__

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = frozenset({"txt", "json", "html", "csv", "sarif", "junit"})


class ReportWriter:
    def __init__(self, results: list[ComplianceResult]) -> None:
        self.results = results
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def write_all(self, output_dir: Path, formats: Iterable[str]) -> dict[str, bool]:
        output_dir.mkdir(parents=True, exist_ok=True)
        chosen = {fmt.lower().strip() for fmt in formats}
        unknown = chosen - SUPPORTED_FORMATS
        if unknown:
            raise ValueError(f"Unsupported formats: {', '.join(sorted(unknown))}")

        outcomes: dict[str, bool] = {}
        if "txt" in chosen:
            outcomes["txt"] = self._write_text(output_dir / "compliance_report.txt")
        if "json" in chosen:
            outcomes["json"] = self._write_json(output_dir / "compliance_report.json")
        if "html" in chosen:
            outcomes["html"] = self._write_html(output_dir / "compliance_report.html")
        if "csv" in chosen:
            outcomes["csv"] = self._write_csv(output_dir / "compliance_report.csv")
        if "sarif" in chosen:
            outcomes["sarif"] = write_sarif_report(self.results, output_dir / "compliance_report.sarif")
        if "junit" in chosen:
            outcomes["junit"] = write_junit_report(self.results, output_dir / "compliance_report.junit.xml")
        return outcomes

    def _write_text(self, path: Path) -> bool:
        lines: list[str] = [
            "=" * 80,
            "NETWORK CONFIGURATION COMPLIANCE REPORT",
            "Offline compliance scanner for network configs in Git",
            "=" * 80,
            f"Generated: {self.timestamp}",
            f"Tool version: {__version__}",
            "",
        ]

        for result in self.results:
            summary = result.summary
            lines.extend(
                [
                    f"Config: {result.config_path}",
                    f"SHA-256: {result.config_sha256}",
                    f"Policy pack: {result.policy_pack_name} v{result.policy_pack_version}",
                    f"Detected vendor: {result.detected_vendor}",
                    "-" * 40,
                    f"Compliance score: {summary['compliance_score']}%",
                    f"Violations: {summary['total_violations']}",
                    "",
                ]
            )
            for rule_key, rule in result.detailed_results.items():
                lines.append(f"  [{rule.status.upper()}] {rule.rule_id} — {rule_key}")
                if rule.status == "non_compliant" and rule.remediation:
                    lines.append(f"    Remediation: {rule.remediation.splitlines()[0]}")
            lines.append("")

            if result.warnings:
                lines.append("Warnings:")
                for warning in result.warnings:
                    lines.append(f"  • {warning}")
                lines.append("")

            lines.append("Recommendations:")
            for item in result.recommendations:
                lines.append(f"  • {item}")
            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Wrote text report: %s", path)
        return True

    def _write_json(self, path: Path) -> bool:
        payload = {
            "metadata": {
                "generated_at": self.timestamp,
                "tool_version": __version__,
                "report_type": "compliance_analysis",
                "author": "Olúmáyòwá Akinkuehinmi",
                "contact": "akintunero101@gmail.com",
            },
            "results": [result.to_serializable() for result in self.results],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Wrote JSON report: %s", path)
        return True

    def _write_csv(self, path: Path) -> bool:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "config_path",
                    "rule_key",
                    "rule_id",
                    "status",
                    "severity",
                    "scope",
                    "target",
                    "message",
                    "remediation",
                ]
            )
            for result in self.results:
                for violation in result.violations:
                    writer.writerow(
                        [
                            result.config_path,
                            violation.rule_key,
                            violation.rule_id,
                            "non_compliant",
                            violation.severity.value,
                            violation.scope.value,
                            violation.target,
                            violation.message,
                            violation.remediation,
                        ]
                    )
        logger.info("Wrote CSV report: %s", path)
        return True

    def _write_html(self, path: Path) -> bool:
        sections: list[str] = []
        for result in self.results:
            rows = []
            for violation in result.violations:
                rows.append(
                    "<tr>"
                    f"<td>{html.escape(violation.rule_id)}</td>"
                    f"<td>{html.escape(violation.severity.value)}</td>"
                    f"<td>{html.escape(violation.target)}</td>"
                    f"<td>{html.escape(violation.message)}</td>"
                    f"<td><pre>{html.escape(violation.remediation)}</pre></td>"
                    "</tr>"
                )
            table_body = "\n".join(rows) if rows else "<tr><td colspan='5'>No violations</td></tr>"
            sections.append(
                f"""
                <section>
                  <h2>{html.escape(result.config_path)}</h2>
                  <p>Policy pack: {html.escape(result.policy_pack_name)} v{html.escape(result.policy_pack_version)}</p>
                  <p>Score: {result.summary["compliance_score"]}% — Violations: {result.summary["total_violations"]}</p>
                  <table>
                    <thead>
                      <tr><th>Rule ID</th><th>Severity</th><th>Target</th><th>Message</th><th>Remediation</th></tr>
                    </thead>
                    <tbody>{table_body}</tbody>
                  </table>
                </section>
                """
            )

        document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Network Config Compliance Report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #f6f8fa; }}
    .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 2rem; border-radius: 8px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; vertical-align: top; }}
    th {{ background: #0d6efd; color: #fff; }}
    pre {{ white-space: pre-wrap; margin: 0; font-family: inherit; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Network Configuration Compliance Report</h1>
    <p>Generated {html.escape(self.timestamp)} — network-config-checker v{html.escape(__version__)}</p>
    <p>Maintainer: Olúmáyòwá Akinkuehinmi &lt;akintunero101@gmail.com&gt;</p>
    {"".join(sections)}
  </div>
</body>
</html>"""
        path.write_text(document, encoding="utf-8")
        logger.info("Wrote HTML report: %s", path)
        return True
