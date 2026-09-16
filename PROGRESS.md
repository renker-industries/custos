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

## Fleet-Scan gebaut (Lauf 2026-09-16)

- `renker-flint` → `aktiv-ueberwacht`; **19 Repos** aktiv.
- `bin/fleet_scan.py`: read-only Content-Scan (Sprach-Erkennung, Lint ruff/eslint
  falls vorhanden, AI-Slop, Secret-Pattern). Kein Write in Fremd-Repos.
- `bin/build_dashboard.py` erweitert: Fleet-Ansicht zeigt echte Funde aus
  `custos/fleet_findings.json` (Severity-Ampel + secrets/lint/slop/skipped +
  Fleet-Totals).
- **Testlauf über 19 Repos**: totals **1 secret**, 0 lint, **7949 slop**,
  **18 Checks übersprungen** (ruff/eslint in den meisten Repos nicht installiert).
  - Das 1 Secret: `rencora` → `dashboard/static/tv.html:70` (generic-secret-assign,
    redacted `TOKE***`). **Vom User zu prüfen** – read-only gemeldet, nicht
    verändert (Fremd-Repo).
  - Bugfix im Bau: gebündeltes `.python312`-venv in rencora wurde erst voll
    gescannt (3989/4000 Files, 109 Falsch-Secrets) → venv/site-packages-Prune +
    minified-Filter ergänzt, danach sauber.
- selfqual weiterhin 16/16 grün. Kein Fremd-Repo geschrieben/committet/gepusht.

## Secret-Fund-Triage (2026-09-16)

- Betroffen: nur `C:\Users\Sebas\Documents\rencora` (Remote rencora-public);
  `renker-repos/rencora` hat die Datei nicht.
- `dashboard/static/tv.html:70` = `const TOKEN="__TVTOKEN__";` → **FALSE POSITIVE**:
  Platzhalter, serverseitig ersetzt (`dashboard/server.py:1234`). Kein echtes
  Secret, **kein Fix/PR** (Schritt 1.2 des Auftrags).
- `fleet_findings.json`: Eintrag als `falsePositive` markiert, echte Secrets = 0.
- **Exposure**: unkritisch – nur ein Platzhalter in Code/Historie, kein echter
  Wert exponiert; keine Token-Rotation, keine Historie-Bereinigung nötig.
- Kein Fremd-Repo verändert; fleet_fix.py nicht ausgeführt (kein echter Fund).

## Läuft gerade

- Nichts offen. Konzept-Funktionsumfang (Phase 1–11) + Fleet-Scan + Fund-Triage
  abgeschlossen.

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

- **Schritt 7:** alle **18** inventarisierten Repos auf `status: aktiv-ueberwacht`
  gesetzt; `autofix: false` explizit pro Repo eingetragen (keins scharf). ✓
- **Schritt 8 — Fleet-Scan (read-only Discovery, `bin/fleet_discover.py`):** rc=0,
  read-only, nichts in Fremd-Repos geschrieben. Ergebnis: **19 Repos** gesehen —
  18 `aktiv-ueberwacht`, **1 neu entdeckt** (`renker-flint`, seit dem letzten
  Scan dazugekommen) → per Default `nur-inventarisiert`.
- **`renker-flint` NICHT auto-aktiviert:** der Auftrag nannte explizit „die 18".
  Aktivierung = Gates anwenden = bewusste Einzelentscheidung (wie beim Fleet-Start
  mit nur `custos`). Bleibt `nur-inventarisiert`, bis der User entscheidet.
- **Funde-Bilanz:** Der Fleet-Scan ist die read-only Discovery (Repo-Inventar) —
  **0 Code-/Security-Funde**, weil inhaltliche Detektoren/aktive Scans bewusst
  hinter `custos/scope.yaml` (leer/aus) liegen und nicht scharf sind. Es existiert
  (absichtlich) kein fleet-weiter Detektor-Runner; kein aktiver Scan gegen Hosts.

### Offene Punkte nach diesem Lauf

- **[BLOCKER] Org-Zugang** für `sebastianrenker` zu `renker-industries` (oben).
- **renker-flint**: neu im Fleet — aktiv überwachen ja/nein? (User)
- **scope.yaml** weiterhin leer/aus (unverändert, wie beauftragt).
- Nach Org-Fix: Push + Branch-Protection `main` + README-Repo-Link final setzen.

## Zusammenfassung Lauf 2026-09-16

- **Repo-URL:** _noch keine_ — Ziel `https://github.com/renker-industries/custos`
  (privat). **BLOCKIERT**: Org von Account `sebastianrenker` nicht erreichbar
  (gh 404, 0 Org-Mitgliedschaften). Push + Branch-Protection `main` stehen aus,
  bis der User Org-Zugang herstellt (siehe SCHRITT 1 oben).
- **Fleet-Scan (read-only Discovery):** 19 Repos gesehen — 18 `aktiv-ueberwacht`,
  1 neu (`renker-flint`) als `nur-inventarisiert`. **0 Code-/Security-Funde**
  (inhaltliche Detektoren/aktive Scans bleiben hinter leerem `scope.yaml` — aus).
  autofix für alle Repos `false` (nichts scharf).
- **README-Repo-Link:** kein Platzhalter-/GitHub-Link vorhanden → nichts geändert
  (kein Link auf ein noch nicht existierendes/erreichbares Repo erfunden).
- **Lokal committet, nicht gepusht** (kein Remote): master→main, Fleet-Aktivierung,
  Scan. Ein späterer Push überträgt alles.
- **Offene Punkte:** (1) Org-Zugang/Push, (2) `renker-flint` aktivieren ja/nein,
  (3) `scope.yaml` weiter leer/aus (unverändert, wie beauftragt).

## NACHTRAG 2. Anlauf 2026-09-16 — BLOCKER GELÖST, veröffentlicht

- Org-Zugang jetzt da (`sebastianrenker` ist Member von `renker-industries`).
- **Repo-URL:** https://github.com/renker-industries/custos (**privat**), `main`
  gepusht, alle bisherigen Commits übertragen. ✓
- **Branch-Protection `main`:** NICHT aktiv — Free-Plan verbietet Protection UND
  Rulesets auf privaten Repos (HTTP 403 "Upgrade to GitHub Pro or make public").
  Repo bleibt bewusst privat → NICHT public gemacht. Regel-JSON liegt bereit,
  mit einem Kommando nachziehbar sobald Pro/Team oder public. (DECISIONS.md)
- **README:** echter Repo-Link ergänzt.
- **Fleet (SCHRITT 2):** unverändert gültig — 18 `aktiv-ueberwacht`, `autofix:false`
  überall; Re-Scan idempotent (0 new). **Fleet-Scan-Funde: 19 Repos inventarisiert**
  (18 aktiv + 1 neu `renker-flint`, bleibt `nur-inventarisiert`), 0 Code-/Security-
  Funde (scope.yaml bleibt leer/aus). custos-Remote jetzt in fleet.yaml erfasst.
- **Offene Punkte:** (1) Branch-Protection erst mit Pro/Team oder public,
  (2) `renker-flint` aktiv überwachen ja/nein, (3) `scope.yaml` weiter leer/aus.
