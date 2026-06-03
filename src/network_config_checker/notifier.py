"""Optional notifications for live monitoring (install with [notify] extra)."""

from __future__ import annotations

import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from network_config_checker.models import ComplianceResult, Severity

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(
        self,
        *,
        email_config: dict[str, Any] | None = None,
        slack_webhook_url: str | None = None,
    ) -> None:
        self.email_config = email_config
        self.slack_webhook_url = slack_webhook_url

    def notify_scan_results(self, results: list[ComplianceResult], *, minimum: Severity = Severity.HIGH) -> None:
        lines: list[str] = []
        for result in results:
            for violation in result.violations:
                if violation.severity.value in {minimum.value, Severity.CRITICAL.value}:
                    lines.append(
                        f"{result.config_path} — {violation.rule_id} [{violation.severity.value}] "
                        f"{violation.target}: {violation.message}"
                    )

        if not lines:
            logger.info("No notifications required; no violations at configured severity.")
            return

        message = "Network compliance violations detected:\n" + "\n".join(lines)
        self.send_email("Network compliance alert", message)
        self.send_slack_notification(message)

    def send_email(self, subject: str, message: str) -> None:
        if not self.email_config:
            logger.debug("Email notifications not configured.")
            return

        msg = MIMEMultipart()
        msg["From"] = str(self.email_config["sender"])
        msg["To"] = str(self.email_config["receiver"])
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server_name = str(self.email_config["smtp_server"])
        server_port = int(self.email_config["smtp_port"])
        sender = str(self.email_config["sender"])
        password = str(self.email_config["password"])
        receiver = str(self.email_config["receiver"])

        with smtplib.SMTP(server_name, server_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        logger.info("Email notification sent to %s", receiver)

    def send_slack_notification(self, message: str) -> None:
        if not self.slack_webhook_url:
            logger.debug("Slack notifications not configured.")
            return

        try:
            import requests
        except ImportError as exc:
            raise ImportError("Install the notify extra: pip install 'network-config-checker[notify]'") from exc

        response = requests.post(
            self.slack_webhook_url,
            data=json.dumps({"text": message}),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        logger.info("Slack notification sent.")
