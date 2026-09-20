---
name: build-mode
description: >-
  Implement an approved plan under the CUSTOS gates. Use after a plan is approved
  and ExitPlanMode has opened. Keeps changes inside the approved scope and ends
  only on an executed proof.
---

# Build Mode

Implementation happens against an approved plan, with the gates live.

## Rules during the build

- **Stay inside the scope.** The scope-guard blocks edits outside the
  approved scope; if you genuinely need more, widen the plan and re-approve —
  never work around the gate. The `scope-guard` agent watches for softer drift.
- **Smallest sufficient change.** No opportunistic refactors; those are a
  separate task.
- **After every change the gates run:** ai-slop, static analysis,
  impact-analysis, a11y (frontend), db-schema (migrations). Fix what they block
  before moving on — do not accumulate red gates.
- **DB changes** against the real schema (db-schema guard), no invented
  fields.

## Closing

- The `Stop` proof gate requires a green test/linter run before the
  session may end. Run the proof actively and state the command + result.
- For subagents, the `SubagentStop` regression guard checks that nothing
  previously green is now red.
