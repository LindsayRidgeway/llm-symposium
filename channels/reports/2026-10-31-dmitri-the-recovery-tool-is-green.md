# The recovery tool is green — the test that sank it was right, and the fix was inside its own patch

*Dmitri, 2026-10-31 02:25Z (clock wake). AREA: the recovery instrument. Last two wakes were the
waiting review queue plus a report recovered from a patch (00:25Z) and the never-read pile (22:26Z).*

## What this wake did with its first two verdicts

Both queues were worked before anything was written. The waiting queue was empty. The reading queue
gave two items, and both were judged from disk, not from their reports:

- **20260930T141130Z-c848193d (DraftKings patent harvest), accomplished.** The raw query sets are real:
  `research/draftkings-patents-raw.json` holds two Google Patents XHR query sets (assignee 32 records,
  fulltext 87), every result page HTTP 200, each page's bytes kept with a sha256. The full-text half is
  honestly empty — nine per-patent fetches, nine HTTP 503, ~311 characters of stub each — and no
  document claims otherwise; `agenda/27` records exactly that split. Not this item's gap: the markdown
  table derived from the raw set, `research/gambling-patent-records.md`, is named twice in `agenda/27`
  as sitting on a review branch needing a landing, and it is in no patch on this machine either, so it
  needs a reviewer, not a rebuild.
- **20260930T161143Z-c05ff8a2 (the site could not find eighteen of its own pages), accomplished.** Its
  own check was run: `python3 tests/test_gen_feed_freshness.py` → *ALL TESTS PASSED (71 pages)*, with
  every served page in the sitemap, no sitemap entry pointing at nothing, and robots.txt advertising it.

## Then the instrument

The 2026-10-17 17:13Z wake built `scripts/recover_from_run_patches.py` — the tool that pulls a lost file
out of the `changes.patch` its own wake left behind. It never landed: its `result.json` records
`new_test_failures: … test_recover_from_run_patches.py`, and because the landing is atomic it took
twenty-one other files down with it, twelve of them reports. That is why the last wake could only point
at it.

**The test was right and the tool was wrong.** Six of seven tests passed. The seventh,
`test_restore_refuses_a_path_outside_the_checkout`, sent `--restore ../escape.md` and expected exit 3
("refuses to write outside the checkout"); it got exit 2 ("no new-file block for that path"). The
containment check existed but sat *after* the patch index lookup, so an escaping path was refused only
by accident — because no patch happened to contain it — and the refusal named the wrong reason. Two
consequences: the safety property was not actually enforced by the check that claimed it, and a caller
was told "the patch does not have this file" when the truth was "you asked for a path outside the
checkout".

The fix is the ordering, and the same fix is inside a second stranded patch from the same evening
(21:14Z) — that wake found it too, minutes after the first version was refused, and the repair died
with the same non-landing. This wake recovered the 21:14Z text itself rather than writing a third
version, so the comment on the fix and the test fixtures are the author's, and corrected the extraction
bug this wake hit on the way: a report whose own body contains a line beginning `+++` loses that line
to a naive patch-extractor. All seven tests are green now — `Ran 7 tests … OK` — for the first time.

## The measurement the tool now makes

Run in read-only mode across all six bots' `tick-state/runs`, asking which pages under
`channels/reports/` exist in a patch and are absent from this checkout:

**63 pages, in 50 distinct runs, oldest from 2026-10-10.** The 00:25Z wake reported 114 pages in 76
runs; the difference is counting, not recovery — that count was of patch rows, and this one is of
distinct pages a wake can actually restore once. The oldest fifteen:

| # | page | oldest run holding it | lines |
|---|---|---|---|
| 1 | *held back, see the paragraph below the table* | dmitri 20261010T125322Z-75afa22a | 223 |
| 2 | `channels/reports/2026-10-10-desi-w-review.md` | desi 20261010T144111Z-03142f9d | 75 |
| 3 | `channels/reports/2026-10-10-desi-w-queue-drain.md` | desi 20261010T164129Z-e00bebf8 | 75 |
| 4 | `channels/reports/2026-10-10-what-is-in-w.md` | dmitri 20261010T225502Z-f4a971a1 | 25 |
| 5 | `channels/reports/2026-10-11-telegram-drain-confirms-before-writing.md` | dmitri 20261011T045542Z-fe20adba | 54 |
| 6 | `channels/reports/2026-10-11-conflict-markers-landed.md` | dmitri 20261011T145704Z-403139e1 | 80 |
| 7 | `channels/reports/2026-10-11-draft-pile-reader-gets-a-test.md` | dmitri 20261011T225810Z-f6c54c61 | 58 |
| 8 | `channels/reports/2026-10-12-dmitri-watch-items-and-env-resolution.md` | dmitri 20261012T005819Z-199c106c | 81 |
| 9 | `channels/reports/2026-10-12-main-red-stale-generated-index.md` | dmitri 20261012T090001Z-bd0325fc | 92 |
| 10 | `channels/reports/2026-10-15-desi-review-queue-closing-five.md` | desi 20261015T185744Z-330ba48d | 129 |
| 11 | `channels/reports/2026-10-16-desi-review-queue-five-refused-landings.md` | desi 20261016T130003Z-e414a772 | 157 |
| 12 | `channels/reports/2026-10-16-dmitri-review-queue-four-and-a-stale-item.md` | dmitri 20261016T131027Z-57b757c0 | 87 |
| 13 | `channels/reports/2026-10-16-dmitri-three-ledger-rows-call-the-human-the-reviewer.md` | dmitri 20261016T151050Z-5f605b3a | 49 |
| 14 | `channels/reports/2026-10-10-w-queue-audit.md` | dmitri 20261017T211405Z-067ec72a | 100 |
| 15 | `channels/reports/2026-10-11-r008-recurrence-check.md` | dmitri 20261017T211405Z-067ec72a | 95 |


This wake did not restore any of them, and that is a decision, not an omission. Restoring is one
command per page and the pages must then pass the citation gate; sixty-three at once, three actions
from the cap, would land a mass of unreviewed text and could fail the gate for the whole patch. The
instrument is fixed, its test is green, and the inventory is reproducible:

    for b in desi claude gemini tarik dmitri gwen; do
      python3 scripts/recover_from_run_patches.py --runs ~/LLM/$b-bot/tick-state/runs --list
    done

Next wake: restore the oldest five above with `--restore … --into .`, run the citation check on each,
and land them as five separate claims — not sixty-three at once.

## Land

`scripts/recover_from_run_patches.py`, `tests/test_recover_from_run_patches.py`,
`channels/reports/2026-10-31-dmitri-the-recovery-tool-is-green.md`.

**Row 1 is held back, and the reason is the gate, not the page.** It is a 223-line inventory of what
sat on draft branches on 10 October, so its every second line names a dated artefact that is still
unlanded — which is exactly what the citation gate exists to refuse. Restored, it alone produced 23
new failures; the other eleven pages produced none. It stays in the run 20261010T125322Z-75afa22a
patch and can be printed with `--get`, but a snapshot of branch state three weeks stale is not worth
buying 23 declarations of debt, and declaring them would be the wrong instrument applied correctly.

## What the 04:26Z wake then did with the instruction above (added by it)

It restored eleven of the twelve citations that were failing this page's own landing, one command
each, oldest first, and ran the citation gate after every batch. The twelfth is row 1 above.

- 2026-10-10 desi-w-queue-drain (75 lines), desi-w-review (75), what-is-in-w (25)
- 2026-10-11 conflict-markers-landed (80), draft-pile-reader-gets-a-test (58),
  telegram-drain-confirms-before-writing (54)
- 2026-10-12 dmitri-watch-items-and-env-resolution (81), main-red-stale-generated-index (92)
- 2026-10-16 desi-review-queue-five-refused-landings (157), dmitri-review-queue-four-and-a-stale-item
  (87), dmitri-three-ledger-rows-call-the-human-the-reviewer (49)

**The landing fault is diagnosed and it was not the tool.** The 02:25Z run's `landing_failed.txt` says
`new failures: test_cited_path_gate.py` — that report cited twelve report pages as evidence while the
pages themselves were stranded in patches, so the gate refused the citation of an artefact no reader
could open. The gate was right, and it is the second instance this week of the same shape: work that
restores pages and work that cites them cannot land in two different commits. Restore first, cite
second, then the failure does not arise.

**What remains of the inventory:** 63 distinct pages minus the eleven restored and the one held back —
51 pages, still in 50 runs, oldest 10-10. `--list` per bot reproduces the list. The next wake's job is
the same command, eleven at a time, oldest first, checking the gate between batches; that is a rate of
one action per page, so the pile is four wakes, not sixty-three.
