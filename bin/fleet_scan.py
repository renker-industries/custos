#!/usr/bin/env python3
"""CUSTOS fleet-wide content scan (concept sections 10.2, 15.2) - READ ONLY.

Applies the CUSTOS checks that work without repo-specific configuration to every
repo marked 'aktiv-ueberwacht' in custos/fleet.yaml, and collects a findings
report per repo in custos/fleet_findings.json.

Checks (all read-only; NEVER writes/commits/pushes into a scanned repo):
  - language detection (file-extension counts)
  - lint / static analysis: reuses the same tools as lint_dispatch.py at repo
    level - ruff for Python, eslint for JS/TS - only if the tool is available;
    a missing tool is recorded as "skipped: tool fehlt", not as an error.
  - AI-slop: the ai_slop_detector.analyse() pass over source files.
  - secrets: a repo-independent pattern scan (private keys, cloud keys, tokens,
    hardcoded passwords) - matches are recorded redacted.

Severity: secrets = high, lint errors = medium, ai-slop = low.

Usage:
  python bin/fleet_scan.py [--fleet custos/fleet.yaml]
      [--out custos/fleet_findings.json] [--max-files 4000]
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "detectors"))
import ai_slop_detector as slop  # noqa: E402  (reuse analyse())

try:
    import yaml
except ImportError:
    print("CUSTOS fleet-scan: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ACTIVE = "aktiv-ueberwacht"
PRUNE = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
         ".next", ".mypy_cache", ".ruff_cache", "vendor", ".idea", ".gradle",
         "site-packages", ".tox", ".pytest_cache", "Pods"}
# Also prune bundled interpreters / virtualenvs by directory name pattern
# (e.g. .python312, python3.12, virtualenv) - these hold dependencies, not
# authored code, and otherwise dominate the scan with false findings. Kept narrow
# so legitimate source dirs like bin/ or lib/ are NOT skipped.
PRUNE_RE = re.compile(r"^(\.?python[\d.]*|\.?virtualenv)$", re.IGNORECASE)
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rb",
            ".php", ".java", ".rs", ".c", ".cpp", ".h", ".cs", ".swift", ".kt"}
TEXT_EXT = CODE_EXT | {".json", ".yaml", ".yml", ".toml", ".env", ".ini", ".cfg",
                       ".sh", ".ps1", ".txt", ".md", ".xml", ".html", ".vue"}
MAX_BYTES = 512 * 1024
# Generated / vendored / lock files: exclude from content checks to avoid noise
# (a minified bundle yields thousands of false slop hits and is not authored code).
SKIP_FILE = re.compile(
    r"(\.min\.(js|css)$|\.bundle\.js$|\.map$|-lock\.(json|yaml)$|"
    r"^package-lock\.json$|^yarn\.lock$|^pnpm-lock\.yaml$|^poetry\.lock$|"
    r"\.generated\.|\.g\.dart$)", re.IGNORECASE)
MAX_LINE = 2000  # a file with a longer max line is treated as minified/generated

# Secret patterns (redacted on record). Repo-independent.
SECRET_PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}")),
    ("github-token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,}")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}")),
    ("generic-secret-assign", re.compile(
        r"(?i)\b(api[_-]?key|secret|token|passwd|password)\b\s*[:=]\s*"
        r"['\"][^'\"\s]{8,}['\"]")),
]
# Reduce false positives from obvious placeholders.
PLACEHOLDER = re.compile(r"(?i)(example|placeholder|your[_-]?|xxx|<[^>]+>|dummy|"
                         r"changeme|test123|\.\.\.)")


def walk_files(root: str, max_files: int) -> list[str]:
    out = []
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in PRUNE and not PRUNE_RE.match(d)]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if SKIP_FILE.search(f):
                continue
            if ext in TEXT_EXT or f in (".env",):
                out.append(os.path.join(dirpath, f))
                if len(out) >= max_files:
                    return out
    return out


def read_text(path: str) -> str | None:
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return None
    # Minified/generated heuristic: a very long single line is not authored code.
    if text and max((len(ln) for ln in text.splitlines()), default=0) > MAX_LINE:
        return None
    return text


def detect_languages(files: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in CODE_EXT:
            counts[ext] = counts.get(ext, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def run(cmd: list[str], cwd: str) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -2, str(exc)
    return p.returncode, (p.stdout + p.stderr)


def lint_repo(repo: str, langs: dict[str, int]) -> dict:
    """Repo-level lint reusing lint_dispatch's tools (ruff/eslint). Missing tool
    -> skipped, not error. py_compile-per-file is intentionally not run fleet-wide
    (too noisy); see DECISIONS.md."""
    result = {"tools": [], "issues": 0, "skipped": []}
    has_py = any(e == ".py" for e in langs)
    has_js = any(e in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"} for e in langs)

    if has_py:
        if shutil.which("ruff"):
            code, out = run(["ruff", "check", "--quiet", "."], repo)
            n = len([ln for ln in out.splitlines() if ln.strip()]) if code == 1 else 0
            result["tools"].append("ruff")
            result["issues"] += n
        else:
            result["skipped"].append("python: ruff fehlt")
    if has_js:
        eslint = shutil.which("eslint")
        if eslint:
            code, out = run([eslint, "."], repo)
            result["tools"].append("eslint")
            result["issues"] += 0 if code == 0 else 1
        else:
            result["skipped"].append("js/ts: eslint fehlt")
    return result


def slop_scan(files: list[str]) -> int:
    total = 0
    for f in files:
        if os.path.splitext(f)[1].lower() not in CODE_EXT:
            continue
        text = read_text(f)
        if text is None:
            continue
        total += len(slop.analyse(text))
    return total


def secret_scan(files: list[str], repo: str) -> list[dict]:
    hits = []
    for f in files:
        text = read_text(f)
        if text is None:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if PLACEHOLDER.search(line):
                continue
            for kind, pat in SECRET_PATTERNS:
                m = pat.search(line)
                if m:
                    rel = os.path.relpath(f, repo).replace(os.sep, "/")
                    snippet = m.group(0)
                    redacted = snippet[:4] + "***" if len(snippet) > 6 else "***"
                    hits.append({"kind": kind, "file": rel, "line": i,
                                 "match": redacted})
                    break
    return hits


def scan_repo(entry: dict, max_files: int) -> dict:
    repo = os.path.abspath(os.path.expanduser(entry.get("path", "")))
    name = entry.get("name", repo)
    ts = datetime.now(timezone.utc).isoformat()
    if not repo or not os.path.isdir(repo):
        return {"repo": name, "timestamp": ts, "status": "error",
                "detail": f"path not found: {repo}"}

    files = walk_files(repo, max_files)
    langs = detect_languages(files)
    lint = lint_repo(repo, langs)
    slop_n = slop_scan(files)
    secrets = secret_scan(files, repo)

    severity = "none"
    if secrets:
        severity = "high"
    elif lint["issues"] > 0:
        severity = "medium"
    elif slop_n > 0:
        severity = "low"

    return {
        "repo": name,
        "path": repo,
        "timestamp": ts,
        "status": "scanned",
        "filesScanned": len(files),
        "languages": langs,
        "findings": {
            "secrets": secrets,
            "lintIssues": lint["issues"],
            "lintTools": lint["tools"],
            "aiSlop": slop_n,
        },
        "severity": severity,
        "skipped": lint["skipped"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fleet", default=os.path.join("custos", "fleet.yaml"))
    ap.add_argument("--out", default=os.path.join("custos", "fleet_findings.json"))
    ap.add_argument("--max-files", type=int, default=4000)
    args = ap.parse_args()

    if not os.path.exists(args.fleet):
        print(f"CUSTOS fleet-scan: {args.fleet} not found.", file=sys.stderr)
        return 1
    with open(args.fleet, encoding="utf-8") as fh:
        fleet = yaml.safe_load(fh) or {}

    targets = [e for e in fleet.get("repos", [])
               if e.get("status") == ACTIVE and e.get("path")]
    print(f"CUSTOS fleet-scan (read-only): {len(targets)} repo(s) marked "
          f"{ACTIVE}.")

    results = []
    tot_secrets = tot_lint = tot_slop = tot_skipped = 0
    for entry in targets:
        r = scan_repo(entry, args.max_files)
        results.append(r)
        if r.get("status") == "scanned":
            fnd = r["findings"]
            tot_secrets += len(fnd["secrets"])
            tot_lint += fnd["lintIssues"]
            tot_slop += fnd["aiSlop"]
            tot_skipped += len(r["skipped"])
            print(f"  [{r['severity']:>6}] {r['repo']}: "
                  f"{len(fnd['secrets'])} secrets, {fnd['lintIssues']} lint, "
                  f"{fnd['aiSlop']} slop; {len(r['skipped'])} skipped")
        else:
            print(f"  [ error] {r['repo']}: {r.get('detail')}")

    import json
    report = {
        "schema": 1,
        "generated": datetime.now(timezone.utc).isoformat(),
        "repos": results,
        "totals": {"secrets": tot_secrets, "lintIssues": tot_lint,
                   "aiSlop": tot_slop, "skippedChecks": tot_skipped,
                   "reposScanned": sum(1 for r in results
                                       if r.get("status") == "scanned")},
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"CUSTOS fleet-scan: totals - {tot_secrets} secrets, {tot_lint} lint, "
          f"{tot_slop} slop, {tot_skipped} checks skipped -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
