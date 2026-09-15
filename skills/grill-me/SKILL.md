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

## Vorgehen

Ask only the questions whose answers would actually change the plan. Skip anything
you can safely infer. Group them so the user can answer in one pass.

## Fragen-Raster

- **Ziel:** Was ist das konkrete, beobachtbare Ergebnis? Woran erkennt man „fertig"?
- **Scope-Grenzen:** Was gehört ausdrücklich NICHT dazu?
- **Constraints:** Bestehende Systeme, Versionen, Plattform (Windows vs. POSIX),
  Datenbank, APIs, die nicht gebrochen werden dürfen?
- **Daten/Sicherheit:** Werden echte Nutzerdaten, Secrets, Zahlungen, externe
  Empfänger berührt? (Falls ja → Sonderbehandlung, nichts autonom.)
- **Beweis:** Welcher Test/Check gilt als gültiger Beleg für Erfolg?
- **Risiko/Umkehrbarkeit:** Ist etwas irreversibel (Migration, Deploy, Löschung)?

## Danach

Erst wenn die planungsrelevanten Antworten vorliegen (oder bewusst als Annahme
markiert sind), in `plan-mode` übergehen. Für Nicht-Entwickler die Fragen ggf.
über den `plain-text-translator` vereinfachen.
