---
name: security-mode
description: >-
  CUSTOS security workflow. In this stage it runs only PASSIVE, local hardening
  checks (Defender/Lynis/rkhunter/ports/SSH/updates) that produce a timestamped
  report, and it maintains custos/scope.yaml as the hard precondition for any
  future active scan. Active scans (nmap/ZAP) are not enabled here.
---

# Security Mode (passive stage)

Security follows the same rule as the rest of CUSTOS: never the sentence "it is
secure", always a scan report with a timestamp in the same findings log.

## Passive Härtung (unkritisch, jederzeit)

```bash
python bin/security_passive.py          # human-readable summary
python bin/security_passive.py --json   # full report to stdout
```

- Local and observational only: nothing leaves the machine, nothing is changed.
- Runs whatever is installed for the current OS (Windows: Defender status, ports,
  autostart, winget upgrades; Linux: Lynis, rkhunter, chkrootkit, `ss`,
  `systemctl`, ufw, apt, SSH config). Missing tools are reported as **skipped**,
  never as a pass.
- Safe to schedule (cron / monitors) — writes into the same `custos_findings.json`
  as the code gates.

## Scope-Datei (`custos/scope.yaml`) — Voraussetzung für alles Aktive

- `scope.yaml` is the **asset allowlist**. Any active scan (later phase) must
  validate its target against it and abort if the target is not listed.
- Seeded **empty** on purpose: empty = no active scan may run.
- ENTSCHEIDUNG NOETIG: add only hosts/IPs/repos you own and are permitted to
  scan; some providers require prior notice even for your own instances.

## Nicht in dieser Phase

- Aktive Scans (nmap, OWASP ZAP, Nikto — section 15.4): require a populated,
  human-approved `scope.yaml` and a defined maintenance window / safe mode. Not
  built yet.
