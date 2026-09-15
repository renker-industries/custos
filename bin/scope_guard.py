#!/usr/bin/env python3
"""CUSTOS scope-guard (PreToolUse on Write|Edit, concept section 8).

During build, every file change is compared against the approved plan scope. A
change to a file outside the approved scope is blocked (exit 2) as scope drift.

Enforced only when a plan is approved AND a non-empty scope was recorded. Without
a recorded scope there is nothing to enforce, so the gate stays open (it cannot
invent the intended boundary).
"""
from __future__ import annotations

import fnmatch
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
    except Exception:
        return {}


def rel(path: str, cwd: str) -> str:
    try:
        return os.path.relpath(os.path.abspath(path), os.path.abspath(cwd)).replace(
            os.sep, "/"
        )
    except ValueError:
        return path.replace(os.sep, "/")


def in_scope(relpath: str, scope: list[str]) -> bool:
    for pat in scope:
        p = pat.replace(os.sep, "/")
        if fnmatch.fnmatch(relpath, p):
            return True
        # allow a directory prefix pattern like "src/**" to match "src/a.py"
        if p.endswith("/**") and (relpath == p[:-3] or relpath.startswith(p[:-2])):
            return True
    return False


def main() -> int:
    payload = read_payload()
    cwd = payload.get("cwd") or os.getcwd()
    ti = payload.get("tool_input", {}) or {}
    target = ti.get("file_path") or ti.get("path")
    if not target:
        return 0

    state = st.load(cwd)
    plan = state.get("plan", {})
    scope = plan.get("scope") or []
    if not plan.get("approved") or not scope:
        return 0  # nothing to enforce

    relpath = rel(target, cwd)
    if in_scope(relpath, scope):
        return 0

    print(
        f"CUSTOS scope-guard BLOCKED {relpath}: outside the approved plan scope "
        f"{scope}. This is scope drift. If the change is genuinely required, "
        f"update the plan (re-approve with the widened scope) before editing.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
