"""Load, merge, and validate YAML policy packs."""

from __future__ import annotations

import json
import sysconfig
from pathlib import Path
from typing import Any

import yaml

from network_config_checker.models import PolicyPack, PolicyRule, PolicyScope, Severity

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_BUILTIN_DIR = REPO_ROOT / "policies" / "builtin"
REPO_SCHEMA_PATH = REPO_ROOT / "policies" / "schema" / "policy.schema.json"


def _share_data_root() -> Path:
    return Path(sysconfig.get_path("data")) / "network-config-checker"


def _builtin_policy_dir() -> Path:
    if REPO_BUILTIN_DIR.is_dir():
        return REPO_BUILTIN_DIR
    installed = _share_data_root() / "policies" / "builtin"
    if installed.is_dir():
        return installed
    return REPO_BUILTIN_DIR


def _schema_path() -> Path:
    if REPO_SCHEMA_PATH.is_file():
        return REPO_SCHEMA_PATH
    installed = _share_data_root() / "schema" / "policy.schema.json"
    if installed.is_file():
        return installed
    return REPO_SCHEMA_PATH


VALID_SCOPES = {s.value for s in PolicyScope}
REQUIRED_RULE_FIELDS = {"description", "severity", "scope"}


class PolicyValidationError(ValueError):
    """Raised when a policy file fails validation."""


def _default_rule_id(rule_key: str) -> str:
    slug = rule_key.upper().replace("-", "_")
    return f"NCC-{slug[:32]}"


def _parse_rule(rule_key: str, raw: dict[str, Any]) -> PolicyRule:
    if not isinstance(raw, dict):
        raise PolicyValidationError(f"Rule {rule_key!r} must be a mapping.")

    missing = REQUIRED_RULE_FIELDS - set(raw.keys())
    if missing:
        raise PolicyValidationError(f"Rule {rule_key!r} missing fields: {sorted(missing)}")

    scope_value = str(raw["scope"]).strip().lower()
    if scope_value not in VALID_SCOPES:
        raise PolicyValidationError(
            f"Rule {rule_key!r} has invalid scope {scope_value!r}. Use one of: {', '.join(sorted(VALID_SCOPES))}."
        )

    conditions = tuple(str(c) for c in raw.get("conditions", []) or [])
    required = tuple(str(c) for c in raw.get("required_conditions", []) or [])
    forbidden = tuple(str(c) for c in raw.get("forbidden_conditions", []) or [])

    if not conditions and not required and not forbidden:
        raise PolicyValidationError(
            f"Rule {rule_key!r} must define at least one of: conditions, required_conditions, forbidden_conditions."
        )

    references_raw = raw.get("references", []) or []
    references: tuple[str, ...]
    if isinstance(references_raw, str):
        references = (references_raw,)
    else:
        references = tuple(str(r) for r in references_raw)

    try:
        severity = Severity.from_string(str(raw["severity"]))
    except ValueError as exc:
        raise PolicyValidationError(f"Rule {rule_key!r}: {exc}") from exc

    replaced_raw = raw.get("replaced_by")
    replaced_by = str(replaced_raw).strip() if replaced_raw else None

    return PolicyRule(
        rule_key=rule_key,
        rule_id=str(raw.get("id", _default_rule_id(rule_key))),
        description=str(raw["description"]),
        severity=severity,
        scope=PolicyScope(scope_value),
        conditions=conditions,
        required_conditions=required,
        forbidden_conditions=forbidden,
        remediation=str(raw.get("remediation", "")),
        references=references,
        vendor=str(raw.get("vendor", "cisco_ios")),
        deprecated=bool(raw.get("deprecated", False)),
        replaced_by=replaced_by,
    )


def _parse_pack_document(data: dict[str, Any], source: Path) -> PolicyPack:
    pack_name = str(data.get("policy_pack_name", source.stem))
    pack_version = str(data.get("policy_pack_version", "1.0.0"))
    rules_block = data.get("rules", data)

    if not isinstance(rules_block, dict):
        raise PolicyValidationError(f"Policy file {source} must contain a rules mapping.")

    rules: dict[str, PolicyRule] = {}
    for rule_key, rule_body in rules_block.items():
        if rule_key in ("policy_pack_name", "policy_pack_version"):
            continue
        if isinstance(rule_body, dict) and "description" in rule_body:
            rules[rule_key] = _parse_rule(rule_key, rule_body)

    if not rules:
        raise PolicyValidationError(f"No valid rules found in {source}.")

    return PolicyPack(name=pack_name, version=pack_version, rules=rules)


def load_policy_file(path: Path) -> PolicyPack:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyValidationError(f"Cannot read policy file {path}: {exc}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise PolicyValidationError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise PolicyValidationError(f"Policy file {path} must be a YAML mapping.")

    validate_document_schema(data, path)
    return _parse_pack_document(data, path)


def merge_policy_packs(packs: list[PolicyPack]) -> PolicyPack:
    if not packs:
        raise PolicyValidationError("No policy packs to merge.")

    merged_rules: dict[str, PolicyRule] = {}
    names: list[str] = []
    versions: list[str] = []

    for pack in packs:
        names.append(pack.name)
        versions.append(pack.version)
        merged_rules.update(pack.rules)

    return PolicyPack(
        name="+".join(names),
        version=",".join(versions),
        rules=merged_rules,
    )


def load_policies(path: Path) -> PolicyPack:
    """Load a single file, directory of YAML files, or builtin pack name."""
    if path.is_file():
        return load_policy_file(path)

    if path.is_dir():
        packs = [load_policy_file(yaml_file) for yaml_file in sorted(path.glob("*.yaml"))]
        packs.extend(load_policy_file(yml_file) for yml_file in sorted(path.glob("*.yml")))
        if not packs:
            raise PolicyValidationError(f"No YAML policies found in {path}.")
        return merge_policy_packs(packs)

    raise PolicyValidationError(f"Policy path does not exist: {path}")


def resolve_policy_path(policy_arg: str) -> Path:
    """Resolve --policy or --policy-pack arguments."""
    candidate = Path(policy_arg)
    if candidate.exists():
        return candidate

    if policy_arg.startswith("builtin/"):
        pack_name = policy_arg.split("/", 1)[1]
    else:
        pack_name = policy_arg

    builtin_dir = _builtin_policy_dir()
    builtin_file = builtin_dir / f"{pack_name}.yaml"
    if builtin_file.is_file():
        return builtin_file

    raise PolicyValidationError(
        f"Policy not found: {policy_arg}. Use a file path, directory, or builtin pack under {builtin_dir}."
    )


def validate_policies(path: Path) -> list[str]:
    """Validate policies and return human-readable success messages."""
    pack = load_policies(path)
    messages: list[str] = [
        f"Valid policy pack: {pack.name} v{pack.version}",
        f"Rules loaded: {len(pack.rules)}",
    ]
    for rule in pack.rules.values():
        line = f"  - {rule.rule_id} [{rule.severity.value}] {rule.rule_key} ({rule.scope.value})"
        if rule.deprecated:
            line += " [DEPRECATED]"
            if rule.replaced_by:
                line += f" -> {rule.replaced_by}"
        messages.append(line)
    return messages


def explain_rule(pack: PolicyPack, rule_id: str) -> str:
    rule = pack.get_rule_by_id(rule_id)
    if rule is None:
        rule = pack.rules.get(rule_id)
    if rule is None:
        available = ", ".join(sorted(r.rule_id for r in pack.rules.values()))
        raise PolicyValidationError(f"Unknown rule {rule_id!r}. Available: {available}")

    lines = [
        f"Rule key: {rule.rule_key}",
        f"Rule ID: {rule.rule_id}",
        f"Severity: {rule.severity.value}",
        f"Scope: {rule.scope.value}",
        f"Vendor: {rule.vendor}",
        f"Description: {rule.description}",
    ]
    if rule.conditions:
        lines.append(f"Conditions: {', '.join(rule.conditions)}")
    if rule.required_conditions:
        lines.append(f"Required: {', '.join(rule.required_conditions)}")
    if rule.forbidden_conditions:
        lines.append(f"Forbidden: {', '.join(rule.forbidden_conditions)}")
    if rule.remediation:
        lines.append(f"Remediation:\n{rule.remediation}")
    if rule.references:
        lines.append("References:")
        lines.extend(f"  - {ref}" for ref in rule.references)
    if rule.deprecated:
        lines.append("Status: DEPRECATED")
        if rule.replaced_by:
            lines.append(f"Replaced by: {rule.replaced_by}")
    return "\n".join(lines)


def validate_document_schema(data: dict[str, Any], source: Path) -> None:
    """Validate policy document against policies/schema/policy.schema.json."""
    schema = load_schema()
    if not schema:
        return
    if jsonschema is None:
        raise PolicyValidationError(
            "jsonschema is required for schema validation. Reinstall network-config-checker."
        )
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:
        raise PolicyValidationError(f"Policy schema validation failed for {source}: {exc.message}") from exc


def load_schema() -> dict[str, Any]:
    path = _schema_path()
    if path.is_file():
        loaded: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return loaded
    return {}
