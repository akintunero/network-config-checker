# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- JSON Schema enforcement at policy load (`jsonschema`)
- Phrase-aware condition matching (`conditions.py`) and `docs/SCOPE.md`
- Config file size limit (5 MiB default, `--max-config-mib`)
- Vendor detection warnings (Juniper `set` vs Cisco IOS)
- Policy deprecation fields: `deprecated`, `replaced_by` + `docs/POLICY_MIGRATION.md`
- Release workflow (wheel, SBOM, GitHub Release) + `docs/RELEASE.md`
- Mypy gate in CI; expanded tests (live, notifier, schema, limits, vendor)
- `config_samples/sample_config.txt` aligned with hardened `configs/` devices

### Changed
- SARIF upload uses `continue-on-error` when Code Scanning is unavailable
- GitHub Action supports optional `version` input for tagged installs
- CI sample scan uses `policies/builtin` (all packs)

### Added (prior unreleased)
- Second builtin pack: `cisco_ios_management_hardening` (enable secret, console, logging, NTP, SNMP)
- Git-tracked `configs/` tree (`production/`, `lab/`, `inventory.csv`)
- Dedicated workflow `.github/workflows/config-compliance.yml` for `configs/**` changes

## [2.1.0] - 2025-06-03

### Added
- **Offline-first product focus:** headline *Offline compliance scanner for network configs in Git*
- Proper Python package `network_config_checker` with `pip install -e .`
- Subcommands: `scan`, `validate-policies`, `policy explain`, `write-baseline`
- Policy scopes: `global`, `interface`, `vlan`
- Builtin pack `cisco_ios_baseline` with CIS-aligned rules and remediation text
- Reports: SARIF, JUnit XML, HTML (escaped), CSV, JSON, TXT
- Fleet scans: directory glob and CSV inventory
- Baseline/regression comparison (`--baseline`, `write-baseline`)
- GitHub Actions workflow, composite `action.yml`, Dockerfile
- Documentation: policy authoring, tutorials, compatibility, security
- Optional extras: `[live]`, `[notify]`, `[dev]`

### Changed
- Python minimum version raised to **3.11**
- Removed duplicate `setup.py` and legacy `src/*.py` module layout
- Core dependencies reduced to PyYAML; Netmiko/NAPALM moved to optional extras

### Removed
- Unused NAPALM dependency from core install path
- Placeholder credentials from live monitoring examples (environment variables only)

## [2.0.0] - 2025-07-27 (historical)

### Added
- Enhanced CLI interface with argument parsing
- Comprehensive logging system
- Multi-format report generation (TXT, JSON, HTML, CSV)
- Advanced policy checking with regex support
- Detailed compliance scoring and recommendations
- Comprehensive unit test suite
- Open-source documentation and guidelines

### Changed
- Refactored main application to class-based architecture
- Improved error handling and validation
- Enhanced configuration parsing with multi-vendor support
- Updated compliance checking with detailed reporting

### Fixed
- Fixed import issues and module dependencies
- Improved file handling and encoding
- Enhanced error messages and debugging

## [2.0.0] - 2025-07-27

### Added
- **Major Refactor**: Complete rewrite of the application architecture
- **Enhanced CLI**: Professional command-line interface with argument parsing
- **Comprehensive Logging**: Structured logging with file and console output
- **Multi-Format Reports**: Support for TXT, JSON, HTML, and CSV report formats
- **Advanced Policy Engine**: Enhanced policy checking with regex patterns and severity levels
- **Detailed Compliance Analysis**: Comprehensive compliance scoring and recommendations
- **Multi-Vendor Support**: Improved parsing for Cisco, Juniper, and other vendors
- **Security Analysis**: Built-in security issue detection and reporting
- **Comprehensive Testing**: Full unit test suite with 80%+ coverage
- **Open-Source Ready**: Complete documentation and community guidelines

### Changed
- **Architecture**: Transformed from simple scripts to robust class-based system
- **Error Handling**: Implemented comprehensive error handling and validation
- **Configuration Parsing**: Enhanced parser with better interface detection
- **Policy System**: Improved policy definition and checking capabilities
- **Report Generation**: Complete rewrite of reporting system with multiple formats

### Fixed
- **Import Issues**: Resolved module import and dependency problems
- **File Handling**: Fixed encoding and file path issues
- **Error Messages**: Improved error reporting and debugging information
- **Code Quality**: Applied consistent formatting and style guidelines

### Technical Improvements
- **Type Hints**: Added comprehensive type annotations
- **Documentation**: Complete docstring coverage for all functions
- **Code Style**: Applied PEP 8 guidelines with custom modifications
- **Testing**: Comprehensive test suite with mocking and fixtures
- **Dependencies**: Updated and organized requirements files

## [1.0.0] - 2025-01-15

### Added
- Initial release of Network Configuration Compliance Checker
- Basic configuration parsing for network devices
- Simple policy checking against YAML-defined rules
- Text and JSON report generation
- Support for Cisco device configurations
- Basic CLI interface
- Sample configuration files and policies

### Features
- Parse network device configurations
- Check compliance against security policies
- Generate basic compliance reports
- Support for multiple interface types
- Basic error handling

---

## Version History

### v2.0.0 (Current)
- **Major Release**: Complete rewrite and enhancement
- **Production Ready**: Enterprise-grade features and reliability
- **Open Source**: Full community documentation and guidelines

### v1.0.0 (Initial)
- **Initial Release**: Basic functionality and features
- **Proof of Concept**: Core compliance checking capabilities
- **Foundation**: Basic architecture and components

## Migration Guide

### From v1.0.0 to v2.0.0

#### Breaking Changes
- **CLI Interface**: Command-line arguments have changed
  - Old: `python src/main.py`
  - New: `python src/main.py -c config.txt -p policies.yaml`

- **Policy Format**: Enhanced policy structure
  ```yaml
  # Old format
  rule_name:
    conditions: ["condition1", "condition2"]
  
  # New format
  rule_name:
    description: "Rule description"
    severity: "medium"
    conditions: ["condition1", "condition2"]
    required_conditions: ["required_condition"]
    forbidden_conditions: ["forbidden_condition"]
  ```

- **Report Output**: Reports are now generated in multiple formats
  - Old: Single text/JSON report
  - New: TXT, JSON, HTML, and CSV formats

#### New Features
- **Enhanced CLI**: Use `-h` for help and `--verbose` for detailed logging
- **Multiple Reports**: All report formats are generated by default
- **Compliance Scoring**: Get overall compliance percentage
- **Security Analysis**: Automatic security issue detection

#### Configuration Updates
- **Logging**: Logs are now saved to `reports/checker.log`
- **Output Directory**: Reports are organized in the specified output directory
- **Error Handling**: Better error messages and validation

---

## Contributing

To contribute to this changelog, please follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format and add your changes under the appropriate section.

## Contact

For questions about releases or the project:

- **Maintainer**: Olúmáyòwá Akinkuehinmi
- **Email**: [akintunero101@gmail.com](mailto:akintunero101@gmail.com)
- **GitHub**: [@akintunero](https://github.com/akintunero) 