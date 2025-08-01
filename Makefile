# Makefile for Network Configuration Compliance Checker
# Provides common development tasks and shortcuts

.PHONY: help install install-dev test test-cov test-fast lint format type-check security clean docs build check-all run docker-build docker-run ci-install ci-test ci-lint ci-security setup-dev quick-test pre-commit release-check docker-clean logs db-migrate db-seed

# Default target
help:
	@echo "Network Configuration Compliance Checker - Development Commands"
	@echo "=============================================================="
	@echo ""
	@echo "Installation:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  setup-dev      Complete development environment setup"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run all tests"
	@echo "  test-cov       Run tests with coverage report"
	@echo "  test-fast      Run tests without coverage (faster)"
	@echo "  quick-test     Run a quick subset of tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code with black and isort"
	@echo "  type-check     Run type checking with mypy"
	@echo "  security       Run security checks"
	@echo "  pre-commit     Run pre-commit hooks"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci-install     Install dependencies for CI"
	@echo "  ci-test        Run tests for CI"
	@echo "  ci-lint        Run linting for CI"
	@echo "  ci-security    Run security checks for CI"
	@echo ""
	@echo "Documentation:"
	@echo "  docs           Build documentation"
	@echo ""
	@echo "Building:"
	@echo "  build          Build the package"
	@echo "  release-check  Check if ready for release"
	@echo ""
	@echo "Running:"
	@echo "  run            Run the application with sample data"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run Docker container"
	@echo "  docker-clean   Clean Docker images and containers"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          Clean build artifacts and cache"
	@echo "  logs           Show recent logs"
	@echo "  check-all      Run all checks (test, lint, type-check, security)"

# Installation
install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup-dev:
	@echo "Setting up development environment..."
	python3 -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  # On macOS/Linux"
	@echo "  venv\\Scripts\\activate     # On Windows"
	@echo ""
	@echo "Then run: make install-dev"

# Testing
test:
	@echo "Running all tests..."
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-cov:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

test-fast:
	@echo "Running tests (fast mode)..."
	python -m pytest tests/ -v

quick-test:
	@echo "Running quick tests..."
	python -m pytest tests/ -v -k "not slow" --tb=short

# Code Quality
lint:
	@echo "Running linting checks..."
	flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503
	black --check src/ tests/ --line-length=120
	isort --check-only src/ tests/

format:
	@echo "Formatting code..."
	black src/ tests/ --line-length=120
	isort src/ tests/

type-check:
	@echo "Running type checks..."
	mypy src/ --ignore-missing-imports

security:
	@echo "Running security checks..."
	bandit -r src/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	@echo "Security reports generated: bandit-report.json, safety-report.json"

pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

# CI/CD
ci-install:
	@echo "Installing dependencies for CI..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

ci-test:
	@echo "Running tests for CI..."
	python -m pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing

ci-lint:
	@echo "Running linting for CI..."
	flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503
	black --check src/ tests/ --line-length=120
	isort --check-only src/ tests/

ci-security:
	@echo "Running security checks for CI..."
	bandit -r src/ -f json -o bandit-report.json
	safety check --json --output safety-report.json

# Documentation
docs:
	@echo "Building documentation..."
	cd docs && make html
	@echo "Documentation built in docs/_build/html/"

# Building
build:
	@echo "Building package..."
	python -m build

release-check:
	@echo "Checking release readiness..."
	@echo "Running all checks..."
	$(MAKE) test-cov
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	@echo "Release check completed!"

# Running
run:
	@echo "Running Network Configuration Compliance Checker..."
	@echo "Using sample configuration and policies..."
	python src/main.py -c config_samples/sample_config.txt -p policies/security_policies.yaml -o reports --verbose

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t network-config-checker .

docker-run:
	@echo "Running Docker container..."
	docker run -it --rm network-config-checker

docker-clean:
	@echo "Cleaning Docker images and containers..."
	docker system prune -f
	docker image prune -f

# Utilities
clean:
	@echo "Cleaning build artifacts and cache..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	@echo "Clean completed!"

logs:
	@echo "Showing recent logs..."
	@if [ -f reports/checker.log ]; then tail -n 50 reports/checker.log; else echo "No log file found."; fi

check-all:
	@echo "Running all checks..."
	$(MAKE) test-cov
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	@echo "All checks completed!"

# Database operations (placeholder for future use)
db-migrate:
	@echo "Database migration not implemented yet"

db-seed:
	@echo "Database seeding not implemented yet" 