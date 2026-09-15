#!/usr/bin/env python3
"""CUSTOS proof gate (Stop hook).

The core of CUSTOS: a session may not end on a claim. Before Claude Code is
allowed to stop, this gate demands an executed proof and checks its exit code.
No green proof, no session end.

Proof command resolution (first match wins):
  1. "proofCommand" in custos.config.json at the repo root.
  2. Auto-detect:
       - pytest available + test files present -> "pytest -q"
       - package.json with a "test" script     -> "npm test"
  3. None resolvable -> block once with guidance (fail-closed).

Loop safety: Claude Code sets "stop_hook_active" once this gate has already
blocked in the current stop cycle. When that flag is set we do not hard-block a
second time on an *unresolvable* proof; we surface the state and allow the stop,
so the agent is never trapped. A genuinely failing proof command still blocks
so the failure gets fixed.

Usage: receives the Stop hook payload as JSON on stdin.
Exit 0 = proof green / allowed, Exit 2 = blocked (proof missing or red).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

CONFIG_FILE = "custos.config.json"
PROOF_LOG = "custos_findings.json"


def read_payload() -> dict:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def configured_command(cwd: str) -> str | None:
    path = os.path.join(cwd, CONFIG_FILE)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
        cmd = cfg.get("proofCommand")
        return cmd or None
    except (OSError, json.JSONDecodeError):
        return None


def detect_command(cwd: str) -> str | None:
    # Python tests?
    has_py_tests = False
    for root, _dirs, files in os.walk(cwd):
        if ".git" in root or "node_modules" in root:
            continue
        if any(f.startswith("test_") and f.endswith(".py") for f in files) or any(
            f.endswith("_test.py") for f in files
        ):
            has_py_tests = True
            break
    if has_py_tests and shutil.which("pytest"):
        return "pytest -q"

    # JS tests?
    pkg = os.path.join(cwd, "package.json")
    if os.path.exists(pkg):
        try:
            with open(pkg, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data.get("scripts"), dict) and data["scripts"].get("test"):
                return "npm test"
        except (OSError, json.JSONDecodeError):
            pass
    return None


def run_proof(command: str, cwd: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            command, cwd=cwd, shell=True, capture_output=True, text=True, timeout=900
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, f"CUSTOS could not run proof command '{command}': {exc}"
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def log_proof(cwd: str, command: str | None, code: int | None, blocked: bool) -> None:
    path = os.path.join(cwd, PROOF_LOG)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detector": "stop_gate",
        "proofCommand": command,
        "exitCode": code,
        "blocked": blocked,
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
        pass


def block(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


def main() -> int:
    payload = read_payload()
    cwd = payload.get("cwd") or os.getcwd()
    already_blocked = bool(payload.get("stop_hook_active"))

    command = configured_command(cwd) or detect_command(cwd)

    if command is None:
        log_proof(cwd, None, None, blocked=not already_blocked)
        if already_blocked:
            # Do not trap the agent: surface, then allow.
            print(
                "CUSTOS proof gate: no proof command configured or detected. "
                "Add \"proofCommand\" to custos.config.json so future sessions "
                "must prove their work.",
                file=sys.stderr,
            )
            return 0
        block(
            "CUSTOS proof gate: a session may not end on a claim. No test/linter "
            "proof command was found. Run your relevant tests or linter now, or "
            "add \"proofCommand\" to custos.config.json (e.g. \"pytest -q\"), "
            "then end the session."
        )

    code, out = run_proof(command, cwd)
    log_proof(cwd, command, code, blocked=(code != 0))
    if code != 0:
        block(
            f"CUSTOS proof gate BLOCKED: proof command '{command}' failed "
            f"(exit {code}). Fix it before ending the session.\n{out[:4000]}"
        )
    # Green proof: allow stop.
    print(f"CUSTOS proof gate: '{command}' passed (exit 0).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
