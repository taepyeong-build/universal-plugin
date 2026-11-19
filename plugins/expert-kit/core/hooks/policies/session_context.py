"""Inject a lean rules pointer at SessionStart for runtimes without native plugin rules/ auto-merge."""

from __future__ import annotations

import os

from ..normalizer import CanonicalEvent, PolicyDecision


def evaluate(event: CanonicalEvent) -> PolicyDecision:
    if event.event != "session.start":
        return PolicyDecision(verdict="allow")

    # Antigravity natively merges plugin rules/AGENTS.md; avoid duplicate context injection.
    if event.runtime == "antigravity":
        return PolicyDecision(verdict="allow")

    rules_path = os.path.join(event.plugin_root, "rules", "AGENTS.md") if event.plugin_root else ""
    if rules_path and os.path.isfile(rules_path):
        pointer = (
            "Expert Kit active. Follow SSOT (`spec/*.json` -> `tools/sync.py`), "
            "deterministic guardrails, and context-budget limits documented in "
            f"{rules_path}."
        )
        return PolicyDecision(verdict="allow", context=pointer)

    return PolicyDecision(verdict="allow")
