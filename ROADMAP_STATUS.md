# ROADMAP STATUS

Reference: `custos-konzept.md` section 19. State: phases 1–11 done (concept
fully implemented); only sharp-to-arm/irreversible parts deliberately open.

## Done (run phases 1–3)

- [x] **Phase 1 – MVP**: `senior-dev` default agent + `plan-reviewer` +
  `Stop` hook that enforces a test run/proof.
- [x] **Phase 2 – static level**: AI-slop detector + language-specific
  linter dispatch (Python/JS-TS) as `PostToolUse` hooks.
- [x] **Phase 3 – branding & repo skeleton**: README (section 17),
  `CUSTOS_BRANDING.md` (section 2), `.gitignore`, `LICENSE` (MIT),
  plugin skeleton + directory structure (section 5).

## Done (run phases 4–6)

- [x] **Phase 4 – special modes**: `agents/root-cause.md` (does not discard the first
  cause immediately), `skills/debug-mode`, `skills/data-analytics-mode`.
- [x] **Phase 5 – fleet mode (read-only, 10.1–10.2)**: `bin/fleet_discover.py`
  (local repo discovery), `custos/fleet.yaml` (custos = actively-monitored, the rest
  inventoried-only), `skills/fleet-mode`. No editing of foreign repos.
- [x] **Phase 6 – security mode (passive, 15.1/15.3)**: `custos/scope.yaml`
  (empty allowlist), `bin/security_passive.py` (local hardening checks),
  `skills/security-mode`. Active scans (15.4) NOT built.

Note: the CI dogfooding workflow (GitHub Actions) from section 17 is still
**not** created (no remote/org confirmed) – see open points.

## Done (run phases 7–11 + cross-cutting)

- [x] Agents complete: `scope-guard`, `council-advisor`, `council-chair`,
  `plain-text-translator`.
- [x] Skills complete: `grill-me`, `plan-mode`, `build-mode`, `cleanup-mode`,
  `council-mode`, `multi-session`.
- [x] Detectors complete: `impact_analysis.py`, `db_schema_guard.py`,
  `a11y_frontend_check.py`.
- [x] All gates from section 8 wired (trivial barrier, plan approval,
  scope guard, DB schema guard, impact, a11y, regression guard).
- [x] **Phase 7 – fleet editing**: `bin/fleet_fix.py` (opt-in branch+PR,
  dry-run default, never directly on main).
- [x] **Phase 8 – council**: `council-advisor`/`council-chair` + `bin/council_log.py`
  (suppression only with an expiry date).
- [x] **Phase 9 – multi-session**: `bin/task_queue.py` (lock-guarded, proof-required)
  + `monitors/monitors.json` (worktree isolation).
- [x] **Phase 10 – interface**: `bin/build_dashboard.py` → `interface/`.
- [x] **Phase 11 – self-qualification**: `tests/` (16 cases) + `bin/selfqual.py`
  (release metric in `custos_findings.json`).
- [x] Fleet discovery GitHub part (`fleet_discover.py --github`).
- [x] Zero-tolerance mode (fail-closed on any finding + missing linter).
- [x] Codex mapping documented (`CODEX.md`).
- [x] CI dogfooding workflow (`.github/workflows/custos.yml`).

## Open – polish / deliberately left as a placeholder

- [ ] Active security scans (nmap/ZAP, section 15.4) – only after a filled,
  released `custos/scope.yaml`. **NOT built** (armed, irreversible).
- [ ] Arm fleet auto-fix: `autofix: true` per repo + `--push` – deliberately
  opt-in, to be triggered by the user.
- [ ] DECISION NEEDED: real hosts/repos in `custos/scope.yaml` (currently empty).
- [ ] Harden zero-tolerance further: several scanners in parallel, time-triggered
  rescans (the basis is in place).
- [ ] Actually implement the Codex event adapter (the mapping is in CODEX.md).
- [ ] Interface polish against the binding Claude Design reference:
  <https://claude.ai/design/p/e5676802-f116-4b7a-bd09-06dc8c891cc8?file=CUSTOS+Dashboard.dc.html&via=share>
- [ ] Cross-check field names of hooks/plugin/settings against the current docs
  (`/docs/en/hooks`, `/docs/en/plugins`, `/docs/en/permissions`) – format implemented
  to the best current knowledge.
- [ ] Create the GitHub org + push (done by the user manually).
