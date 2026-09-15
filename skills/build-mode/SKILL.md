---
name: build-mode
description: >-
  Implement an approved plan under the CUSTOS gates. Use after a plan is approved
  and ExitPlanMode has opened. Keeps changes inside the approved scope and ends
  only on an executed proof.
---

# Build Mode

Implementation happens against an approved plan, with the gates live.

## Regeln während des Baus

- **Innerhalb des Scopes bleiben.** The scope-guard blocks edits outside the
  approved scope; if you genuinely need more, widen the plan and re-approve —
  never work around the gate. The `scope-guard` agent watches for softer drift.
- **Kleinste ausreichende Änderung.** No opportunistic refactors; those are a
  separate task.
- **Nach jeder Änderung laufen die Gates:** ai-slop, static analysis,
  impact-analysis, a11y (frontend), db-schema (migrations). Fix what they block
  before moving on — do not accumulate red gates.
- **DB-Änderungen** gegen das echte Schema (db-schema guard), keine erfundenen
  Felder.

## Abschluss

- Der `Stop`-Beweis-Gate verlangt einen grünen Test-/Linter-Lauf, bevor die
  Session enden darf. Führe den Beweis aktiv aus und nenne Kommando + Ergebnis.
- Bei Subagenten prüft der `SubagentStop`-Regressions-Wächter, dass nichts
  vorher Grünes jetzt rot ist.
