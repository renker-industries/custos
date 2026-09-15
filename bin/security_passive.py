#!/usr/bin/env python3
"""CUSTOS passive security hardening checks (concept section 15.3).

Local, observational only. No packet leaves the machine, nothing is attacked,
nothing is changed. These checks are safe to run repeatedly / on a schedule. They
follow the CUSTOS proof logic: instead of claiming "the box is secure", they run
real tools and write a timestamped report to custos_findings.json.

Active scans (nmap/ZAP, section 15.4) are deliberately NOT here — those require a
populated, human-approved custos/scope.yaml and are a later phase.

Per platform it runs whichever tools are installed; missing tools are recorded as
a skipped check (with an install hint), never as a pass.

Usage:
  python bin/security_passive.py [--json]   # --json prints the report to stdout
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

PROOF_LOG = "custos_findings.json"

# (id, platforms, description, argv, required_tool)
CHECKS: list[tuple[str, set[str], str, list[str], str]] = [
    # Windows
    (
        "win-defender",
        {"win32"},
        "Windows Defender status",
        ["powershell", "-NoProfile", "-Command",
         "Get-MpComputerStatus | Select-Object AMServiceEnabled,"
         "RealTimeProtectionEnabled,AntivirusSignatureLastUpdated | Format-List"],
        "powershell",
    ),
    (
        "win-listening-ports",
        {"win32"},
        "Listening TCP ports",
        ["netstat", "-ano", "-p", "tcp"],
        "netstat",
    ),
    (
        "win-autostart",
        {"win32"},
        "Autostart entries",
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_StartupCommand | "
         "Select-Object Name,Command,Location | Format-Table -Auto"],
        "powershell",
    ),
    (
        "win-upgradable",
        {"win32"},
        "Pending package upgrades (winget, read-only)",
        ["winget", "upgrade"],
        "winget",
    ),
    # Linux
    (
        "lynis-audit",
        {"linux"},
        "Lynis hardening audit",
        ["lynis", "audit", "system", "--quick", "--quiet"],
        "lynis",
    ),
    (
        "rkhunter",
        {"linux"},
        "rkhunter rootkit check",
        ["rkhunter", "--check", "--sk", "--nocolors"],
        "rkhunter",
    ),
    (
        "chkrootkit",
        {"linux"},
        "chkrootkit rootkit check",
        ["chkrootkit", "-q"],
        "chkrootkit",
    ),
    (
        "linux-sockets",
        {"linux"},
        "Open listening sockets",
        ["ss", "-tulpn"],
        "ss",
    ),
    (
        "linux-services",
        {"linux"},
        "Running services",
        ["systemctl", "list-units", "--type=service", "--state=running",
         "--no-pager"],
        "systemctl",
    ),
    (
        "linux-firewall",
        {"linux"},
        "Firewall (ufw) status",
        ["ufw", "status", "verbose"],
        "ufw",
    ),
    (
        "linux-upgradable",
        {"linux"},
        "Pending apt upgrades",
        ["apt", "list", "--upgradable"],
        "apt",
    ),
]

SSHD_CONFIG = "/etc/ssh/sshd_config"


def current_platform() -> str:
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "win32":
        return "win32"
    if sys.platform == "darwin":
        return "darwin"
    return sys.platform


def run_check(argv: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=600
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, f"could not run: {exc}"
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def inspect_sshd() -> dict:
    """Read-only SSH hardening inspection (no tool needed)."""
    if not os.path.exists(SSHD_CONFIG):
        return {"id": "linux-ssh", "status": "skipped",
                "detail": f"{SSHD_CONFIG} not present"}
    findings = []
    try:
        with open(SSHD_CONFIG, encoding="utf-8", errors="replace") as fh:
            lines = [ln.strip() for ln in fh
                     if ln.strip() and not ln.strip().startswith("#")]
    except OSError as exc:
        return {"id": "linux-ssh", "status": "error", "detail": str(exc)}
    joined = "\n".join(lines).lower()
    if "permitrootlogin yes" in joined:
        findings.append("PermitRootLogin yes (root login enabled)")
    if "passwordauthentication yes" in joined:
        findings.append("PasswordAuthentication yes (password login enabled)")
    return {
        "id": "linux-ssh",
        "status": "finding" if findings else "ok",
        "detail": "; ".join(findings) or "root login / password auth not enabled",
    }


def log_report(cwd: str, report: dict) -> None:
    path = os.path.join(cwd, PROOF_LOG)
    store: dict = {"schema": 1, "runs": []}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict) and isinstance(loaded.get("runs"), list):
                store = loaded
        except (OSError, json.JSONDecodeError):
            pass
    store["runs"].append(report)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(store, fh, indent=2, ensure_ascii=False)
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    plat = current_platform()
    results = []
    for cid, plats, desc, argv, tool in CHECKS:
        if plat not in plats:
            continue
        if not shutil.which(tool):
            results.append({
                "id": cid, "description": desc, "status": "skipped",
                "detail": f"{tool} not installed",
            })
            continue
        code, out = run_check(argv)
        results.append({
            "id": cid, "description": desc,
            "status": "ok" if code == 0 else ("error" if code == -1 else "review"),
            "exitCode": code,
            "output": out[:4000],
        })

    if plat == "linux":
        results.append(inspect_sshd())

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detector": "security_passive",
        "platform": plat,
        "checks": results,
    }
    log_report(os.getcwd(), report)

    ran = sum(1 for r in results if r["status"] not in ("skipped",))
    skipped = sum(1 for r in results if r["status"] == "skipped")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"CUSTOS passive security ({plat}): {len(results)} check(s), "
            f"{ran} ran, {skipped} skipped. Report -> {PROOF_LOG}"
        )
        for r in results:
            print(f"  [{r['status']:>7}] {r['id']} - {r.get('description','')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
