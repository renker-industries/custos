---
name: debug-mode
description: >-
  CUSTOS debug workflow. Use when the task is to fix a bug, a failing test, a
  crash, or a regression rather than to build a new feature. Enforces
  reproduce-before-theorize and delegates the causal analysis to the root-cause
  agent, which must rule out a second cause before any fix.
---

# Debug Mode

Bug fixing under CUSTOS follows one rule: **reproduce before you theorize, prove
before you claim fixed.**

## Ablauf

1. **Reproduzieren.** Turn the report into a concrete failing command/input and
   capture the exact error. If it cannot be reproduced, that is the first thing
   to resolve — do not patch a bug you cannot trigger.
2. **Root-Cause-Agent.** Delegate to the `root-cause` agent. It does not stop at
   the first plausible cause; it forces at least one alternative hypothesis and
   backs the chosen cause with evidence.
3. **Minimaler Fix.** Apply the smallest change that removes the proven cause.
   No opportunistic refactors in a bug fix (that is scope drift → separate task).
4. **Beweis.** Re-run the original repro (must pass) and the existing tests (must
   stay green). The CUSTOS `Stop` proof gate independently demands this.

## Anti-Pattern (blockiert)

- "Vermutlich lag es an X" ohne Repro und ohne Beleg.
- Fix ohne erneuten Lauf der ursprünglichen Repro.
- Symptom kaschieren (Fehler abfangen/unterdrücken), statt Ursache beheben.
