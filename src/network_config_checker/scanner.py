"""Scan one or many configuration files (offline)."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Iterator

from network_config_checker.compliance import ComplianceEngine, violations_at_or_above
from network_config_checker.models import ComplianceResult, Severity
from network_config_checker.parser import ConfigParser
from network_config_checker.limits import DEFAULT_MAX_CONFIG_BYTES
from network_config_checker.models import PolicyPack

logger = logging.getLogger(__name__)

CONFIG_GLOBS = ("*.cfg", "*.conf", "*.txt", "*.config")


def iter_config_paths(config_path: Path, inventory_path: Path | None = None) -> Iterator[tuple[str, Path]]:
    if inventory_path:
        yield from _iter_inventory(inventory_path)
        return

    if config_path.is_file():
        yield config_path.name, config_path
        return

    if config_path.is_dir():
        for pattern in CONFIG_GLOBS:
            for file_path in sorted(config_path.rglob(pattern)):
                if file_path.is_file():
                    yield str(file_path.relative_to(config_path)), file_path
        return

    raise FileNotFoundError(f"Configuration path not found: {config_path}")


def _iter_inventory(inventory_path: Path) -> Iterator[tuple[str, Path]]:
    with inventory_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"hostname", "path"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"Inventory CSV must include columns: {', '.join(sorted(required))}")

        for row in reader:
            hostname = row["hostname"].strip()
            path = Path(row["path"].strip())
            if not path.is_file():
                raise FileNotFoundError(f"Inventory entry {hostname}: missing file {path}")
            yield hostname, path


def scan_file(
    config_file: Path,
    policy_pack: PolicyPack,
    *,
    label: str | None = None,
    max_config_bytes: int = DEFAULT_MAX_CONFIG_BYTES,
) -> ComplianceResult:
    parser = ConfigParser(
        config_file,
        source_label=label or str(config_file),
        max_config_bytes=max_config_bytes,
    )
    engine = ComplianceEngine(parser, policy_pack)
    return engine.check(config_path=label or str(config_file))


def scan_paths(
    config_path: Path,
    policy_pack: PolicyPack,
    *,
    inventory_path: Path | None = None,
    max_config_bytes: int = DEFAULT_MAX_CONFIG_BYTES,
) -> list[ComplianceResult]:
    results: list[ComplianceResult] = []
    for label, file_path in iter_config_paths(config_path, inventory_path):
        logger.info("Scanning %s", file_path)
        results.append(
            scan_file(
                file_path,
                policy_pack,
                label=label,
                max_config_bytes=max_config_bytes,
            )
        )
    if not results:
        raise FileNotFoundError(f"No configuration files found under {config_path}")
    return results


def load_baseline_summary(baseline_path: Path) -> dict[str, dict[str, int]]:
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Baseline file must be a JSON object keyed by config path.")
    return data


def diff_against_baseline(
    current: list[ComplianceResult],
    baseline_path: Path,
) -> list[str]:
    baseline = load_baseline_summary(baseline_path)
    messages: list[str] = []

    for result in current:
        previous = baseline.get(result.config_path)
        if previous is None:
            messages.append(f"{result.config_path}: new config (no baseline)")
            continue
        prev_violations = int(previous.get("total_violations", 0))
        curr_violations = int(result.summary["total_violations"])
        delta = curr_violations - prev_violations
        if delta > 0:
            messages.append(f"{result.config_path}: regressions (+{delta} violations, now {curr_violations})")
        elif delta < 0:
            messages.append(f"{result.config_path}: improved ({delta} violations, now {curr_violations})")
        else:
            messages.append(f"{result.config_path}: unchanged ({curr_violations} violations)")

    return messages


def baseline_summary(results: list[ComplianceResult]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for result in results:
        summary[result.config_path] = {
            "total_violations": int(result.summary["total_violations"]),
            "non_compliant_policies": int(result.summary["non_compliant_policies"]),
        }
    return summary


def should_fail(
    results: list[ComplianceResult],
    fail_on: Severity,
) -> bool:
    for result in results:
        if violations_at_or_above(result.violations, fail_on):
            return True
    return False
