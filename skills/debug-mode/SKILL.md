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

## Flow

1. **Reproduce.** Turn the report into a concrete failing command/input and
   capture the exact error. If it cannot be reproduced, that is the first thing
   to resolve — do not patch a bug you cannot trigger.
2. **Root-cause agent.** Delegate to the `root-cause` agent. It does not stop at
   the first plausible cause; it forces at least one alternative hypothesis and
   backs the chosen cause with evidence.
3. **Minimal fix.** Apply the smallest change that removes the proven cause.
   No opportunistic refactors in a bug fix (that is scope drift → a separate task).
4. **Proof.** Re-run the original repro (must pass) and the existing tests (must
   stay green). The CUSTOS `Stop` proof gate independently demands this.

## Anti-patterns (blocked)

- "It was probably X" without a repro and without evidence.
- A fix without a re-run of the original repro.
- Masking the symptom (catching/suppressing the error) instead of fixing the cause.
