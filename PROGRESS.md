# PROGRESS

Zuerst lesen nach Rückkehr. Stichpunkte, Stand dieses Laufs.

## Fertig (getestet)

- **Plugin-Grundgerüst**: `.claude-plugin/plugin.json` (name "custos", v0.1.0),
  `settings.json` (Default-Agent = `senior-dev`), Verzeichnisstruktur nach
  Abschnitt 5 angelegt. → JSON aller Configs validiert (`json.load` grün).
- **Agenten**: `agents/senior-dev.md` (Default, Haltung/Triage/Delegation),
  `agents/plan-reviewer.md` (Plan-Review-Checkliste, APPROVED/CHANGES REQUIRED).
- **AI-Slop-Detektor** (`detectors/ai_slop_detector.py`, `PostToolUse`):
  → Test dirty (6 Funde) = Exit 2 blockiert ✓ ; clean = Exit 0 ✓.
- **Statik-Dispatch** (`detectors/lint_dispatch.py`, `PostToolUse`):
  → valides .py = Exit 0 (py_compile) ✓ ; kaputtes .py = Exit 2 mit
  SyntaxError ✓ ; fehlender Linter → nicht-blockierender Hinweis.
- **Beweis-Gate** (`bin/custos_stop_gate.py`, `Stop`):
  → kein Proof-Kommando + frisch = Exit 2 ✓ ; loop-active = Exit 0 (kein Trap) ✓ ;
  proofCommand grün = Exit 0 ✓ ; proofCommand rot = Exit 2 ✓.
- **Hook-Wiring** (`hooks/hooks.json`): PostToolUse(Write|Edit|MultiEdit) →
  slop + lint ; Stop → proof gate. JSON valide.
- **Branding/Doku**: `README.md` (Abschnitt 17), `CUSTOS_BRANDING.md`
  (Abschnitt 2), `.gitignore`, `LICENSE`-Platzhalter,
  `custos.config.example.json`.
- **Tracking**: `DECISIONS.md`, `ROADMAP_STATUS.md`, diese Datei.
- Alle Zwischenschritte einzeln committet (kein Big-Bang).

## Fertig (Lauf Phase 4–6, getestet)

- **Phase 4 – Debug/Analytics**: `agents/root-cause.md` (2. Ursache erzwungen),
  `skills/debug-mode`, `skills/data-analytics-mode`. (Markdown-Agenten/Skills,
  kein Laufzeittest nötig.)
- **Phase 5 – Fleet read-only**: `bin/fleet_discover.py`, `custos/fleet.yaml`,
  `skills/fleet-mode`. → Test in Temp: custos=aktiv-ueberwacht,
  fakerepo=nur-inventarisiert, `node_modules`-Sub-Repo geprunt (1 statt 2),
  Re-Run idempotent (0 new) ✓. Schreibt nie in gefundene Repos.
- **Phase 6 – Security passiv**: `bin/security_passive.py`, `custos/scope.yaml`
  (leer=kein aktiver Scan), `skills/security-mode`. → Test Windows: 4 Checks
  liefen (Defender/Ports/Autostart/winget), alle ok, Report in
  `custos_findings.json` ✓. Aktive Scans (15.4) nicht gebaut.

## Beweislage (Selbstanwendung)

Alle Gates/Tools mit realen Eingaben ausgeführt; Verhalten wie oben dokumentiert.
Kein Baustein nur behauptet – jeder ausgeführt.

## Fertig (Lauf Phase 7–11 + Querschnitt, getestet)

- **Alle Gates aus Abschnitt 8** verdrahtet + getestet: UserPromptSubmit-Triage,
  Plan-Freigabe (`plan_gate`), Scope-Wächter (`scope_guard`), DB-Schema-Guard,
  Impact-Analyse, A11y-Check, Regressions-Wächter (`regression_guard`). Grün/rot
  je mit echten Payloads geprüft.
- **Restliche Agenten/Skills** (scope-guard, council-advisor/-chair,
  plain-text-translator; grill-me, plan-mode, build-mode, cleanup-mode,
  council-mode, multi-session) – Frontmatter validiert (alle ok).
- **Phase 7** `bin/fleet_fix.py`: dry-run default, opt-in, nie auf main. Getestet:
  no-opt-in + dry-run lässt Ziel-Repo clean.
- **Phase 8** `bin/council_log.py`: Suppression nur mit Zukunfts-Ablauf. Getestet.
- **Phase 9** `bin/task_queue.py`: claim-Konflikt + proof-Pflicht. Getestet.
- **Phase 10** `bin/build_dashboard.py`: 4 Ansichten, Branding-Palette. Mit
  synthetischen + echten Daten getestet; Sample an User gesendet.
- **Phase 11** `tests/` (16 Fälle) + `bin/selfqual.py`: **16/16 grün**,
  Release-Metrik geloggt. CUSTOS eigener proofCommand.
- **Querschnitt**: GitHub-Discovery (`--github`), Zero-Tolerance-Modus,
  CI-Workflow, CODEX.md. Windows-Lint-Bug (npx.cmd) gefixt + Regressionstest.
- Version → 0.2.0.

## Läuft gerade

- Nichts offen. Konzept-Funktionsumfang (Phase 1–11) abgeschlossen.

## Noch offen (bewusst, scharf-zu-schaltend/irreversibel)

Siehe `ROADMAP_STATUS.md`. Kern: aktive Security-Scans (nmap/ZAP, brauchen
befüllte scope.yaml), Fleet-Auto-Fix-Push scharfschalten (opt-in pro Repo),
Codex-Event-Adapter, Interface-Feinschliff gegen Design-Referenz, GitHub-Org +
Push (manuell durch User).

## Fleet roots gesetzt (2026-09-15)

- `roots:` in `custos/fleet.yaml` = `C:\Users\Sebas\CascadeProjects` +
  `C:\Users\Sebas\Documents`.
- `fleet_discover.py` gelaufen: **18 Repos** erfasst (1 aktiv-ueberwacht =
  custos, 17 nur-inventarisiert), 17 new, rc=0 ✓. Read-only, nichts in
  Fremd-Repos geschrieben.

## ENTSCHEIDUNG NÖTIG (Platzhalter im Code)

- Hosts/Repos in `custos/scope.yaml` – echte, scan-erlaubte Assets (aktuell leer).
- Welche der 17 inventarisierten Repos als nächstes „aktiv-ueberwacht"?

## Entscheidungen getroffen (Abschnitt 20, vom User)

- Lizenz = **MIT** (c) 2026 Renker Industries → `LICENSE` + README aktualisiert.
- GitHub-Org `renker-industries` wird angelegt – **Org-Anlegen + Push macht der
  User manuell**, nicht dieser Lauf.
- Fleet-Modus startet nur mit `custos` selbst als „aktiv überwacht".

Siehe `DECISIONS.md`.

## Lauf 2026-09-16 — Veröffentlichung + Fleet-Aktivierung

### SCHRITT 1 (Veröffentlichung) — BLOCKIERT

- `gh auth status`: eingeloggt als **`sebastianrenker`** (Scopes: `repo`,
  `workflow`, `read:org`, `gist`) ✓ — also KEIN Login-Blocker.
- Working tree war clean; Branch `master` → **`main`** umbenannt (Task will
  `main`-Schutz; Entscheidung in DECISIONS.md).
- `gh repo create renker-industries/custos --private --source=. --remote=origin
  --push` → **HTTP 404: Not Found (https://api.github.com/users/renker-industries)**.
- Diagnose: `gh api user/orgs` und `user/memberships/orgs` beide **leer** → der
  eingeloggte Account `sebastianrenker` hat **keine Org-Mitgliedschaft**; GitHub
  liefert Nicht-Mitgliedern 404 statt 403.

**BLOCKIERT: Org `renker-industries` von diesem Account nicht erreichbar / keine
Push-Rechte.** Nicht selbst umgangen (kein Push unter den falschen Account
`sebastianrenker`). Damit gestoppt: Repo-Anlage, Push, Branch-Protection auf
`main` (Schritte 3–4, 6 der Veröffentlichung).

**Was der User tun muss (eine dieser Optionen):**
1. `sebastianrenker` als **Member/Owner** der Org `renker-industries` hinzufügen
   (falls die Org unter einem anderen GitHub-Account angelegt wurde), ODER
2. gh mit dem Account einloggen, der die Org besitzt: `gh auth login`, ODER
3. Org-Slug prüfen (evtl. anderer Name als `renker-industries`).
Danach genügt erneut: `gh repo create renker-industries/custos --private
--source=. --remote=origin --push` (Branch ist bereits `main`).

### SCHRITT 2 (Fleet-Aktivierung) — lokal ausgeführt (unabhängig vom Push)
