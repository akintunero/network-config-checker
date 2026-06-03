"""Supported configuration vendors (offline parsers)."""

from __future__ import annotations

import re
from enum import Enum


class ConfigVendor(str, Enum):
    CISCO_IOS = "cisco_ios"
    JUNIPER_SET = "juniper_set"
    UNKNOWN = "unknown"


_JUNIPER_SET = re.compile(r"^\s*set\s+", re.MULTILINE)


def detect_vendor(config_text: str) -> ConfigVendor:
    """
    Best-effort vendor detection for user-facing warnings.

    Only cisco_ios is evaluated by the compliance engine today.
    """
    if _JUNIPER_SET.search(config_text):
        return ConfigVendor.JUNIPER_SET
    if re.search(r"^interface\s+\S+", config_text, re.MULTILINE | re.IGNORECASE):
        return ConfigVendor.CISCO_IOS
    return ConfigVendor.UNKNOWN


def unsupported_vendor_message(vendor: ConfigVendor) -> str | None:
    if vendor == ConfigVendor.CISCO_IOS:
        return None
    if vendor == ConfigVendor.JUNIPER_SET:
        return (
            "Juniper 'set' configuration syntax detected. "
            "Only Cisco IOS-style plain text is supported for compliance checks."
        )
    return (
        "Configuration format not recognized as Cisco IOS-style plain text. "
        "Supported offline input: 'show running-config' style exports. "
        "Not supported: Juniper set, Arista EOS JSON, OpenConfig payloads."
    )
