"""Data models for policies and compliance results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PolicyScope(str, Enum):
    GLOBAL = "global"
    INTERFACE = "interface"
    VLAN = "vlan"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def from_string(cls, value: str) -> Severity:
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Invalid severity: {value!r}. Use critical, high, medium, or low.")


SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
}


@dataclass(frozen=True)
class PolicyRule:
    rule_key: str
    rule_id: str
    description: str
    severity: Severity
    scope: PolicyScope
    conditions: tuple[str, ...] = ()
    required_conditions: tuple[str, ...] = ()
    forbidden_conditions: tuple[str, ...] = ()
    remediation: str = ""
    references: tuple[str, ...] = ()
    vendor: str = "cisco_ios"
    deprecated: bool = False
    replaced_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.rule_id,
            "description": self.description,
            "severity": self.severity.value,
            "scope": self.scope.value,
            "conditions": list(self.conditions),
            "required_conditions": list(self.required_conditions),
            "forbidden_conditions": list(self.forbidden_conditions),
            "remediation": self.remediation,
            "references": list(self.references),
            "vendor": self.vendor,
            "deprecated": self.deprecated,
            "replaced_by": self.replaced_by,
        }


@dataclass
class PolicyPack:
    name: str
    version: str
    rules: dict[str, PolicyRule] = field(default_factory=dict)

    def get_rule_by_id(self, rule_id: str) -> PolicyRule | None:
        for rule in self.rules.values():
            if rule.rule_id == rule_id:
                return rule
        return None


@dataclass
class Violation:
    rule_key: str
    rule_id: str
    severity: Severity
    scope: PolicyScope
    target: str
    message: str
    remediation: str
    references: tuple[str, ...]


@dataclass
class RuleResult:
    rule_key: str
    rule_id: str
    status: str
    description: str
    severity: str
    scope: str
    details: list[dict[str, Any]]
    non_compliant_targets: list[str]
    remediation: str
    references: list[str]
    deprecated: bool = False
    replaced_by: str | None = None


@dataclass
class ComplianceResult:
    config_path: str
    config_sha256: str
    policy_pack_name: str
    policy_pack_version: str
    summary: dict[str, Any]
    detailed_results: dict[str, RuleResult]
    violations: list[Violation]
    recommendations: list[str]
    detected_vendor: str = "cisco_ios"
    warnings: list[str] = field(default_factory=list)

    def to_serializable(self) -> dict[str, Any]:
        return {
            "config_path": self.config_path,
            "config_sha256": self.config_sha256,
            "policy_pack_name": self.policy_pack_name,
            "policy_pack_version": self.policy_pack_version,
            "detected_vendor": self.detected_vendor,
            "warnings": self.warnings,
            "summary": self.summary,
            "detailed_results": {
                key: {
                    "rule_id": result.rule_id,
                    "status": result.status,
                    "description": result.description,
                    "severity": result.severity,
                    "scope": result.scope,
                    "details": result.details,
                    "non_compliant_targets": result.non_compliant_targets,
                    "remediation": result.remediation,
                    "references": result.references,
                    "deprecated": result.deprecated,
                    "replaced_by": result.replaced_by,
                }
                for key, result in self.detailed_results.items()
            },
            "violations": [
                {
                    "rule_key": v.rule_key,
                    "rule_id": v.rule_id,
                    "severity": v.severity.value,
                    "scope": v.scope.value,
                    "target": v.target,
                    "message": v.message,
                    "remediation": v.remediation,
                    "references": list(v.references),
                }
                for v in self.violations
            ],
            "recommendations": self.recommendations,
        }
