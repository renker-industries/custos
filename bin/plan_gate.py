#!/usr/bin/env python3
"""CUSTOS plan-freigabe gate (PreToolUse on ExitPlanMode, concept section 8).

ExitPlanMode may only run after the plan-reviewer has approved the plan. Approval
is recorded in custos_state.json (plan.approved = true) by custos_approve_plan.py,
which the plan-reviewer agent calls when it returns APPROVED.

Exit 2 blocks the tool call while the plan is not approved.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "detectors"))
import custos_state as st  # noqa: E402


def read_payload() -> dict:
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        return json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, Exception):
        return {}


def main() -> int:
    payload = read_payload()
    cwd = payload.get("cwd") or os.getcwd()
    state = st.load(cwd)
    if state.get("plan", {}).get("approved"):
        return 0
    print(
        "CUSTOS plan gate BLOCKED ExitPlanMode: the plan has not been approved by "
        "the plan-reviewer. Route the plan to the plan-reviewer agent; on APPROVED "
        "it records approval (custos_approve_plan.py) and this gate opens.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
