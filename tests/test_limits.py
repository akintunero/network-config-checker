from pathlib import Path

import pytest

from network_config_checker.limits import ConfigSizeError, enforce_max_bytes
from network_config_checker.parser import ConfigParser

pytestmark = pytest.mark.unit


def test_enforce_max_bytes_raises() -> None:
    with pytest.raises(ConfigSizeError):
        enforce_max_bytes(10_000_000, "huge.cfg", max_bytes=1024)


def test_parser_rejects_oversized_file(tmp_path: Path) -> None:
    big = tmp_path / "big.cfg"
    big.write_text("!\n" * 200_000, encoding="utf-8")
    with pytest.raises(ConfigSizeError):
        ConfigParser(big, max_config_bytes=4096)
