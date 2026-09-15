#!/usr/bin/env python3
"""CUSTOS code-council decision recorder (concept sections 6, 9, 16).

When static analysis and the model disagree on a finding, five council-advisor
agents vote and the council-chair decides. This tool writes that binding decision
to the audit log (custos_findings.json) and, for a suppression, records it in
custos_suppressions.json WITH A MANDATORY EXPIRY DATE - there is no silent or
permanent self-granted exception (concept section 16).

Usage:
  python bin/council_log.py --finding "SQLi in q()" --decision uphold \
      --votes "4 uphold, 1 dismiss" --rationale "reachable with user input"
  python bin/council_log.py --finding "ruff E501 in legacy.py" --decision suppress \
      --expiry 2026-12-31 --votes "3 suppress, 2 uphold" --rationale "cosmetic"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone

FINDINGS = "custos_findings.json"
SUPPRESSIONS = "custos_suppressions.json"


def append_json_list(path: str, key: str, entry: dict) -> None:
    store: dict = {"schema": 1, key: []}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict) and isinstance(loaded.get(key), list):
                store = loaded
        except (OSError, json.JSONDecodeError):
            pass
    store[key].append(entry)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2, ensure_ascii=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--finding", required=True)
    ap.add_argument("--decision", required=True,
                    choices=["uphold", "dismiss", "suppress"])
    ap.add_argument("--votes", default="")
    ap.add_argument("--rationale", default="")
    ap.add_argument("--expiry", default="")
    ap.add_argument("--cwd", default=os.getcwd())
    args = ap.parse_args()

    if args.decision == "suppress":
        if not args.expiry:
            print("CUSTOS council: a suppression REQUIRES --expiry YYYY-MM-DD "
                  "(no permanent silent exceptions).", file=sys.stderr)
            return 2
        try:
            exp = date.fromisoformat(args.expiry)
        except ValueError:
            print(f"CUSTOS council: invalid --expiry '{args.expiry}' "
                  "(use YYYY-MM-DD).", file=sys.stderr)
            return 2
        if exp <= date.today():
            print(f"CUSTOS council: --expiry {args.expiry} must be in the future.",
                  file=sys.stderr)
            return 2

    ts = datetime.now(timezone.utc).isoformat()
    entry = {
        "timestamp": ts,
        "detector": "council",
        "finding": args.finding,
        "decision": args.decision,
        "votes": args.votes,
        "rationale": args.rationale,
    }
    if args.decision == "suppress":
        entry["expiry"] = args.expiry
    append_json_list(os.path.join(args.cwd, FINDINGS), "runs", entry)

    if args.decision == "suppress":
        append_json_list(os.path.join(args.cwd, SUPPRESSIONS), "suppressions", {
            "timestamp": ts, "finding": args.finding, "expiry": args.expiry,
            "rationale": args.rationale, "votes": args.votes,
        })
        print(f"CUSTOS council: suppression recorded for '{args.finding}' "
              f"until {args.expiry}.")
    else:
        print(f"CUSTOS council: decision '{args.decision}' recorded for "
              f"'{args.finding}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
