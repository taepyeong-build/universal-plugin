#!/usr/bin/env python3
"""Deterministic SSOT compiler: registry.json + spec/*.json -> 3-CLI Zero-Collision adapters."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any, Dict, List, Tuple

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

AGY_ACTION_MATCHERS: Dict[str, List[str]] = {
    "shell.exec": ["run_command"],
    "fs.write": ["edit_file", "write_file"],
    "fs.read": ["read_file"],
    "all": ["*"],
}

CLAUDE_ACTION_MATCHERS: Dict[str, List[str]] = {
    "shell.exec": ["Bash"],
    "fs.write": ["Edit", "Write", "MultiEdit"],
    "fs.read": ["Read"],
    "all": ["*"],
}

CODEX_ACTION_MATCHERS: Dict[str, List[str]] = {
    "shell.exec": ["Bash", "shell"],
    "fs.write": ["Write", "apply_patch"],
    "fs.read": ["Read"],
    "all": ["*"],
}

AGY_EVENT_NAMES: Dict[str, str] = {
    "session.start": "SessionStart",
    "prompt.submit": "PreInvocation",
    "tool.before": "PreToolUse",
    "tool.after": "PostToolUse",
    "turn.stop": "Stop",
}

CLAUDE_EVENT_NAMES: Dict[str, str] = {
    "session.start": "SessionStart",
    "prompt.submit": "UserPromptSubmit",
    "tool.before": "PreToolUse",
    "tool.after": "PostToolUse",
    "turn.stop": "Stop",
}


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _replace_vars(obj: Any, replacements: Dict[str, str]) -> Any:
    if isinstance(obj, str):
        out = obj
        for src, dst in replacements.items():
            out = out.replace(src, dst)
        return out
    if isinstance(obj, list):
        return [_replace_vars(v, replacements) for v in obj]
    if isinstance(obj, dict):
        return {k: _replace_vars(v, replacements) for k, v in obj.items()}
    return obj


def _join_matchers(actions: List[str], mapping: Dict[str, List[str]]) -> str:
    tokens: List[str] = []
    for act in actions:
        for t in mapping.get(act, []):
            if t not in tokens:
                tokens.append(t)
    if not tokens or "*" in tokens:
        return "*"
    return "|".join(tokens)


def _validate_plugin_spec(spec: Dict[str, Any], expected_name: str) -> None:
    name = spec.get("name", "")
    if name != expected_name:
        raise ValueError(f"spec/plugin.json name '{name}' does not match registry name '{expected_name}'.")
    if not SLUG_RE.match(name):
        raise ValueError(f"Invalid plugin name '{name}'.")
    if not SEMVER_RE.match(str(spec.get("version", ""))):
        raise ValueError(f"Plugin '{name}' version must be SemVer X.Y.Z.")


def _render_root_plugin_json(spec: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": spec["name"],
        "version": spec["version"],
        "description": spec["description"],
        "author": spec["author"],
        "license": spec["license"],
    }
    if spec.get("keywords"):
        out["keywords"] = spec["keywords"]
    if spec.get("homepage"):
        out["homepage"] = spec["homepage"]
    if spec.get("repository"):
        out["repository"] = spec["repository"]
    if spec.get("icon"):
        out["logo"] = spec["icon"]
    if spec.get("disabled") is True:
        out["disabled"] = True

    openai_ext: Dict[str, Any] = {}
    if spec.get("displayName"):
        openai_ext["displayName"] = spec["displayName"]
    if spec.get("category"):
        openai_ext["category"] = spec["category"]
    if spec.get("icon"):
        openai_ext["icon"] = spec["icon"]
    if openai_ext:
        out["extensions"] = {"com.openai": openai_ext}
    return out


def _render_claude_plugin_json(spec: Dict[str, Any], has_hooks: bool) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "name": spec["name"],
        "version": spec["version"],
        "description": spec["description"],
        "author": spec["author"],
        "license": spec["license"],
    }
    if spec.get("keywords"):
        out["keywords"] = spec["keywords"]
    if spec.get("homepage"):
        out["homepage"] = spec["homepage"]
    if spec.get("repository"):
        out["repository"] = spec["repository"]
    if spec.get("icon"):
        out["icon"] = spec["icon"]
    if has_hooks:
        out["hooks"] = "./.claude-plugin/hooks.json"
    return out


def _render_mcp_files(mcp_spec: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    servers = mcp_spec.get("servers", {})
    if not isinstance(servers, dict) or not servers:
        raise ValueError("spec/mcp.json must declare at least one server in 'servers'.")

    agent_plugins_servers: Dict[str, Any] = {}
    agy_legacy_servers: Dict[str, Any] = {}
    claude_servers: Dict[str, Any] = {}

    for srv_name, cfg in servers.items():
        transport = cfg.get("transport")
        if transport not in {"stdio", "streamable-http"}:
            raise ValueError(
                f"MCP server '{srv_name}' uses unsupported transport '{transport}'. Use 'stdio' or 'streamable-http'."
            )

        if transport == "stdio":
            if not cfg.get("command"):
                raise ValueError(f"Stdio MCP server '{srv_name}' requires 'command'.")
            base: Dict[str, Any] = {"command": cfg["command"]}
            if cfg.get("args"):
                base["args"] = cfg["args"]
            if cfg.get("env"):
                base["env"] = cfg["env"]

            agent_plugins_servers[srv_name] = {"type": "stdio", **base}
            agy_legacy_servers[srv_name] = dict(base)
            claude_servers[srv_name] = _replace_vars(
                base,
                {
                    "${PLUGIN_ROOT}": "${CLAUDE_PLUGIN_ROOT}",
                    "${PLUGIN_DATA}": "${CLAUDE_PLUGIN_DATA}",
                },
            )
        else:
            if not cfg.get("url"):
                raise ValueError(f"HTTP MCP server '{srv_name}' requires 'url'.")
            agent_plugins_servers[srv_name] = {"type": "streamable-http", "url": cfg["url"]}
            agy_legacy_servers[srv_name] = {"url": cfg["url"]}
            claude_servers[srv_name] = {"type": "http", "url": cfg["url"]}

    mcp_json = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        "mcpServers": agent_plugins_servers,
    }
    mcp_config_json = {"mcpServers": agy_legacy_servers}
    dot_mcp_json = {"mcpServers": claude_servers}
    return mcp_json, mcp_config_json, dot_mcp_json


def _render_hooks_files(hooks_spec: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    agy_hooks: Dict[str, Any] = {}
    claude_events: Dict[str, List[Dict[str, Any]]] = {}
    codex_events: Dict[str, List[Dict[str, Any]]] = {}

    for group in hooks_spec.get("groups", []):
        group_name = group["name"]
        enabled = group.get("enabled", True)
        agy_group: Dict[str, Any] = {}
        if not enabled:
            agy_group["enabled"] = False

        for rule in group.get("rules", []):
            ev = rule["event"]
            policy = rule["policy"]
            timeout = int(rule.get("timeoutSec", 15))
            actions = rule.get("actions", ["all"])
            runtimes = set(rule.get("runtimes", ["antigravity", "claude", "codex"]))

            # 1. Antigravity root hooks.json
            if "antigravity" in runtimes and ev in AGY_EVENT_NAMES:
                agy_ev = AGY_EVENT_NAMES[ev]
                handler = {
                    "type": "command",
                    "command": f"python3 ./core/hooks/dispatch.py --policy {policy}",
                    "timeout": timeout,
                }
                if ev in {"tool.before", "tool.after"}:
                    agy_group.setdefault(agy_ev, []).append(
                        {
                            "matcher": _join_matchers(actions, AGY_ACTION_MATCHERS),
                            "hooks": [handler],
                        }
                    )
                else:
                    # Antigravity non-tool events use a flat array of handler objects.
                    agy_group.setdefault(agy_ev, []).append(handler)

            # 2. Claude Code .claude-plugin/hooks.json (always quoted placeholder!)
            if enabled and "claude" in runtimes and ev in CLAUDE_EVENT_NAMES:
                cl_ev = CLAUDE_EVENT_NAMES[ev]
                cl_handler = {
                    "type": "command",
                    "command": f'python3 "${{CLAUDE_PLUGIN_ROOT}}/core/hooks/dispatch.py" --policy {policy}',
                    "timeout": timeout,
                }
                entry: Dict[str, Any] = {"hooks": [cl_handler]}
                if ev in {"tool.before", "tool.after"}:
                    entry = {
                        "matcher": _join_matchers(actions, CLAUDE_ACTION_MATCHERS),
                        "hooks": [cl_handler],
                    }
                claude_events.setdefault(cl_ev, []).append(entry)

            # 3. Codex CLI com.openai/hooks.json (opt-in workspace template)
            if enabled and "codex" in runtimes and ev in CLAUDE_EVENT_NAMES:
                cx_ev = CLAUDE_EVENT_NAMES[ev]
                cx_handler = {
                    "type": "command",
                    "command": f'python3 "${{PLUGIN_ROOT}}/core/hooks/dispatch.py" --policy {policy}',
                    "timeout": timeout,
                }
                cx_entry: Dict[str, Any] = {"hooks": [cx_handler]}
                if ev in {"tool.before", "tool.after"}:
                    cx_entry = {
                        "matcher": _join_matchers(actions, CODEX_ACTION_MATCHERS),
                        "hooks": [cx_handler],
                    }
                codex_events.setdefault(cx_ev, []).append(cx_entry)

        if any(k != "enabled" for k in agy_group):
            agy_hooks[group_name] = agy_group

    return agy_hooks, {"hooks": claude_events}, {"hooks": codex_events}


def _toml_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _render_agent_files(agent_spec: Dict[str, Any]) -> Tuple[str, str]:
    name = agent_spec["name"]
    description = agent_spec["description"]
    capabilities = agent_spec["capabilities"]
    model_tier = agent_spec.get("modelTier", "inherit")
    instructions = agent_spec["instructions"].strip()

    # Portable Markdown shared across Claude Code & Antigravity CLI.
    # Deliberately omits runtime-specific tool names so neither parser rejects it.
    cap_line = ", ".join(capabilities)
    md_lines = [
        "---",
        f"name: {name}",
        f"description: {json.dumps(description, ensure_ascii=False)}",
    ]
    if model_tier == "inherit":
        md_lines.append("model: inherit")
    md_lines.extend(
        [
            "---",
            "",
            f"<!-- Generated from spec/agents/{name}.json. Capabilities: {cap_line} -->",
            "",
            instructions,
            "",
        ]
    )
    md_content = "\n".join(md_lines)

    # Codex CLI strict TOML manifest under com.openai/agents/<name>.toml
    read_only = not any(c in {"write", "exec"} for c in capabilities)
    sandbox_mode = "read-only" if read_only else "workspace-write"
    safe_inst = instructions.replace('"""', '\\"\\"\\"')
    toml_content = (
        f'# Generated from spec/agents/{name}.json\n'
        f'name = "{_toml_escape(name)}"\n'
        f'description = "{_toml_escape(description)}"\n'
        f'sandbox_mode = "{sandbox_mode}"\n'
        f'developer_instructions = """\n{safe_inst}\n"""\n'
    )
    return md_content, toml_content


def build_expected_files(repo_root: pathlib.Path) -> Tuple[Dict[pathlib.Path, str], List[pathlib.Path]]:
    """Compute all expected generated files and list of potentially stale generated paths."""
    registry = _load_json(repo_root / "registry.json")
    mp = registry["marketplace"]
    repo_url = mp["repository"]["url"].rstrip("/")
    repo_branch = mp["repository"]["branch"]

    expected: Dict[pathlib.Path, str] = {}
    managed_cleanup: List[pathlib.Path] = []

    claude_mp_plugins: List[Dict[str, Any]] = []
    codex_mp_plugins: List[Dict[str, Any]] = []
    agy_mp_plugins: List[Dict[str, Any]] = []

    for entry in registry["plugins"]:
        name = entry["name"]
        rel_path = entry["path"]
        pdir = repo_root / rel_path
        spec_dir = pdir / "spec"
        plugin_spec = _load_json(spec_dir / "plugin.json")
        _validate_plugin_spec(plugin_spec, name)

        hooks_spec_path = spec_dir / "hooks.json"
        mcp_spec_path = spec_dir / "mcp.json"
        agents_spec_dir = spec_dir / "agents"

        has_hooks = hooks_spec_path.is_file()
        has_mcp = mcp_spec_path.is_file()

        # 1. Core dual manifests
        expected[pdir / "plugin.json"] = _dump_json(_render_root_plugin_json(plugin_spec))
        expected[pdir / ".claude-plugin" / "plugin.json"] = _dump_json(
            _render_claude_plugin_json(plugin_spec, has_hooks=has_hooks)
        )

        # 2. Optional MCP adapters
        mcp_targets = [pdir / "mcp.json", pdir / "mcp_config.json", pdir / ".mcp.json"]
        if has_mcp:
            mcp_json, mcp_cfg, dot_mcp = _render_mcp_files(_load_json(mcp_spec_path))
            expected[pdir / "mcp.json"] = _dump_json(mcp_json)
            expected[pdir / "mcp_config.json"] = _dump_json(mcp_cfg)
            expected[pdir / ".mcp.json"] = _dump_json(dot_mcp)
        else:
            managed_cleanup.extend(mcp_targets)

        # 3. Optional Hooks adapters (NEVER generate hooks/hooks.json!)
        hook_targets = [
            pdir / "hooks.json",
            pdir / ".claude-plugin" / "hooks.json",
            pdir / "com.openai" / "hooks.json",
        ]
        if has_hooks:
            agy_h, claude_h, codex_h = _render_hooks_files(_load_json(hooks_spec_path))
            if agy_h:
                expected[pdir / "hooks.json"] = _dump_json(agy_h)
            else:
                managed_cleanup.append(pdir / "hooks.json")
            expected[pdir / ".claude-plugin" / "hooks.json"] = _dump_json(claude_h)
            expected[pdir / "com.openai" / "hooks.json"] = _dump_json(codex_h)
        else:
            managed_cleanup.extend(hook_targets)

        # 4. Optional Subagents
        if agents_spec_dir.is_dir():
            for agent_file in sorted(agents_spec_dir.glob("*.json")):
                agent_spec = _load_json(agent_file)
                md_out, toml_out = _render_agent_files(agent_spec)
                agent_name = agent_spec["name"]
                expected[pdir / "agents" / f"{agent_name}.md"] = md_out
                expected[pdir / "com.openai" / "agents" / f"{agent_name}.toml"] = toml_out

        # 5. Marketplace entries
        claude_mp_plugins.append(
            {
                "name": name,
                "description": plugin_spec["description"],
                "version": plugin_spec["version"],
                "source": f"./{rel_path}",
            }
        )
        codex_mp_plugins.append(
            {
                "name": name,
                "source": {"source": "local", "path": f"./{rel_path}"},
                "policy": entry["policy"],
                "category": entry["category"],
            }
        )
        agy_mp_plugins.append(
            {
                "name": name,
                "description": plugin_spec["description"],
                "version": plugin_spec["version"],
                "source": {
                    "url": f"{repo_url}/tree/{repo_branch}/{rel_path}",
                },
            }
        )

    # Root 3 marketplaces
    claude_marketplace: Dict[str, Any] = {
        "name": mp["name"],
        "description": mp["description"],
        "version": mp["version"],
        "owner": {k: v for k, v in mp["owner"].items() if k in {"name", "email"}},
        "plugins": claude_mp_plugins,
    }
    codex_marketplace = {
        "name": mp["name"],
        "interface": {"displayName": mp["displayName"]},
        "plugins": codex_mp_plugins,
    }
    agy_marketplace = {
        "name": mp["name"],
        "description": mp["description"],
        "version": mp["version"],
        "plugins": agy_mp_plugins,
    }

    expected[repo_root / ".claude-plugin" / "marketplace.json"] = _dump_json(claude_marketplace)
    expected[repo_root / ".agents" / "plugins" / "marketplace.json"] = _dump_json(codex_marketplace)
    expected[repo_root / "marketplace.json"] = _dump_json(agy_marketplace)

    return expected, managed_cleanup


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync canonical specs to 3-CLI adapters and marketplaces.")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if any generated file is out of sync.")
    args = parser.parse_args()

    expected, cleanup = build_expected_files(REPO_ROOT)
    drifted: List[str] = []

    for path, content in sorted(expected.items()):
        rel = str(path.relative_to(REPO_ROOT))
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != content:
            drifted.append(rel)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    for stale in cleanup:
        if stale.is_file():
            rel = str(stale.relative_to(REPO_ROOT))
            drifted.append(f"{rel} (stale)")
            if not args.check:
                stale.unlink()

    if args.check:
        if drifted:
            print("SSOT drift detected. Run `python3 tools/sync.py` to regenerate:", file=sys.stderr)
            for item in drifted:
                print(f"  - {item}", file=sys.stderr)
            return 1
        print(f"OK: {len(expected)} generated files are in sync with canonical specs.")
        return 0

    print(f"Synced {len(expected)} generated files ({len(drifted)} updated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
