import pytest

from network_config_checker.parser import ConfigParser
from network_config_checker.vendor import ConfigVendor, detect_vendor, unsupported_vendor_message

pytestmark = pytest.mark.unit


def test_detect_cisco_ios() -> None:
    text = "hostname sw1\ninterface GigabitEthernet0/1\n description uplink\n"
    assert detect_vendor(text) == ConfigVendor.CISCO_IOS


def test_detect_juniper_set() -> None:
    text = "set system host-name lab-sw\nset interfaces ge-0/0/0 unit 0 family inet\n"
    assert detect_vendor(text) == ConfigVendor.JUNIPER_SET


def test_parser_warns_on_juniper() -> None:
    parser = ConfigParser("set system host-name lab\n")
    assert parser.vendor_warning is not None
    assert "Juniper" in parser.vendor_warning


def test_unsupported_message_for_juniper() -> None:
    msg = unsupported_vendor_message(ConfigVendor.JUNIPER_SET)
    assert msg is not None
    assert "cisco_ios" in msg.lower() or "Cisco" in msg
