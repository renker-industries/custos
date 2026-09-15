#!/usr/bin/env python3
"""CUSTOS self-qualification runner (concept section 12).

Runs the reference test suite (the gates against known fixtures) and records the
result as a release metric in custos_findings.json. This is the dogfooding gate:
CUSTOS must pass its own proof obligation before it is considered releasable.

Usage:
  python bin/selfqual.py
Exit 0 if the suite passes, 1 otherwise.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDINGS = os.path.join(ROOT, "custos_findings.json")


def main() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests",
         "-p", "test_*.py", "-v"],
        cwd=ROOT, capture_output=True, text=True,
    )
    out = proc.stdout + proc.stderr
    m = re.search(r"Ran (\d+) tests? in ([\d.]+)s", out)
    total = int(m.group(1)) if m else 0
    duration = float(m.group(2)) if m else 0.0
    passed = proc.returncode == 0
    fails = len(re.findall(r"^(FAIL|ERROR):", out, re.MULTILINE))

    metric = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detector": "selfqual",
        "suite": "tests/",
        "tests": total,
        "failures": fails,
        "passed": passed,
        "durationSeconds": duration,
    }
    store = {"schema": 1, "runs": []}
    if os.path.exists(FINDINGS):
        try:
            with open(FINDINGS, encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict) and isinstance(loaded.get("runs"), list):
                store = loaded
        except (OSError, json.JSONDecodeError):
            pass
    store["runs"].append(metric)
    try:
        with open(FINDINGS, "w", encoding="utf-8") as fh:
            json.dump(store, fh, indent=2, ensure_ascii=False)
    except OSError:
        pass

    status = "PASS" if passed else "FAIL"
    print(f"CUSTOS self-qualification: {status} - {total} tests, {fails} failing, "
          f"{duration:.2f}s. Metric logged.")
    if not passed:
        print(out[-2000:], file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
