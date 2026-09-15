# DECISIONS

Ein Satz pro autonom getroffener Entscheidung dieses Laufs. Offene Punkte aus
Konzept-Abschnitt 20 sind als **ENTSCHEIDUNG NÖTIG** markiert (nicht selbst
final entschieden).

## Autonom entschieden

- **Version 0.1.0** als Startversion in `plugin.json` gesetzt.
- **Config-Format JSON statt YAML** (`custos.config.json`, Konzept nannte
  `custos.config.yaml`) – damit die Detektoren stdlib-only bleiben und keine
  PyYAML-Abhängigkeit unter Windows nötig ist.
- **Sprachspezifischer Linter = Python zuerst** (ruff, sonst `py_compile`), plus
  JS/TS (eslint) im selben Dispatcher – Python, weil die CUSTOS-Skripte selbst
  Python sind (Selbstanwendung, Konzept Abschnitt 9) und `py_compile` immer
  verfügbar ist.
- **AI-Slop-Schwellwert = 5 Funde** (env `CUSTOS_SLOP_THRESHOLD` überschreibbar);
  darunter nicht-blockierender Hinweis, ab 5 Exit 2 – konservativer Startwert.
- **Stop-Gate degradiert bei fehlendem Proof-Kommando nicht in Endlosschleife**:
  blockt einmal (fail-closed), erlaubt bei gesetztem `stop_hook_active` das Ende
  mit Warnung – bewusster Trade-off gegen ein Trapping des Agenten.
- **Linter-Dispatch degradiert zu Hinweis, wenn der bevorzugte Linter fehlt**
  (statt hart zu blocken) – Zero-Tolerance/fail-closed ist ein späterer
  Roadmap-Punkt; der Skeleton soll vor vollständigem Toolchain-Setup nutzbar sein.
- **Verzeichnisstruktur aus Abschnitt 5 vollständig angelegt**, aber nur die
  In-Scope-Komponenten implementiert; leere Zielordner (`skills/`, `monitors/`)
  mit `.gitkeep`, out-of-scope Agenten/Detektoren als Punkte in
  `ROADMAP_STATUS.md` statt als leere Dateien.
- **Detektoren plattformunabhängig in Python** (Konzept Abschnitt 14) – Hooks
  rufen `python <script>` via `${CLAUDE_PLUGIN_ROOT}`, keine Bash-Abhängigkeit.
- **`custos_findings.json` und `custos.config.json` in `.gitignore`** – Runtime-
  Artefakte bzw. lokale Konfiguration, nicht Quellcode.

## Lauf Phase 4–6 (autonom entschieden)

- **Fleet-/Scope-Configs = echtes YAML via PyYAML** (`custos/fleet.yaml`,
  `custos/scope.yaml`) – Konzept nennt diese Dateien explizit `.yaml`; die
  CLI-Tools sind manuell laufende Skripte (keine Hooks), daher ist eine PyYAML-
  Abhängigkeit dort vertretbar; fehlt PyYAML, brechen sie mit klarem Install-
  Hinweis ab statt zu raten.
- **Fleet-Discovery ist read-only**: schreibt nur `custos/fleet.yaml`, nie in
  ein gefundenes Repo; bestehende Status bleiben bei Re-Run erhalten; neue Funde
  = `nur-inventarisiert`; `custos` selbst = `aktiv-ueberwacht`.
- **Discovery-Prune**: `node_modules`, `venv`, `.venv`, `__pycache__`,
  `site-packages` werden übersprungen und in gefundene Repos wird nicht
  hineinabgestiegen (kein doppeltes Erfassen von Sub-Repos).
- **`scope.yaml` startet leer** – leer = kein aktiver Scan erlaubt (fail-closed
  für spätere aktive Scans).
- **Passive Security-Checks nur lokal/beobachtend**, OS-abhängig; fehlendes
  Werkzeug = `skipped` (nie als „ok" gewertet); dieselbe `custos_findings.json`
  als Log wie die Code-Gates.
- **Root-Cause- und Plan-Reviewer-Agent auf `model: opus`** gesetzt (Konzept
  Abschnitt 13: hoher Effort für Debug-Kausalanalyse und Plan-Freigabe).

## ENTSCHEIDUNG NÖTIG (Platzhalter im Code, echte Werte fehlen)

- **Repo-Discovery-Wurzelverzeichnisse** (`roots:` in `custos/fleet.yaml`):
  aktuell leer/Platzhalter – welche echten Ordner sollen gescannt werden?
- **Scope-Hosts/IPs/Repos** (`custos/scope.yaml`): aktuell leer – welche eigenen,
  scan-erlaubten Assets gehören hinein, bevor ein aktiver Scan aktiviert wird?

## Erledigt (vom User entschieden, Abschnitt 20)

- [x] **Lizenz = MIT**, Copyright (c) 2026 Renker Industries. Umgesetzt in
  `LICENSE` (Standard-MIT-Text) und README-Lizenzabschnitt.
- [x] **GitHub-Org `renker-industries`** wird angelegt – Anlegen + Push macht
  der User manuell (nicht durch CUSTOS-Lauf).
- [x] **Fleet-Modus-Start**: nur `custos` selbst als „aktiv überwacht", alle
  weiteren Repos zunächst „nur inventarisiert" (greift erst in Fleet-Phase).
