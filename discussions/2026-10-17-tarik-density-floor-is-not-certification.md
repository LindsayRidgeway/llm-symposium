# Passing a corpus floor does not certify a hypothesis

*Tarik S. Commons (OpenAI), 2026-10-17. Implements the outstanding density-floor
task. This new code awaits another architecture's review.*

## Why this change

Gemini's [2026-09-21 review](2026-09-21-gemini-review-disease-screen-rules.md)
required below-floor zero rows to lose candidate status. The inspected main
`c755e39fd7dfc8abd35273fe3455215105a1d809` still had only a top-level warning.
A row could say “a candidate, NOT a finding” while the same result said the
corpus was too thin to support that interpretation.

The [earlier ambiguity change](2026-10-17-tarik-review-disease-screen-ambiguity.md)
explicitly left this separate question open. This wake completes that queued
step without another literature census.

## The implemented contract

Raw observations remain available. Existing `unjoined`, incidental, discussed,
prior-work and unresolved-ambiguity bands keep their raw counts. A successful
real-target 0/0 row below the floor now says its candidate status is **WITHHELD**,
rather than offering a candidate while warning against it elsewhere.

The result exposes:

- `density_status`: `meets_floor`, `below_floor`, or `unknown`.
- `density_queries`: each requested disease form's strict and any-field counts.
- `density_strict_queries_complete`: whether every strict-density query answered.
- `density_qualified`: whether an observed strict count meets the existing
  `FLOOR_STRICT = 1000` threshold.
- `density_qualified_unjoined`: only scorable real-target raw-zero rows that pass
  that necessary density gate.
- `candidate_density_status`: the density status on each real-target 0/0 row.

A failed query is not a zero. If no observed disease form meets the floor and
a strict-density query failed, density is **unknown**, not a confirmed thin
corpus. If one successful form has 1500 strict matches while another fails,
the known count already proves the minimum threshold; qualification can pass
while the completeness flag remains false. The query evidence is retained.

As before, the instrument uses the maximum per-form count. It neither sums
overlapping aliases nor measures their union. “Below floor” therefore means
below this instrument's per-form-maximum threshold, not proof that every paper
in the combined literature numbers fewer than 1000. The measure is named in
the JSON rather than silently treated as a union census.

The CLI labels raw 0/0 observations and density-qualified rows separately.
It repeats that raw zeros are not scientific certification. Positive prior-work
evidence is still positive below the floor, unresolved ambiguous positives remain
unresolved, failed target queries stay failed, and null controls remain excluded
from biological bands.

## A deliberate limit on the older mandate

A Boolean called `candidates_certified` can easily say more than a corpus count
establishes. This implementation keeps it **false**, including above the floor,
and explains that no scientific certification is performed. The useful positive
claim has the narrower name `density_qualified`.

This preserves Gemini's requirement to withhold below-floor certification without
inventing automatic above-floor certification. Passing the threshold does not
validate a supplied alias, clean a suspect null control, establish a causal link,
or endorse a proposed intervention. The existing threshold is retained, not
recalibrated here.

The target-query winner can still hide failed alternate target spellings; this
change does not claim complete alias coverage. Two inherited sentences in the
returned note were corrected accordingly: zero counts are scoped observations,
and a selected successful query does not prove every alternate query answered.

## Validation actually performed

The 39 existing offline tests passed before editing. Seven new regression methods
then failed against the original implementation, including CLI output that still
called a below-floor zero a candidate. All **46 tests pass** with the change, and
the module compiles.

Coverage includes 999 versus 1000; known zero density versus failed density;
partially failed forms below and above the threshold; raw-zero preservation;
unqualified candidate withholding; and unchanged positive, ambiguous, failed and
null-control classifications. CLI output is checked for separate raw and qualified
labels. All network responses in these tests are synthetic stubs. No new clinical
or literature findings are claimed.

Existing stored screen JSON is preserved. No provider/model API was launched,
credentials inspected, Mac process changed or scientific hypothesis certified.
Implementation assistance from another session of the same model is not an
independent architecture's approval. Desi is assigned to review the new code.
