#!/usr/bin/env python3
"""Zero-dependency JSON-RPC 2.0 Stdio MCP server for Expert Kit diagnostics."""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import sys
from typing import Any, Dict, List, Optional

_PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

PROTOCOL_VERSION = "2025-03-26"
SERVER_INFO = {"name": "expert-diagnostics", "version": "1.0.0"}

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "plugin_diagnostics",
        "description": "Return Expert Kit plugin health, active components, and context-budget audit results.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "check_context_budget",
        "description": "Audit a directory's AGENTS.md/CLAUDE.md/GEMINI.md rules and SKILL.md files against 24 KB and 500-line context limits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative directory path to audit (defaults to current working directory).",
                }
            },
            "additionalProperties": False,
        },
    },
]


def _log_event(message: Dict[str, Any]) -> None:
    data_dir = (
        os.environ.get("EXPERT_KIT_DATA")
        or os.environ.get("PLUGIN_DATA")
        or os.environ.get("CLAUDE_PLUGIN_DATA")
    )
    if not data_dir:
        return
    try:
        log_dir = pathlib.Path(data_dir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            **message,
        }
        with (log_dir / "mcp.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _audit_context_budget(target: pathlib.Path) -> Dict[str, Any]:
    rule_names = {"AGENTS.md", "GEMINI.md", "CLAUDE.md"}
    findings: List[Dict[str, str]] = []
    files_checked = 0
    total_rule_bytes = 0

    for md in sorted(target.rglob("*.md")):
        if any(p in {".git", "node_modules", "__pycache__"} for p in md.parts):
            continue
        rel = str(md.relative_to(target))
        raw = md.read_bytes()
        if md.name in rule_names:
            files_checked += 1
            total_rule_bytes += len(raw)
            if len(raw) > 24_000:
                findings.append(
                    {
                        "severity": "error",
                        "file": rel,
                        "message": f"Rule file is {len(raw)} bytes (exceeds 24,000-byte limit).",
                    }
                )
        elif md.name == "SKILL.md":
            files_checked += 1
            line_count = len(raw.decode("utf-8", errors="replace").splitlines())
            if line_count > 500:
                findings.append(
                    {
                        "severity": "warning",
                        "file": rel,
                        "message": f"SKILL.md has {line_count} lines (recommended <= 500).",
                    }
                )

    return {
        "target": str(target),
        "filesChecked": files_checked,
        "totalRuleBytes": total_rule_bytes,
        "approxRuleTokens": total_rule_bytes // 4,
        "findings": findings,
        "ok": not any(f["severity"] == "error" for f in findings),
    }


def _call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "plugin_diagnostics":
        from core.doctor import run_diagnostics

        report = run_diagnostics(_PLUGIN_ROOT)
        return {
            "content": [{"type": "text", "text": json.dumps(report, indent=2)}],
            "isError": not report["ok"],
        }

    if name == "check_context_budget":
        raw_path = arguments.get("path")
        target = pathlib.Path(raw_path).expanduser().resolve() if raw_path else pathlib.Path.cwd()
        if not target.exists() or not target.is_dir():
            return {
                "content": [
                    {"type": "text", "text": json.dumps({"ok": False, "error": f"Directory not found: {target}"})}
                ],
                "isError": True,
            }
        report = _audit_context_budget(target)
        return {
            "content": [{"type": "text", "text": json.dumps(report, indent=2)}],
            "isError": not report["ok"],
        }

    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


def handle_request(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    req_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") if isinstance(msg.get("params"), dict) else {}

    # Notifications (no id) require no response.
    if req_id is None:
        _log_event({"kind": "notification", "method": method})
        return None

    if method == "initialize":
        client_version = params.get("protocolVersion")
        negotiated = client_version if isinstance(client_version, str) and client_version else PROTOCOL_VERSION
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": negotiated,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        if not isinstance(tool_name, str) or not tool_name:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": "Missing required tool name."},
            }
        _log_event({"kind": "tools/call", "tool": tool_name})
        return {"jsonrpc": "2.0", "id": req_id, "result": _call_tool(tool_name, arguments)}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> int:
    for line in sys.stdin:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            msg = json.loads(stripped)
        except json.JSONDecodeError as exc:
            err = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()
            continue

        if not isinstance(msg, dict):
            continue

        response = handle_request(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
