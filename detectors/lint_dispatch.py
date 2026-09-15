#!/usr/bin/env python3
"""CUSTOS language-specific static analysis dispatch (PostToolUse on Write|Edit).

Picks the right independent linter/typecheck for the edited file's language and
runs it against the real file on disk. This is the "second, independent instance"
from concept section 9: the judgement comes from a real static-analysis tool, not
from the language model re-reading its own code.

Currently wired:
  - Python  -> ruff (if installed) else `python -m py_compile` (always available)
  - JS/TS   -> eslint (if installed on PATH / npx) else skip-with-notice

If a preferred linter is not installed, the gate degrades to a non-blocking
notice rather than blocking, so the skeleton is usable before every toolchain is
present. Zero-tolerance / fail-closed hardening is a later roadmap item.

Usage: receives the Claude Code hook payload as JSON on stdin.
Exit 0 = pass / notice, Exit 2 = lint failure (blocked).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custos_lib as cl  # noqa: E402

PY_EXT = {".py"}
JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}


def _run(cmd: list[str], cwd: str | None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=120
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, f"CUSTOS could not run {cmd[0]}: {exc}"
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def lint_python(path: str, cwd: str | None) -> tuple[int, str, str]:
    if shutil.which("ruff"):
        code, out = _run(["ruff", "check", path], cwd)
        return code, out, "ruff"
    # py_compile is always present with any CPython.
    code, out = _run([sys.executable, "-m", "py_compile", path], cwd)
    return code, out, "py_compile"


def lint_js(path: str, cwd: str | None) -> tuple[int, str, str]:
    if shutil.which("eslint"):
        code, out = _run(["eslint", path], cwd)
        return code, out, "eslint"
    if shutil.which("npx"):
        code, out = _run(["npx", "--no-install", "eslint", path], cwd)
        # npx --no-install returns non-zero if eslint absent; treat as "no tool".
        if "could not determine executable" in out or "not found" in out.lower():
            return -1, "eslint not installed", "eslint"
        return code, out, "eslint"
    return -1, "eslint not installed", "eslint"


def main() -> int:
    payload = cl.read_payload()
    path = cl.target_path(payload)
    if not path:
        return 0
    cwd = payload.get("cwd")
    abspath = path if os.path.isabs(path) else os.path.join(cwd or os.getcwd(), path)
    if not os.path.exists(abspath):
        return 0

    ext = os.path.splitext(abspath)[1].lower()
    if ext in PY_EXT:
        code, out, tool = lint_python(abspath, cwd)
    elif ext in JS_EXT:
        code, out, tool = lint_js(abspath, cwd)
    else:
        return 0  # no linter wired for this language yet

    if code == -1:
        # Preferred linter missing -> non-blocking notice.
        cl.record(
            payload,
            f"lint_dispatch:{tool}",
            [{"kind": "linter-missing", "text": out}],
            blocked=False,
        )
        cl.emit_context(
            f"CUSTOS static-analysis notice: {tool} not installed, skipped {path}. "
            f"Install it to enforce this gate."
        )
        return 0

    if code != 0:
        findings = [{"kind": "lint-error", "text": out[:4000]}]
        cl.record(payload, f"lint_dispatch:{tool}", findings, blocked=True)
        cl.block(
            f"CUSTOS static-analysis gate BLOCKED {path} via {tool} "
            f"(exit {code}):\n{out[:4000]}"
        )
        return 2  # not reached

    cl.record(payload, f"lint_dispatch:{tool}", [], blocked=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
