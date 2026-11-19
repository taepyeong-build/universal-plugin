"""L2 Contract tests for Universal Hook Protocol Adapter across AGY, Claude, and Codex."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
DISPATCH = PLUGIN_ROOT / "core" / "hooks" / "dispatch.py"

if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from core.hooks.normalizer import normalize_event
from core.hooks.policies import quality_gate, safety_guard, session_context
from core.hooks.serializer import serialize_decision


class HookContractTests(unittest.TestCase):
    def _load_fixture(self, name: str) -> dict:
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_antigravity_pre_tool_deny(self) -> None:
        payload = self._load_fixture("agy_pre_tool_deny.json")
        event = normalize_event(payload)
        self.assertEqual(event.runtime, "antigravity")
        self.assertEqual(event.event, "tool.before")
        self.assertEqual(event.action, "shell.exec")

        decision = safety_guard.evaluate(event)
        out, code = serialize_decision(event, decision)
        self.assertEqual(code, 0)
        self.assertEqual(out["decision"], "deny")
        self.assertIn("recursive deletion", out["reason"])

    def test_claude_pre_tool_deny(self) -> None:
        payload = self._load_fixture("claude_pre_tool_deny.json")
        event = normalize_event(payload, env={"CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)})
        self.assertEqual(event.runtime, "claude")

        decision = safety_guard.evaluate(event)
        out, code = serialize_decision(event, decision)
        self.assertEqual(code, 0)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_codex_pre_tool_deny(self) -> None:
        payload = self._load_fixture("codex_pre_tool_deny.json")
        event = normalize_event(payload, env={"CODEX_HOME": "/tmp/codex"})
        self.assertEqual(event.runtime, "codex")

        decision = safety_guard.evaluate(event)
        out, code = serialize_decision(event, decision)
        self.assertEqual(code, 0)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_ask_on_risky_command_and_allow_safe(self) -> None:
        risky = normalize_event(
            {
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "run_command", "args": {"CommandLine": "git reset --hard HEAD~1"}},
            }
        )
        self.assertEqual(safety_guard.evaluate(risky).verdict, "ask")

        safe = normalize_event(
            {
                "hookEventName": "PreToolUse",
                "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 --version"}},
            }
        )
        self.assertEqual(safety_guard.evaluate(safe).verdict, "allow")

    def test_stop_anti_loop_invariant_antigravity(self) -> None:
        failing_env = {"EXPERT_KIT_STOP_CHECK_CMD": "exit 1"}

        # First stop attempt should request continuation.
        first_payload = dict(self._load_fixture("agy_stop_loop.json"), continuationActive=False, cwd=str(PLUGIN_ROOT))
        first_event = normalize_event(first_payload)
        first_out, _ = serialize_decision(first_event, quality_gate.evaluate(first_event, env=failing_env))
        self.assertEqual(first_out.get("decision"), "continue")

        # Subsequent stop attempt with continuationActive=True MUST allow stopping.
        loop_payload = self._load_fixture("agy_stop_loop.json")
        loop_event = normalize_event(loop_payload)
        loop_out, _ = serialize_decision(loop_event, quality_gate.evaluate(loop_event, env=failing_env))
        self.assertEqual(loop_out, {})

    def test_stop_anti_loop_invariant_claude(self) -> None:
        failing_env = {"EXPERT_KIT_STOP_CHECK_CMD": "exit 1"}

        first_payload = dict(self._load_fixture("claude_stop_loop.json"), stop_hook_active=False, cwd=str(PLUGIN_ROOT))
        first_event = normalize_event(first_payload, env={"CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)})
        first_out, _ = serialize_decision(first_event, quality_gate.evaluate(first_event, env=failing_env))
        self.assertEqual(first_out.get("decision"), "block")

        loop_event = normalize_event(
            self._load_fixture("claude_stop_loop.json"),
            env={"CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
        )
        loop_out, _ = serialize_decision(loop_event, quality_gate.evaluate(loop_event, env=failing_env))
        self.assertEqual(loop_out, {})

    def test_session_context_deduplication(self) -> None:
        agy_evt = normalize_event(
            {"hookEventName": "SessionStart", "conversationId": "c1"},
            plugin_root=str(PLUGIN_ROOT),
        )
        self.assertEqual(session_context.evaluate(agy_evt).context, "")

        claude_evt = normalize_event(
            {"hook_event_name": "SessionStart", "session_id": "s1"},
            env={"CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT)},
            plugin_root=str(PLUGIN_ROOT),
        )
        dec = session_context.evaluate(claude_evt)
        self.assertIn("rules/AGENTS.md", dec.context)
        out, _ = serialize_decision(claude_evt, dec)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")

    def test_dispatch_subprocess_stdout_clean_and_audit_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["PLUGIN_ROOT"] = str(PLUGIN_ROOT)
            env["PLUGIN_DATA"] = tmp
            payload = (FIXTURES / "agy_pre_tool_deny.json").read_text(encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(DISPATCH), "--policy", "safety_guard"],
                input=payload,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            parsed = json.loads(proc.stdout)
            self.assertEqual(parsed["decision"], "deny")

            audit_file = pathlib.Path(tmp) / "logs" / "hooks.jsonl"
            self.assertTrue(audit_file.is_file())
            record = json.loads(audit_file.read_text(encoding="utf-8").strip().splitlines()[-1])
            self.assertEqual(record["runtime"], "antigravity")
            self.assertEqual(record["verdict"], "deny")


if __name__ == "__main__":
    unittest.main()
