import sys
from unittest.mock import MagicMock, patch

import pytest

from network_config_checker.live import LiveMonitor, device_from_env
from network_config_checker.models import ComplianceResult, Severity, Violation, PolicyScope
from network_config_checker.notifier import Notifier

pytestmark = pytest.mark.unit


def test_device_from_env_requires_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NETCHECK_DEVICE_HOST", raising=False)
    with pytest.raises(ValueError, match="NETCHECK_DEVICE_HOST"):
        device_from_env()


def test_device_from_env_builds_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NETCHECK_DEVICE_HOST", "203.0.113.10")
    monkeypatch.setenv("NETCHECK_DEVICE_USERNAME", "netops")
    monkeypatch.setenv("NETCHECK_DEVICE_PASSWORD", "secret-from-vault")
    device = device_from_env()
    assert device["host"] == "203.0.113.10"
    assert device["username"] == "netops"


def test_live_monitor_fetch_config(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_netmiko = MagicMock()
    connection = MagicMock()
    connection.send_command.return_value = "hostname test\n!"
    mock_netmiko.ConnectHandler.return_value.__enter__.return_value = connection
    monkeypatch.setitem(sys.modules, "netmiko", mock_netmiko)

    monitor = LiveMonitor(
        {"device_type": "cisco_ios", "host": "203.0.113.10", "username": "u", "password": "p"},
        "builtin/cisco_ios_baseline",
    )
    config = monitor.fetch_config()
    assert config is not None
    assert "hostname test" in config


def test_notifier_skips_when_no_violations_at_severity() -> None:
    notifier = Notifier(email_config={"sender": "a@b.com"})
    result = ComplianceResult(
        config_path="x",
        config_sha256="abc",
        policy_pack_name="p",
        policy_pack_version="1",
        summary={},
        detailed_results={},
        violations=[],
        recommendations=[],
    )
    with patch.object(notifier, "send_email") as mock_email:
        notifier.notify_scan_results([result], minimum=Severity.HIGH)
        mock_email.assert_not_called()


@patch("network_config_checker.notifier.smtplib.SMTP")
def test_notifier_send_email(mock_smtp: MagicMock) -> None:
    server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = server
    notifier = Notifier(
        email_config={
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "sender": "alerts@example.com",
            "password": "vault-token",
            "receiver": "netops@example.com",
        }
    )
    violation = Violation(
        rule_key="forbid_telnet",
        rule_id="NCC-FORBID_TELNET",
        severity=Severity.CRITICAL,
        scope=PolicyScope.GLOBAL,
        target="global",
        message="telnet enabled",
        remediation="transport input ssh",
        references=(),
    )
    result = ComplianceResult(
        config_path="edge-sw-01",
        config_sha256="abc",
        policy_pack_name="p",
        policy_pack_version="1",
        summary={},
        detailed_results={},
        violations=[violation],
        recommendations=[],
    )
    notifier.notify_scan_results([result], minimum=Severity.HIGH)
    server.sendmail.assert_called_once()
