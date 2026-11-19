#!/usr/bin/env python3
"""Deterministic context-budget auditor for rules and skills."""

import json
import pathlib
import sys

RULE_MAX_BYTES = 24_000
SKILL_MAX_LINES = 500
RULE_NAMES = {"AGENTS.md", "GEMINI.md", "CLAUDE.md"}


def audit_directory(root: pathlib.Path) -> dict:
    findings = []
    files_checked = 0
    total_rule_bytes = 0

    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", "node_modules", "__pycache__"} for part in path.parts):
            continue
        rel = str(path.relative_to(root))
        data = path.read_bytes()
        lines = data.decode("utf-8", errors="replace").splitlines()

        if path.name in RULE_NAMES:
            files_checked += 1
            size = len(data)
            total_rule_bytes += size
            if size > RULE_MAX_BYTES:
                findings.append(
                    {
                        "severity": "error",
                        "file": rel,
                        "message": f"Rule file is {size} bytes (exceeds {RULE_MAX_BYTES}-byte cap).",
                    }
                )
        elif path.name == "SKILL.md":
            files_checked += 1
            if len(lines) > SKILL_MAX_LINES:
                findings.append(
                    {
                        "severity": "warning",
                        "file": rel,
                        "message": f"SKILL.md has {len(lines)} lines (recommended <= {SKILL_MAX_LINES}).",
                    }
                )

    return {
        "root": str(root),
        "filesChecked": files_checked,
        "totalRuleBytes": total_rule_bytes,
        "approxRuleTokens": total_rule_bytes // 4,
        "findings": findings,
        "ok": not any(f["severity"] == "error" for f in findings),
    }


def main() -> int:
    target = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path.cwd()
    if not target.exists():
        print(json.dumps({"ok": False, "error": f"Path not found: {target}"}))
        return 2
    report = audit_directory(target)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
