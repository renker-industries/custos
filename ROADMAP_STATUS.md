# ROADMAP STATUS

Bezug: `custos-konzept.md` Abschnitt 19. Stand: Phase 1–11 erledigt (Konzept
vollständig umgesetzt); nur scharf-zu-schaltende/irreversible Teile bewusst offen.

## Erledigt (Lauf Phase 1–3)

- [x] **Phase 1 – MVP**: `senior-dev` Default-Agent + `plan-reviewer` +
  `Stop`-Hook, der einen Testlauf/Proof erzwingt.
- [x] **Phase 2 – Statik-Ebene**: AI-Slop-Detektor + sprachspezifischer
  Linter-Dispatch (Python/JS-TS) als `PostToolUse`-Hooks.
- [x] **Phase 3 – Branding & Repo-Grundgerüst**: README (Abschnitt 17),
  `CUSTOS_BRANDING.md` (Abschnitt 2), `.gitignore`, `LICENSE` (MIT),
  Plugin-Grundgerüst + Verzeichnisstruktur (Abschnitt 5).

## Erledigt (Lauf Phase 4–6)

- [x] **Phase 4 – Spezialmodi**: `agents/root-cause.md` (verwirft erste Ursache
  nicht sofort), `skills/debug-mode`, `skills/data-analytics-mode`.
- [x] **Phase 5 – Fleet-Modus (read-only, 10.1–10.2)**: `bin/fleet_discover.py`
  (lokale Repo-Discovery), `custos/fleet.yaml` (custos = aktiv-ueberwacht, Rest
  nur-inventarisiert), `skills/fleet-mode`. Keine Bearbeitung fremder Repos.
- [x] **Phase 6 – Security-Mode (passiv, 15.1/15.3)**: `custos/scope.yaml`
  (leere Allowlist), `bin/security_passive.py` (lokale Härtungs-Checks),
  `skills/security-mode`. Aktive Scans (15.4) NICHT gebaut.

Hinweis: CI-Dogfooding-Workflow (GitHub Actions) aus Abschnitt 17 ist noch
**nicht** angelegt (kein Remote/Org bestätigt) – siehe offene Punkte.

## Erledigt (Lauf Phase 7–11 + Querschnitt)

- [x] Agenten komplett: `scope-guard`, `council-advisor`, `council-chair`,
  `plain-text-translator`.
- [x] Skills komplett: `grill-me`, `plan-mode`, `build-mode`, `cleanup-mode`,
  `council-mode`, `multi-session`.
- [x] Detektoren komplett: `impact_analysis.py`, `db_schema_guard.py`,
  `a11y_frontend_check.py`.
- [x] Alle Gates aus Abschnitt 8 verdrahtet (Trivial-Schranke, Plan-Freigabe,
  Scope-Wächter, DB-Schema-Guard, Impact, A11y, Regressions-Wächter).
- [x] **Phase 7 – Fleet-Bearbeitung**: `bin/fleet_fix.py` (opt-in Branch+PR,
  dry-run default, nie direkt auf main).
- [x] **Phase 8 – Council**: `council-advisor`/`council-chair` + `bin/council_log.py`
  (Suppression nur mit Ablaufdatum).
- [x] **Phase 9 – Multi-Session**: `bin/task_queue.py` (lock-guarded, proof-pflichtig)
  + `monitors/monitors.json` (Worktree-Isolation).
- [x] **Phase 10 – Interface**: `bin/build_dashboard.py` → `interface/`.
- [x] **Phase 11 – Selbstqualifizierung**: `tests/` (16 Fälle) + `bin/selfqual.py`
  (Release-Metrik in `custos_findings.json`).
- [x] Fleet-Discovery GitHub-Teil (`fleet_discover.py --github`).
- [x] Zero-Tolerance-Modus (fail-closed bei jedem Fund + fehlendem Linter).
- [x] Codex-Mapping dokumentiert (`CODEX.md`).
- [x] CI-Dogfooding-Workflow (`.github/workflows/custos.yml`).

## Offen – Feinschliff / bewusst als Platzhalter belassen

- [ ] Aktive Security-Scans (nmap/ZAP, Abschnitt 15.4) – erst nach befüllter,
  freigegebener `custos/scope.yaml`. **NICHT gebaut** (scharf, irreversibel).
- [ ] Fleet-Auto-Fix scharfschalten: `autofix: true` pro Repo + `--push` – bewusst
  opt-in, vom User auszulösen.
- [ ] ENTSCHEIDUNG NÖTIG: echte Hosts/Repos in `custos/scope.yaml` (aktuell leer).
- [ ] Zero-Tolerance weiter härten: mehrere Scanner parallel, zeitgesteuerte
  Rescans (Basis steht).
- [ ] Codex-Event-Adapter tatsächlich implementieren (Mapping steht in CODEX.md).
- [ ] Interface-Feinschliff gegen die verbindliche Claude-Design-Referenz:
  <https://claude.ai/design/p/e5676802-f116-4b7a-bd09-06dc8c891cc8?file=CUSTOS+Dashboard.dc.html&via=share>
- [ ] Feldnamen von Hooks/Plugin/Settings gegen aktuelle Doku gegenprüfen
  (`/docs/en/hooks`, `/docs/en/plugins`, `/docs/en/permissions`) – Format nach
  bestem aktuellen Wissen umgesetzt.
- [ ] GitHub-Org anlegen + Push (macht der User manuell).
