"""Resource limits for offline scanning."""

from __future__ import annotations

# Default 5 MiB per configuration file (CI-safe)
DEFAULT_MAX_CONFIG_BYTES = 5 * 1024 * 1024


class ConfigSizeError(ValueError):
    """Raised when a configuration file exceeds the allowed size."""


def enforce_max_bytes(size: int, path: str, *, max_bytes: int = DEFAULT_MAX_CONFIG_BYTES) -> None:
    if size > max_bytes:
        mib = max_bytes / (1024 * 1024)
        actual_mib = size / (1024 * 1024)
        raise ConfigSizeError(
            f"Configuration {path} is {actual_mib:.1f} MiB; maximum allowed is {mib:.1f} MiB. "
            "Split large exports or raise the limit only for trusted local runs."
        )
