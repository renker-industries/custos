#!/usr/bin/env python3
"""CUSTOS accessibility / frontend check (PostToolUse on *.tsx|jsx|vue|html).

Concept section 8/9: basic, model-free accessibility checks on frontend files -
missing image alt text, controls without an accessible name, inputs without a
label/aria, and a missing lang on <html>. This is a fast first pass (not a full
axe-core run, which is a later, heavier integration).

Below the block threshold it surfaces findings as context; at/above it blocks
(exit 2) so obviously inaccessible markup does not land silently.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custos_lib as cl  # noqa: E402

BLOCK_THRESHOLD = int(os.environ.get("CUSTOS_A11Y_THRESHOLD", "5"))
EXT = {".tsx", ".jsx", ".vue", ".html", ".htm"}

_IMG = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
_HAS_ALT = re.compile(r"\balt\s*=", re.IGNORECASE)
_INPUT = re.compile(r"<input\b[^>]*>", re.IGNORECASE | re.DOTALL)
_HAS_ARIA_LABEL = re.compile(r"\b(aria-label|aria-labelledby|id)\s*=", re.IGNORECASE)
_INPUT_TYPE_EXEMPT = re.compile(r'\btype\s*=\s*["\'](hidden|submit|button|reset)["\']',
                                re.IGNORECASE)
# button/anchor with no text and no aria-label -> icon-only control без Namen
_EMPTY_CTRL = re.compile(
    r"<(button|a)\b(?![^>]*\baria-label)(?![^>]*\baria-labelledby)[^>]*>\s*</\1>",
    re.IGNORECASE,
)
_HTML_TAG = re.compile(r"<html\b([^>]*)>", re.IGNORECASE)
_HTML_HAS_LANG = re.compile(r"\blang\s*=", re.IGNORECASE)


def line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def analyse(text: str) -> list[dict]:
    findings: list[dict] = []

    for m in _IMG.finditer(text):
        if not _HAS_ALT.search(m.group(0)):
            findings.append({"line": line_of(text, m.start()), "kind": "img-no-alt"})

    for m in _INPUT.finditer(text):
        tag = m.group(0)
        if _INPUT_TYPE_EXEMPT.search(tag):
            continue
        if not _HAS_ARIA_LABEL.search(tag):
            findings.append({"line": line_of(text, m.start()),
                             "kind": "input-no-label"})

    for m in _EMPTY_CTRL.finditer(text):
        findings.append({"line": line_of(text, m.start()),
                         "kind": "control-no-accessible-name"})

    for m in _HTML_TAG.finditer(text):
        if not _HTML_HAS_LANG.search(m.group(1)):
            findings.append({"line": line_of(text, m.start()), "kind": "html-no-lang"})

    return findings


def main() -> int:
    payload = cl.read_payload()
    path = cl.target_path(payload)
    text = cl.changed_text(payload)
    if not path or not text:
        return 0
    if os.path.splitext(path)[1].lower() not in EXT:
        return 0

    findings = analyse(text)
    if not findings:
        cl.record(payload, "a11y_frontend_check", [], blocked=False)
        return 0

    summary = "; ".join(f"L{f['line']} {f['kind']}" for f in findings[:12])
    if len(findings) >= BLOCK_THRESHOLD:
        cl.record(payload, "a11y_frontend_check", findings, blocked=True)
        cl.block(
            f"CUSTOS a11y gate BLOCKED {path}: {len(findings)} accessibility "
            f"issue(s) (threshold {BLOCK_THRESHOLD}). {summary}."
        )
        return 2  # not reached

    cl.record(payload, "a11y_frontend_check", findings, blocked=False)
    cl.emit_context(
        f"CUSTOS a11y notice for {path}: {len(findings)} issue(s): {summary}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
