---
name: council-mode
description: >-
  Resolve a disputed finding where static analysis and the model's judgement
  disagree, or a suppression request. Convenes five independent advisors and a
  chair, then records the binding decision. Use when a gate finding is contested or
  someone wants to suppress a finding.
---

# Council Mode

Static analysis and the model do not always agree. When they conflict, the finding
is not decided by whoever is more convenient — it goes to the council.

## Ablauf

1. **Fünf Advisor parallel.** Spawn the `council-advisor` agent five times (via the
   Agent tool) on the same disputed finding, independently. Each returns a vote
   (`UPHOLD` / `DISMISS` / `SUPPRESS-WITH-EXPIRY`) with a one-paragraph rationale.
2. **Chair entscheidet.** The `council-chair` agent aggregates the five votes into
   one binding decision (security wins ties; suppressions need an expiry).
3. **Protokollieren.** Record the decision in the audit log:
   ```bash
   python bin/council_log.py --finding "<desc>" --decision uphold|dismiss|suppress \
       --votes "4 uphold, 1 dismiss" --rationale "<why>" [--expiry YYYY-MM-DD]
   ```

## Regeln (concept section 16)

- **Keine stille Selbst-Freigabe.** A finding may only be suppressed through this
  council flow, never by the working model deciding on its own.
- **Suppression braucht Ablaufdatum.** `council_log.py` refuses a suppression
  without a future `--expiry`; the finding re-surfaces after it.
- **Bestandscode zählt wie neuer Code.** "It was always like this" is not a reason
  to dismiss.
