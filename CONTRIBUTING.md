# Contributing to Network Configuration Compliance Checker

Thank you for your interest in contributing to the Network Configuration Compliance Checker! 🚀

This document provides guidelines and information for contributors to help make the contribution process smooth and effective.

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Adding New Features](#adding-new-features)
- [Bug Fixes](#bug-fixes)
- [Code Review Process](#code-review-process)
- [Release Process](#release-process)
- [Communication](#communication)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

## How to Contribute

There are many ways to contribute to this project:

### 🐛 **Bug Reports**
- Report bugs and issues you encounter
- Provide detailed reproduction steps
- Include configuration files and error messages

### 💡 **Feature Requests**
- Suggest new features and improvements
- Discuss implementation approaches
- Help prioritize features

### 📝 **Documentation**
- Improve existing documentation
- Add examples and tutorials
- Fix typos and clarify instructions

### 🔧 **Code Contributions**
- Fix bugs and implement features
- Improve code quality and performance
- Add tests and improve test coverage

### 🧪 **Testing**
- Test the tool with different configurations
- Report edge cases and compatibility issues
- Help improve test coverage

## Development Guidelines

### Code Style

We follow PEP 8 style guidelines with some modifications:

- **Line length**: 120 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Naming conventions**: 
  - Classes: `PascalCase`
  - Functions and variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Code Quality

- **Type hints**: Use type hints for all function parameters and return values
- **Docstrings**: Include comprehensive docstrings for all public functions and classes
- **Error handling**: Implement proper error handling with meaningful error messages
- **Logging**: Use appropriate logging levels and messages

### Testing

- **Unit tests**: Write unit tests for all new functionality
- **Integration tests**: Test the complete workflow
- **Test coverage**: Aim for at least 80% test coverage
- **Test naming**: Use descriptive test names that explain what is being tested

### Code Formatting

We use automated tools to maintain consistent code formatting:

```bash
# Format code with black
black src/ tests/ --line-length=120

# Sort imports with isort
isort src/ tests/

# Check code style with flake8
flake8 src/ tests/ --max-line-length=120
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

### Examples
```bash
feat: add support for Juniper device configurations
fix: resolve parsing error in interface detection
docs: update README with installation instructions
test: add unit tests for compliance checker
refactor: improve error handling in config parser
```

## Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the development guidelines
3. **Write tests** for new functionality
4. **Update documentation** if needed
5. **Run the test suite** to ensure everything works
6. **Submit a pull request** with a clear description

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] No new warnings generated
- [ ] Tests added that prove the fix is effective or feature works
```

## Issue Reporting

When reporting issues, please include:

1. **Environment information**:
   - Operating system and version
   - Python version
   - Tool version

2. **Steps to reproduce**:
   - Clear, step-by-step instructions
   - Sample configuration files
   - Expected vs actual behavior

3. **Error messages**:
   - Full error traceback
   - Log files if available

4. **Additional context**:
   - Any relevant configuration details
   - Workarounds you've tried

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

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
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

## Project Structure

```
network-config-checker/
├── src/                    # Source code
│   ├── main.py            # Main entry point
│   ├── parser.py          # Configuration parser
│   ├── compliance_checker.py  # Compliance checking logic
│   ├── report_generator.py    # Report generation
│   └── live_monitor.py    # Live device monitoring
├── tests/                  # Test files
├── config_samples/         # Sample configuration files
├── policies/              # Policy definitions
├── reports/               # Generated reports
├── docs/                  # Documentation
└── examples/              # Usage examples
```

## Adding New Features

### 1. **Plan the Feature**
- Create an issue describing the feature
- Discuss implementation approach
- Define acceptance criteria

### 2. **Implement the Feature**
- Create a feature branch
- Implement the functionality
- Add comprehensive tests
- Update documentation

### 3. **Test Thoroughly**
- Run unit tests
- Test with different configurations
- Verify edge cases
- Check performance impact

### 4. **Submit for Review**
- Create a pull request
- Provide clear description
- Include test results
- Address review feedback

## Bug Fixes

### 1. **Reproduce the Bug**
- Create a minimal test case
- Document the exact steps
- Identify the root cause

### 2. **Fix the Bug**
- Implement the fix
- Add regression tests
- Verify the fix works

### 3. **Test the Fix**
- Run existing tests
- Test the specific bug scenario
- Check for side effects

## Code Review Process

### Review Guidelines
- **Be constructive**: Provide helpful, specific feedback
- **Focus on code**: Review the code, not the person
- **Ask questions**: If something is unclear, ask for clarification
- **Suggest improvements**: Offer specific suggestions for improvement

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Functionality is correct
- [ ] Error handling is appropriate
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] Performance is acceptable
- [ ] Security considerations are addressed

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Release Steps
1. **Update version** in relevant files
2. **Update changelog** with new features and fixes
3. **Create release branch** for final testing
4. **Run full test suite** and manual testing
5. **Create release tag** and GitHub release
6. **Update documentation** if needed

## Communication

### Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code review and collaboration

### Guidelines
- **Be respectful**: Treat others with respect and kindness
- **Be patient**: Contributors may have different time zones and schedules
- **Be helpful**: Help others learn and contribute effectively
- **Be clear**: Use clear, concise language in communications

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

### Reporting Issues
If you experience or witness unacceptable behavior, please report it to:
- **Email**: [akintunero101@gmail.com](mailto:akintunero101@gmail.com)
- **GitHub Issues**: [Create an issue](https://github.com/akintunero/network-config-checker/issues)

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

## Contact

For questions about contributing or the project in general:

- **Email**: [akintunero101@gmail.com](mailto:akintunero101@gmail.com)
- **GitHub Issues**: [Create an issue](https://github.com/akintunero/network-config-checker/issues)
- **GitHub Discussions**: [Start a discussion](https://github.com/akintunero/network-config-checker/discussions)

## Acknowledgments

Thank you to all contributors who help make Network Configuration Compliance Checker better!

---

Thank you for contributing to Network Configuration Compliance Checker! 🚀

**Maintainer**: Olúmáyòwá Akinkuehinmi - [akintunero101@gmail.com](mailto:akintunero101@gmail.com) 