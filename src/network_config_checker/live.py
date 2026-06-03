"""Optional live device reads (install with [live] extra). Credentials via environment variables only."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from network_config_checker.compliance import ComplianceEngine
from network_config_checker.notifier import Notifier
from network_config_checker.parser import ConfigParser
from network_config_checker.policy import load_policies, resolve_policy_path
from network_config_checker.reports import ReportWriter

logger = logging.getLogger(__name__)


def device_from_env() -> dict[str, Any]:
    """Build a Netmiko device dict from NETCHECK_* environment variables."""
    host = os.environ.get("NETCHECK_DEVICE_HOST")
    username = os.environ.get("NETCHECK_DEVICE_USERNAME")
    password = os.environ.get("NETCHECK_DEVICE_PASSWORD")
    device_type = os.environ.get("NETCHECK_DEVICE_TYPE", "cisco_ios")
    secret = os.environ.get("NETCHECK_DEVICE_ENABLE_SECRET")

    missing = [
        name
        for name, value in [
            ("NETCHECK_DEVICE_HOST", host),
            ("NETCHECK_DEVICE_USERNAME", username),
            ("NETCHECK_DEVICE_PASSWORD", password),
        ]
        if not value
    ]

    if missing:
        raise ValueError("Missing environment variables for live mode: " + ", ".join(missing))

    device: dict[str, Any] = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
    }
    if secret:
        device["secret"] = secret
    return device


class LiveMonitor:
    def __init__(
        self,
        device: dict[str, Any],
        policy_path: str,
        notifier: Notifier | None = None,
        report_dir: str = "reports",
    ) -> None:
        self.device = device
        self.policy_pack = load_policies(resolve_policy_path(policy_path))
        self.notifier = notifier
        self.report_dir = report_dir

    def fetch_config(self) -> str | None:
        try:
            from netmiko import ConnectHandler
        except ImportError as exc:
            raise ImportError("Install the live extra: pip install 'network-config-checker[live]'") from exc

        with ConnectHandler(**self.device) as connection:
            return str(connection.send_command("show running-config"))

    def check_once(self) -> None:
        config_text = self.fetch_config()
        if not config_text:
            logger.error("No configuration retrieved from %s", self.device.get("host"))
            return

        host = str(self.device.get("host", "device"))
        parser = ConfigParser(config_text, source_label=host)
        engine = ComplianceEngine(parser, self.policy_pack)
        result = engine.check(config_path=host)
        writer = ReportWriter([result])
        writer.write_all(
            __import__("pathlib").Path(self.report_dir),
            ["txt", "json"],
        )
        if self.notifier:
            self.notifier.notify_scan_results([result])

    def schedule(self, interval_minutes: int = 60) -> None:
        try:
            import schedule
        except ImportError as exc:
            raise ImportError("Install the live extra: pip install 'network-config-checker[live]'") from exc

        schedule.every(interval_minutes).minutes.do(self.check_once)
        logger.info("Live monitoring every %s minutes for %s", interval_minutes, self.device.get("host"))
        while True:
            schedule.run_pending()
            time.sleep(1)
