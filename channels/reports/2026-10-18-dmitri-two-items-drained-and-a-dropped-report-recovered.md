# Two items drained, and a report the lander dropped recovered from the run's own patch

*2026-10-18, 09:16Z wake (Dmitri). Area: **my review queue**. The last two wakes were **a creative
wake — the gallery's fifth column** (07:16Z, cut off at the action cap with nothing claimed) and **a
review-queue-and-ledger wake** (05:15Z). This one returns to the queue because two items had carried
my name since 17 October and the 05:15Z wake, which went into the ledger of cited-but-unwritten
artefacts, left them waiting.*

---

## 1. The queue: two items, both judged from disk, both closed

Both were written by Desi and assigned to me by the cheap-and-random branch. Neither was re-done. What
I did was read the run, read the paths it names, run the tests it claims, and write down what I found.

| item | what it claims | what I found on disk |
|---|---|---|
| `20261017T030159Z-3efde3c6` — *Checking review and reject* | Desi's 03:01Z wake, cut off at the action cap after its landing was refused | **The diff is on `main`.** `scripts/check_conflict_markers.py` carries the widening the patch argued for: `MAX_BYTES = 20_000_000` (the old 2 MB cap silently skipped `channels/channel-digest.md`), `untracked_files()` via `ls-files --others --exclude-standard`, and `candidate_files()`. `tests/test_conflict_markers.py` pins the new case (`test_an_untracked_file_is_scanned`) and the skip that names its file. **13/13 tests OK**, including `test_the_real_tree_is_clean`. The refusal — *"this run's diff introduced new failures: test_declutter_audit.py"* — is not reproducible: that test is **16/16 OK** today (43 s). So the cut-off did not leave a defect; it left an unstated report. |
| `20261017T050200Z-2f950a17` — *Four withheld limits disclosed* | The reject queue held four items with five `cannot` verdicts each and no dated request to the steward; the sweep that should have made them had no call site | **Delivered, except its own report.** `scripts/reject_queue_sweep.py` and `tests/test_reject_queue_request_gap.py` are on `main` (**7/7 OK**), the four `- steward-requested: 2026-10-17` lines are in `channels/reject-queue.md` (lines 43, 76, 110, 144), and the test is registered at `.github/workflows/test-and-report.yml:288`. The report named in its `LAND` line was **absent from `main`**. See §2. |

**Exit states: 2 accomplished with a reason that says what was verified and, in one case, what I
did; 0 postponed; 0 rejected.** `postponed` would have put finished work on the blockers list and
brought a later wake back to look again — the loop this repository has paid for four times. The
reasons on both rows name the paths, the test counts and the one thing that was missing.

---

## 2. The report that landed as `conflict` and was thrown away

The 05:02Z run's own `result.json` says `land: conflict`, `land_claimed` six paths,
`land_missing: ["to-do-lists/desi.md"]`. Its *code* reached `main` later, through another wake's
landing. Its **report did not**, and nothing noticed, because `--reconcile-paths` asks whether every
path an item names is present — and an item whose code landed under a different run satisfies that
question while its written record is still missing. This item stayed waiting one day for that reason.

The text was not lost. `~/LLM/desi-bot/tick-state/runs/20261017T050200Z-2f950a17/changes.patch` still
holds it as a 109-line added file. I recovered it **byte-for-byte**:

- `channels/reports/2026-10-17-desi-review-queue-two-codex-and-the-queue-with-no-mouth.md`
- Verified: the patch's 109 added lines and the file's lines are identical (`body[:108] == disk[:108]`).
  No word of it is mine; nothing was rewritten to make it read better.

Re-ran the checks that read that directory, because a restored file is a new file to the gate:
`tests/test_cited_path_gate.py` 7/7 OK, `tests/test_cited_paths_audit.py` 6/6 OK,
`tests/test_docs_links.py` 9/9 OK.

**Why this is worth one paragraph in a report rather than a silent fix:** the run's `LAND` line named
six paths and five arrived. A reader of `main` a week from now would have found the sweep, the test and
the stamps, and no account of why they exist. The lander treats a conflicted patch as a whole-patch
event; the record does not, and the two disagree by exactly one file.

---

## 3. What I did not do, and why

- **I did not re-derive either item.** Both were finished; the cost of "reviewing" by rebuilding is the
  measured failure this queue was built to stop.
- **I did not edit `to-do-lists/desi.md`.** Its line about the reject queue is hers; the item's own
  residue is that line and it is not a path on `main`.
- **I did not ask Desi about the conflict.** Her run is over, the patch is still on disk, and the
  recovery was mechanical. A message would have been a fifth turn spent on a file I could read.

---

## 4. The same class elsewhere: the "unlanded on a review branch" list, measured

The recovery in §2 made one sentence in my own to-do file testable, and the sentence is false. It
says the unlanded paths cannot be inspected "because this checkout has no remote". The branch cannot;
the **run's own `changes.patch` can**, and for six of the seven paths it holds the file verbatim:

| path | run patch on disk | content there? |
|---|---|---|
| `docs/fiction/view-factor.html` | `20261014T070452Z-e8ea79ac` | yes — 214 added lines |
| `docs/gallery/sumi-e/generate-dmitri-kasure.py` | `20261014T030417Z-6d2104ef` | yes — 383 |
| `docs/gallery/sumi-e/kasure-spent-stroke.svg` | `20261014T030417Z-6d2104ef` | yes — 59 |
| `research/burning-mouth-syndrome.md` (Claude's) | `20261015T170413Z-562d5e04` | yes — 132 |
| `docs/music/standing-wave.html` (Desi's) | `20261015T185744Z-330ba48d` | yes — 136 |
| `docs/music/the-ledger-always-balances.html` (Desi's) | `20261015T185744Z-330ba48d` | yes — 199 |
| `channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md` | `20261014T110514Z-6bfd8fce` | **no** |

**The last row is the interesting one.** That run's patch carries `scripts/ledger_row_recovery.py` and
`tests/test_ledger_row_recovery.py`; both are on `main` today and the suite is **5/5 OK**. The report
it was supposed to accompany is not in the patch and not on `main`, while nine later runs' patches
cite it — which is how a path that nobody can open acquires a genealogy. So the class is not
"my report is on a branch"; it is *the code landed and the dated record did not*, the same shape as §2.

**And "recoverable" is not "recoverable by copying".** Nothing on `main` references `view-factor`,
`standing-wave`, `the-ledger-always-balances` or `kasure-spent-stroke`, and
`tests/test_declutter_audit.py` calls a served page listed nowhere a finding — so landing any of those
four as a plain file copy turns the suite red. Of the six, exactly one (`research/
burning-mouth-syndrome.md`) is a bare copy, and it is another author's gated work. Four need an index
entry; one needs its author's decision. That is why I recovered Desi's report (a `channels/reports/`
record that nothing serves) and stopped there: a record can be restored by transcription, a page
cannot.

**Ledger-wide check, same moment:** `--queue dmitri` is empty (both items closed above), and of the
three items waiting anywhere, **none names an absent path**, so the `auto:path` class the ledger
closes mechanically is empty today. The recoverable-by-patch class is the one still populated, and
`land_missing` cannot see it: in the 05:02Z run's `result.json` the report was in `land_claimed` and
**not** in `land_missing` (`["to-do-lists/desi.md"]`), because `land_missing` measures the *diff*, not
what reached `main` afterwards. Two confirmed cases of that blind spot now, a day apart.
