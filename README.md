# Network Configuration Compliance Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/akintunero/network-config-checker/actions)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen.svg)](https://github.com/akintunero/network-config-checker/actions)

The **Network Configuration Compliance Checker** is a comprehensive Python-based tool designed to analyze and validate network device configurations against predefined security and operational policies. It ensures compliance with industry best practices and aids in maintaining secure and consistent network environments across multi-vendor infrastructures.

This tool is particularly useful for network administrators, security teams, and IT professionals seeking to automate configuration validation, identify misconfigurations, and ensure policy adherence across diverse network environments.

## 🚀 Key Features

### 🔍 **Advanced Configuration Analysis**
- **Multi-Vendor Support**: Parse configurations from Cisco, Juniper, and other network devices
- **Intelligent Parsing**: Advanced interface detection and configuration parsing
- **Security Analysis**: Built-in security issue detection and reporting
- **Comprehensive Validation**: Check against multiple policy types and severity levels

### 🛡️ **Robust Compliance Engine**
- **Flexible Policy System**: YAML-based policy definitions with regex support
- **Severity Levels**: Critical, High, Medium, and Low severity classifications
- **Detailed Reporting**: Comprehensive compliance scoring and recommendations
- **Real-time Analysis**: Live configuration monitoring capabilities

### 📊 **Professional Reporting**
- **Multiple Formats**: Generate reports in TXT, JSON, HTML, and CSV formats
- **Visual Dashboards**: Beautiful HTML reports with interactive elements
- **Compliance Scoring**: Overall compliance percentage and detailed breakdowns
- **Actionable Insights**: Specific recommendations for policy violations

### 🛠️ **Enterprise-Grade Features**
- **Professional CLI**: Command-line interface with argument parsing and help
- **Comprehensive Logging**: Structured logging with file and console output
- **Error Handling**: Robust error handling and validation
- **Extensible Architecture**: Modular design for easy customization

## 🏗️ Tech Stack

- **Python 3.8+**: Core programming language
- **PyYAML**: YAML configuration parsing
- **Netmiko**: Network device automation
- **NAPALM**: Multi-vendor network automation
- **Pytest**: Comprehensive testing framework
- **Black/Flake8**: Code formatting and linting
- **MyPy**: Type checking and validation

## ⚡ Quick Start

### Prerequisites

- Python 3.8 or higher
- Network device configurations (text format)
- Policy definitions (YAML format)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/akintunero/network-config-checker.git
   cd network-config-checker
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

1. **Define your policies** in `policies/security_policies.yaml`:
   ```yaml
   require_interface_description:
     description: "Ensure all interfaces have descriptions"
     severity: "medium"
     conditions: ["description"]
   
   disable_http_server:
     description: "Disable HTTP server on all interfaces"
     severity: "high"
     required_conditions: ["no ip http server"]
   ```

2. **Prepare your configuration file** (e.g., `config.txt`):
   ```
   interface GigabitEthernet0/1
     description Uplink to Core
     ip address 192.168.1.1 255.255.255.0
     no ip http server
   ```

3. **Run the compliance check**:
   ```bash
   python src/main.py -c config.txt -p policies/security_policies.yaml -o reports --verbose
   ```

4. **View results** in the `reports/` directory:
   - `compliance_report.txt` - Human-readable text report
   - `compliance_report.json` - Machine-readable JSON data
   - `compliance_report.html` - Interactive HTML dashboard
   - `compliance_report.csv` - Spreadsheet-compatible data

## 📖 Documentation

### Configuration

The tool supports various configuration options:

```bash
python src/main.py -c <config_file> -p <policy_file> [options]

Options:
  -c, --config     Path to network configuration file
  -p, --policy     Path to policy file (YAML format)
  -o, --output     Output directory for reports (default: reports)
  -v, --verbose    Enable verbose logging
  -h, --help       Show help message
```

### Policy Format

Policies are defined in YAML format with the following structure:

```yaml
rule_name:
  description: "Human-readable description"
  severity: "critical|high|medium|low"
  conditions: ["condition1", "condition2"]           # Optional
  required_conditions: ["required1", "required2"]    # Optional
  forbidden_conditions: ["forbidden1", "forbidden2"] # Optional
```

### Advanced Features

#### Regex Support
```yaml
complex_rule:
  description: "Check for specific IP patterns"
  conditions: ["regex:ip address 192\.168\.\d+\.\d+"]
```

#### Negative Conditions
```yaml
security_rule:
  description: "Ensure HTTP server is disabled"
  required_conditions: ["not:ip http server"]
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test categories
python -m pytest tests/ -m "unit"     # Unit tests only
python -m pytest tests/ -m "integration"  # Integration tests only
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/akintunero/network-config-checker.git
cd network-config-checker
make setup-dev
make install-dev

# Run code quality checks
make lint
make format
make type-check
make security

# Run all checks
make check-all
```

### Project Structure

```
network-config-checker/
├── src/                    # Source code
│   ├── main.py            # Main entry point with CLI
│   ├── parser.py          # Configuration parser
│   ├── compliance_checker.py  # Compliance checking engine
│   ├── report_generator.py    # Report generation
│   └── live_monitor.py    # Live device monitoring
├── tests/                  # Test suite
├── config_samples/         # Sample configurations
├── policies/              # Policy definitions
├── reports/               # Generated reports
├── docs/                  # Documentation
└── examples/              # Usage examples
```

## 📊 Recent Improvements

### v2.0.0 - Major Release (2025-07-27)
- ✅ **Complete Architecture Overhaul**: Transformed from simple scripts to robust class-based system
- ✅ **Professional CLI Interface**: Command-line arguments, help system, and verbose logging
- ✅ **Multi-Format Reporting**: TXT, JSON, HTML, and CSV report generation
- ✅ **Advanced Policy Engine**: Regex support, severity levels, and detailed analysis
- ✅ **Comprehensive Testing**: 80%+ test coverage with mocking and fixtures
- ✅ **Code Quality**: Type hints, docstrings, and consistent formatting
- ✅ **Open-Source Ready**: Complete documentation and community guidelines

### Key Enhancements
- **Enhanced Error Handling**: Comprehensive validation and meaningful error messages
- **Multi-Vendor Support**: Improved parsing for Cisco, Juniper, and other devices
- **Security Analysis**: Built-in security issue detection and reporting
- **Compliance Scoring**: Overall compliance percentage and detailed breakdowns
- **Professional Logging**: Structured logging with file and console output

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check the [README](README.md) and [docs/](docs/) directory
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/akintunero/network-config-checker/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/akintunero/network-config-checker/discussions)

### Community
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- **Code of Conduct**: Read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Changelog**: Track changes in [CHANGELOG.md](CHANGELOG.md)

---

## 👨‍💻 Author

**Olúmáyòwá Akinkuehinmi** - [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

- GitHub: [@akintunero](https://github.com/akintunero)
- LinkedIn: [Olúmáyòwá Akinkuehinmi](https://linkedin.com/in/akintunero)
- Twitter: [@akintunero](https://twitter.com/akintunero)

## 🤝 Support the Project

If you find this project helpful, please consider:

- ⭐ **Starring** the repository
- 🐛 **Reporting** bugs and issues
- 💡 **Suggesting** new features
- 📝 **Contributing** code improvements
- 📢 **Sharing** with your network

---

**Built with ❤️ by Olúmáyòwá Akinkuehinmi for the network engineering community**

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
