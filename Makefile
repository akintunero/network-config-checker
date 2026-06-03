.PHONY: help install install-dev test lint format check run scan scan-configs docker-build clean

help:
	@echo "network-config-checker — Offline compliance scanner for network configs in Git"
	@echo ""
	@echo "  install      Install package (production)"
	@echo "  install-dev  Install package with dev dependencies"
	@echo "  test         Run pytest with coverage"
	@echo "  lint         Run ruff"
	@echo "  format       Format with ruff"
	@echo "  check        lint + test"
	@echo "  scan         Scan compliant config from configs/"
	@echo "  scan-configs Scan configs/ with all builtin policy packs"
	@echo "  scan-fail    Scan noncompliant sample (expect exit 1)"
	@echo "  docker-build Build container image"
	@echo "  clean        Remove build artifacts"

install:
	python3 -m pip install -e .

install-dev:
	python3 -m pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=network_config_checker --cov-report=term-missing

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

check: lint test

scan:
	network-config-checker scan \
		-c configs/production/edge-sw-01.cfg \
		-p policies/builtin \
		-o reports \
		--format txt,json,html,csv,sarif,junit \
		--verbose

scan-configs:
	network-config-checker validate-policies -p policies/builtin
	network-config-checker scan \
		-c configs \
		-p policies/builtin \
		-o reports/configs \
		--format txt,json,html,sarif,junit \
		--fail-on high \
		--write-baseline-to reports/configs/baseline-summary.json

scan-fail:
	network-config-checker scan \
		-c config_samples/noncompliant_config.txt \
		-p builtin/cisco_ios_baseline \
		-o reports \
		--fail-on high

docker-build:
	docker build -t network-config-checker:2.1.0 .

clean:
	rm -rf build dist .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find reports -mindepth 1 ! -name '.gitkeep' -delete 2>/dev/null || true
