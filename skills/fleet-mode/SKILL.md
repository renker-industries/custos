---
name: fleet-mode
description: >-
  CUSTOS fleet workflow (read-only stage). Use to inventory the local git repos
  across configured root directories and apply the CUSTOS gates to released repos
  as a findings report only. Never edits a discovered repo; auto-fix / PRs are a
  separate later phase and are out of scope here.
---

# Fleet Mode (read-only)

CUSTOS is not limited to the repo it runs in — it can cover the whole local
software fleet. This stage is **read-only**: discover repos, produce reports, and
change nothing in anyone's code.

## Discovery

```bash
python bin/fleet_discover.py            # uses roots from custos/fleet.yaml
python bin/fleet_discover.py --root C:\path\to\projects
```

- Scans the configured `roots` for `.git` directories.
- Writes/updates `custos/fleet.yaml`, preserving existing statuses on re-run.
- New repos default to `nur-inventarisiert`; `custos` itself stays
  `aktiv-ueberwacht`.

## Per-repo check (only `aktiv-ueberwacht`)

For repos marked `aktiv-ueberwacht`, apply the same static gates as the home
project (ai-slop, static analysis, later secret-scan) and emit a **findings
report only** — no automatic change.

## Harte Schranke

- **Read-only per Default.** No commit, no push, no file write inside a
  discovered repo in this phase.
- **Nur gelistete Repos.** Only repos explicitly in `fleet.yaml` are touched.
  There is no "scan everything on disk / on GitHub" mode — a mis-scoped run must
  never reach a foreign or third-party repo.
- **Auto-Fix ist Phase 7.** Branch+PR fixes for released repos come later and are
  opt-in per repo. Not here.
