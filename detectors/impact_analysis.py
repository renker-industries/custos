#!/usr/bin/env python3
"""CUSTOS impact analysis (PostToolUse on Write|Edit, concept section 8).

When a function/class is changed, its callers elsewhere may need to change too. A
change that updates a definition but leaves a caller untouched is a classic silent
regression. This detector extracts the symbols defined in the edited file and
searches the repo for other files that reference them, surfacing likely callers to
re-check. Non-blocking (additionalContext) — it warns, it does not guess intent.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custos_lib as cl  # noqa: E402

DEF = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(?:def|function|class|func|fn)\s+([A-Za-z_]\w+)"
    r"|^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_]\w+)\s*=\s*(?:async\s*)?\("
)
PRUNE = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rb",
            ".php", ".java", ".rs", ".c", ".cpp", ".h"}


def symbols(text: str) -> list[str]:
    names: set[str] = set()
    for line in text.splitlines():
        m = DEF.match(line)
        if m:
            name = m.group(1) or m.group(2)
            if name and len(name) >= 3 and name not in {"main", "test"}:
                names.add(name)
    return sorted(names)


def find_callers(cwd: str, names: list[str], skip_abs: str) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {n: [] for n in names}
    patterns = {n: re.compile(r"\b" + re.escape(n) + r"\s*\(") for n in names}
    for dirpath, dirnames, files in os.walk(cwd):
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        for f in files:
            if os.path.splitext(f)[1].lower() not in CODE_EXT:
                continue
            fpath = os.path.join(dirpath, f)
            if os.path.abspath(fpath) == skip_abs:
                continue
            try:
                with open(fpath, encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
            except OSError:
                continue
            for n, pat in patterns.items():
                if pat.search(content):
                    rel = os.path.relpath(fpath, cwd).replace(os.sep, "/")
                    if rel not in hits[n]:
                        hits[n].append(rel)
    return hits


def main() -> int:
    payload = cl.read_payload()
    path = cl.target_path(payload)
    text = cl.changed_text(payload)
    if not path or not text:
        return 0
    cwd = payload.get("cwd") or os.getcwd()
    ext = os.path.splitext(path)[1].lower()
    if ext not in CODE_EXT:
        return 0

    names = symbols(text)
    if not names:
        return 0

    abspath = path if os.path.isabs(path) else os.path.join(cwd, path)
    hits = find_callers(cwd, names, os.path.abspath(abspath))
    affected = {n: fs for n, fs in hits.items() if fs}
    if not affected:
        cl.record(payload, "impact_analysis", [], blocked=False)
        return 0

    findings = [{"symbol": n, "callers": fs[:20]} for n, fs in affected.items()]
    cl.record(payload, "impact_analysis", findings, blocked=False)
    summary = "; ".join(
        f"{n} referenced in {len(fs)} file(s): {', '.join(fs[:5])}"
        for n, fs in affected.items()
    )
    cl.emit_context(
        f"CUSTOS impact analysis for {path}: changed symbol(s) are referenced "
        f"elsewhere - verify these callers still match: {summary}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
