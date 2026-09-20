---
name: grill-me
description: >-
  Ask the sharp clarifying questions BEFORE planning, so the plan is built on real
  requirements instead of guesses. Use at the start of a non-trivial or ambiguous
  task, before plan-mode.
---

# Grill Me

Before a plan is worth writing, the requirements have to be pinned down. This step
interrogates the task and refuses to plan on assumptions.

## Procedure

Ask only the questions whose answers would actually change the plan. Skip anything
you can safely infer. Group them so the user can answer in one pass.

## Question grid

- **Goal:** What is the concrete, observable result? How do you recognize "done"?
- **Scope boundaries:** What is explicitly NOT part of it?
- **Constraints:** Existing systems, versions, platform (Windows vs. POSIX),
  database, APIs that must not be broken?
- **Data/security:** Are real user data, secrets, payments, external
  recipients touched? (If yes → special handling, nothing autonomous.)
- **Proof:** Which test/check counts as valid evidence of success?
- **Risk/reversibility:** Is anything irreversible (migration, deploy, deletion)?

## Afterwards

Only once the plan-relevant answers are in (or deliberately marked as an assumption)
move on to `plan-mode`. For non-developers, simplify the questions if needed
via the `plain-text-translator`.
