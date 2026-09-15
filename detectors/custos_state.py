"""Shared session/workflow state for CUSTOS gates (stdlib only).

Holds the small amount of cross-hook state the workflow gates need:
  - plan approval + approved scope (for the plan-freigabe and scope-guard gates)
  - a test baseline (for the regression guard)

Stored as custos_state.json in the repo root (gitignored, runtime artifact).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

STATE_FILE = "custos_state.json"


def _path(cwd: str | None) -> str:
    return os.path.join(cwd or os.getcwd(), STATE_FILE)


def default_state() -> dict:
    return {
        "plan": {"approved": False, "scope": [], "reviewer": None, "ts": None},
        "test_baseline": {"command": None, "exitCode": None, "ts": None},
    }


def load(cwd: str | None = None) -> dict:
    path = _path(cwd)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                base = default_state()
                base.update(data)
                return base
        except (OSError, json.JSONDecodeError):
            pass
    return default_state()


def save(state: dict, cwd: str | None = None) -> None:
    try:
        with open(_path(cwd), "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, ensure_ascii=False)
    except OSError:
        pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
