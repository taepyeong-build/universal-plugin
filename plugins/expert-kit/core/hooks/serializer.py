"""Serialize Canonical PolicyDecision objects into runtime-exact stdout payloads and exit codes."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .normalizer import CanonicalEvent, PolicyDecision


def serialize_decision(
    event: CanonicalEvent,
    decision: PolicyDecision,
) -> Tuple[Dict[str, Any], int]:
    """Return (stdout_json_dict, exit_code) honoring each CLI's exact hook contract."""
    if event.runtime == "antigravity":
        return _serialize_antigravity(event, decision)
    return _serialize_claude_or_codex(event, decision)


def _serialize_antigravity(
    event: CanonicalEvent,
    decision: PolicyDecision,
) -> Tuple[Dict[str, Any], int]:
    if event.event == "tool.before":
        verdict = decision.verdict if decision.verdict in {"allow", "deny", "ask", "force_ask"} else "allow"
        out: Dict[str, Any] = {"decision": verdict}
        if decision.reason:
            out["reason"] = decision.reason
        if decision.overwrite:
            out["overwrite"] = decision.overwrite
        return out, 0

    if event.event == "turn.stop":
        if decision.verdict == "continue":
            out = {"decision": "continue"}
            if decision.reason:
                out["reason"] = decision.reason
            return out, 0
        return {}, 0

    if event.event in {"session.start", "prompt.submit"}:
        if decision.context:
            return {
                "injectSteps": [
                    {"systemMessage": {"systemMessage": decision.context}}
                ]
            }, 0
        if decision.verdict == "deny" and event.event == "prompt.submit":
            return {
                "injectSteps": [
                    {"errorMessage": {"userMessage": decision.reason or "Blocked by policy."}}
                ],
                "terminationBehavior": "terminate",
            }, 0
        return {}, 0

    return {}, 0


def _serialize_claude_or_codex(
    event: CanonicalEvent,
    decision: PolicyDecision,
) -> Tuple[Dict[str, Any], int]:
    if event.event == "tool.before":
        if decision.verdict == "allow" and not decision.reason:
            return {}, 0
        perm = decision.verdict if decision.verdict in {"allow", "deny", "ask"} else "allow"
        hook_out: Dict[str, Any] = {
            "hookEventName": "PreToolUse",
            "permissionDecision": perm,
        }
        if decision.reason:
            hook_out["permissionDecisionReason"] = decision.reason
        return {"hookSpecificOutput": hook_out}, 0

    if event.event == "turn.stop":
        if decision.verdict == "continue":
            return {
                "decision": "block",
                "reason": decision.reason or "Verification checks must complete before stopping.",
            }, 0
        return {}, 0

    if event.event == "session.start":
        if decision.context:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": decision.context,
                }
            }, 0
        return {}, 0

    if event.event == "prompt.submit" and decision.verdict == "deny":
        return {
            "decision": "block",
            "reason": decision.reason or "Blocked by policy.",
        }, 0

    return {}, 0
