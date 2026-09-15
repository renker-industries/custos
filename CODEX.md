# CUSTOS für Codex (funktional äquivalente Variante)

Konzept-Abschnitt 14: CUSTOS soll neben Claude Code auch für **Codex** verfügbar
sein – keine 1:1-Portierung der Dateien, aber **dieselbe Gate-Logik** in dessen
eigenem Erweiterungs-/Konfigurationsformat.

Diese Datei hält fest, wie die Bausteine abgebildet werden. Der eigentliche
Codex-Adapter ist noch nicht implementiert (offener Roadmap-Punkt); die
Detektor-/Gate-Skripte selbst sind bewusst hüllen-unabhängig geschrieben
(stdlib-Python, JSON-Payload auf stdin, Exit-Codes) und damit wiederverwendbar.

## Abbildung der Ebenen

| CUSTOS-Baustein (Claude Code) | Codex-Entsprechung (Zielbild) |
|---|---|
| `hooks/hooks.json` (Hook-Events) | Codex-eigene Hook-/Event-Konfiguration, gleiche Events (vor/nach Tool-Aufruf, Sessionende) |
| Default-Agent via `settings.json: "agent"` | Codex-System-Prompt/Profil für den Senior-Dev |
| Subagents (`agents/*.md`) | Codex-Rollen/Profile mit denselben Beschreibungen |
| Skills (`skills/*/SKILL.md`) | Codex-Modus-Prompts |
| Detektoren (`detectors/*.py`, `bin/*.py`) | **unverändert wiederverwendbar** – reine CLI-Skripte |

## Wiederverwendbarkeit der Skripte

Alle Gate-/Detektor-Skripte:

- lesen den Tool-/Event-Payload als **JSON auf stdin**,
- signalisieren Blockade über **Exit-Code 2** (+ stderr-Begründung),
- schreiben Funde nach `custos_findings.json`.

Ein Codex-Adapter muss daher nur die Codex-Events auf denselben stdin/Exit-Code-
Vertrag mappen; die Prüf-Logik bleibt identisch. Damit ist die Beweislogik
plattformübergreifend gleich, nur die Hülle unterscheidet sich.

## Status

- [x] Skripte hüllen-unabhängig (stdin-JSON / Exit-Code / Findings-Log).
- [ ] Codex-Event-Adapter (Mapping der Codex-Hooks auf den Skript-Vertrag).
- [ ] Codex-Profile für Agenten/Modi.
