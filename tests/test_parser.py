import pytest
from src.parser import ConfigParser

@pytest.fixture
def sample_config():
    return """
    interface GigabitEthernet0/1
      description Uplink to Core
      ip address 192.168.1.1 255.255.255.0
    """

def test_parser(sample_config):
    parser = ConfigParser(sample_config)
    parsed_data = parser.get_interfaces()

    assert "GigabitEthernet0/1" in parsed_data
    assert any("ip address 192.168.1.1 255.255.255.0" in line for line in parsed_data["GigabitEthernet0/1"])
