import json

class ReportGenerator:
    def __init__(self, compliance_results):
        self.compliance_results = compliance_results

    def generate_text_report(self, output_file):
        """Generates a plain text report."""
        with open(output_file, "w") as file:
            for rule, result in self.compliance_results.items():
                file.write(f"{rule}: {result}\n")
        print(f"Text report saved to {output_file}")

    def generate_json_report(self, output_file):
        """Generates a JSON report."""
        with open(output_file, "w") as file:
            json.dump(self.compliance_results, file, indent=4)
        print(f"JSON report saved to {output_file}")
