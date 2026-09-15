#!/usr/bin/env python3
"""Record plan approval for the CUSTOS plan gate.

Called by the plan-reviewer agent when it returns APPROVED. Sets
plan.approved = true and stores the approved file scope (globs) that the
scope-guard then enforces during build.

Usage:
  python bin/custos_approve_plan.py --reviewer plan-reviewer \
      --scope "src/**" --scope "tests/**"
  python bin/custos_approve_plan.py --reset   # revoke approval (new task)
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "detectors"))
import custos_state as st  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviewer", default="plan-reviewer")
    ap.add_argument("--scope", action="append", default=[], dest="scope")
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--cwd", default=os.getcwd())
    args = ap.parse_args()

    state = st.load(args.cwd)
    if args.reset:
        state["plan"] = {"approved": False, "scope": [], "reviewer": None,
                         "ts": st.now()}
        st.save(state, args.cwd)
        print("CUSTOS: plan approval reset.")
        return 0

    state["plan"] = {
        "approved": True,
        "scope": args.scope,
        "reviewer": args.reviewer,
        "ts": st.now(),
    }
    st.save(state, args.cwd)
    print(f"CUSTOS: plan approved by {args.reviewer}; scope={args.scope or '[any]'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
