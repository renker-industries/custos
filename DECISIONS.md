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

## ENTSCHEIDUNG NÖTIG (nicht autonom – Konzept Abschnitt 20)

- **Lizenzwahl** für die Veröffentlichung (MIT/Apache-2.0 vs. restriktiver).
  Aktuell Platzhalter in `LICENSE` und README.
- **GitHub-Org `renker-industries`** – existiert sie schon oder neu anzulegen?
- **Repo-Freigaben**: welche eigenen GitHub-Repos zum Start „aktiv überwacht"
  vs. „nur inventarisiert" (relevant erst für Fleet-Modus, spätere Phase).
