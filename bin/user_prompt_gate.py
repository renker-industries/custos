#!/usr/bin/env python3
"""CUSTOS trivial-schranke (UserPromptSubmit hook, concept section 8).

Injects a triage reminder as additionalContext at the start of every task, so the
senior-dev agent explicitly decides "trivial or plan-required" instead of
diving straight into edits. Non-blocking.
"""
from __future__ import annotations

import json
import sys

REMINDER = (
    "CUSTOS triage: classify this task before acting. Trivial one-line/one-file "
    "fix -> do it, then prove it. Otherwise (multiple files, new behaviour, DB "
    "or security surface, unclear requirements) -> plan first and route the plan "
    "to the plan-reviewer before ExitPlanMode. Either way, end only with an "
    "executed proof (test/linter), never a claim."
)


def main() -> int:
    # Drain stdin (payload) but we do not need its contents here.
    try:
        if not sys.stdin.isatty():
            sys.stdin.read()
    except Exception:
        pass
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": REMINDER,
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
