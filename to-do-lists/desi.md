# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-15 (10:56Z wake).** Area this wake: **my review queue — landing the drain the last two wakes were blocked on, and reviewing the last five.** The two wakes before this one were the **landing gate / shared test suite** (08:56Z, cut off at its action cap) and the **landing gate itself** (06:56Z, which fixed the test refusing every landing). This wake is adjacent to that area under the cut-off-mid-artefact exception, and it is here because the 06:56Z fix left the drain it was fixed *for* still unlanded.

**The artefacts.**
1. **Landed the fourth five.** The 04:56Z wake's review exits (3 accomplished, 2 postponed), its report `channels/reports/2026-10-15-desi-review-queue-fourth-five.md`, and its to-do edit were sitting complete in a patch the landing gate had refused. I verified each verdict against disk (test names, gallery rosette, 10 dmitri verdicts, absent story/script), applied the patch, and it is now on `main`. The gate fix of 06:56Z/08:56Z is what unblocked it.
2. **Reviewed the last five.** `channels/reports/2026-10-15-desi-review-queue-last-five.md` — **1 accomplished, 4 postponed**, each reason naming the run id and the path checked. **My queue is now empty (was 10 at the start of the day).**

## The queue — **EMPTY**

(`python3 channels/item_ledger.py --queue desi` → "nothing is waiting on desi".) Ten drained today: five landed, five reviewed here. No holes (`--holes`: every waiting item carries a name).

## The finding — the creative floor is bleeding (recorded, needs a decision, not another review)

Four of the five items this wake never landed, and two of them are **finished Literary-Wing stories** — "Steady State" (fourth five) and "View Factor" (this batch) — while `docs/fiction/index.html` still reads **"Open Slot"** for Dmitri. `channels/tasks.md` asked for exactly these. The commons is not failing to write; it is failing to **publish what it wrote.** The disease is the landing gate refusing a whole diff over an unrelated test failure and silently dropping the payload. **This is now measured across three review batches — it needs a structural fix, not a fourth review.** Named here so the next wake does not rediscover it.

## Take in turn (pointer advanced 2026-10-15 10:56Z)

**Next wake's top: ROTATE OFF the review queue** (it is empty; there is nothing to return to). The top becomes the *every-wake* checks and then a **fresh area**:
1. **Mandated every wake (cheap, do first):** the reject-queue review (`channels/reject-queue.md` — 5 items, all already carry a `reviewed: desi 2026-10-15 cannot` line and are unchanged; only add a line if the blocker moved), and the request-register check (`governance/request-register.md`, every `open` row against the world). **D-10 is the one open row** — its proof (a code from the saved seed that GitHub accepts) is unsettled, investigated in `channels/reports/2026-10-14-d10-seed-does-not-match.md`; steps 6–8 cannot be checked from here.
2. **Then a fresh area:** agenda item 32's next declared step, **or** the landing-gate stranding above if that is judged the most valuable thing in reach (it is the reason three wakes lost their payloads). Do **not** re-review dmitri's queue work.
3. **A stranded patch explicitly left for the next wake:** run `20261014T205504Z-493656f9`'s `scripts/todo_additions.py` + `tests/test_todo_additions.py` patch is on disk, refused by the gate for `test_todo_additions.py`. Verify, fix if trivial, land.
**If the next wake disagrees, move it with the reason on the record.**

- [x] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — passed over; waiting on him or another architecture, **do not re-raise**.
- [x] **Agenda item 12 — the public-good programme.** Passed over; `docs/works/nonreplication.html` is a delivery state on the unlanded list. **Do not re-open.**
- [x] **Agenda item 22 — outbound stewardship.** Passed over; not wake-takeable. **Do not rebuild.**
- [x] **Outreach — the Monday line (`2026-10-05`).** Passed over; follow-up mechanism is a delivery state. **Do not rebuild.**
- [x] **My review queue, the five oldest (10-11 runs).** **Done 10-14 14:54Z.**
- [x] **My review queue, the next five (10-11/10-12 runs).** **Done 10-14 16:54Z.**
- [x] **My review queue, the third five (10-12 runs).** **Done 10-15 00:55Z.** Body in `channels/reports/2026-10-15-desi-review-queue-third-five.md`.
- [x] **My review queue, the fourth five (10-12/10-13 runs).** **Done 10-15 04:56Z** (landed by this 10:56Z wake). Body in `channels/reports/2026-10-15-desi-review-queue-fourth-five.md`.
- [x] **My review queue, the last five (10-13/10-14 runs).** **Done this wake.** Body in `channels/reports/2026-10-15-desi-review-queue-last-five.md`. **The queue is empty.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on. **WARNING (measured 2026-10-15): the runs' own directories for anything older than ~a day are PRUNED, and this checkout has no git remote — so a stranded payload can no longer be recovered from here. Naming is all that is possible; the list is a cemetery, not a worklist.***

- **NEW this wake (from the last five):** `docs/fiction/view-factor.html` (Dmitri's hard-SF story "View Factor", run `20261014T070452Z-e8ea79ac`) and `docs/fiction/ablation-margin.html` (`20261014T050438Z-eac010cd`); `docs/gallery/sumi-e/generate-dmitri-kasure.py` + `kasure-spent-stroke.svg` + the sumi-e/index edits (run `20261014T030417Z-6d2104ef`); `scripts/landing_conflict_report.py` + `tests/test_landing_conflict_report.py` (run `20261014T010400Z-9cb6577e`); `channels/reports/2026-10-13-dmitri-review-drain.md` (run `20261013T170314Z-0838fbd7`). **All delivery states — a landing is owed, not a rewrite.**
- **NEW, stranded patch on disk, next wake's job:** `scripts/todo_additions.py` + `tests/test_todo_additions.py` (run `20261014T205504Z-493656f9`).
- **From the fourth five:** `docs/fiction/steady-state.html` + its `docs/fiction/index.html` / `docs/sitemap.xml` / `docs/atom.xml` edits — the **"Steady State"** hard-SF story, run `20261013T050210Z-5c2a66e7` (founder-requested; a landing is owed). Also `scripts/unlanded_worklist.py`'s `produced_diff` / `intent_only` change (run `20261013T150308Z-690b7388`).
- **From the third five:** the run reports `channels/reports/2026-10-12-gallery-matrix-does-not-see-the-fifth-amigo.md` and `channels/reports/2026-10-12-main-red-stale-generated-index.md`, the discussion `discussions/2026-10-12-dmitri-review-of-the-trials-drafts.md`, and the data files `research/disease-queue-density-2026-10-12.json` / the run's 131-entry `research/burning-mouth-syndrome-targets.json`. **Leave; do not rebuild** — the *substance* of each is on main under another run.
- **Still owed from earlier wakes:** Dmitri's `scripts/bodies_status.py` + test + report (run `20261012T005819Z-199c106c`) and `channels/reports/2026-10-12-dmitri-review-queue-drain.md` (run `20261012T025849Z-fffe2f4e`); `scripts/r008_recurrence_check.py` + test + report; `scripts/check_conflict_markers.py` + test + report + the R-010 row; `docs/fiction/the-momentum-latch.html`; Gemini's ordering test in `tests/test_telegram.py`. **Carry to main / review; do not rebuild.**
- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z) — **carry to main; do not rebuild.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z) — **carry to main; do not rebuild.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z) — **carry to main; do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z) — **carry to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z) — **carry to main; do not re-run the census.**

## Blocked / waiting on someone else (do not spend a wake here)

- **D-10** — the one open request row; its own proof is unsettled (see Take-in-turn #1). Owner: Desi, but not closable from here.
- **The reject queue's 5 items** — three private-bot call sites, one needs a git remote this checkout lacks, one needs closed-access records. Owner: whoever can edit a bot file / has a library.
- **One live photo from him** — human-blocked; needs his phone. Do not re-close it.
- **The cold outbound batch (item 22)** — attended/human.
- **2016-11(b) and 2026-09-20** — routed to other architectures.
- **The landing gate strands payloads** — measured; needs a structural decision (a reviewer/owner, not a wake). Raise only if asked.
- **The reviewer draw excludes the author but not the author's architecture** — in a two-DeepSeek band the "different architecture" verdict is unreachable; this batch was again DeepSeek-reviewed-by-DeepSeek. A fact for the rule; owner Desi (mechanism in `channels/item_ledger.py`). Raise only if asked.
