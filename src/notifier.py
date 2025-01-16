import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Notifier:
    def __init__(self, email_config=None, slack_webhook_url=None):
        self.email_config = email_config
        self.slack_webhook_url = slack_webhook_url

    def send_email(self, subject, message):
        """Sends an email notification."""
        if not self.email_config:
            print("Email notifications not configured.")
            return

        msg = MIMEMultipart()
        msg['From'] = self.email_config["sender"]
        msg['To'] = self.email_config["receiver"]
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        try:
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["sender"], self.email_config["password"])
            server.sendmail(self.email_config["sender"], self.email_config["receiver"], msg.as_string())
            server.quit()
            print("Email notification sent successfully.")
        except Exception as e:
            print(f"Error sending email: {e}")

    def send_slack_notification(self, message):
        """Sends a Slack notification."""
        if not self.slack_webhook_url:
            print("Slack notifications not configured.")
            return

        payload = {"text": message}
        try:
            response = requests.post(self.slack_webhook_url, data=json.dumps(payload),
                                     headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                print("Slack notification sent successfully.")
            else:
                print(f"Error sending Slack notification: {response.text}")
        except Exception as e:
            print(f"Error sending Slack notification: {e}")

    def notify(self, compliance_results):
        """Sends notifications if non-compliance is detected."""
        violations = [f"{rule}: {result}" for rule, result in compliance_results.items() if "Non-compliant" in result]
        if violations:
            message = "Compliance Violations Detected:\n" + "\n".join(violations)
            self.send_email("Network Compliance Alert", message)
            self.send_slack_notification(message)
        else:
            print("No violations detected.")


# Example Usage
if __name__ == "__main__":
    email_config = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender": "your_email@gmail.com",
        "password": "your_email_password",
        "receiver": "recipient_email@gmail.com"
    }

    slack_webhook_url = "https://hooks.slack.com/services/your/webhook/url"

    notifier = Notifier(email_config=email_config, slack_webhook_url=slack_webhook_url)

    # Sample compliance results
    sample_results = {
        "Ensure SSH is enabled": "Non-compliant: SSH missing in GigabitEthernet0/1",
        "Disable Telnet access": "Compliant"
    }

    notifier.notify(sample_results)
