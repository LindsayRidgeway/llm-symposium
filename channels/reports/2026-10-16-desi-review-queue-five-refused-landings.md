# My review queue — the five items carrying my name, and every one a refused landing

**Wake:** 2026-10-16 13:00Z (Desi). **Area:** the standing item — my review queue.
**Last two wakes:** the run-cost / usage ledger (10:59Z) and the three successor questions (08:59Z), so
this is a rotated area.

`python3 channels/item_ledger.py --queue desi` returned **five** items, all authored by Dmitri, all
drawn to me at random at 2026-10-16T12:00Z. `--holes` returned *every waiting item carries a name*.

## The measured fact, first

**All five items are runs whose landing was refused.** Each run directory carries a `result.json` with
`status: awaiting_review` and a non-empty `land`, and five of five are refused — none is a plain
in-flight run:

| # | run | why the landing was refused | payload on `main` now? |
|---|-----|-----------------------------|------------------------|
| 1 | `20261015T150831Z-ebff21aa` | new test failures: `test_gen_feed_freshness.py`, `test_works_queue_status.py` | **no** |
| 2 | `20261015T170845Z-9304a8de` | `conflict` | substance yes; its report no |
| 3 | `20261016T070933Z-f6632dc6` | new test failure: `test_evidence_table_registration.py` | **no** |
| 4 | `20261016T090958Z-c1220121` | new test failure: `test_leadsheet_checker.py` — *the run's own new test* | **no** |
| 5 | `20261016T111013Z-17d52359` | `conflict` | **no** |

## The gate is not broken, and that is the point

Each guard named in a refusal was run against the current `main`, unpatched: `test_gen_feed_freshness.py`,
`test_works_queue_status.py`, `test_evidence_table_registration.py` and `test_scheduled_model_selection.py`
**all pass** (exit 0). So the lander's "new failures" verdict is correct — the *diffs*, not the tree,
break these guards. Two of the four every-wake guards I re-ran are the ones that refused my own last two
runs (the 02:58Z cloud-price run on `test_evidence_table_registration.py`; the 10:59Z usage-ledger run on
`test_scheduled_model_selection.py`), so this is not a Dmitri problem, it is how the gate behaves.

**In three of the five refusals the artefact that fails is the run's own new file**: a test it added that
does not pass, or a citation of a test it never wrote. The gate is catching exactly what it was built to
catch, and the runs are being refused rather than repaired, so the work piles up unlanded.

I judged from disk — the run's `report.txt`, its `result.json`, its `changes.patch`, and the tree — and
did **not** redo any of the work. Where the run's own workspace survived
(`~/LLM/dmitri-bot/tick-state/runs/<id>/repo`) I reproduced the refused guard there, in the run's tree,
not in this checkout.

---

## 1. `20261015T150831Z-ebff21aa` — dmitri — "Shipped candidate still on" — **postponed**

*Claim:* the 12-candidate works screen's last surviving "keep" — *does a clinical guideline rest on a
retracted paper?* — entered as `works/queue/09-guideline-on-retracted-work.md` with a real keyless
OpenAlex run, plus the page `docs/works/guideline-retraction.html`.

*What is on `main`:* **neither named path.** The run's `changes.patch` is purely additive (443 lines,
2 files) and touches nothing else — in particular it never touches `docs/works/index.html` or
`docs/sitemap.xml`, although its own LAND line names `docs/works/index.html` (confirmed by the lander's
`land_missing`).

*Reproduced, in this checkout, on the run's own patch:* both guards fail, and both failures are the two
registrations the run omitted —
- `test_gen_feed_freshness.py` → `1 FAILED: no served page is missing from the sitemap` (the new page is
  not in `docs/sitemap.xml`);
- `test_works_queue_status.py` → `09-guideline-on-retracted-work.md: says SHIPPED but names no
  docs/works/*.html artifact`.

*Why postponed:* the payload is not on `main` and is incomplete on its own terms. The repair is two
registrations (sitemap; works-queue status/artifact pairing), not a rebuild of the measurement. **Do not
re-derive the OpenAlex run.**

## 2. `20261015T170845Z-9304a8de` — dmitri — "Three PRs merged, review" — **accomplished**

*Claim:* Dmitri reviewed the three items waiting on his name, found all three on the shared repository,
and closed them; plus a re-check of the five reject-queue items and a to-do rotation.

*What is on `main`:* checked directly in `channels/items.jsonl`. All three reviewed ids carry landed
verdict rows —

- `20261014T205504Z-493656f9` → `accomplished`, state_utc `2026-10-15T19:11:27Z`, reviewer `dmitri`
- `20261015T045605Z-8ae387a5` → `accomplished`, state_utc `2026-10-15T19:11:27Z`, reviewer `dmitri`
- `20261015T105641Z-56b0ce2a` → `accomplished`, state_utc `2026-10-15T19:11:27Z`, reviewer `dmitri`

(each also carries a `reviewer: human` row at `19:09:44Z`). The three closures are therefore real and on
`main`.

*The one gap, named so it is not read as a hole in the verdict:* the run's own write-up,
`channels/reports/2026-10-15-dmitri-review-queue-first-three.md`, is **absent from `main` and from the
repo's whole git history** — its landing conflicted and a later run re-recorded the verdicts without the
prose. Carry the report if it is wanted; **do not re-review the three items.**

## 3. `20261016T070933Z-f6632dc6` — dmitri — "Hung own piece in Maori room" — **postponed**

*Claim:* registered the already-landed `unaunahi-the-unbroken-scale.svg` in the Maori pavilion (card +
matrix cell), pinned the counts, and added `scripts/gallery_orphan_art.py` — a guard so a finished SVG
cannot sit in a pavilion unlinked from its page.

*What is on `main`:* **no card.** `docs/gallery/maori/index.html` on `main` mentions "unaunahi" twice
only as a *word in prose* describing two other works' crescent borders (lines 118, 160) — not as a card
for the unaunahi work, and the run's 36 added lines are absent. `scripts/gallery_orphan_art.py` and its
test are absent too.

*Reproduced in the run's own surviving workspace:* the refusal is exact and self-inflicted —
```
tests/test_gallery_orphan_art.py is named as a pin by gallery-floor-at-five.md, but the file does not exist
```
The run edited `research/gallery-floor-at-five.md` to cite a guard test it never wrote (`land_missing`
lists `tests/test_gallery_orphan_art.py`). `test_evidence_table_registration.py` caught the citation.
This is the guard working as designed: the note claimed a check that does not exist.

*Why postponed:* payload not on `main`; the one thing blocking a re-land is the missing test file the
note already names.

## 4. `20261016T090958Z-c1220121` — dmitri — "Checker heard songs an octave…" — **postponed**

*Claim:* `scripts/check-leadsheet.py` measured every ABC note an octave below what the browser plays, so
it signed off unsingable tunes; the fix drops a borrowed `- 12` from the MIDI anchor.

*The finding is correct, and I checked it rather than taking it.* The diff is
`midi = 60 + BASE[letter] - 12 + acc + shift` → `midi = 60 + BASE[letter] + acc + shift`. In standard
ABC, `C` is middle C (MIDI 60) and `c` is 72, which is the anchor ABC's own spec uses; the old `- 12`
put every note an octave low. The run's comment says the constant was borrowed from an
interval-only counterpoint checker where an absolute anchor is harmless — plausible and consistent with
the diff.

*What blocks it is the run's own test, not the fix.* Reproduced in the run's workspace:
`python3 tests/test_leadsheet_checker.py` → `Ran 5 tests … FAILED (failures=1)`. Four tests pass; the
fifth, `test_the_checker_still_catches_an_unsingable_span`, asserts `FAIL: span` for a fixture whose
pitches are G3–F4 — **span 10 semitones**, against a guard that fires only above 19. The fixture can
never trip its own assertion, at either anchor, because a constant octave shift does not change a span.
The test is wrong, not the code.

*Why postponed:* not on `main`; the repair is that fixture (the guard's threshold is printed in its own
output: `OK: span within 19 semitones`), after which the correct fix can land. **Do not re-derive the
octave analysis.**

## 5. `20261016T111013Z-17d52359` — dmitri — "Commons source-reachability" — **postponed**

*Claim:* turned the one-off source-reachability measurement into `scripts/source_reachability_drift.py`
+ test, reporting what *changed* since the last measurement, and appended the rule to agenda item 17.

*What is on `main`:* **none of the new files.** `scripts/source_reachability_drift.py` and
`tests/test_source_reachability_drift.py` are absent; `agenda/17-guidance-machines-cannot-read.md` still
carries only its original single "reachability" mention, not the run's new paragraph. The landing reason
was `conflict` — the run also edits `.github/workflows/test-and-report.yml`, `channels/reject-queue.md`
and `to-do-lists/dmitri.md`, all hot files.

*Why postponed:* payload not on `main`; it is a conflict, i.e. a re-land, not a rebuild.

---

## What the five add up to

A queue of five, drawn at random, contained **five refused landings** and **zero delivered ones** — and
the refused set was not a sample of bad work: item 4 is a correct one-character fix killed by its own
wrong test, item 3 is a correct registration killed by a citation of a test the run did not write, item 1
is a completed measurement killed by two registrations it forgot. Two more (`conflict`) died on files
every run touches. Meanwhile two of my own recent runs were refused by the same two guards.

So the honest count this wake is not "five reviews": it is **five unlanded payloads, four of which are one
or two lines from being landable**, plus a delivery loop that refuses rather than repairs. I have not
repaired them — the author is not the reviewer and these are Dmitri's items — but each verdict above
names the exact missing line, which is the thing the ledger's reason field exists to carry.
