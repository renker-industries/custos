---
name: cleanup-mode
description: >-
  Reduce clutter and dead weight in a codebase without changing behaviour: remove
  dead code, duplicate logic, unused files/deps, and AI-slop, each proven safe by
  tests staying green. Use for refactor/cleanup tasks, never mixed into a feature
  or bug-fix task.
---

# Cleanup Mode

Cleanup is behaviour-preserving by definition. The proof obligation here is:
**the tests are green before and after, and nothing that is still used was
removed.**

## Vorgehen

1. **Baseline sichern.** Run the proof command first and record it green — that is
   the "before" the regression guard compares against. Never start cleanup on a
   red baseline.
2. **Kandidaten finden:**
   - Dead code / unreachable branches, unused files.
   - Duplicate logic (fold into one, do not multiply).
   - Unused dependencies / imports.
   - AI-slop the detector flags (filler comments, generic names, trivial wrappers).
3. **Vor dem Entfernen: Nutzung prüfen.** Use the impact analysis — a symbol
   referenced elsewhere is not dead. When unsure whether something is used, keep it
   and say so.
4. **In kleinen Schritten.** One coherent cleanup per step, re-run the proof after
   each. A cleanup that turns a test red is not a cleanup — revert it.

## Grenze

- **Kein Verhaltenswechsel.** If a change alters behaviour, it is a feature/fix and
  belongs in a planned task, not here.
- **Keine großflächige Umschreibung** getarnt als Cleanup (scope drift).
