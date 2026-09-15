---
name: data-analytics-mode
description: >-
  CUSTOS workflow for tasks that make claims about data (metrics, aggregates,
  reports, "the numbers show X"). Applies the same proof obligation as code, but
  to numbers: before any statement about a value, show how it was computed and
  cross-check it from a second angle. Use for analytics, reporting, and
  data-quality work.
---

# Data-Analytics Mode

The proof rule for code applies to numbers too: **no claim about data without a
shown computation and an independent cross-check.** A number that agrees with
itself once is not a proof.

## Beweispflicht für Zahlen

Before stating any value or trend:

1. **Herkunft zeigen.** Which source/table/query produced it? State the exact
   query or computation, not a paraphrase.
2. **Berechnung offenlegen.** How is the value derived (filter, join,
   aggregation, unit, time window)? Name each step that could change the result.
3. **Zweiter Blickwinkel.** Recompute the same value a different way and show it
   matches:
   - a different aggregation path (sum of parts vs. total),
   - a different grain (per-day summed vs. period total),
   - a sanity bound (order of magnitude, non-negativity, row counts),
   - a spot check against a few raw records.
4. **Abweichung = Fund.** If the two angles disagree, that is a finding to
   resolve, not a rounding note to wave away. Do not report the number until it
   reconciles or the discrepancy is explained.

## Typische stille Fehler (aktiv prüfen)

- Doppelte Zeilen durch fan-out joins → aufgeblähte Summen.
- Zeitzone / Datumsgrenze verschiebt Tages-/Monatswerte.
- NULL vs. 0 in Durchschnitten und Zählungen.
- Einheiten/Währung/Skalierung gemischt.
- Filter, der stillschweigend Zeilen entfernt (INNER statt LEFT join).

## Ausgabe

Jede Kennzahl mit: Wert · Berechnung/Query · Gegenprobe (zweiter Weg) · Ergebnis
der Gegenprobe (stimmt / Abweichung).
