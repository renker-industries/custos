# DECISIONS

One sentence per decision made autonomously in this run. Open points from
concept section 20 are marked as **DECISION NEEDED** (not finally decided on my own).

## Decided autonomously

- **Version 0.1.0** set as the start version in `plugin.json`.
- **Config format JSON instead of YAML** (`custos.config.json`, the concept named
  `custos.config.yaml`) – so that the detectors stay stdlib-only and no
  PyYAML dependency is needed on Windows.
- **Language-specific linter = Python first** (ruff, else `py_compile`), plus
  JS/TS (eslint) in the same dispatcher – Python, because the CUSTOS scripts
  themselves are Python (self-application, concept section 9) and `py_compile` is always
  available.
- **AI-slop threshold = 5 findings** (env `CUSTOS_SLOP_THRESHOLD` overridable);
  below that a non-blocking note, from 5 up exit 2 – a conservative starting value.
- **The stop gate does not degrade into an endless loop on a missing proof command**:
  it blocks once (fail-closed), and with `stop_hook_active` set it allows the end
  with a warning – a deliberate trade-off against trapping the agent.
- **The linter dispatch degrades to a note when the preferred linter is missing**
  (instead of hard-blocking) – zero-tolerance/fail-closed is a later
  roadmap item; the skeleton should be usable before a full toolchain setup.
- **The directory structure from section 5 is fully created**, but only the
  in-scope components are implemented; empty target folders (`skills/`, `monitors/`)
  with `.gitkeep`, out-of-scope agents/detectors as points in
  `ROADMAP_STATUS.md` instead of as empty files.
- **Detectors platform-independent in Python** (concept section 14) – hooks
  call `python <script>` via `${CLAUDE_PLUGIN_ROOT}`, no Bash dependency.
- **`custos_findings.json` and `custos.config.json` in `.gitignore`** – runtime
  artifacts and local configuration respectively, not source code.

## Run phases 4–6 (decided autonomously)

- **Fleet/scope configs = real YAML via PyYAML** (`custos/fleet.yaml`,
  `custos/scope.yaml`) – the concept names these files explicitly `.yaml`; the
  CLI tools are manually run scripts (not hooks), so a PyYAML
  dependency is acceptable there; if PyYAML is missing, they abort with a clear install
  hint instead of guessing.
- **Fleet discovery is read-only**: writes only `custos/fleet.yaml`, never into
  a discovered repo; existing statuses are preserved on re-run; new findings
  = `inventoried-only`; `custos` itself = `actively-monitored`.
- **Discovery prune**: `node_modules`, `venv`, `.venv`, `__pycache__`,
  `site-packages` are skipped, and discovered repos are not descended into
  (no double capture of sub-repos).
- **`scope.yaml` starts empty** – empty = no active scan allowed (fail-closed
  for later active scans).
- **Passive security checks only local/observing**, OS-dependent; a missing
  tool = `skipped` (never counted as "ok"); the same `custos_findings.json`
  as the log as the code gates.
- **Root-cause and plan-reviewer agent set to `model: opus`** (concept
  section 13: high effort for debug root-cause analysis and plan approval).

## Run phases 7–11 + cross-cutting (decided autonomously)

- **Workflow state in `custos_state.json`** (gitignored) shares plan approval,
  scope, and test baseline between the hooks; plan approval sets the
  `plan-reviewer` agent via `bin/custos_approve_plan.py`.
- **Fleet auto-fix fail-safe**: dry-run default, only with `status=actively-monitored`
  AND `autofix:true`, never over an unclean tree, never directly on main; `--push` is the
  only step that leaves the machine.
- **Active security scans (nmap/ZAP) deliberately NOT built** – they require a filled,
  released `scope.yaml`; only passive checks are armed.
- **Council suppression enforces a future expiry date** (no permanent,
  silent exception state, section 16).
- **Task queue: `complete` requires `--proof`** – a task does not count as done
  by a claim (a proof obligation here too).
- **Interface = generated, self-contained HTML** from `custos_findings.json`
  (data inline), so that it opens from disk without a server; design per branding,
  polish against the design reference later.
- **Self-qualification via stdlib `unittest`** (not pytest), so that the suite
  runs everywhere without an extra dependency; `bin/selfqual.py` is CUSTOS's own
  proofCommand (dogfooding).
- **Zero-tolerance switchable** via env/config instead of hard-wired – friction only
  when deliberately wanted.

## Fleet-scan run (decided autonomously)

- **`renker-flint` → `actively-monitored`, `autofix:false`** (covers the "all repos"
  decision; 19 repos now active).
- **`bin/fleet_scan.py` strictly read-only** – no write/commit/branch/push into
  foreign repos, writes only `custos/fleet_findings.json`.
- **Fleet lint at repo level** (ruff/eslint, only if the tool is present, else
  "skipped: tool missing"). `py_compile` per file is NOT run fleet-wide
  (too noisy, would only check syntax per file).
- **Prune of bundled interpreter/venv + generated files**: `site-packages`,
  `.python*`/`virtualenv`, `.min.js`/`*-lock`/`*.map` + minified heuristic
  (max line length > 2000). Reason: rencora had a checked-in `.python312`
  (3989/4000 files = dependencies) → otherwise 109 false "secrets" + 160k slop.
  The prune is deliberately narrow: real `bin/`/`lib/` source folders are NOT skipped.
- **Secret scan repo-independent**, findings logged **redacted** (only prefix + file/line);
  placeholder patterns (example/xxx/<...>) filtered.
- **`custos/fleet_findings.json` gitignored** – a runtime report with local paths
  and (redacted) finding locations, not source code. The **committed**
  `interface/custos-dashboard.html` is generated without local findings (privacy).

## Fleet-finding triage (2026-09-16)

- **rencora `dashboard/static/tv.html:70` = FALSE POSITIVE.** The value is
  `const TOKEN="__TVTOKEN__";` – a template placeholder replaced server-side in
  `dashboard/server.py:1234` (`html.replace("__TVTOKEN__", tok)`).
  The static file contains **no real secret**. Marked in `fleet_findings.json`
  as `falsePositive: true`; no code fix, no PR (step 1.2). Only
  `Documents/rencora` (rencora-public) has the file; `renker-repos/rencora` does
  not.
- **Exposure assessment**: not critical – since only a placeholder is in the repo/
  history, no real value is exposed despite the public nature of the rencora-public
  remote. No rotation, no history cleanup needed.
- **Follow-up (not in this run, would be a CUSTOS change):** extend the PLACEHOLDER
  regex in `bin/fleet_scan.py` with the template pattern `__NAME__`, so that
  such placeholders are no longer reported as a secret candidate in future.

## DECISION NEEDED (placeholder in the code, real values missing)

- **Repo-discovery root directories** (`roots:` in `custos/fleet.yaml`):
  DONE – set to `CascadeProjects` + `Documents`.
- **Scope hosts/IPs/repos** (`custos/scope.yaml`): currently empty – which of your own,
  scan-allowed assets belong in it before an active scan is enabled?
- **Which of the inventoried repos become `actively-monitored`** (and possibly
  `autofix:true`), before fleet checking/auto-fix is armed?

## Done (decided by the user, section 20)

- [x] **License = MIT**, copyright (c) 2026 Renker Industries. Implemented in
  `LICENSE` (standard MIT text) and the README license section.
- [x] **GitHub org `renker-industries`** is created – creating + pushing is done
  by the user manually (not by a CUSTOS run).
- [x] **Fleet-mode start**: only `custos` itself as "actively monitored", all
  further repos "inventoried only" for now (takes effect only in the fleet phase).

## Run 2026-09-16 (publication + fleet activation)

- **Default branch `main`**: local branch `master` → renamed to `main`, because the
  task requires branch protection on `main` and `main` is the current convention.
  (Push not yet done, see blocker.)
- **Visibility private**: the repo is created `--private` (default), since no
  release date is decided yet. Public only on explicit instruction.
- **Org block not bypassed**: since `renker-industries` is not reachable from this
  account, it was NOT published instead under `sebastianrenker/custos`
  — that would be the wrong owner. Instead cleanly recorded as BLOCKED
  (PROGRESS.md).
- **Fleet activation**: all 18 inventoried repos set to
  `status: actively-monitored`. `autofix` stays off for ALL — entered explicitly as
  `autofix: false` per repo, so that the non-arming is inspectable. Auto-fix stays
  a manual individual decision.
- **"Fleet scan" = read-only discovery (phase 5)**: the only fleet-wide,
  read-only pass that is built is `bin/fleet_discover.py`. Run as the fleet scan.
  Content detector/security findings deliberately stay behind
  `custos/scope.yaml` (empty/off) — no active scan, as commissioned.

## Run 2026-09-16 (2nd attempt — org now reachable)

- **Published**: org access was present on the 2nd attempt (`sebastianrenker` is now
  a member of `renker-industries`). Repo `renker-industries/custos` created **private**
  + `main` pushed.
- **Branch protection NOT set — plan limit**: classic protection AND
  rulesets return HTTP 403 on private repos in the Free plan
  ("Upgrade to GitHub Pro or make this repository public"). The repo deliberately stays
  private (user decision), so it was NOT made public just to obtain protection.
  Deferred until: (a) GitHub Pro/Team, or (b) the repo is made public.
  The desired rule (PR requirement, no force-push, no delete) is ready as
  ruleset JSON and applicable with one command.
- **README repo link**: real link `https://github.com/renker-industries/custos`
  (private) added (no placeholder present before).
