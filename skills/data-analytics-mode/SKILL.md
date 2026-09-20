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

## Proof obligation for numbers

Before stating any value or trend:

1. **Show the origin.** Which source/table/query produced it? State the exact
   query or computation, not a paraphrase.
2. **Disclose the computation.** How is the value derived (filter, join,
   aggregation, unit, time window)? Name each step that could change the result.
3. **A second angle.** Recompute the same value a different way and show it
   matches:
   - a different aggregation path (sum of parts vs. total),
   - a different grain (per-day summed vs. period total),
   - a sanity bound (order of magnitude, non-negativity, row counts),
   - a spot check against a few raw records.
4. **A deviation = a finding.** If the two angles disagree, that is a finding to
   resolve, not a rounding note to wave away. Do not report the number until it
   reconciles or the discrepancy is explained.

## Typical silent errors (check actively)

- Duplicate rows from fan-out joins → inflated sums.
- Timezone / date boundary shifts daily/monthly values.
- NULL vs. 0 in averages and counts.
- Units/currency/scaling mixed.
- A filter that silently removes rows (INNER instead of LEFT join).

## Output

Every metric with: value · computation/query · cross-check (a second way) · result
of the cross-check (matches / deviation).
