"""Command-line interface for offline compliance scanning."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from network_config_checker import __version__
from network_config_checker.exit_codes import EXIT_ERROR, EXIT_SUCCESS, EXIT_VIOLATIONS
from network_config_checker.limits import DEFAULT_MAX_CONFIG_BYTES, ConfigSizeError
from network_config_checker.logging_config import configure_logging
from network_config_checker.models import Severity
from network_config_checker.policy import (
    PolicyValidationError,
    explain_rule,
    load_policies,
    resolve_policy_path,
    validate_policies,
)
from network_config_checker.reports import SUPPORTED_FORMATS, ReportWriter
from network_config_checker.scanner import (
    baseline_summary,
    diff_against_baseline,
    scan_paths,
    should_fail,
)

logger = logging.getLogger(__name__)

DEFAULT_FORMATS = "txt,json,html,csv,sarif,junit"


def _parse_severity_list(value: str) -> Severity:
    try:
        return Severity.from_string(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="network-config-checker",
        description="Offline compliance scanner for network configs in Git",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  network-config-checker scan -c configs -p policies/builtin\n"
            "  network-config-checker scan -c ./configs -p policies/builtin "
            "--format sarif,junit --fail-on high\n"
            "  network-config-checker validate-policies -p builtin/cisco_ios_baseline\n"
            "  network-config-checker policy explain -p builtin/cisco_ios_baseline "
            "--rule-id NCC-REQUIRE_INTERFACE_DESCRIPTION\n"
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan configuration file(s) against policies")
    _add_scan_arguments(scan_parser)

    validate_parser = subparsers.add_parser("validate-policies", help="Validate policy YAML files")
    validate_parser.add_argument(
        "-p",
        "--policy",
        required=True,
        help="Policy file, directory, or builtin pack (e.g. builtin/cisco_ios_baseline)",
    )

    explain_parser = subparsers.add_parser("policy", help="Policy utilities")
    explain_sub = explain_parser.add_subparsers(dest="policy_command", required=True)
    explain_cmd = explain_sub.add_parser("explain", help="Explain a rule by rule ID or rule key")
    explain_cmd.add_argument(
        "-p",
        "--policy",
        required=True,
        help="Policy file, directory, or builtin pack",
    )
    explain_cmd.add_argument(
        "--rule-id",
        required=True,
        help="Rule ID (e.g. NCC-REQUIRE_INTERFACE_DESCRIPTION) or rule key",
    )

    baseline_parser = subparsers.add_parser(
        "write-baseline",
        help="Write a JSON baseline summary for --baseline comparisons in CI",
    )
    _add_scan_arguments(baseline_parser, require_output=False)

    return parser


def _add_scan_arguments(parser: argparse.ArgumentParser, *, require_output: bool = True) -> None:
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Configuration file or directory (recursive *.cfg, *.conf, *.txt)",
    )
    parser.add_argument(
        "-p",
        "--policy",
        required=True,
        help="Policy file, directory, or builtin pack (e.g. builtin/cisco_ios_baseline)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    parser.add_argument(
        "--format",
        default=DEFAULT_FORMATS,
        help=f"Comma-separated report formats: {', '.join(sorted(SUPPORTED_FORMATS))}",
    )
    parser.add_argument(
        "--fail-on",
        type=_parse_severity_list,
        default=Severity.HIGH,
        help="Exit code 1 when violations at or above this severity exist (default: high)",
    )
    parser.add_argument(
        "--inventory",
        help="CSV inventory with columns hostname,path[,vendor] for fleet scans",
    )
    parser.add_argument(
        "--baseline",
        help="JSON baseline from write-baseline; report regressions in logs",
    )
    parser.add_argument(
        "--write-baseline-to",
        help="Write baseline JSON after scan (for storing in Git)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Emit structured JSON logs",
    )
    parser.add_argument(
        "--max-config-mib",
        type=float,
        default=DEFAULT_MAX_CONFIG_BYTES / (1024 * 1024),
        help="Maximum size per configuration file in MiB (default: 5)",
    )
    if require_output:
        parser.set_defaults(output="reports")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "scan":
            code = _cmd_scan(args)
        elif args.command == "write-baseline":
            code = _cmd_write_baseline(args)
        elif args.command == "validate-policies":
            code = _cmd_validate_policies(args)
        elif args.command == "policy" and args.policy_command == "explain":
            code = _cmd_policy_explain(args)
        else:
            parser.error(f"Unknown command: {args.command}")
            code = EXIT_ERROR
    except (PolicyValidationError, FileNotFoundError, ValueError, ConfigSizeError) as exc:
        logger.error("%s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        code = EXIT_ERROR
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        code = EXIT_ERROR

    sys.exit(code)


def _cmd_validate_policies(args: argparse.Namespace) -> int:
    policy_path = resolve_policy_path(args.policy)
    load_policies(policy_path)
    for line in validate_policies(policy_path):
        print(line)
    return EXIT_SUCCESS


def _cmd_policy_explain(args: argparse.Namespace) -> int:
    policy_path = resolve_policy_path(args.policy)
    pack = load_policies(policy_path)
    print(explain_rule(pack, args.rule_id))
    return EXIT_SUCCESS


def _cmd_scan(args: argparse.Namespace) -> int:
    output_dir = Path(args.output)
    configure_logging(
        verbose=args.verbose,
        json_logs=args.json_logs,
        log_file=output_dir / "checker.log",
    )

    policy_path = resolve_policy_path(args.policy)
    policy_pack = load_policies(policy_path)
    config_path = Path(args.config)
    inventory = Path(args.inventory) if args.inventory else None

    max_bytes = int(args.max_config_mib * 1024 * 1024)
    results = scan_paths(
        config_path,
        policy_pack,
        inventory_path=inventory,
        max_config_bytes=max_bytes,
    )

    if args.baseline:
        for message in diff_against_baseline(results, Path(args.baseline)):
            logger.warning(message)

    formats = [part.strip() for part in args.format.split(",") if part.strip()]
    writer = ReportWriter(results)
    writer.write_all(output_dir, formats)

    if args.write_baseline_to:
        baseline_path = Path(args.write_baseline_to)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(baseline_summary(results), indent=2), encoding="utf-8")
        logger.info("Wrote baseline summary: %s", baseline_path)

    if should_fail(results, args.fail_on):
        logger.error("Compliance failures at or above severity: %s", args.fail_on.value)
        return EXIT_VIOLATIONS

    logger.info("Scan completed with no failures at or above %s", args.fail_on.value)
    return EXIT_SUCCESS


def _cmd_write_baseline(args: argparse.Namespace) -> int:
    args.write_baseline_to = args.write_baseline_to or str(Path(args.output) / "baseline.json")
    code = _cmd_scan(args)
    if code == EXIT_SUCCESS:
        print(f"Baseline written to {args.write_baseline_to}")
    return code
