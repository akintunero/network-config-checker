from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CONFIG = REPO_ROOT / "configs" / "production" / "edge-sw-01.cfg"
NONCOMPLIANT_CONFIG = REPO_ROOT / "config_samples" / "noncompliant_config.txt"
BUILTIN_POLICY = "builtin/cisco_ios_baseline"


@pytest.fixture
def sample_config_path() -> Path:
    return SAMPLE_CONFIG


@pytest.fixture
def builtin_policy() -> str:
    return BUILTIN_POLICY


@pytest.fixture
def noncompliant_config_path() -> Path:
    return NONCOMPLIANT_CONFIG
