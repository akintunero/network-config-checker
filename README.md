# Network Configuration Compliance Checker

The **Network Configuration Compliance Checker** is a Python-based tool designed to analyze and validate network device configurations against predefined security and operational policies. It ensures compliance with industry best practices and aids in maintaining secure and consistent network environments.

This tool is particularly useful for network administrators and IT teams seeking to automate configuration validation, identify misconfigurations, and ensure policy adherence across multi-vendor environments.

---

## Features

- Parse and validate router/switch configurations against YAML-defined policies.
- Supports multi-vendor environments, including Cisco, Juniper, and others.
- Generates detailed compliance reports in both text and JSON formats.
- Extendable with custom policies for diverse use cases.
- Future support for:
    - Real-time configuration monitoring.
    - Notifications via email or Slack.
    - A web interface for managing configurations and reports.

---

## Installation

### Prerequisites

- Python 3.8 or higher.
- Network device configurations saved in plain text format.
- Policies defined in YAML files.

### Clone the Repository

```
git clone https://github.com/akintunero/network-config-checker.git
cd network-config-checker
```

Create a Virtual Environment (Recommended)
```
python -m venv venv

source venv/bin/activate  # For macOS/Linux

venv\Scripts\activate     # For Windows
```

Install Required Libraries

The following Python libraries are required:

    pyyaml
    netmiko
    napalm
    schedule

Install all dependencies using:

```
pip install -r requirements.txt
```

### Usage
1. Define Your Policies

Create a YAML file containing your security and operational policies. Example:

```
require_interface_description:
  description: "Ensure all interfaces have descriptions."
  conditions:
    - "description"

require_ip_address:
  description: "Ensure all interfaces have an IP address."
  conditions:
    - "ip address"
```

- Save this file in the policies/ directory, e.g., policies/security_policies.yaml

2. Prepare Configuration Files

Save your router or switch configuration in text format. Example:
```
interface GigabitEthernet0/1
  description Uplink to Core
  ip address 192.168.1.1 255.255.255.0
```

- Place the configuration files in the config_samples/ directory.

3. Run the Compliance Checker

To analyze a configuration file against your policies, use the Command Line Interface (CLI):

```
python src/main.py --config config_samples/sample_config.txt --policy policies/security_policies.yaml
```

Output Example

- Text Report: reports/compliance_report.txt
- JSON Report: reports/compliance_report.json

### Advanced Usage with Network Devices
Fetch Configuration from a Cisco Router:
```
python src/live_monitor.py --device cisco_router --ip 192.168.1.1 --username admin --password secret
```

Fetch Configuration from a Juniper Switch:
```
python src/live_monitor.py --device juniper_switch --ip 192.168.2.1 --username admin --password secret
```

### Testing
Unit tests are available to validate the tool's functionality. Run the following command:
```
pytest tests/
```

### Configuration File Format

- Each configuration file should follow the plain text format typical for router/switch configurations.
- Ensure configurations are compatible with the device vendor's standards.

Example:
```
interface GigabitEthernet0/2
  description Connection to ISP
  ip address 10.0.0.1 255.255.255.0
```

### Policy File Structure

Policies are defined in YAML format and specify conditions to validate configurations.

- Each policy must have:
    - A unique identifier as the key.
    - A description of the policy.
    -  A list of conditions to validate.

Example:
```
require_vlan_configuration:
  description: "Ensure VLANs are configured properly."
  conditions:
    - "vlan"
    - "name"
```

### Error Handling

The tool provides error messages for:

- Missing or invalid configuration files.
- Malformed policy files.
- Unrecognized commands or parameters.

Ensure all files follow the specified formats to avoid errors.
Security Considerations

- Avoid hardcoding sensitive credentials (e.g., passwords) in scripts or files.
- Use encrypted storage or environment variables for sensitive information.
- Restrict access to the tool and configuration files to authorized users only.

### Troubleshooting
Common Issues

- Missing Dependencies: Ensure all required libraries are installed using:
    ```
        pip install -r requirements.txt
    ```
- File Not Found: Verify the paths to configuration and policy files.
- Invalid Policy Format: Ensure your YAML policies are correctly structured.

### Future Improvements

- Real-Time Monitoring: Continuously fetch and validate configurations.
- Notification System: Alert users of policy violations via email or Slack.
- Web Interface: Provide a dashboard for uploading files, viewing reports, and monitoring compliance.

### Compatibility

The tool supports configurations from:

- Cisco routers and switches.
- Juniper switches.
- Additional vendors can be supported by extending the tool's parsing logic.

### Contributing

Contributions are welcome! To contribute by submitting a pull request

### License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
