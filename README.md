# CUSTOS

> CUSTOS is the guardian that turns every claim your AI agent makes into proof —
> before any code, repo, or server is allowed to call itself "done".

An AI coding agent likes to claim that something is finished, correct, or secure.
CUSTOS makes it **prove that** at every relevant point in the workflow — with an
executed command (linter, test run, static check), not with a sentence in its
reply.

CUSTOS is built as a Claude Code plugin and is part of the Renker Industries
product family — the cross-cutting quality and security layer over all projects.

**Repository:** <https://github.com/renker-industries/custos>

## What it does

Four layers, each mapped onto a real Claude Code building block:

- **Posture** – a default agent (`senior-dev`) opens every session and triages:
  trivial, or planning-required.
- **Reflexes** – hooks feed in context and force clarifying questions before
  anything is planned blindly.
- **Mechanics** – hooks run linters/static tools and block on exit code 2.
- **Proof** – a `Stop` hook forces a test run/linter before a session is allowed
  to end. No green exit code, no session end.

### Included (roadmap phases 1–11, concept fully implemented)

**Agents:** `senior-dev` (default, triage), `plan-reviewer`, `scope-guard`,
`root-cause` (debug causal analysis), `council-advisor` ×5 + `council-chair`,
`plain-text-translator`.

**Skills/modes:** `grill-me`, `plan-mode`, `build-mode`, `debug-mode`,
`cleanup-mode`, `data-analytics-mode`, `fleet-mode`, `security-mode`,
`council-mode`, `multi-session`.

**Gates (hooks, concept section 8):**
- `UserPromptSubmit` – trivial gate (triage reminder)
- `PreToolUse ExitPlanMode` – plan approval (blocks until the plan reviewer clears it)
- `PreToolUse Write|Edit` – scope guard + DB-schema guard
- `PostToolUse` – AI-slop detector, static dispatch (ruff/`py_compile`, eslint),
  impact analysis, a11y check
- `Stop` – proof gate (forces a green proof run)
- `SubagentStop` – regression guard (blocks green→red)

**Tools (`bin/`):** fleet discovery (local + GitHub, read-only), fleet auto-fix
(opt-in branch+PR, dry-run by default), passive security checks, council log,
multi-session task queue, dashboard generator, self-qualification.

**Zero-tolerance mode** (section 16): `CUSTOS_ZERO_TOLERANCE=1` or
`zeroTolerance: true` – fail-closed, blocks on every single finding.

Every finding lands time-stamped in `custos_findings.json` — a record, not a
claim. Dashboard: `python bin/build_dashboard.py` → `interface/`.

## Installation

```bash
# Load as a local plugin
claude --plugin-dir /path/to/custos
```

Optionally create a `custos.config.json` in the repo root (see
`custos.config.example.json`) to set the proof command:

```json
{ "proofCommand": "pytest -q" }
```

Without configuration the proof gate auto-detects `pytest` or an `npm test` script.

**Requirement:** Python 3 on the PATH (the detectors are written in
platform-independent Python — no WSL required on Windows).

## Dogfooding

CUSTOS applies its own rules to itself: `python bin/selfqual.py` runs the
reference test suite (`tests/`) — the same proof obligation CUSTOS enforces on
other projects. CI (`.github/workflows/custos.yml`) does this on every push/PR.

## Status

Version 0.2.0 – the concept feature set (roadmap phases 1–11) is implemented.
Deliberately left as ready-to-arm placeholders: active security scans (nmap/ZAP,
which need a populated `custos/scope.yaml`) and fleet auto-fix push (opt-in per
repo). Details and polish points in [`ROADMAP_STATUS.md`](ROADMAP_STATUS.md).

## License

MIT License – Copyright (c) 2026 Renker Industries. See [`LICENSE`](LICENSE).
