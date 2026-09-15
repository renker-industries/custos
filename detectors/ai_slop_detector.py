#!/usr/bin/env python3
"""CUSTOS AI-Slop detector (PostToolUse on Write|Edit).

Independent, model-free static pass over freshly written/edited content, looking
for the tell-tale patterns of low-effort AI code: filler comments, generic
throwaway names, obvious duplicate lines, and needless one-line wrapper
abstractions. Below the threshold it surfaces the findings as context; at or
above it, it blocks (exit 2) so slop cannot silently land.

Language-agnostic on purpose — it reads text, not an AST — so it works on any
file a coding agent writes.

Usage: receives the Claude Code hook payload as JSON on stdin.
Exit 0 = pass or non-blocking notice, Exit 2 = blocked.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custos_lib as cl  # noqa: E402

# Findings at or above this count fail the gate (fail-closed).
BLOCK_THRESHOLD = int(os.environ.get("CUSTOS_SLOP_THRESHOLD", "5"))

# Comment prefixes across common languages.
_COMMENT = re.compile(r"^\s*(//|#|--|\*|/\*)\s*(.*)$")

# Filler comments that restate the obvious.
_FILLER_COMMENT = re.compile(
    r"\b("
    r"increment (the )?(counter|value|variable|index)( by (one|1))?"
    r"|add (one|1) to"
    r"|loop (over|through) (the )?(items|elements|array|list)"
    r"|return (the )?(result|value|output)"
    r"|set (the )?variable"
    r"|declare (a|the) variable"
    r"|create (a|the) (new )?(object|instance|array|list)"
    r"|call (the )?function"
    r"|this (is|will) (a|the)?\s*(placeholder|dummy|example)"
    r"|end of (the )?(function|loop|class|file)"
    r"|start of (the )?(function|loop|class)"
    r"|initialize (the )?(variable|value|counter)"
    r")\b",
    re.IGNORECASE,
)

# Generic throwaway identifiers in declarations.
_GENERIC_NAME = re.compile(
    r"\b(?:let|const|var|def|func|fn|function)\s+"
    r"(data|data2|temp|tmp|foo|bar|baz|thing|stuff|obj|obj2|res|res2|val|val2|"
    r"result2|myVar|myFunction|test123|asdf|xxx)\b"
)

# Trivial one-line wrapper: def/function that only returns another call.
_WRAPPER = re.compile(
    r"^\s*(?:def|function|fn|func|const)\s+\w+.*?[:{(].*?\breturn\s+\w+\([^;{]*\)\s*[;}]?\s*$"
)


def analyse(text: str) -> list[dict]:
    findings: list[dict] = []
    lines = text.splitlines()
    seen_nonblank: dict[str, int] = {}

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        m = _COMMENT.match(line)
        if m and _FILLER_COMMENT.search(m.group(2)):
            findings.append({"line": i, "kind": "filler-comment", "text": stripped})

        if _GENERIC_NAME.search(line):
            findings.append({"line": i, "kind": "generic-name", "text": stripped})

        if _WRAPPER.match(line):
            findings.append({"line": i, "kind": "trivial-wrapper", "text": stripped})

        # Duplicate non-trivial code line (ignore short lines / pure braces).
        if len(stripped) >= 12 and not _COMMENT.match(line):
            if stripped in seen_nonblank:
                findings.append(
                    {
                        "line": i,
                        "kind": "duplicate-line",
                        "text": stripped,
                        "first_seen_line": seen_nonblank[stripped],
                    }
                )
            else:
                seen_nonblank[stripped] = i

    return findings


def main() -> int:
    payload = cl.read_payload()
    path = cl.target_path(payload)
    text = cl.changed_text(payload)
    if not text:
        return 0

    findings = analyse(text)
    if not findings:
        cl.record(payload, "ai_slop_detector", [], blocked=False)
        return 0

    summary = "; ".join(
        f"L{f['line']} {f['kind']}" for f in findings[:12]
    )
    threshold = 1 if cl.zero_tolerance(payload) else BLOCK_THRESHOLD
    if len(findings) >= threshold:
        cl.record(payload, "ai_slop_detector", findings, blocked=True)
        cl.block(
            f"CUSTOS ai-slop gate BLOCKED {path}: {len(findings)} findings "
            f"(threshold {threshold}). {summary}. "
            f"Clean these up before continuing."
        )
        return 2  # not reached; cl.block exits

    cl.record(payload, "ai_slop_detector", findings, blocked=False)
    cl.emit_context(
        f"CUSTOS ai-slop notice for {path}: {len(findings)} finding(s): {summary}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
