#!/usr/bin/env python3
"""Modular opt-in scaffolder for creating new 3-CLI compatible plugins under plugins/<name>/."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tools"))

from icon import generate_icon_png

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _write_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new cross-CLI plugin (core skills and rules plus optional hooks, MCP, subagents, and evals)."
    )
    parser.add_argument(
        "name",
        help="Lowercase hyphenated plugin slug (1-64 chars: a-z, 0-9, hyphens; e.g. security-kit).",
    )
    parser.add_argument("--description", required=True, help="Concise plugin description (at least 10 characters).")
    parser.add_argument("--category", default="Developer Tools", help="Marketplace category (default: Developer Tools).")
    parser.add_argument("--with-hooks", action="store_true", help="Include canonical hooks spec and hook runtime.")
    parser.add_argument("--with-mcp", action="store_true", help="Include canonical MCP spec and stdio server.")
    parser.add_argument("--with-agents", action="store_true", help="Include canonical read-only subagent spec.")
    parser.add_argument("--with-evals", action="store_true", help="Include starter L3 behavioral eval scaffold.")
    parser.add_argument("--full", action="store_true", help="Enable all optional components (hooks, MCP, subagents, evals).")
    args = parser.parse_args()

    if not SLUG_RE.match(args.name):
        print(f"Error: invalid plugin slug '{args.name}' (use 1-64 lowercase a-z, 0-9, or hyphens).", file=sys.stderr)
        return 2

    desc_clean = args.description.strip()
    if len(desc_clean) < 10:
        print("Error: --description must be at least 10 characters.", file=sys.stderr)
        return 2
    desc_sentence = desc_clean.rstrip(".") + "."

    pdir = REPO_ROOT / "plugins" / args.name
    if pdir.exists():
        print(f"Error: plugin directory already exists: {pdir}", file=sys.stderr)
        return 2

    registry_path = REPO_ROOT / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    mp_name = registry["marketplace"]["name"]
    repo_slug = registry["marketplace"]["repository"]["slug"]
    repo_url = registry["marketplace"]["repository"]["url"].rstrip("/")
    repo_branch = registry["marketplace"]["repository"]["branch"]
    owner_url = registry["marketplace"]["owner"].get("url", repo_url)

    display_name = " ".join(part.capitalize() for part in args.name.split("-"))

    # Core required components: spec/plugin.json, icon, README, rules/AGENTS.md, starter skill
    generate_icon_png(pdir / "assets" / "icon.png")
    _write_json(
        pdir / "spec" / "plugin.json",
        {
            "$schema": "../../../schemas/plugin-spec.schema.json",
            "name": args.name,
            "displayName": display_name,
            "version": "0.1.0",
            "description": desc_sentence,
            "author": {"name": registry["marketplace"]["owner"]["name"], "url": owner_url},
            "homepage": repo_url,
            "repository": repo_url,
            "license": "MIT",
            "keywords": [args.name, "cross-cli"],
            "icon": "assets/icon.png",
            "category": args.category,
        },
    )

    (pdir / "rules").mkdir(parents=True, exist_ok=True)
    (pdir / "rules" / "AGENTS.md").write_text(
        f"# {display_name} Rules\n\nKeep always-on rules concise (< 2,000 tokens, <= 24 KB).\n",
        encoding="utf-8",
    )

    skill_dir = pdir / "skills" / f"{args.name}-workflow"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\n"
        f"name: {args.name}-workflow\n"
        f"description: Use when executing {display_name} tasks and verification procedures.\n"
        f"---\n\n"
        f"# {display_name} Workflow\n\n"
        f"1. Inspect workspace constraints and relevant files.\n"
        f"2. Execute deterministic checks before making changes.\n"
        f"3. Verify results with concrete command output.\n",
        encoding="utf-8",
    )

    (pdir / "README.md").write_text(
        f"# {display_name}\n\n"
        f"{desc_sentence} Built from canonical specs under `spec/` for **Claude Code**, "
        f"**Codex CLI**, and **Antigravity CLI** with Python 3.9+ and zero third-party packages.\n\n"
        f"## Installation\n\n"
        f"### Claude Code\n"
        f"```text\n/plugin install {args.name} --marketplace {repo_slug}\n```\n\n"
        f"### Codex CLI\n"
        f"```bash\ncodex plugin marketplace add {repo_url}\ncodex plugin add {args.name}@{mp_name}\n```\n\n"
        f"### Antigravity CLI\n"
        f"```bash\nagy plugin install {repo_url}/tree/{repo_branch}/plugins/{args.name}\n```\n\n"
        f"## Verification\n\n"
        f"Run the self-diagnostic check from `plugins/{args.name}` (Python 3.9+):\n\n"
        f"```bash\ncd plugins/{args.name}\npython3 core/doctor.py --ci\n```\n",
        encoding="utf-8",
    )

    if args.full or args.with_agents:
        _write_json(
            pdir / "spec" / "agents" / f"{args.name}-reviewer.json",
            {
                "$schema": "../../../../schemas/agent-spec.schema.json",
                "name": f"{args.name}-reviewer",
                "description": f"Read-only specialist reviewer for {display_name} outputs.",
                "capabilities": ["read", "search"],
                "modelTier": "inherit",
                "instructions": f"You are a read-only specialist reviewer for {display_name}. Cite exact file paths and concrete evidence.",
            },
        )

    if args.full or args.with_evals:
        eval_dir = pdir / "evals" / "baseline"
        (eval_dir / "graders").mkdir(parents=True, exist_ok=True)
        (eval_dir / "prompt.md").write_text(f"Demonstrate the {display_name} workflow on a sample scenario.\n", encoding="utf-8")
        (eval_dir / "graders" / "rubric.md").write_text("# Rubric\n1. Follows workflow steps.\n2. Includes concrete verification.\n", encoding="utf-8")

    template_core = REPO_ROOT / "plugins" / "expert-kit" / "core"
    (pdir / "core").mkdir(parents=True, exist_ok=True)
    if (template_core / "__init__.py").is_file():
        shutil.copy2(template_core / "__init__.py", pdir / "core" / "__init__.py")
    if (template_core / "doctor.py").is_file():
        shutil.copy2(template_core / "doctor.py", pdir / "core" / "doctor.py")

    if args.full or args.with_hooks:
        if (template_core / "hooks").is_dir():
            shutil.copytree(template_core / "hooks", pdir / "core" / "hooks")
        _write_json(
            pdir / "spec" / "hooks.json",
            {
                "$schema": "../../../schemas/hooks-spec.schema.json",
                "groups": [
                    {
                        "name": "safety-guard",
                        "enabled": True,
                        "rules": [
                            {
                                "event": "tool.before",
                                "actions": ["shell.exec"],
                                "policy": "safety_guard",
                                "timeoutSec": 10,
                            }
                        ],
                    }
                ],
            },
        )
    if args.full or args.with_mcp:
        if (template_core / "mcp").is_dir():
            shutil.copytree(template_core / "mcp", pdir / "core" / "mcp")
        _write_json(
            pdir / "spec" / "mcp.json",
            {
                "$schema": "../../../schemas/mcp-spec.schema.json",
                "servers": {
                    f"{args.name}-diagnostics": {
                        "transport": "stdio",
                        "command": "python3",
                        "args": ["${PLUGIN_ROOT}/core/mcp/server.py"],
                        "env": {"EXPERT_KIT_DATA": "${PLUGIN_DATA}"},
                    }
                },
            },
        )

    # Register in registry.json
    registry["plugins"].append(
        {
            "name": args.name,
            "path": f"plugins/{args.name}",
            "category": args.category,
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        }
    )
    _write_json(registry_path, registry)

    # Run sync.py immediately
    subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "sync.py")], check=True)
    print(
        f"Scaffolded and synced plugins/{args.name}. "
        f"Next: customize plugins/{args.name}/README.md and run python3 tools/verify.py."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
