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

## Läuft gerade

- Nichts offen. Scope (Phase 4–6) abgeschlossen.

## Noch offen (nächster Lauf)

Siehe `ROADMAP_STATUS.md`. Kern: Phase 7–11 (Fleet-Bearbeitung/Auto-Fix-PRs,
Council, Multi-Session, Interface, Selbstqualifizierung), restliche
Agenten/Skills/Detektoren + Gates aus Abschnitt 8, Fleet-GitHub-Discovery
(`gh repo list`), Zero-Tolerance-Härtung, CI-Dogfooding.

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

## BLOCKIERT

- Nichts. Kein Blocker aufgetreten.
