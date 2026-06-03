"""Parse offline network device configuration text (Cisco IOS-style)."""

from __future__ import annotations

import hashlib
import logging
import os
import re
from pathlib import Path
from typing import Any

from network_config_checker.limits import DEFAULT_MAX_CONFIG_BYTES, enforce_max_bytes
from network_config_checker.vendor import detect_vendor, unsupported_vendor_message

logger = logging.getLogger(__name__)


class ConfigParser:
    """Parser for Cisco IOS-style configuration backups stored in Git."""

    def __init__(
        self,
        config_source: str | Path,
        *,
        source_label: str | None = None,
        max_config_bytes: int = DEFAULT_MAX_CONFIG_BYTES,
    ) -> None:
        self.source_label = source_label or str(config_source)
        self.max_config_bytes = max_config_bytes
        self.config_text, self.config_sha256 = self._load_config(config_source)
        self.detected_vendor = detect_vendor(self.config_text)
        self.vendor_warning = unsupported_vendor_message(self.detected_vendor)
        if self.vendor_warning:
            logger.warning("%s (%s)", self.vendor_warning, self.source_label)
        self.interfaces: dict[str, list[str]] = {}
        self.security_settings: dict[str, list[str]] = {}
        self.vlan_configs: dict[str, dict[str, Any]] = {}
        self.routing_configs: dict[str, list[str]] = {}
        self._parse_configuration()

    def _load_config(self, config_source: str | Path) -> tuple[str, str]:
        if isinstance(config_source, Path):
            config_source = str(config_source)

        if os.path.isfile(config_source):
            path = Path(config_source)
            enforce_max_bytes(path.stat().st_size, config_source, max_bytes=self.max_config_bytes)
            content = path.read_text(encoding="utf-8")
            enforce_max_bytes(len(content.encode("utf-8")), config_source, max_bytes=self.max_config_bytes)
            logger.info("Loaded configuration from file: %s", config_source)
        else:
            content = config_source
            logger.info("Loaded configuration from inline text")

        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return content, digest

    def _parse_configuration(self) -> None:
        lines = self.config_text.splitlines()
        self._parse_interfaces(lines)
        self._parse_security_settings(lines)
        self._parse_vlan_configurations(lines)
        self._parse_routing_configurations(lines)
        logger.info(
            "Parsed %d interfaces, %d security setting groups",
            len(self.interfaces),
            len(self.security_settings),
        )

    def _parse_interfaces(self, lines: list[str]) -> None:
        current_interface: str | None = None
        current_config: list[str] = []

        for raw_line in lines:
            line = raw_line.strip()
            if self._is_interface_start(line):
                if current_interface:
                    self.interfaces[current_interface] = current_config
                current_interface = self._extract_interface_name(line)
                current_config = [line]
            elif line == "!" and current_interface:
                current_config.append(line)
                self.interfaces[current_interface] = current_config
                current_interface = None
                current_config = []
            elif current_interface and line:
                current_config.append(line)

        if current_interface:
            self.interfaces[current_interface] = current_config

    def _parse_security_settings(self, lines: list[str]) -> None:
        patterns = [
            r"no\s+ip\s+http\s+server",
            r"no\s+ip\s+http\s+secure-server",
            r"service\s+password-encryption",
            r"enable\s+secret",
            r"username\s+\w+\s+privilege",
            r"access-list",
            r"ip\s+access-group",
            r"crypto\s+key",
            r"ip\s+ssh\s+version\s+2",
            r"line\s+vty",
            r"login\s+local",
            r"no\s+service\s+pad",
            r"no\s+service\s+tcp-small-servers",
            r"no\s+service\s+udp-small-servers",
            r"hostname\s+\S+",
            r"banner\s+",
        ]

        for raw_line in lines:
            line = raw_line.strip()
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    category = self._categorize_security_setting(line)
                    self.security_settings.setdefault(category, []).append(line)
                    break

    def _parse_vlan_configurations(self, lines: list[str]) -> None:
        vlan_pattern = re.compile(r"vlan\s+(\d+)", re.IGNORECASE)
        name_pattern = re.compile(r"name\s+(.+)", re.IGNORECASE)
        current_vlan: str | None = None

        for raw_line in lines:
            line = raw_line.strip()
            vlan_match = vlan_pattern.search(line)
            if vlan_match:
                current_vlan = vlan_match.group(1)
                self.vlan_configs[current_vlan] = {"config": [line]}
                continue

            if current_vlan and line and line != "!":
                name_match = name_pattern.search(line)
                if name_match:
                    self.vlan_configs[current_vlan]["name"] = name_match.group(1)
                self.vlan_configs[current_vlan]["config"].append(line)
            elif line == "!":
                current_vlan = None

    def _parse_routing_configurations(self, lines: list[str]) -> None:
        router_pattern = re.compile(r"router\s+(\w+)", re.IGNORECASE)
        current_protocol: str | None = None

        for raw_line in lines:
            line = raw_line.strip()
            router_match = router_pattern.search(line)
            if router_match:
                current_protocol = router_match.group(1)
                self.routing_configs[current_protocol] = [line]
            elif current_protocol and line and line != "!":
                self.routing_configs[current_protocol].append(line)
            elif line == "!":
                current_protocol = None

    def _is_interface_start(self, line: str) -> bool:
        patterns = (
            r"^interface\s+",
            r"^interface-port\s+",
            r"^interface\s+ethernet\s+",
            r"^interface\s+fastethernet\s+",
            r"^interface\s+gigabitethernet\s+",
            r"^interface\s+serial\s+",
            r"^interface\s+loopback\s+",
            r"^interface\s+port-channel\s+",
            r"^interface\s+vlan\s+",
        )
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns)

    def _extract_interface_name(self, line: str) -> str:
        return re.sub(r"^interface\s+", "", line, flags=re.IGNORECASE).strip()

    def _categorize_security_setting(self, line: str) -> str:
        lowered = line.lower()
        if "http" in lowered:
            return "http_security"
        if "password" in lowered or "secret" in lowered:
            return "password_security"
        if "access-list" in lowered:
            return "access_control"
        if "crypto" in lowered or "ssh" in lowered:
            return "encryption"
        if "service" in lowered:
            return "service_security"
        if "line" in lowered:
            return "line_security"
        if "hostname" in lowered:
            return "hostname"
        return "other_security"

    def get_interfaces(self) -> dict[str, list[str]]:
        return self.interfaces

    def get_vlan_configs(self) -> dict[str, dict[str, Any]]:
        return self.vlan_configs

    def get_full_config_text(self) -> str:
        return self.config_text.lower()

    def get_global_context_text(self) -> str:
        """Text used for global-scope policy checks (excludes interface blocks)."""
        interface_starts = tuple(
            re.compile(p, re.IGNORECASE)
            for p in (
                r"^interface\s+",
                r"^interface-port\s+",
            )
        )
        global_lines: list[str] = []
        inside_interface = False

        for raw_line in self.config_text.splitlines():
            stripped = raw_line.strip()
            if any(pattern.search(stripped) for pattern in interface_starts):
                inside_interface = True
                continue
            if stripped == "!":
                inside_interface = False
                continue
            if not inside_interface and stripped:
                global_lines.append(stripped)

        return " ".join(global_lines).lower()

    def get_security_settings(self) -> dict[str, list[str]]:
        return self.security_settings

    def get_security_issues(self) -> list[str]:
        issues: list[str] = []
        for interface_name, config_lines in self.interfaces.items():
            config_text = " ".join(config_lines).lower()
            if "description" not in config_text:
                issues.append(f"Interface {interface_name}: missing description")
            if "transport input telnet" in config_text:
                issues.append(f"Interface {interface_name}: telnet enabled (prefer SSH)")
        return issues
