# CUSTOS

> CUSTOS ist der Wächter, der jede Behauptung deines KI-Agenten in einen Beweis
> verwandelt – bevor Code, Repo oder Server sich „fertig" nennen dürfen.

Ein KI-Coding-Agent behauptet gerne, dass etwas fertig, korrekt oder sicher ist.
CUSTOS sorgt dafür, dass er das an jeder relevanten Stelle im Ablauf **belegen
muss** – mit einem ausgeführten Kommando (Linter, Testlauf, Statik-Check),
nicht mit einem Satz in der Antwort.

CUSTOS ist als Claude-Code-Plugin gebaut und Teil der Renker-Industries-
Produktfamilie – die querschnittliche Qualitäts- und Sicherheitsschicht über
allen Projekten.

## Was es tut

Vier Ebenen, jede auf einen realen Claude-Code-Baustein abgebildet:

- **Haltung** – Ein Default-Agent (`senior-dev`) eröffnet jede Session und
  triagiert: trivial oder planungspflichtig.
- **Reflexe** – Hooks speisen Kontext ein und erzwingen Rückfragen, bevor blind
  geplant wird.
- **Mechanik** – Hooks führen Linter/Statik-Tools aus und blocken bei Exit-Code 2.
- **Beweise** – Ein `Stop`-Hook erzwingt einen Testlauf/Linter, bevor die Session
  enden darf. Kein grüner Exit-Code, kein Sessionende.

### Enthalten (Roadmap-Phase 1–11, Konzept vollständig umgesetzt)

**Agenten:** `senior-dev` (Default, Triage), `plan-reviewer`, `scope-guard`,
`root-cause` (Debug-Kausalanalyse), `council-advisor` ×5 + `council-chair`,
`plain-text-translator`.

**Skills/Modi:** `grill-me`, `plan-mode`, `build-mode`, `debug-mode`,
`cleanup-mode`, `data-analytics-mode`, `fleet-mode`, `security-mode`,
`council-mode`, `multi-session`.

**Gates (Hooks, Konzept Abschnitt 8):**
- `UserPromptSubmit` – Trivial-Schranke (Triage-Reminder)
- `PreToolUse ExitPlanMode` – Plan-Freigabe (blockt bis Plan-Reviewer freigibt)
- `PreToolUse Write|Edit` – Scope-Wächter + DB-Schema-Guard
- `PostToolUse` – AI-Slop-Detektor, Statik-Dispatch (ruff/`py_compile`, eslint),
  Impact-Analyse, A11y-Check
- `Stop` – Beweis-Gate (erzwingt grünen Proof-Lauf)
- `SubagentStop` – Regressions-Wächter (blockt grün→rot)

**Werkzeuge (`bin/`):** Fleet-Discovery (lokal + GitHub, read-only), Fleet-
Auto-Fix (opt-in Branch+PR, dry-run default), passive Security-Checks, Council-
Log, Multi-Session-Task-Queue, Dashboard-Generator, Selbstqualifizierung.

**Zero-Tolerance-Modus** (Abschnitt 16): `CUSTOS_ZERO_TOLERANCE=1` bzw.
`zeroTolerance: true` – fail-closed, blockt bei jedem einzelnen Fund.

Alle Funde landen zeitgestempelt in `custos_findings.json` – ein Beleg, keine
Behauptung. Dashboard: `python bin/build_dashboard.py` → `interface/`.

## Installation

```bash
# Als lokales Plugin laden
claude --plugin-dir /pfad/zu/custos
```

Optional eine `custos.config.json` im Repo-Root anlegen (siehe
`custos.config.example.json`), um das Beweis-Kommando festzulegen:

```json
{ "proofCommand": "pytest -q" }
```

Ohne Konfiguration erkennt das Beweis-Gate `pytest` oder ein `npm test`-Skript
automatisch.

**Voraussetzung:** Python 3 auf dem PATH (die Detektoren sind plattform-
unabhängig in Python geschrieben – keine WSL-Pflicht unter Windows).

## Dogfooding

CUSTOS wendet die eigenen Regeln auf sich selbst an: `python bin/selfqual.py`
lässt die Referenz-Testsuite (`tests/`) laufen – dieselbe Beweispflicht, die
CUSTOS für andere Projekte durchsetzt. CI (`.github/workflows/custos.yml`) macht
das bei jedem Push/PR.

## Status

Version 0.2.0 – der Konzept-Funktionsumfang (Roadmap-Phase 1–11) ist umgesetzt.
Bewusst als scharf-zu-schaltende Platzhalter belassen: aktive Security-Scans
(nmap/ZAP, brauchen befüllte `custos/scope.yaml`) und Fleet-Auto-Fix-Push (opt-in
pro Repo). Details und Feinschliff-Punkte in
[`ROADMAP_STATUS.md`](ROADMAP_STATUS.md).

## Lizenz

MIT License – Copyright (c) 2026 Renker Industries. Siehe [`LICENSE`](LICENSE).
