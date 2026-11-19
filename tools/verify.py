#!/usr/bin/env python3
"""3-Layer Verification Gate (L1: 3-CLI Strict, L2: Contract/Doctor, L3: Opt-in Evals)."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Dict, List, Tuple

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _run(cmd: List[str], env: Dict[str, str] | None = None, cwd: pathlib.Path = REPO_ROOT) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _check_marketplace_structures(registry: Dict) -> Tuple[bool, str]:
    expected_names = [p["name"] for p in registry["plugins"]]
    agy_mp = json.loads((REPO_ROOT / "marketplace.json").read_text(encoding="utf-8"))
    codex_mp = json.loads((REPO_ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))

    agy_names = [p["name"] for p in agy_mp.get("plugins", [])]
    codex_names = [p["name"] for p in codex_mp.get("plugins", [])]
    if agy_names != expected_names or codex_names != expected_names:
        return False, f"Marketplace plugin lists diverge: registry={expected_names}, agy={agy_names}, codex={codex_names}"

    for p in agy_mp.get("plugins", []):
        url = p.get("source", {}).get("url", "")
        if not url.startswith("https://"):
            return False, f"Antigravity marketplace.json plugin '{p.get('name')}' requires an https:// source.url"

    return True, "All 3 marketplace manifests structurally consistent with registry.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run 3-layer cross-CLI plugin verification.")
    parser.add_argument("--with-evals", action="store_true", help="Also run L3 behavioral evals (uses LLM tokens).")
    args = parser.parse_args()

    registry = json.loads((REPO_ROOT / "registry.json").read_text(encoding="utf-8"))
    mp_name = registry["marketplace"]["name"]
    plugins = registry["plugins"]

    results: List[Tuple[str, bool, str]] = []

    def record(label: str, ok: bool, detail: str) -> None:
        results.append((label, ok, detail))
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}: {detail}")

    # --- L1: SSOT Drift & 3-CLI Official Validators ---
    rc, out, err = _run([sys.executable, str(REPO_ROOT / "tools" / "sync.py"), "--check"])
    record("L1.sync-drift", rc == 0, (out or err).strip())

    mp_ok, mp_detail = _check_marketplace_structures(registry)
    record("L1.marketplace-parity", mp_ok, mp_detail)

    has_agy = shutil.which("agy") is not None
    has_claude = shutil.which("claude") is not None
    has_codex = shutil.which("codex") is not None

    if has_claude:
        rc, out, err = _run(
            ["claude", "plugin", "validate", "--strict", "--json", str(REPO_ROOT / ".claude-plugin" / "marketplace.json")]
        )
        record("L1.claude-marketplace", rc == 0, "0 errors, 0 warnings" if rc == 0 else (out or err).strip()[:300])
    else:
        record("L1.claude-marketplace", False, "claude CLI not found on PATH")

    for entry in plugins:
        name = entry["name"]
        pdir = REPO_ROOT / entry["path"]

        if has_agy:
            rc, out, err = _run(["agy", "plugin", "validate", "--strict", "--json", str(pdir)])
            detail = "0 errors, 0 warnings"
            if rc != 0:
                detail = (out or err).strip()[:400]
            else:
                try:
                    parsed = json.loads(out)
                    comps = parsed.get("components", {})
                    detail = f"agentPluginsSpec={parsed.get('agentPluginsSpec')} components={comps}"
                except json.JSONDecodeError:
                    pass
            record(f"L1.agy-strict[{name}]", rc == 0, detail)
        else:
            record(f"L1.agy-strict[{name}]", False, "agy CLI not found on PATH")

        if has_claude:
            rc, out, err = _run(
                ["claude", "plugin", "validate", "--strict", "--profile", "directory", "--json", str(pdir)]
            )
            detail = "strict + directory profile clean"
            if rc != 0:
                detail = (out or err).strip()[:500]
            record(f"L1.claude-strict-dir[{name}]", rc == 0, detail)
        else:
            record(f"L1.claude-strict-dir[{name}]", False, "claude CLI not found on PATH")

    # Isolated Codex CLI marketplace add + plugin install smoke test
    if has_codex:
        with tempfile.TemporaryDirectory(prefix="codex-verify-") as tmp_codex:
            env = dict(os.environ)
            env["CODEX_HOME"] = tmp_codex
            rc_mp, out_mp, err_mp = _run(
                ["codex", "plugin", "marketplace", "add", str(REPO_ROOT), "--json"], env=env
            )
            record(
                "L1.codex-marketplace-add",
                rc_mp == 0,
                f"marketplace '{mp_name}' registered in isolated CODEX_HOME" if rc_mp == 0 else (err_mp or out_mp).strip()[:300],
            )
            for entry in plugins:
                name = entry["name"]
                rc_add, out_add, err_add = _run(
                    ["codex", "plugin", "add", f"{name}@{mp_name}", "--json"], env=env
                )
                detail = f"installed {name}@{mp_name}"
                if rc_add != 0:
                    detail = (err_add or out_add).strip()[:300]
                record(f"L1.codex-plugin-add[{name}]", rc_add == 0, detail)
    else:
        record("L1.codex-marketplace-add", False, "codex CLI not found on PATH")

    # --- L2: Contract Unit Tests & Self-Diagnostic Doctor ---
    for entry in plugins:
        name = entry["name"]
        pdir = REPO_ROOT / entry["path"]
        tests_dir = pdir / "tests"
        if tests_dir.is_dir():
            rc, out, err = _run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir), "-p", "test_*.py"]
            )
            summary = (err or out).strip().splitlines()[-1] if (err or out).strip() else "ok"
            record(f"L2.unittest[{name}]", rc == 0, summary)

        doctor_py = pdir / "core" / "doctor.py"
        if doctor_py.is_file():
            rc, out, err = _run([sys.executable, str(doctor_py), "--ci"])
            detail = "0 errors, 0 warnings" if rc == 0 else (out or err).strip()[:300]
            record(f"L2.doctor-ci[{name}]", rc == 0, detail)

    # --- L3: Behavioral Evals (Opt-in) ---
    if args.with_evals:
        for entry in plugins:
            name = entry["name"]
            pdir = REPO_ROOT / entry["path"]
            evals_dir = pdir / "evals"
            if evals_dir.is_dir() and has_claude:
                rc, out, err = _run(["claude", "plugin", "eval", "--trust-plugin", str(pdir)])
                record(f"L3.claude-eval[{name}]", rc == 0, (out or err).strip()[:300])
    else:
        eval_cases = sum(len(list((REPO_ROOT / e["path"] / "evals").glob("*/prompt.md"))) for e in plugins if (REPO_ROOT / e["path"] / "evals").is_dir())
        print(f"[INFO] L3.evals skipped (run with --with-evals; {eval_cases} behavioral eval case(s) ready).")

    failed = [r for r in results if not r[1]]
    print(f"\nVerification summary: {len(results) - len(failed)}/{len(results)} gates passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
