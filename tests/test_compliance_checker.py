import pytest
from src.compliance_checker import ComplianceChecker


def test_compliance_checker():
    parsed_config = {
        "GigabitEthernet0/1": ["ip address 192.168.1.1 255.255.255.0"]
    }

    sample_policies = {
        "IP Addressing": {
            "conditions": ["ip address"]
        }
    }

    checker = ComplianceChecker(parsed_config, sample_policies)
    results = checker.check_compliance()

    assert "IP Addressing" in results
    assert results["IP Addressing"] == "Compliant"
