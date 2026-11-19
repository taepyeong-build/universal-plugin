#!/usr/bin/env python3
"""Zero-dependency self-diagnostic doctor for cross-CLI plugin health and invariants."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import sys
from typing import Any, Dict, List

RULE_HARD_CAP_BYTES = 24_000
RULE_WARN_CAP_BYTES = 8_000
SKILL_MAX_LINES = 500
MIN_README_WORDS = 40
MAX_ICON_BYTES = 2 * 1024 * 1024

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
]

UNQUOTED_ROOT_RE = re.compile(r'(?<!")\$\{(?:CLAUDE_PLUGIN_ROOT|CLAUDE_PLUGIN_DATA|PLUGIN_ROOT|PLUGIN_DATA)\}')


def _check_png(path: pathlib.Path) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    if not path.is_file():
        return [
            {
                "severity": "error",
                "check": "icon",
                "message": f"Missing icon file: assets/{path.name} (generate one with `python3 tools/icon.py`).",
            }
        ]
    raw = path.read_bytes()
    if len(raw) > MAX_ICON_BYTES:
        issues.append({"severity": "error", "check": "icon", "message": f"Icon exceeds 2 MB ({len(raw)} bytes)."})
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        issues.append({"severity": "error", "check": "icon", "message": "Icon is not a valid PNG file."})
        return issues
    width, height = struct.unpack(">II", raw[16:24])
    if width != height:
        issues.append({"severity": "error", "check": "icon", "message": f"Icon must be square, got {width}x{height}."})
    if not (512 <= width <= 2048):
        issues.append(
            {
                "severity": "error",
                "check": "icon",
                "message": f"Icon dimensions must be 512..2048px for Claude Directory, got {width}x{height}.",
            }
        )
    return issues


def _extract_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    return text[4:end] if end != -1 else ""


def run_diagnostics(plugin_root: pathlib.Path) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []

    if sys.version_info < (3, 9):
        findings.append(
            {
                "severity": "error",
                "check": "python",
                "message": f"Python 3.9+ required, got {sys.version.split()[0]}.",
            }
        )

    if (plugin_root / "plugin.json").is_file() and (plugin_root / "hooks" / "hooks.json").is_file():
        findings.append(
            {
                "severity": "error",
                "check": "zero-collision",
                "message": "hooks/hooks.json collides with Antigravity root hooks.json; isolate Claude hooks in .claude-plugin/hooks.json.",
            }
        )

    rules_file = plugin_root / "rules" / "AGENTS.md"
    if rules_file.is_file():
        size = rules_file.stat().st_size
        if size > RULE_HARD_CAP_BYTES:
            findings.append(
                {
                    "severity": "error",
                    "check": "context-budget",
                    "message": f"rules/AGENTS.md is {size} bytes (> {RULE_HARD_CAP_BYTES} bytes hard limit).",
                }
            )
        elif size > RULE_WARN_CAP_BYTES:
            findings.append(
                {
                    "severity": "warning",
                    "check": "context-budget",
                    "message": f"rules/AGENTS.md is {size} bytes (> {RULE_WARN_CAP_BYTES} bytes recommended ~2,000-token budget).",
                }
            )

    skills_dir = plugin_root / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            lines = skill_md.read_text(encoding="utf-8").splitlines()
            if len(lines) > SKILL_MAX_LINES:
                findings.append(
                    {
                        "severity": "warning",
                        "check": "context-budget",
                        "message": f"{skill_md.relative_to(plugin_root)} has {len(lines)} lines (> {SKILL_MAX_LINES}).",
                    }
                )

    claude_hooks = plugin_root / ".claude-plugin" / "hooks.json"
    if claude_hooks.is_file():
        data = json.loads(claude_hooks.read_text(encoding="utf-8"))
        for event_name, groups in data.get("hooks", {}).items():
            for group in groups:
                for handler in group.get("hooks", []):
                    cmd = handler.get("command", "")
                    if isinstance(cmd, str) and UNQUOTED_ROOT_RE.search(cmd):
                        findings.append(
                            {
                                "severity": "error",
                                "check": "hook-quoting",
                                "message": f"Unquoted plugin path variable in .claude-plugin/hooks.json ({event_name}): {cmd}. Re-run `python3 tools/sync.py` to regenerate quoted commands.",
                            }
                        )

    for mcp_name in ("mcp.json", "mcp_config.json", ".mcp.json"):
        mcp_path = plugin_root / mcp_name
        if mcp_path.is_file():
            mcp_data = json.loads(mcp_path.read_text(encoding="utf-8"))
            for srv_name, cfg in mcp_data.get("mcpServers", {}).items():
                if cfg.get("type") == "sse":
                    findings.append(
                        {
                            "severity": "error",
                            "check": "mcp-transport",
                            "message": f"{mcp_name} server '{srv_name}' uses legacy SSE transport (unsupported by Antigravity); switch to 'stdio' or 'streamable-http' in spec/mcp.json.",
                        }
                    )

    agents_dir = plugin_root / "agents"
    if agents_dir.is_dir():
        for agent_md in sorted(agents_dir.glob("*.md")):
            fm = _extract_frontmatter(agent_md.read_text(encoding="utf-8"))
            for line in fm.splitlines():
                stripped = line.strip()
                if stripped.startswith("tools:") and len(stripped) > len("tools:"):
                    val = stripped[len("tools:") :].strip()
                    if not val.startswith("["):
                        findings.append(
                            {
                                "severity": "error",
                                "check": "agent-frontmatter",
                                "message": f"{agent_md.relative_to(plugin_root)} uses string 'tools:' (breaks Antigravity YAML []string parser).",
                            }
                        )

    findings.extend(_check_png(plugin_root / "assets" / "icon.png"))
    readme = plugin_root / "README.md"
    if not readme.is_file():
        findings.append({"severity": "error", "check": "readme", "message": "Missing README.md."})
    else:
        word_count = len(readme.read_text(encoding="utf-8").split())
        if word_count < MIN_README_WORDS:
            findings.append(
                {
                    "severity": "error",
                    "check": "readme",
                    "message": f"README.md has {word_count} words (minimum {MIN_README_WORDS} required).",
                }
            )

    for path in sorted(plugin_root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        if path.name == "doctor.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                findings.append(
                    {
                        "severity": "error",
                        "check": "secrets",
                        "message": f"Potential hardcoded secret detected in {path.relative_to(plugin_root)}.",
                    }
                )
                break

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    return {
        "plugin": plugin_root.name,
        "python": sys.version.split()[0],
        "ok": len(errors) == 0,
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-CLI plugin self-diagnostic doctor.")
    parser.add_argument(
        "--root",
        default=str(pathlib.Path(__file__).resolve().parents[1]),
        help="Plugin root directory to inspect (defaults to this plugin root).",
    )
    parser.add_argument("--ci", action="store_true", help="Exit non-zero on warnings as well as errors.")
    args = parser.parse_args()

    report = run_diagnostics(pathlib.Path(args.root).resolve())
    print(json.dumps(report, indent=2))
    if report["errorCount"] > 0:
        return 1
    if args.ci and report["warningCount"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
