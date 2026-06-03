"""Condition matching for policy evaluation (phrase-aware, not full config engine)."""

from __future__ import annotations

import re


def normalize_config_text(text: str) -> str:
    """Collapse whitespace for consistent phrase matching across line breaks."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def phrase_pattern(condition: str) -> str:
    """
    Build a regex for a policy phrase.

    Single tokens use word boundaries; multi-word phrases allow flexible whitespace.
    """
    tokens = condition.strip().lower().split()
    if not tokens:
        return r"(?!)"
    if len(tokens) == 1:
        return rf"\b{re.escape(tokens[0])}\b"
    return r"\s+".join(re.escape(token) for token in tokens)


def match_condition(text: str, condition: str) -> bool:
    """
    Evaluate a policy condition against configuration text.

    Prefixes:
      regex:     Python regular expression (anchored search in normalized text)
      not:       Phrase must NOT match (same rules as default)
      substring: Loose substring match (legacy / explicit opt-in)
      phrase:    Alias for default matching
    """
    normalized = normalize_config_text(text)
    stripped = condition.strip()

    if stripped.startswith("regex:"):
        pattern = stripped[6:]
        try:
            return bool(re.search(pattern, normalized, re.IGNORECASE))
        except re.error as exc:
            raise ValueError(f"Invalid regex in condition {condition!r}: {exc}") from exc

    if stripped.startswith("substring:"):
        return stripped[10:].lower() in normalized

    if stripped.startswith("not:"):
        inner = stripped[4:].strip()
        if inner.startswith("regex:"):
            pattern = inner[6:]
            return not bool(re.search(pattern, normalized, re.IGNORECASE))
        return not bool(re.search(phrase_pattern(inner), normalized))

    if stripped.startswith("phrase:"):
        stripped = stripped[7:].strip()

    return bool(re.search(phrase_pattern(stripped), normalized))
