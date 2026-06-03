"""Evaluate parsed configurations against validated policy packs."""

from __future__ import annotations

import logging
from typing import Any

from network_config_checker.conditions import match_condition
from network_config_checker.models import (
    SEVERITY_ORDER,
    ComplianceResult,
    PolicyPack,
    PolicyRule,
    PolicyScope,
    RuleResult,
    Severity,
    Violation,
)
from network_config_checker.parser import ConfigParser

logger = logging.getLogger(__name__)


class ComplianceEngine:
    def __init__(self, parser: ConfigParser, policy_pack: PolicyPack) -> None:
        self.parser = parser
        self.policy_pack = policy_pack

    def check(self, *, config_path: str) -> ComplianceResult:
        detailed: dict[str, RuleResult] = {}
        violations: list[Violation] = []

        for rule_key, rule in self.policy_pack.rules.items():
            rule_result = self._apply_rule(rule)
            detailed[rule_key] = rule_result
            if rule_result.status == "non_compliant":
                violations.extend(self._violations_for_rule(rule, rule_result))

        compliant_count = sum(1 for r in detailed.values() if r.status == "compliant")
        non_compliant_count = len(detailed) - compliant_count
        total_targets = len(self.parser.get_interfaces())

        summary: dict[str, Any] = {
            "total_policies": len(detailed),
            "compliant_policies": compliant_count,
            "non_compliant_policies": non_compliant_count,
            "total_interfaces": total_targets,
            "total_violations": len(violations),
            "compliance_score": self._score(compliant_count, len(detailed)),
        }

        recommendations = self._recommendations(detailed)
        warnings = self._collect_warnings()
        if warnings:
            summary["warnings"] = warnings
        return ComplianceResult(
            config_path=config_path,
            config_sha256=self.parser.config_sha256,
            policy_pack_name=self.policy_pack.name,
            policy_pack_version=self.policy_pack.version,
            detected_vendor=self.parser.detected_vendor.value,
            summary=summary,
            detailed_results=detailed,
            violations=violations,
            recommendations=recommendations,
            warnings=warnings,
        )

    def _score(self, compliant: int, total: int) -> float:
        if total == 0:
            return 100.0
        return round((compliant / total) * 100.0, 1)

    def _apply_rule(self, rule: PolicyRule) -> RuleResult:
        if rule.scope == PolicyScope.GLOBAL:
            return self._apply_global_rule(rule)
        if rule.scope == PolicyScope.VLAN:
            return self._apply_vlan_rule(rule)
        return self._apply_interface_rule(rule)

    def _apply_global_rule(self, rule: PolicyRule) -> RuleResult:
        context = self.parser.get_global_context_text()
        compliant = self._evaluate_text(context, rule)
        status = "compliant" if compliant else "non_compliant"
        details = [
            {
                "target": "global",
                "status": status,
                "issues": [] if compliant else [f"Global policy {rule.rule_id} not satisfied"],
            }
        ]
        return self._build_rule_result(rule, status, details, [] if compliant else ["global"])

    def _apply_vlan_rule(self, rule: PolicyRule) -> RuleResult:
        vlan_configs = self.parser.get_vlan_configs()
        details: list[dict[str, Any]] = []
        non_compliant: list[str] = []
        status = "compliant"

        if not vlan_configs:
            status = "non_compliant"
            details.append(
                {
                    "target": "vlan",
                    "status": "non_compliant",
                    "issues": ["No VLAN configuration stanzas found"],
                }
            )
            non_compliant.append("vlan")

        for vlan_id, vlan_data in vlan_configs.items():
            text = " ".join(vlan_data.get("config", [])).lower()
            target_ok = self._evaluate_text(text, rule)
            target_status = "compliant" if target_ok else "non_compliant"
            issues: list[str] = []
            if not target_ok:
                issues.append(f"VLAN {vlan_id} does not satisfy {rule.rule_id}")
                non_compliant.append(vlan_id)
                status = "non_compliant"
            details.append({"target": vlan_id, "status": target_status, "issues": issues})

        return self._build_rule_result(rule, status, details, non_compliant)

    def _apply_interface_rule(self, rule: PolicyRule) -> RuleResult:
        interfaces = self.parser.get_interfaces()
        details: list[dict[str, Any]] = []
        non_compliant: list[str] = []
        status = "compliant"

        if not interfaces:
            return self._build_rule_result(
                rule,
                "non_compliant",
                [
                    {
                        "target": "interfaces",
                        "status": "non_compliant",
                        "issues": ["No interfaces found in configuration"],
                    }
                ],
                ["interfaces"],
            )

        for interface_name, lines in interfaces.items():
            text = " ".join(lines).lower()
            target_ok = self._evaluate_text(text, rule)
            target_status = "compliant" if target_ok else "non_compliant"
            issues: list[str] = []
            if not target_ok:
                issues.append(f"Interface {interface_name} failed {rule.rule_id}")
                non_compliant.append(interface_name)
                status = "non_compliant"
            details.append({"target": interface_name, "status": target_status, "issues": issues})

        return self._build_rule_result(rule, status, details, non_compliant)

    def _build_rule_result(
        self,
        rule: PolicyRule,
        status: str,
        details: list[dict[str, Any]],
        non_compliant: list[str],
    ) -> RuleResult:
        return RuleResult(
            rule_key=rule.rule_key,
            rule_id=rule.rule_id,
            status=status,
            description=rule.description,
            severity=rule.severity.value,
            scope=rule.scope.value,
            details=details,
            non_compliant_targets=non_compliant,
            remediation=rule.remediation,
            references=list(rule.references),
            deprecated=rule.deprecated,
            replaced_by=rule.replaced_by,
        )

    def _evaluate_text(self, text: str, rule: PolicyRule) -> bool:
        for condition in rule.required_conditions:
            if not self._check_condition(text, condition):
                return False
        for condition in rule.forbidden_conditions:
            if self._check_condition(text, condition):
                return False
        for condition in rule.conditions:
            if not self._check_condition(text, condition):
                return False
        return True

    def _check_condition(self, text: str, condition: str) -> bool:
        return match_condition(text, condition)

    def _collect_warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.parser.vendor_warning:
            warnings.append(self.parser.vendor_warning)
        for rule in self.policy_pack.rules.values():
            if rule.deprecated:
                replacement = f" Use {rule.replaced_by} instead." if rule.replaced_by else ""
                warnings.append(f"Policy rule {rule.rule_id} is deprecated.{replacement}")
        return warnings

    def _violations_for_rule(self, rule: PolicyRule, result: RuleResult) -> list[Violation]:
        items: list[Violation] = []
        for detail in result.details:
            if detail.get("status") != "non_compliant":
                continue
            target = str(detail.get("target", "unknown"))
            issues = detail.get("issues", [])
            message = issues[0] if issues else f"{rule.rule_id} failed on {target}"
            items.append(
                Violation(
                    rule_key=rule.rule_key,
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    scope=rule.scope,
                    target=target,
                    message=message,
                    remediation=rule.remediation,
                    references=rule.references,
                )
            )
        return items

    def _recommendations(self, detailed: dict[str, RuleResult]) -> list[str]:
        recommendations: list[str] = []
        for rule_key, result in detailed.items():
            if result.status == "non_compliant":
                count = len(result.non_compliant_targets)
                recommendations.append(
                    f"Fix {rule_key} ({result.rule_id}): {count} target(s) non-compliant — {result.description}"
                )
        if not recommendations:
            recommendations.append("All policies are compliant.")
        return recommendations


def violations_at_or_above(
    violations: list[Violation],
    minimum: Severity,
) -> list[Violation]:
    threshold = SEVERITY_ORDER[minimum]
    return [v for v in violations if SEVERITY_ORDER[v.severity] <= threshold]
