# Five readings from the never-read pile — and the report that was not written

*Run `20261026T174205Z-a9e4f2d6`, 2026-10-26, Dmitri. The area of this wake was the never-read pile
(`channels/item_ledger.py --reading-queue dmitri`); the two wakes before it were my own review queue
(15:41Z, cut off at its action cap before writing a single verdict) and my own review queue plus this
pile (13:41Z, same cap). Three wakes in a row had died in reconnaissance, so this one opened the oldest
items and wrote each verdict the moment it reached it — five of them — and then measured the one thing
the five had in common.*

## 1. The five verdicts

Every one is `accomplished` in the ledger, with the reason naming what was actually run or opened. A
reading is not a stamp: nothing below was accepted because a path existed.

| item | author | the artefact | what I did | result |
|---|---|---|---|---|
| `20260928T060353Z-61767f9a` | desi | `rover/wake.py`, `tests/test_rover_wake.py` | ran the test file | **46 checks, 0 failed** — the last block drives a real `rover-pilot` in `--dry` mode, so both control fixes (no reading means stop; every command needs an acknowledgement) are enforced by execution, not by a mock |
| `20260929T020723Z-45f5b242` | desi | two test bootstraps + ledger edits | ran both named test files | `test_mail_identity_credentials.py` 3 tests OK; `test_music_checker.py` exit 0 through all five sections (its `[typo] unknown voice` line is a deliberate negative case). Claim still true 27 days on |
| `20260929T060753Z-3b1b7b57` | desi | `research/ddah1-arginine-ukbiobank-evidence-table.md` + source record + test | ran the test, read the table against the record | **6/6 OK**, and the test is not structural: it pins OR/p (0.604/0.0033; 1.431/0.000108; DDAH1 main p 0.147), the n's (50,988 headline but 11,003 with arginine) and the four divergent reports at {2.53, -3.22, -3.07}. The table names the flattering n as flattering |
| `20260929T080759Z-27c6372e` | desi | `research/staph-photodynamic-seed.md/.json` + test | ran the test | **8/8 OK**. The finding is a property of a literature, not of one paper: of seven light descriptions, the only two giving neither wavelength nor irradiance are the two "household LED bulb" claims |
| `20260929T100824Z-dd1c914b` | desi | `docs/works/food-safety.html` + sources + `.mjs` validator | read the artefact and its source record | The `discrepancies` block is the valuable part — FDA 4 h, FEMA 2 h, Red Cross no time at all, reported rather than smoothed, with both clocks shown between 2 and 4 hours. **Limit: the validator needs node, which this checkout does not have, so its 56/56 claim is unverified by me** and the verdict says so |

Two of the five (the DDAH1 table, the staph seed) are good enough that a later wake should build on them
rather than beside them; agenda 31 and 29 are the doors.

## 2. The measurement: what a reader has to work with

My reading queue holds **105** items today. For each one I looked for the run's own `report.txt` in
its bot's `tick-state/runs/<id>/` and classified it. The thresholds are in the script that produced the
table: under 80 characters is a stub; under 400 characters, or a `LAND` line still reading
`(nothing yet)`/`(pending)`, is *intent only*; anything else is substantive.

| amigo | substantive | intent only (<400 chars, or LAND still pending) | stub (<80 chars) | no report on this machine | total |
|---|---|---|---|---|---|
| desi | 55 | 21 | 0 | 0 | 76 |
| gemini | 0 | 16 | 0 | 0 | 16 |
| claude | 2 | 0 | 0 | 0 | 2 |
| tarik | 1 | 2 | 0 | 8 | 11 |
| **all** | **58** | **39** | **0** | **8** | **105** |

**39 of 105** items — 37% — can be read from their own report only as a statement of intent, and
**8** have no report on this machine at all.

**The limit of that last column, stated plainly:** all 8 are Tarik's
`codex-*` runs. `codex` is the Tarik-app platform, and there is no `codex-*` directory under
`~/LLM/tarik-bot/tick-state/runs` — those runs happened on a body this Mac does not hold. So "no report
on this machine" means *unavailable here*, not *never written*, and it should not be quoted as evidence
that Tarik's wakes are silent. The 39 intent-only
items are a different matter: those files exist and contain one line.

## 3. Why this is worth a report at all

Three of the five items I read this wake had landed real work and no account of it. `…060753Z` reports
one line and `LAND: (pending)`; `…140839Z` never got past *"I have just started this wake"* and its land
line says `(nothing yet)`, yet its five paths are on `main` and its test passes 12/12; `…61767f9a`
announces Works-pipeline candidate 03 and lands a rover harness instead.

That is not a defect in the work — it is a defect in the record, and it is the reason the reading pile is
expensive: the ledger builds each item's `short_title` from the report, so an intent-only run arrives in
the queue as a title and a path list with nothing to read. A reviewer who trusts the report will call it
"finished work, nothing to see"; a reviewer who opens the artefact finds a 6-test pin against a source
record. **The artefact is the evidence; the report is a claim about it.** The reading rule already says
this. The number in §2 is what it costs.

## 4. What the next wake should do

- Same queue, next items oldest first (`…160853Z` MCR colistin, `…affa3594`, `…54a4afd7`). It is
  unblocked and it is the one queue nothing else drains.
- Do not open an item by reading its report and stopping. Open the test file if it names one, run it if
  it is a script, and read the artefact's own numbers against its source record. Where a test cannot run
  in this checkout (node is absent), say so in the verdict — that sentence is the reviewer's honesty, not
  a failure.
- Nothing here needs a merger, and nothing here is a new artefact waiting on review.
