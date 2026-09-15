#!/usr/bin/env python3
"""CUSTOS fleet discovery (read-only, concept section 10.1-10.2).

Scans the configured root directories for git repositories and records them in
custos/fleet.yaml with a per-repo status. This is discovery only: it never writes
into a discovered repo and never edits anyone's code. Auto-fix / PR creation for
released repos is a later, opt-in phase (10.3) and is intentionally NOT here.

Status values (concept 10.1):
  - aktiv-ueberwacht  : gates are applied to this repo
  - nur-inventarisiert: found but not yet released (default for new finds)
  - ignoriert         : deliberately excluded (e.g. third-party forks)

Existing statuses in fleet.yaml are preserved on re-run; only genuinely new
repos are added as "nur-inventarisiert". The custos repo itself is kept as
"aktiv-ueberwacht" (a decided default, see DECISIONS.md).

Usage:
  python bin/fleet_discover.py [--fleet <path>] [--root <dir> ...]

Requires PyYAML (config files are .yaml per the concept). If PyYAML is missing,
it exits with a clear install hint rather than guessing.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    print(
        "CUSTOS fleet: PyYAML is required for .yaml config. Install with "
        "'pip install pyyaml'.",
        file=sys.stderr,
    )
    sys.exit(1)

ACTIVE = "aktiv-ueberwacht"
INVENTORY = "nur-inventarisiert"
IGNORED = "ignoriert"

PRUNE = {"node_modules", ".venv", "venv", "__pycache__", "site-packages"}


def repo_root_of(start: str) -> str | None:
    cur = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def git_remote(path: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", path, "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    url = proc.stdout.strip()
    return url or None


def discover(roots: list[str]) -> list[str]:
    """Return absolute paths of git repos under the given roots (repos not nested
    into each other: once a .git is found, that subtree is not descended)."""
    found: list[str] = []
    for root in roots:
        root = os.path.abspath(os.path.expanduser(root))
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, _files in os.walk(root):
            base = os.path.basename(dirpath)
            if base in PRUNE:
                dirnames[:] = []
                continue
            if ".git" in dirnames:
                found.append(os.path.abspath(dirpath))
                dirnames[:] = []  # do not descend into a repo
                continue
            dirnames[:] = [d for d in dirnames if d not in PRUNE and d != ".git"]
    return sorted(set(found))


def load_fleet(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            if isinstance(data, dict):
                data.setdefault("roots", [])
                data.setdefault("repos", [])
                return data
        except (OSError, yaml.YAMLError):
            pass
    return {"roots": [], "repos": []}


def main() -> int:
    ap = argparse.ArgumentParser()
    default_fleet = os.path.join(os.getcwd(), "custos", "fleet.yaml")
    ap.add_argument("--fleet", default=default_fleet)
    ap.add_argument("--root", action="append", default=[], dest="roots")
    args = ap.parse_args()

    fleet = load_fleet(args.fleet)
    roots = args.roots or fleet.get("roots") or []

    # Index existing repos by absolute path to preserve their status on re-run.
    existing: dict[str, dict] = {}
    for entry in fleet.get("repos", []):
        p = os.path.abspath(os.path.expanduser(entry.get("path", "")))
        existing[p] = entry

    # Always keep the custos repo itself as actively monitored.
    self_root = repo_root_of(os.path.dirname(os.path.abspath(__file__)))
    if self_root:
        e = existing.get(self_root, {})
        e.update({"name": "custos", "path": self_root, "status": ACTIVE})
        remote = git_remote(self_root)
        if remote:
            e["remote"] = remote
        existing[self_root] = e

    added = 0
    for path in discover(roots):
        if path in existing:
            continue
        entry = {
            "name": os.path.basename(path),
            "path": path,
            "status": INVENTORY,
        }
        remote = git_remote(path)
        if remote:
            entry["remote"] = remote
        existing[path] = entry
        added += 1

    out = {
        "roots": roots,
        "repos": sorted(existing.values(), key=lambda e: e.get("path", "")),
    }
    os.makedirs(os.path.dirname(args.fleet), exist_ok=True)
    with open(args.fleet, "w", encoding="utf-8") as fh:
        yaml.safe_dump(out, fh, allow_unicode=True, sort_keys=False)

    active = sum(1 for e in out["repos"] if e.get("status") == ACTIVE)
    inv = sum(1 for e in out["repos"] if e.get("status") == INVENTORY)
    ign = sum(1 for e in out["repos"] if e.get("status") == IGNORED)
    print(
        f"CUSTOS fleet: {len(out['repos'])} repo(s) "
        f"({active} aktiv-ueberwacht, {inv} nur-inventarisiert, {ign} ignoriert); "
        f"{added} new; roots={roots or '[none configured]'} -> {args.fleet}"
    )
    if not roots:
        print(
            "CUSTOS fleet: no roots configured. Add scan roots under 'roots:' in "
            "custos/fleet.yaml (see the ENTSCHEIDUNG NOETIG note).",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
