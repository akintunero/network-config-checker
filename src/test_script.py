from parser import ConfigParser
from compliance_checker import ComplianceChecker
from report_generator import ReportGenerator

sample_config = """
interface GigabitEthernet0/1
  description Uplink to Core
  ip address 192.168.1.1 255.255.255.0
  no ip http server
"""

policy_file = "policies/security_policies.yaml"

parser = ConfigParser(sample_config)
checker = ComplianceChecker(parser.get_interfaces(), policy_file)
compliance_results = checker.check_compliance()

# Generate Reports
report_generator = ReportGenerator(compliance_results)
report_generator.generate_text_report("reports/compliance_report.txt")
report_generator.generate_json_report("reports/compliance_report.json")
