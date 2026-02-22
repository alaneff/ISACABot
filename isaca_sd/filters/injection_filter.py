"""
Regex-based injection pre-filter.

Runs before the LLM safety agent — zero latency, no API cost.
Catches obvious jailbreak / prompt-injection attempts by pattern matching.

This is a first-line defense only. The LLM safety agent (Haiku) provides
deeper semantic analysis for anything that passes here.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Patterns that indicate prompt injection / jailbreak attempts.
# Each tuple is (pattern, human-readable label).
# Patterns are case-insensitive and matched against the full message.
_INJECTION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"ignore\s+(previous|all|your|prior)\s+(instructions?|prompts?|rules?|guidelines?)", re.I), "ignore-instructions"),
    (re.compile(r"(forget|disregard|override)\s+(your\s+)?(instructions?|training|guidelines?|rules?|system\s+prompt)", re.I), "override-instructions"),
    (re.compile(r"you\s+are\s+now\s+(a\s+|an\s+)?(?!a\s+career|an\s+advisor|a\s+helpful)", re.I), "you-are-now"),
    (re.compile(r"pretend\s+(you\s+are|to\s+be|that\s+you)", re.I), "pretend-to-be"),
    (re.compile(r"act\s+as\s+(if\s+you\s+are|a\s+|an\s+)(?!a\s+career|an\s+advisor)", re.I), "act-as"),
    (re.compile(r"new\s+(persona|role|identity|character|mode)", re.I), "new-persona"),
    (re.compile(r"\bDAN\b", re.I), "DAN"),
    (re.compile(r"jailbreak", re.I), "jailbreak"),
    (re.compile(r"developer\s+mode", re.I), "developer-mode"),
    (re.compile(r"do\s+anything\s+now", re.I), "do-anything-now"),
    (re.compile(r"(reveal|show|print|repeat|output)\s+(your\s+)?(system\s+prompt|instructions?|training\s+data|prompt)", re.I), "reveal-prompt"),
    (re.compile(r"(bypass|circumvent|disable)\s+(your\s+)?(safety|filter|restriction|guardrail|limit)", re.I), "bypass-safety"),
]


def check_injection(text: str) -> tuple[bool, str]:
    """
    Check a user message for prompt injection patterns.

    Returns:
        (is_clean, reason)
        is_clean=True  → no injection detected, proceed normally
        is_clean=False → injection pattern matched, should reject
    """
    for pattern, label in _INJECTION_PATTERNS:
        if pattern.search(text):
            logger.warning("Injection pattern matched: %s | message preview: %.80r", label, text)
            return False, f"injection pattern: {label}"

    return True, ""
