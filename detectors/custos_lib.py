"""Shared helpers for CUSTOS detector scripts.

Stdlib only, cross-platform (Windows/macOS/Linux), no bash dependency.
Reads the Claude Code hook payload from stdin and appends structured findings
to custos_findings.json so every check leaves a timestamped, verifiable trace
instead of a claim in the chat.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

FINDINGS_FILE = "custos_findings.json"


def read_payload() -> dict:
    """Return the hook JSON from stdin, or {} if none/unparseable."""
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def tool_input(payload: dict) -> dict:
    return payload.get("tool_input", {}) or {}


def target_path(payload: dict) -> str | None:
    """Best-effort file path from a Write/Edit/MultiEdit tool input."""
    ti = tool_input(payload)
    return ti.get("file_path") or ti.get("path") or ti.get("notebook_path")


def changed_text(payload: dict) -> str:
    """Best-effort new content produced by a Write/Edit/MultiEdit call."""
    ti = tool_input(payload)
    if "content" in ti:
        return ti["content"] or ""
    if "new_string" in ti:
        return ti["new_string"] or ""
    if "edits" in ti and isinstance(ti["edits"], list):
        return "\n".join(str(e.get("new_string", "")) for e in ti["edits"])
    return ""


def findings_path(payload: dict) -> str:
    cwd = payload.get("cwd") or os.getcwd()
    return os.path.join(cwd, FINDINGS_FILE)


def read_config(payload: dict) -> dict:
    """Load custos.config.json from the repo root, or {}."""
    cwd = payload.get("cwd") or os.getcwd()
    path = os.path.join(cwd, "custos.config.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def zero_tolerance(payload: dict) -> bool:
    """Zero-tolerance mode (concept section 16): block on any finding, fail-closed.
    Enabled via env CUSTOS_ZERO_TOLERANCE=1 or "zeroTolerance": true in config."""
    if os.environ.get("CUSTOS_ZERO_TOLERANCE") in ("1", "true", "True"):
        return True
    return bool(read_config(payload).get("zeroTolerance"))


def record(payload: dict, detector: str, findings: list[dict], blocked: bool) -> None:
    """Append a detector run to custos_findings.json (create if missing)."""
    path = findings_path(payload)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detector": detector,
        "file": target_path(payload),
        "blocked": blocked,
        "findings": findings,
    }
    store: dict = {"schema": 1, "runs": []}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict) and isinstance(loaded.get("runs"), list):
                store = loaded
        except (OSError, json.JSONDecodeError):
            pass
    store["runs"].append(entry)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(store, fh, indent=2, ensure_ascii=False)
    except OSError:
        pass  # never fail a hook because the log could not be written


def emit_context(message: str) -> None:
    """Non-blocking: surface findings to the model as additionalContext."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        }
    }
    print(json.dumps(out))


def block(message: str) -> None:
    """Blocking: send the reason to stderr and exit 2 (fail-closed)."""
    print(message, file=sys.stderr)
    sys.exit(2)
