"""Deterministic Stop quality gate with strict anti-loop invariant."""

from __future__ import annotations

import os
import subprocess
from typing import Mapping, Optional

from ..normalizer import CanonicalEvent, PolicyDecision


def evaluate(
    event: CanonicalEvent,
    env: Optional[Mapping[str, str]] = None,
) -> PolicyDecision:
    if event.event != "turn.stop":
        return PolicyDecision(verdict="allow")

    # CRITICAL INVARIANT: Never trap the agent in a recursive Stop continuation loop.
    if event.loop_active:
        return PolicyDecision(verdict="allow")

    env_map = env if env is not None else os.environ
    check_cmd = env_map.get("EXPERT_KIT_STOP_CHECK_CMD", "").strip()
    if not check_cmd:
        return PolicyDecision(verdict="allow")

    cwd = event.cwd if event.cwd and os.path.isdir(event.cwd) else None
    try:
        result = subprocess.run(
            check_cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return PolicyDecision(
            verdict="continue",
            reason=f"Stop quality gate (EXPERT_KIT_STOP_CHECK_CMD) timed out after 10s: {check_cmd}.",
        )

    if result.returncode != 0:
        summary = (result.stderr or result.stdout or "").strip().splitlines()
        tail = summary[-1].rstrip(".") if summary else ""
        detail = f": {tail}" if tail else ""
        return PolicyDecision(
            verdict="continue",
            reason=f"Stop quality gate (EXPERT_KIT_STOP_CHECK_CMD) exited {result.returncode} ({check_cmd}){detail}. Fix before finishing.",
        )

    return PolicyDecision(verdict="allow")
