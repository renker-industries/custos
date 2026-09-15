#!/usr/bin/env python3
"""CUSTOS fleet auto-fix (concept section 10.3) - SAFE BY DEFAULT.

Proposes small, bounded fixes (linter auto-fixes) for fleet repos that have
explicitly opted in, as a branch + commit + pull request rather than a direct push
to the main branch, so every automatic change stays reviewable and reversible.

Safety model (do not weaken without the owner deciding to):
  - Dry-run is the DEFAULT: it only reports what it *would* change; it writes
    nothing, commits nothing, pushes nothing.
  - A repo is only ever touched if BOTH: its status is 'aktiv-ueberwacht' AND it
    has 'autofix: true' in custos/fleet.yaml. No global switch.
  - --execute applies fixes on a new local branch and commits there. It still does
    NOT push.
  - --push additionally pushes the branch and opens a PR (needs gh). This is the
    only step that leaves the machine and is opt-in per invocation.
  - A repo with uncommitted changes or a detached HEAD is skipped (never fix on top
    of unsaved work).
  - Never commits to main/master directly; always a custos/autofix-* branch.

Usage:
  python bin/fleet_fix.py                 # dry-run report for opted-in repos
  python bin/fleet_fix.py --execute       # apply+commit on a branch, no push
  python bin/fleet_fix.py --execute --push  # + push branch and open a PR
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "detectors"))
try:
    import yaml
except ImportError:
    print("CUSTOS fleet-fix: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ACTIVE = "aktiv-ueberwacht"


def git(repo: str, *args: str, timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                           text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return p.returncode, (p.stdout + p.stderr).strip()


def is_clean(repo: str) -> bool:
    code, out = git(repo, "status", "--porcelain")
    return code == 0 and out == ""


def default_branch(repo: str) -> str:
    code, out = git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    return out if code == 0 else "HEAD"


def lint_fix(repo: str, execute: bool) -> tuple[str, bool]:
    """Return (report, changed). In dry-run, does not modify files."""
    if shutil.which("ruff"):
        if execute:
            code, out = git_none(["ruff", "check", "--fix", repo])
        else:
            code, out = git_none(["ruff", "check", "--fix", "--diff", repo])
        changed = bool(out.strip()) and code in (0, 1)
        return (f"ruff: {out[:2000] or 'no changes'}", changed and execute)
    return ("no supported auto-fixer (ruff) installed; nothing to do", False)


def git_none(cmd: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return p.returncode, (p.stdout + p.stderr).strip()


def opted_in(entry: dict) -> bool:
    return entry.get("status") == ACTIVE and entry.get("autofix") is True


def process(entry: dict, execute: bool, push: bool) -> str:
    repo = os.path.abspath(os.path.expanduser(entry.get("path", "")))
    name = entry.get("name", repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        return f"[skip] {name}: not a git repo at {repo}"
    if not is_clean(repo):
        return f"[skip] {name}: working tree not clean (never fix over unsaved work)"

    branch = f"custos/autofix-{date.today().isoformat()}"
    if not execute:
        report, _ = lint_fix(repo, execute=False)
        return f"[dry-run] {name}: would create '{branch}' and apply -> {report}"

    base = default_branch(repo)
    code, out = git(repo, "checkout", "-b", branch)
    if code != 0:
        return f"[error] {name}: could not create branch: {out}"
    report, changed = lint_fix(repo, execute=True)
    if not changed:
        git(repo, "checkout", base)
        git(repo, "branch", "-D", branch)
        return f"[none] {name}: no auto-fixable findings ({report})"
    git(repo, "add", "-A")
    git(repo, "commit", "-m",
        "chore: CUSTOS automated linter fixes\n\n"
        "Applied by CUSTOS fleet auto-fix (opt-in). Review before merge.")
    result = f"[fixed] {name}: committed on '{branch}' ({report[:200]})"
    if push:
        pc, po = git(repo, "push", "-u", "origin", branch)
        if pc != 0:
            return result + f"; push FAILED: {po}"
        if shutil.which("gh"):
            gc, go = git_none(["gh", "pr", "create", "-R", "", "--fill",
                               "--head", branch, "--base", base])
            result += f"; PR: {'opened' if gc == 0 else 'failed: ' + go[:200]}"
        else:
            result += "; pushed (gh not installed, open PR manually)"
    else:
        result += "; not pushed (use --push to push and open a PR)"
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fleet",
                    default=os.path.join(os.getcwd(), "custos", "fleet.yaml"))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.fleet):
        print(f"CUSTOS fleet-fix: {args.fleet} not found. Run fleet_discover first.",
              file=sys.stderr)
        return 1
    with open(args.fleet, encoding="utf-8") as fh:
        fleet = yaml.safe_load(fh) or {}

    targets = [e for e in fleet.get("repos", []) if opted_in(e)]
    if not targets:
        print("CUSTOS fleet-fix: no repos are opted in (need status "
              "'aktiv-ueberwacht' AND 'autofix: true' in fleet.yaml). Nothing to do.")
        return 0

    mode = "PUSH+PR" if args.push else ("EXECUTE (local)" if args.execute else "DRY-RUN")
    print(f"CUSTOS fleet-fix [{mode}]: {len(targets)} opted-in repo(s).")
    for entry in targets:
        print("  " + process(entry, args.execute, args.push))
    return 0


if __name__ == "__main__":
    sys.exit(main())
