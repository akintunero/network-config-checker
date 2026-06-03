from pathlib import Path

import pytest
import yaml

from network_config_checker.policy import PolicyValidationError, load_policy_file, validate_document_schema

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_builtin_packs_pass_json_schema() -> None:
    for pack_file in (REPO_ROOT / "policies" / "builtin").glob("*.yaml"):
        load_policy_file(pack_file)


def test_invalid_schema_rejected(tmp_path: Path) -> None:
    bad = {
        "policy_pack_name": "bad",
        "rules": {
            "x": {
                "description": "missing severity and scope",
                "conditions": ["hostname"],
            }
        },
    }
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.dump(bad), encoding="utf-8")
    with pytest.raises(PolicyValidationError, match="schema validation failed"):
        load_policy_file(path)


def test_validate_document_schema_direct() -> None:
    data = yaml.safe_load((REPO_ROOT / "policies" / "builtin" / "cisco_ios_baseline.yaml").read_text())
    validate_document_schema(data, REPO_ROOT / "policies" / "builtin" / "cisco_ios_baseline.yaml")
