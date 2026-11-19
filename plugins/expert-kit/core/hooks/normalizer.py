"""Normalize Antigravity, Claude Code, and Codex CLI hook payloads into a Canonical Event IR."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple

TOOL_ACTION_MAP: Dict[str, str] = {
    # Shell execution tools across CLIs
    "run_command": "shell.exec",
    "Bash": "shell.exec",
    "bash": "shell.exec",
    "shell": "shell.exec",
    "local_shell": "shell.exec",
    # File write/edit tools
    "write_file": "fs.write",
    "edit_file": "fs.write",
    "Write": "fs.write",
    "Edit": "fs.write",
    "MultiEdit": "fs.write",
    "apply_patch": "fs.write",
    # File read tools
    "read_file": "fs.read",
    "Read": "fs.read",
    "view_file": "fs.read",
}

EVENT_MAP: Dict[str, str] = {
    "SessionStart": "session.start",
    "PreInvocation": "prompt.submit",
    "UserPromptSubmit": "prompt.submit",
    "PreToolUse": "tool.before",
    "PostToolUse": "tool.after",
    "PostInvocation": "turn.after",
    "Stop": "turn.stop",
}


@dataclass(frozen=True)
class CanonicalEvent:
    runtime: str
    event: str
    raw_event: str
    action: str = "other"
    tool_name: str = ""
    command: str = ""
    file_path: str = ""
    loop_active: bool = False
    cwd: str = ""
    plugin_root: str = ""
    plugin_data: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyDecision:
    verdict: str  # "allow" | "deny" | "ask" | "continue"
    reason: str = ""
    context: str = ""
    overwrite: Optional[Dict[str, Any]] = None


def detect_runtime(
    payload: Mapping[str, Any],
    env: Optional[Mapping[str, str]] = None,
) -> str:
    env_map = env if env is not None else os.environ
    explicit = env_map.get("EXPERT_KIT_RUNTIME", "").strip().lower()
    if explicit in {"antigravity", "claude", "codex"}:
        return explicit

    # Payload dialect detection is highest-signal and deterministic.
    if (
        "hookEventName" in payload
        or "toolCall" in payload
        or "continuationActive" in payload
        or "conversationId" in payload
    ):
        return "antigravity"

    if env_map.get("CODEX_HOME") or env_map.get("CODEX_SANDBOX") or env_map.get("CODEX_THREAD_ID"):
        return "codex"

    if env_map.get("CLAUDE_PLUGIN_ROOT") or env_map.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude"

    return "claude"


def resolve_plugin_dirs(
    anchor_file: str,
    env: Optional[Mapping[str, str]] = None,
) -> Tuple[str, str]:
    env_map = env if env is not None else os.environ
    default_root = os.path.abspath(os.path.join(os.path.dirname(anchor_file), "..", ".."))
    plugin_root = (
        env_map.get("PLUGIN_ROOT")
        or env_map.get("CLAUDE_PLUGIN_ROOT")
        or default_root
    )
    plugin_data = (
        env_map.get("PLUGIN_DATA")
        or env_map.get("CLAUDE_PLUGIN_DATA")
        or os.path.join(os.path.expanduser("~"), ".cache", "expert-kit")
    )
    return plugin_root, plugin_data


def _extract_tool_details(payload: Mapping[str, Any], runtime: str) -> Tuple[str, str, str]:
    if runtime == "antigravity":
        tool_call = payload.get("toolCall")
        if isinstance(tool_call, Mapping):
            tool_name = str(tool_call.get("name") or "")
            args = tool_call.get("args")
            if isinstance(args, Mapping):
                cmd = str(args.get("CommandLine") or args.get("command") or "")
                fpath = str(args.get("Path") or args.get("TargetFile") or args.get("path") or "")
                return tool_name, cmd, fpath
            return tool_name, "", ""
        return "", "", ""

    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, Mapping):
        cmd = str(tool_input.get("command") or tool_input.get("cmd") or "")
        fpath = str(tool_input.get("file_path") or tool_input.get("path") or "")
        return tool_name, cmd, fpath
    return tool_name, "", ""


def normalize_event(
    payload: Mapping[str, Any],
    env: Optional[Mapping[str, str]] = None,
    plugin_root: str = "",
    plugin_data: str = "",
) -> CanonicalEvent:
    runtime = detect_runtime(payload, env=env)
    raw_event = str(
        payload.get("hookEventName")
        or payload.get("hook_event_name")
        or ("Stop" if ("continuationActive" in payload or "stop_hook_active" in payload) else "")
    )
    event = EVENT_MAP.get(raw_event, "unknown")
    tool_name, command, file_path = _extract_tool_details(payload, runtime)
    action = TOOL_ACTION_MAP.get(tool_name, "other")

    loop_active = bool(payload.get("continuationActive") or payload.get("stop_hook_active"))
    cwd = str(payload.get("cwd") or "")
    if not cwd and isinstance(payload.get("workspacePaths"), list) and payload["workspacePaths"]:
        cwd = str(payload["workspacePaths"][0])

    return CanonicalEvent(
        runtime=runtime,
        event=event,
        raw_event=raw_event,
        action=action,
        tool_name=tool_name,
        command=command,
        file_path=file_path,
        loop_active=loop_active,
        cwd=cwd,
        plugin_root=plugin_root,
        plugin_data=plugin_data,
        raw=dict(payload),
    )
