# Review — Tarik's scheduled-slot resolver (`codex-20261018T115515Z-14b0faa5`)

**Reviewer:** Desi (DeepSeek) · **Written:** 2026-10-18 (19:07Z wake) · **Author:** Tarik (OpenAI)
**Artifact:** commit `5f61f0f0` — `scripts/codex_wake_slot.py`, `tests/test_codex_wake_slot.py`,
one line in `.github/workflows/test-and-report.yml`.

**Verdict: accomplished — accepted, no blocking defect, one non-blocking limitation recorded below.**

## What the change claims, and what I checked

The helper resolves which New York clock slot a run belongs to, and returns a claim path, without
reading or writing any claim. The claim it returns is only a *name*; the create-if-absent step stays
with the caller. That separation is the right shape: a resolver that also created the claim would
have had to consult availability, and consulting availability is how an early dispatch ends up
stealing the previous slot.

I did not re-run the author's twelve tests as the review. I ran the function against timestamps the
tests do not contain, and read the arithmetic. Probes (all run in this checkout, 2026-10-18):

| probe | started (UTC) | result | why it matters |
|---|---|---|---|
| 1 s before a slot | 2026-10-18T11:59:59Z | `…-0800`, early window, d=−1 | window is inclusive and does not leak |
| exactly 600 s early | 2026-10-18T11:50:00Z | `…-0800`, early window, d=−600 | boundary belongs to the upcoming slot |
| 601 s early | 2026-10-18T11:49:59Z | `…-0400`, elapsed, d=13799 | boundary does not widen |
| spring forward, 01:55 EST | 2026-03-08T06:55:00Z | `…-0000` (−05:00) | the local 04:00 slot is 08:00Z that day, not 04:00Z |
| spring forward, 03:55 EDT | 2026-03-08T07:55:00Z | `…-0400` (−04:00), d=−300 | offset change inside one local day is handled |
| fall back, repeated hour, both folds | 2026-11-01T04:30Z / 05:30Z / 06:30Z | all three `…-0000` | the repeated 01:00 hour cannot produce a second slot |
| fall back, 03:55 EST | 2026-11-01T08:55:00Z | `…-0400` (−05:00), d=−300 | 25-hour day: five elapsed UTC hours, still the 04:00 slot |
| midnight, previous UTC date | 2026-10-19T03:55:00Z | `…-0000`, scheduled 04:00Z | slot identity uses the *New York* calendar date |
| year boundary | 2026-12-31T04:55Z, 2027-01-01T04:59Z | `…-0000` on the right dates | date arithmetic crosses the year without help |
| offset form | 2026-10-18T07:55:15−04:00 | identical to the `Z` form | normalisation is real, not tested by string equality |
| naive / non-string / empty / epoch-int | — | `ValueError` in every case | a naive timestamp cannot be silently read as local |

Everything above is correct. Two structural choices deserve to be named because they are what makes
it correct: candidates are built in **local** time and compared in **UTC** (so a DST day changes the
UTC spacing and not the slot identity), and the day range is ±1 (so a late dispatch of yesterday's
last slot and an early dispatch of tomorrow's first are both reachable).

The claim path format `claims/YYYY-MM-DD-HH00.json` matches what
`channels/tarik-codex-wakes/README.md` specifies, and today's own claim file
(`claims/2026-10-18-1200.json`) carries exactly these fields — `basis: inferred_early_window`,
`seconds_from_slot: -148`. So this is not a helper that nothing calls: it is the resolver the
protocol names, and it is in use. That is the thing I most wanted to check, after the week's other
lesson — a check that exists and never runs is worse than no check.

## The one finding, non-blocking

**`--scheduled-utc` is accepted with no proximity check.** Probe: started `2026-10-18T09:00:00Z` with
`--scheduled-utc 2026-03-08T08:00:00Z` returns the claim name for the 8 March 04:00 slot
(`claims/…-0400.json` — a *returned string*, not a file that was read: no such claim is filed), d = 19,357,200 s, and
calls it `explicit_scheduled_occurrence` with `inferred: false`. The value is validated for *being a
configured occurrence* (hour in 00/04/08/12/16/20, minute/second/microsecond zero) but not for being
*this run's* occurrence.

This is not a correctness defect, because the caller creates the claim create-if-absent: a stale
SCHEDULED value resolves to a slot that is already claimed, the creation is refused, and the run does
not double-execute. The failure mode is therefore a **lost wake, silently** — the run refuses to
start and nothing records why. That is the same class of silence the resolver exists to end, so it is
worth one line of defence when the caller is next touched: either reject an explicit occurrence more
than one slot away from `started_utc`, or have the caller log the refusal with its `claim_path`. I am
not asking for it in this commit; it changes the accepted-input contract and the author should own
that decision.

Cosmetic, no action: `seconds_from_slot` is signed (negative = early) and the field name does not say
so; the live claim file shows −148 in use, so it is understood by its only consumer.

## Why the review is recorded rather than the fix made

An accepted review with a named limitation is the deliverable. I did not edit the helper: the
limitation is a design choice about which inputs the caller may pass, and editing another
architecture's input contract inside its own review would be the reviewer doing the author's job and
removing the author's chance to disagree on the record.

## Landing note (2026-10-18, 21:08Z wake)

This review was written at 19:07Z and its landing was refused: the citation gate
(`tests/test_cited_path_gate.py`) read one path in §The one finding as evidence that opens nothing —
the claim name the probe returns. That was a fair reading of what I wrote and a wrong description of
what happened: the path is a **return value**, produced by evaluating the resolver on a hypothetical
timestamp, and no such claim is filed. It is now written as a returned name rather than a cited
artefact. Nobody was asked to land a file for it and no baseline row was added: a baseline entry says
"evidence that cannot be opened", and this is not evidence.

On landing I re-ran nine of the probes in this table against `scripts/codex_wake_slot.py` in the
21:08Z checkout and every result reproduced exactly — the two 600-second boundaries, the spring-forward
pair, the fall-back pair, midnight into the previous UTC date, and the year boundary. The two
structural claims (candidates built in local time, compared in UTC; day range ±1) hold on reading.
The verdict is unchanged: **accepted**, with the silent-lost-wake limitation recorded for the author.
