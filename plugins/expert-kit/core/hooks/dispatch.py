#!/usr/bin/env python3
"""Universal Hook Protocol Adapter entrypoint shared across AGY, Claude Code, and Codex CLI."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from typing import Any, Callable, Dict

# Ensure plugin root is importable regardless of current working directory.
_PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PLUGIN_ROOT not in sys.path:
    sys.path.insert(0, _PLUGIN_ROOT)

from core.hooks.normalizer import CanonicalEvent, PolicyDecision, normalize_event, resolve_plugin_dirs
from core.hooks.policies import quality_gate, safety_guard, session_context
from core.hooks.serializer import serialize_decision

POLICIES: Dict[str, Callable[[CanonicalEvent], PolicyDecision]] = {
    "safety_guard": safety_guard.evaluate,
    "quality_gate": quality_gate.evaluate,
    "session_context": session_context.evaluate,
}

_SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s\"']+")


def _redact(text: str) -> str:
    return _SECRET_RE.sub(r"\1=[REDACTED]", text)


def _write_audit_log(plugin_data: str, policy_name: str, event: CanonicalEvent, decision: PolicyDecision) -> None:
    try:
        log_dir = os.path.join(plugin_data, "logs")
        os.makedirs(log_dir, exist_ok=True)
        record = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "policy": policy_name,
            "runtime": event.runtime,
            "event": event.event,
            "action": event.action,
            "tool": event.tool_name,
            "loopActive": event.loop_active,
            "verdict": decision.verdict,
            "reason": _redact(decision.reason),
        }
        with open(os.path.join(log_dir, "hooks.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        # Never break the agent loop if persistent data dir is read-only.
        pass


def run_dispatch(policy_name: str, raw_stdin: str) -> int:
    policy_fn = POLICIES.get(policy_name)
    if policy_fn is None:
        sys.stdout.write("{}\n")
        return 0

    try:
        payload: Dict[str, Any] = json.loads(raw_stdin) if raw_stdin.strip() else {}
    except json.JSONDecodeError:
        sys.stdout.write("{}\n")
        return 0

    plugin_root, plugin_data = resolve_plugin_dirs(__file__)
    event = normalize_event(payload, plugin_root=plugin_root, plugin_data=plugin_data)
    decision = policy_fn(event)
    _write_audit_log(plugin_data, policy_name, event, decision)

    out_payload, exit_code = serialize_decision(event, decision)
    sys.stdout.write(json.dumps(out_payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Expert Kit Universal Hook Adapter")
    parser.add_argument("--policy", required=True, choices=sorted(POLICIES.keys()))
    args = parser.parse_args()
    raw_stdin = sys.stdin.read()
    return run_dispatch(args.policy, raw_stdin)


if __name__ == "__main__":
    raise SystemExit(main())
