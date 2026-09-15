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

## Auto-Fix (opt-in, safe by default)

`bin/fleet_fix.py` proposes bounded linter auto-fixes as a branch + PR, never a
direct push to main:

```bash
python bin/fleet_fix.py              # dry-run: reports only, writes nothing
python bin/fleet_fix.py --execute    # apply+commit on a custos/autofix-* branch
python bin/fleet_fix.py --execute --push  # + push and open a PR (needs gh)
```

- A repo is touched only if BOTH `status: aktiv-ueberwacht` AND `autofix: true`
  in `fleet.yaml` — no global switch.
- Repos with an unclean working tree are skipped (never fix over unsaved work).
- Dry-run is the default; `--push` is the only step that leaves the machine.

## Harte Schranke

- **Read-only per Default**, auch beim Auto-Fix (dry-run). Kein Schreiben/Commit/
  Push ohne die expliziten Flags oben.
- **Nur gelistete, opt-in Repos.** Only repos explicitly in `fleet.yaml` and
  opted in are touched. No "scan everything on disk / on GitHub" mode — a
  mis-scoped run must never reach a foreign or third-party repo.
- **Nie direkt auf main.** Fixes gehen immer auf einen `custos/autofix-*`-Branch.
