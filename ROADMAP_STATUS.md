# ROADMAP STATUS

Bezug: `custos-konzept.md` Abschnitt 19. Stand: Phase 1–6 erledigt.

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

## Offen – für nächste Läufe (bewusst NICHT gebaut)

### Struktur-Platzhalter, noch zu implementieren (Abschnitt 5/6)
- [ ] Agenten: `scope-guard`, `council-advisor` (×5), `council-chair`,
  `plain-text-translator`
- [ ] Skills: `grill-me`, `plan-mode`, `build-mode`, `cleanup-mode`
- [ ] Detektoren: `impact_analysis.py`, `db_schema_guard.py`,
  `a11y_frontend_check.py`
- [ ] Weitere Gates aus Abschnitt 8: Trivial-Schranke (`UserPromptSubmit`),
  Plan-Freigabe-Gate (`PreToolUse` auf `ExitPlanMode`), Scope-Wächter,
  DB-Schema-Guard, Impact-Analyse, A11y-Check, Regressions-Wächter
  (`SubagentStop`)

### Größere Phasen (Abschnitt 19, Phase 7–11)
- [ ] **Phase 7 – Fleet-Bearbeitung**: Auto-Fix-PRs für freigegebene Repos
  (Abschnitt 10.3)
- [ ] **Phase 8 – Council**: Fünf-Advisor-Mechanismus für strittige Fälle
  (Abschnitt 6/9)
- [ ] **Phase 9 – Multi-Session**: Worktree-Isolation + Task-Queue-Koordination
  (Abschnitt 11)
- [ ] **Phase 10 – Interface**: Dark-Terminal-Dashboard aus Abschnitt 18,
  gespeist aus `custos_findings.json`. **Verbindliche Design-Referenz:**
  <https://claude.ai/design/p/e5676802-f116-4b7a-bd09-06dc8c891cc8?file=CUSTOS+Dashboard.dc.html&via=share>
- [ ] **Phase 11 – Selbstqualifizierung**: Referenz-Testsuite, Session-Logs,
  Release-Metriken (Abschnitt 12)

### Querschnitt
- [ ] Fleet-Discovery GitHub-Teil (`gh repo list`, Abschnitt 10.1) – bisher nur
  lokale `.git`-Discovery gebaut.
- [ ] ENTSCHEIDUNG NÖTIG: echte `roots:` in `custos/fleet.yaml` und echte
  Hosts/Repos in `custos/scope.yaml` befüllen (aktuell Platzhalter/leer).
- [ ] Zero-Tolerance-Policy härten (Abschnitt 16): fail-closed auch bei
  fehlendem Linter, mehrere Scanner parallel, zeitgesteuerte Rescans
- [ ] Codex-Variante (Abschnitt 14)
- [ ] CI-Dogfooding-Workflow (Abschnitt 17)
- [ ] Feldnamen von Hooks/Plugin/Settings gegen aktuelle Doku gegenprüfen
  (`/docs/en/hooks`, `/docs/en/plugins`, `/docs/en/permissions`) – Konzept-
  Fußnote; Format hier nach bestem aktuellen Wissen umgesetzt.
