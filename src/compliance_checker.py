import yaml

class ComplianceChecker:
    def __init__(self, parsed_config, policies):
        self.parsed_config = parsed_config
        self.policies = self.load_policies(policies)

    def load_policies(self, policies):
        """Loads compliance policies from a YAML file or dictionary."""
        if isinstance(policies, dict):
            return policies
        elif isinstance(policies, str):
            try:
                with open(policies, "r") as file:
                    return yaml.safe_load(file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Policy file not found: {policies}")
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file: {e}")
        else:
            raise ValueError("Policies must be either a dictionary or a file path string.")

    def check_compliance(self):
        """Checks configuration against security policies."""
        results = {}
        for rule, rule_details in self.policies.items():
            results[rule] = self.apply_rule(rule, rule_details)
        return results

    def apply_rule(self, rule, rule_details):
        """Applies a compliance rule to the parsed configuration."""
        for interface, config_lines in self.parsed_config.items():
            for condition in rule_details.get("conditions", []):
                if not any(condition in line for line in config_lines):
                    return f"Non-compliant: {rule} missing in {interface}"
        return "Compliant"
