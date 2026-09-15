---
name: plan-mode
description: >-
  Produce an implementation plan that can pass the plan-reviewer and open the
  ExitPlanMode gate. Use for any non-trivial task after requirements are clear.
---

# Plan Mode

A plan under CUSTOS is not a wish list — it is the contract the build is measured
against. The `plan_gate` blocks `ExitPlanMode` until the `plan-reviewer` approves,
so write the plan to survive that review.

## Der Plan muss enthalten

1. **Ziel & Fertig-Kriterium** — observable, testable.
2. **Scope** — exactly which files/modules will change (this becomes the approved
   scope the scope-guard enforces). Name what is explicitly out of scope.
3. **Schritte** — small, ordered, each independently verifiable.
4. **Sicherheit** — for every touched security surface, the control that covers it.
5. **DB-Auswirkung** — any schema/migration change, checked against the real
   schema (db-schema guard), no invented fields.
6. **Betroffene Module / Aufrufer** — who calls the code being changed.
7. **Beweisplan** — the exact test/linter/check that will prove each part.

## Freigabe

- Route the finished plan to the `plan-reviewer` agent.
- On `APPROVED`, record it: `python bin/custos_approve_plan.py --scope "<glob>" ...`
  with the plan's file scope. This opens the ExitPlanMode gate and arms the
  scope-guard.
- On `CHANGES REQUIRED`, revise and resubmit. Do not exit plan mode.
