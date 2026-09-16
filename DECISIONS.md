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

## Lauf Phase 7–11 + Querschnitt (autonom entschieden)

- **Workflow-State in `custos_state.json`** (gitignored) teilt Plan-Freigabe,
  Scope und Test-Baseline zwischen den Hooks; Plan-Freigabe setzt die
  `plan-reviewer`-Agent via `bin/custos_approve_plan.py`.
- **Fleet-Auto-Fix fail-safe**: dry-run default, nur bei `status=aktiv-ueberwacht`
  UND `autofix:true`, nie über unclean tree, nie direkt auf main; `--push` ist der
  einzige Schritt, der die Maschine verlässt.
- **Aktive Security-Scans (nmap/ZAP) bewusst NICHT gebaut** – erfordern befüllte,
  freigegebene `scope.yaml`; nur passive Checks sind scharf.
- **Council-Suppression erzwingt Zukunfts-Ablaufdatum** (kein permanenter,
  stiller Ausnahme-Zustand, Abschnitt 16).
- **Task-Queue: `complete` erfordert `--proof`** – eine Aufgabe gilt nicht per
  Claim als erledigt (Beweispflicht auch hier).
- **Interface = generierte, self-contained HTML** aus `custos_findings.json`
  (Daten inline), damit sie ohne Server von Platte öffnet; Design nach Branding,
  Feinschliff gegen die Design-Referenz später.
- **Selbstqualifizierung via stdlib-`unittest`** (nicht pytest), damit die Suite
  ohne Zusatz-Abhängigkeit überall läuft; `bin/selfqual.py` ist CUSTOS' eigener
  proofCommand (Dogfooding).
- **Zero-Tolerance schaltbar** per env/Config statt hart verdrahtet – Reibung nur
  wenn bewusst gewollt.

## Lauf Fleet-Scan (autonom entschieden)

- **`renker-flint` → `aktiv-ueberwacht`, `autofix:false`** (deckt „alle Repos"-
  Entscheidung; 19 Repos jetzt aktiv).
- **`bin/fleet_scan.py` strikt read-only** – kein Write/Commit/Branch/Push in
  Fremd-Repos, schreibt nur `custos/fleet_findings.json`.
- **Fleet-Lint auf Repo-Ebene** (ruff/eslint, nur wenn Tool vorhanden, sonst
  „skipped: Tool fehlt"). `py_compile` pro Datei wird fleet-weit NICHT gefahren
  (zu laut, würde nur Syntax je Datei prüfen).
- **Prune gebündelter Interpreter/venv + generierte Dateien**: `site-packages`,
  `.python*`/`virtualenv`, `.min.js`/`*-lock`/`*.map` + minified-Heuristik
  (max Zeilenlänge > 2000). Grund: rencora hatte ein eingecheckt es `.python312`
  (3989/4000 Dateien = Dependencies) → sonst 109 Falsch-„Secrets" + 160k Slop.
  Prune bewusst eng: echte `bin/`/`lib/`-Quellordner werden NICHT übersprungen.
- **Secret-Scan repo-unabhängig**, Funde **redacted** (nur Präfix + Datei/Zeile)
  protokolliert; Placeholder-Muster (example/xxx/<...>) gefiltert.
- **`custos/fleet_findings.json` gitignored** – Runtime-Report mit lokalen Pfaden
  und (redacted) Fund-Orten, kein Quellcode. Die **committete**
  `interface/custos-dashboard.html` wird ohne lokale Funde generiert (Privacy).

## ENTSCHEIDUNG NÖTIG (Platzhalter im Code, echte Werte fehlen)

- **Repo-Discovery-Wurzelverzeichnisse** (`roots:` in `custos/fleet.yaml`):
  ERLEDIGT – gesetzt auf `CascadeProjects` + `Documents`.
- **Scope-Hosts/IPs/Repos** (`custos/scope.yaml`): aktuell leer – welche eigenen,
  scan-erlaubten Assets gehören hinein, bevor ein aktiver Scan aktiviert wird?
- **Welche der inventarisierten Repos werden `aktiv-ueberwacht`** (und ggf.
  `autofix:true`), bevor Fleet-Prüfung/Auto-Fix scharfgeschaltet wird?

## Erledigt (vom User entschieden, Abschnitt 20)

- [x] **Lizenz = MIT**, Copyright (c) 2026 Renker Industries. Umgesetzt in
  `LICENSE` (Standard-MIT-Text) und README-Lizenzabschnitt.
- [x] **GitHub-Org `renker-industries`** wird angelegt – Anlegen + Push macht
  der User manuell (nicht durch CUSTOS-Lauf).
- [x] **Fleet-Modus-Start**: nur `custos` selbst als „aktiv überwacht", alle
  weiteren Repos zunächst „nur inventarisiert" (greift erst in Fleet-Phase).

## Lauf 2026-09-16 (Veröffentlichung + Fleet-Aktivierung)

- **Default-Branch `main`**: lokaler Branch `master` → `main` umbenannt, weil der
  Auftrag Branch-Protection auf `main` verlangt und `main` die aktuelle Konvention
  ist. (Push noch nicht erfolgt, siehe Blocker.)
- **Sichtbarkeit privat**: Repo wird `--private` angelegt (Default), da noch kein
  Release-Zeitpunkt entschieden ist. Öffentlich erst auf ausdrückliche Ansage.
- **Org-Block nicht umgangen**: Da `renker-industries` von diesem Account nicht
  erreichbar ist, wurde NICHT ersatzweise unter `sebastianrenker/custos`
  veröffentlicht — das wäre der falsche Owner. Stattdessen sauber BLOCKIERT
  eingetragen (PROGRESS.md).
- **Fleet-Aktivierung**: alle 18 inventarisierten Repos auf
  `status: aktiv-ueberwacht` gesetzt. `autofix` bleibt für ALLE aus — explizit als
  `autofix: false` pro Repo eingetragen, damit die Nicht-Scharfschaltung
  inspizierbar ist. Auto-Fix bleibt manuelle Einzelentscheidung.
- **„Fleet-Scan" = read-only Discovery (Phase 5)**: der einzige fleet-weite,
  read-only Pass, der gebaut ist, ist `bin/fleet_discover.py`. Als Fleet-Scan
  ausgeführt. Inhaltliche Detektor-/Security-Funde bleiben bewusst hinter
  `custos/scope.yaml` (leer/aus) — kein aktiver Scan, wie beauftragt.

## Lauf 2026-09-16 (2. Anlauf — Org jetzt erreichbar)

- **Veröffentlicht**: Org-Zugang war beim 2. Anlauf da (`sebastianrenker` ist jetzt
  Member von `renker-industries`). Repo `renker-industries/custos` **privat**
  angelegt + `main` gepusht.
- **Branch-Protection NICHT gesetzt — Plan-Limit**: klassische Protection UND
  Rulesets liefern auf privaten Repos im Free-Plan HTTP 403
  ("Upgrade to GitHub Pro or make this repository public"). Repo bleibt bewusst
  privat (User-Entscheidung), daher NICHT public gemacht, nur um Protection zu
  bekommen. Aufgeschoben bis: (a) GitHub Pro/Team, oder (b) Repo wird public.
  Gewünschte Regel (PR-Pflicht, kein Force-Push, kein Delete) liegt als
  Ruleset-JSON bereit und ist mit einem Kommando nachziehbar.
- **README-Repo-Link**: echten Link `https://github.com/renker-industries/custos`
  (privat) ergänzt (vorher kein Platzhalter vorhanden).
