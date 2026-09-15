#!/usr/bin/env python3
"""CUSTOS regression guard (SubagentStop hook, concept section 8).

Compares the proof command's result against the recorded baseline. If the
baseline was green (exit 0) and it is now red, the subagent stop is blocked so the
new failure gets fixed instead of quietly shipped. If there is no baseline yet,
the current result is recorded as the baseline and the stop is allowed.

Resolves the proof command the same way the Stop proof gate does (custos.config
json 'proofCommand', else auto-detect pytest / npm test). If no proof command can
be resolved, the guard is a no-op (nothing to compare).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "detectors"))
import custos_state as st  # noqa: E402

# Reuse the resolution + run logic from the stop gate.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custos_stop_gate as gate  # noqa: E402


def read_payload() -> dict:
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main() -> int:
    payload = read_payload()
    cwd = payload.get("cwd") or os.getcwd()
    if payload.get("stop_hook_active"):
        return 0  # loop safety

    command = gate.configured_command(cwd) or gate.detect_command(cwd)
    if command is None:
        return 0  # nothing to compare

    code, out = gate.run_proof(command, cwd)
    state = st.load(cwd)
    baseline = state.get("test_baseline", {})
    prev = baseline.get("exitCode")

    if prev is None:
        state["test_baseline"] = {"command": command, "exitCode": code,
                                  "ts": st.now()}
        st.save(state, cwd)
        print(f"CUSTOS regression guard: baseline recorded ('{command}' exit {code}).",
              file=sys.stderr)
        return 0

    if prev == 0 and code != 0:
        print(
            f"CUSTOS regression guard BLOCKED: '{command}' was green (baseline) "
            f"and is now failing (exit {code}). A new regression was introduced. "
            f"Fix it before the subagent stops.\n{out[:3000]}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Update baseline to the latest good state.
    if code == 0:
        state["test_baseline"] = {"command": command, "exitCode": 0, "ts": st.now()}
        st.save(state, cwd)
    print(f"CUSTOS regression guard: '{command}' exit {code} (baseline exit {prev}).",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
