import pytest

from network_config_checker.conditions import match_condition, normalize_config_text

pytestmark = pytest.mark.unit


def test_normalize_collapses_whitespace() -> None:
    assert normalize_config_text("line con 0\n login local") == "line con 0 login local"


def test_phrase_matches_across_lines() -> None:
    text = "no ip http server\nno ip http secure-server"
    assert match_condition(text, "no ip http server")


def test_single_token_word_boundary() -> None:
    assert match_condition("login local", "login")
    assert not match_condition("catalogin local", "login")


def test_forbidden_not_prefix() -> None:
    assert match_condition("transport input ssh", "not:telnet")


def test_substring_prefix_legacy() -> None:
    assert match_condition("foobar", "substring:oba")
