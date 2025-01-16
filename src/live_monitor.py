import time
import schedule
from netmiko import ConnectHandler
from parser import ConfigParser
from compliance_checker import ComplianceChecker
from report_generator import ReportGenerator
from notifier import Notifier


class LiveMonitor:
    def __init__(self, device, policy_file, notifier, report_dir="reports/"):
        self.device = device
        self.policy_file = policy_file
        self.notifier = notifier
        self.report_dir = report_dir

    def fetch_config(self):
        """Fetches live configuration from the network device."""
        try:
            with ConnectHandler(**self.device) as conn:
                config = conn.send_command("show running-config")
            return config
        except Exception as e:
            print(f"Error fetching configuration: {e}")
            return None

    def check_compliance(self):
        """Fetches the config, checks compliance, and generates reports."""
        config_data = self.fetch_config()
        if config_data:
            parser = ConfigParser(config_data)
            checker = ComplianceChecker(parser.get_interfaces(), self.policy_file)
            compliance_results = checker.check_compliance()

            # Generate reports
            report_generator = ReportGenerator(compliance_results)
            report_generator.generate_text_report(f"{self.report_dir}live_compliance_report.txt")
            report_generator.generate_json_report(f"{self.report_dir}live_compliance_report.json")

            # Send notifications if violations exist
            self.notifier.notify(compliance_results)

    def schedule_monitoring(self, interval=10):
        """Schedules periodic compliance checks."""
        schedule.every(interval).minutes.do(self.check_compliance)
        print(f"Live monitoring started... Checking every {interval} minutes.")
        while True:
            schedule.run_pending()
            time.sleep(1)


# Example Usage
if __name__ == "__main__":
    # Define network device credentials
    device = {
        "device_type": "cisco_ios",
        "host": "192.168.1.1",
        "username": "admin",
        "password": "password",
        "secret": "enable_password",
    }

    policy_file = "policies/security_policies.yaml"

    email_config = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender": "your_email@gmail.com",
        "password": "your_email_password",
        "receiver": "recipient_email@gmail.com"
    }

    slack_webhook_url = "https://hooks.slack.com/services/your/webhook/url"

    notifier = Notifier(email_config=email_config, slack_webhook_url=slack_webhook_url)
    monitor = LiveMonitor(device, policy_file, notifier)

    monitor.schedule_monitoring(interval=10)  # Check every 10 minutes
