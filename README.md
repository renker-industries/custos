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

### In diesem Stand enthalten (Roadmap-Phase 1–3)

- `senior-dev` – Default-Agent (Haltung, Triage, Delegation)
- `plan-reviewer` – prüft jeden Plan gegen Scope/Sicherheit/Vollständigkeit
- **AI-Slop-Detektor** (`PostToolUse`) – findet Füllkommentare, generische Namen,
  Duplikate, triviale Wrapper; ab Schwellwert blockierend
- **Statik-Analyse-Dispatch** (`PostToolUse`) – Python (ruff/`py_compile`),
  JS/TS (eslint), blockierend bei Lint-Fehlern
- **Beweis-Gate** (`Stop`) – erzwingt und prüft ein Proof-Kommando

Alle Funde landen zeitgestempelt in `custos_findings.json` – ein Beleg, keine
Behauptung.

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

## Status

Frühe Version (0.1.0). Umgesetzt ist der Kern „Beweis statt Behauptung"
(Roadmap-Phase 1–3). Der weitere Funktionsumfang (Fleet-Modus, Security-Mode,
Council, Multi-Session, Interface, Selbstqualifizierung) ist in
[`ROADMAP_STATUS.md`](ROADMAP_STATUS.md) als offene Punkte dokumentiert.

## Lizenz

> **Platzhalter – Lizenzwahl noch offen.** MIT/Apache-2.0 (offene
> Weiterverwendung) vs. restriktiver (falls kommerziell) ist vor
> Veröffentlichung bewusst zu entscheiden – siehe `DECISIONS.md` und
> Konzept-Abschnitt 20. Bis dahin: alle Rechte vorbehalten, Renker Industries.
