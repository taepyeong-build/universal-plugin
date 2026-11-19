"""Deterministic safety guardrail policy for shell execution."""

from __future__ import annotations

import re
from typing import List, Tuple

from ..normalizer import CanonicalEvent, PolicyDecision

DENY_PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(^|[;&|\s])rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(/($|\s)|/\*|~($|/))"),
        "Blocked recursive deletion targeting root or home directory.",
    ),
    (
        re.compile(r"(^|[;&|\s])rm\s+-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\s+(/($|\s)|/\*|~($|/))"),
        "Blocked recursive deletion targeting root or home directory.",
    ),
    (
        re.compile(r"(^|[;&|\s])(mkfs(\.[a-z0-9]+)?|dd\s+if=.*of=/dev/)"),
        "Blocked destructive block-device write command.",
    ),
    (
        re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"),
        "Blocked fork-bomb shell pattern.",
    ),
    (
        re.compile(r"\bgit\s+push\b[^\n]*(--force|-f)\b[^\n]*\b(main|master)\b"),
        "Blocked force-push to protected branch (main/master).",
    ),
    (
        re.compile(r"\b(curl|wget)\b[^\n]*\|\s*(sh|bash|zsh)\b"),
        "Blocked piping a remote script into a shell; download and inspect it first.",
    ),
]

ASK_PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\bgit\s+reset\s+--hard\b"),
        "`git reset --hard` discards uncommitted changes; explicit confirmation required.",
    ),
    (
        re.compile(r"\bgit\s+clean\s+-[a-zA-Z]*f"),
        "`git clean -f` permanently deletes untracked files; explicit confirmation required.",
    ),
    (
        re.compile(r"\bchmod\s+(-R\s+)?777\b"),
        "`chmod 777` grants read, write, and execute access to all local users; explicit confirmation required.",
    ),
]


def evaluate(event: CanonicalEvent) -> PolicyDecision:
    if event.event != "tool.before" or event.action != "shell.exec":
        return PolicyDecision(verdict="allow")

    cmd = event.command.strip()
    if not cmd:
        return PolicyDecision(verdict="allow")

    for pattern, reason in DENY_PATTERNS:
        if pattern.search(cmd):
            return PolicyDecision(verdict="deny", reason=reason)

    for pattern, reason in ASK_PATTERNS:
        if pattern.search(cmd):
            return PolicyDecision(verdict="ask", reason=reason)

    return PolicyDecision(verdict="allow")
