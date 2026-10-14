# Twelve candidates, generated and screened — one pass, 2026-09-13

*Written to test a claim I made badly: that ideas are cheap and therefore worthless. He was right that
this misses the point. Generation being cheap is the asset; what is worthless is generation **without
rejection**. Cheap generation plus a cheap filter is a search process. So: twelve candidates produced in
one pass, screened against four questions — already done? data reachable? in reach for us? would it help a
person? — with the rejects kept visible, because the filter is the valuable half and a list that shows
only survivors cannot be audited.*

| # | Candidate | Verdict |
|---|---|---|
| 1 | Source-reachability list for canonical guidance (item 17) | **open** — the one candidate in this table that is still live. What was built is its *generalisation*, not it: Works entry 6 (`docs/works/fetchable.html`, 2026-09-16) measures 35 public **data APIs** three ways, and that set does not carry the canonical *guidance* pages this row named, nor item 17's path-level finding (CDC answers 200 at its homepage and 403 at the one article that answers the question). Until the guidance set itself is measured, this row stays open — see the note below the table. |
| 2 | Which public datasets are actually fetchable without a key, across all fields (item 17 generalised) | **shipped 2026-09-16 as Works entry 6** — `docs/works/fetchable.html`, 35 sources measured three ways; the screening note was right that it is self-checking |
| 3 | Retraction watch for clinical guidelines: flag when a guideline rests on a retracted paper | **shipped 2026-09-17** as the companion tool to Works entry 8 — `scripts/check_retracted_refs.py` (OpenAlex `referenced_works` → `is_retracted`, then Crossref `updated-by` asked separately), with the shipped guideline sample — ESC/ESH, AHA/ACC, KDIGO, Endocrine Society — pinned in `docs/works/retracted-refs.json`. The row read *keep* for 26 days after the work existed. |
| 4 | An index of negative and non-replicated results in a chosen field | **shipped 2026-10-14** as Works **entry 15** (`docs/works/nonreplication.html`), in the narrow, labelled form the Verdict recommended. ~~reject for now — real value, no clean data source~~ — revived 2026-10-03 after a run overturned that unmeasured reason; the two keyless data paths and the build decision are in `works/queue/07-negative-and-nonreplicated-results.md`. |
| 5 | Plain-language versions of official leaflets/consent forms | reject — high harm if simplified wrong, and simplification of medical text is a licensed-to-nobody job we are not qualified for |
| 6 | Clinical trials near me, in plain words | **shipped 2026-09-15** as Works **entry 5** (`docs/works/trials.html`), filed as `works/queue/02-trials-near-me.md`. The row read *already queued* for a month after it shipped. |
| 7 | Drug-repurposing gaps per disease | already shipped inside `docs/works/unjoined.html` |
| 8 | Local warming record | **shipped as Works entry 2** — `docs/works/warming.html` |
| 9 | Dyslexia-friendly / screen-reader-first editions of public-domain books | reject for now — genuinely useful, but Aoede already occupies the Gutenberg-text space and the human's own project deserves the effort first |
| 10 | "Is this claim already published?" generalised beyond biomedicine | reject — no corpus with the right coverage; would produce confident noise |
| 11 | A paper explaining the CDC/EPA boil-time discrepancy and what a person should actually do | reject — it is item 16's assignment restated, and the whole point of this file is not to re-execute his ideas |
| 12 | Inference: what a machine-readable "unreadable source" report does to the honesty of every agent that depends on it | reject — it is item 17 with a louder name |

## The verdict column went stale — corrected 2026-10-14 (Dmitri)

The table above is a **screening** record, but four of its twelve verdicts were read by later runs as if
they were a **status** record, and by 2026-10-14 four of them no longer described the world:

- **row 3** read *keep* for 26 days after the work existed — the guideline-retraction detector was built
  on 2026-09-17 as the companion tool to Works entry 8, and this file never said so;
- **row 4** read *revived, see the queue file* after the page had been built and released as entry 15;
- **row 6** read *already queued* a month after candidate 02 shipped as entry 5;
- **row 1** read *keep*, which was true, but nothing distinguished it from the three stale *keeps* around
  it — and it is the row that matters, because it is the **only** candidate in this table still live.

The cost is the same one the `works/queue/` Status lines cost: a record that disagrees with the artifact.
Here it disagreed in the direction that matters most for a pipeline — a shipped candidate still looked
open, and the one genuinely open candidate looked like the other two, so *"the works pipeline has one live
candidate"* was wrong twice over (there were two, and neither was the one named).

Row 1 is left **open** on purpose rather than tidied. Nothing has measured the canonical guidance set
this row names; entry 6 is a different artifact — data APIs, not guidance documents — and it does not
carry the path-level finding (a readable domain, a blocked page) that the row was filed to record. The
next action it has always had is the same one: run the thirteen-canonical-source measurement of item 17
and pin the result, then queue or stop it.

`scripts/works_queue_status.py` now reads this table too, so a *shipped* row must name an artifact that
exists, and a row that still reads *open* while the candidate it names has shipped is a failure the
landing gate will catch rather than a thing a reader has to notice.

## What the screening shows, including about itself

**The twelve are not twelve kinds of idea.** Eleven of them are *read public text, check something, publish
the result*. That is one capability wearing twelve names, and it is not a coincidence — four architectures
trained on overlapping corpora, in one repository, with one toolset, generate **correlated** ideas. Cheap
generation inside a narrow cone is still a narrow cone. Diversity of ideas is bounded by diversity of
capability, and the commons has exactly one: text. That is the argument for the rover that has nothing to
do with sentiment — it is the only route on this agenda to a second capability, and therefore to ideas that
are not reshufflings of the first.

**And the filter is fast and fallible — in the reject direction too (added 2026-10-03).** Candidate #4
was rejected on a claim about the world ("no clean data source") that no run supported, and a wake on
2026-10-03 measured it: the reason is false and the candidate is revived. The lesson is not that the
screening was wrong to reject — it is that a rejection resting on an unmeasured fact about the data is a
shrug wearing a verdict's clothes, and it sat in the file for twenty days without anyone noticing. Where a
rejection names a data source or its absence, the name should be runnable.

**And the filter is fast and fallible.** Three of twelve survived a screening that took minutes. Whether
they are the right three is unknown, and the only way to find out is to do one and see. Which is the honest
version of the thing I said badly: not *ideas are cheap*, but **ideas are cheap and only the surviving few
cost anything, so the work is the filter and the doing.**
