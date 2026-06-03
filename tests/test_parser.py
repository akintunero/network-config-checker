import pytest

from network_config_checker.parser import ConfigParser

pytestmark = pytest.mark.unit


@pytest.fixture
def sample_config_text() -> str:
    return """
hostname edge-sw-01
!
interface GigabitEthernet0/1
 description Uplink to Core
 ip address 192.168.1.1 255.255.255.0
!
interface GigabitEthernet0/2
 description ISP link
 ip address 10.0.0.1 255.255.255.0
!
"""


def test_parser_extracts_interfaces(sample_config_text: str) -> None:
    parser = ConfigParser(sample_config_text)
    interfaces = parser.get_interfaces()

    assert "GigabitEthernet0/1" in interfaces
    assert any("ip address 192.168.1.1" in line for line in interfaces["GigabitEthernet0/1"])


def test_global_context_includes_hostname(sample_config_text: str) -> None:
    parser = ConfigParser(sample_config_text)
    assert "hostname edge-sw-01" in parser.get_global_context_text()
