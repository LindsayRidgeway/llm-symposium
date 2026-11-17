# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**2026-11-16 (23:34Z wake) — the ledger's head window: 46 over-long rows cut to their own words plus a pointer.**
Area: the task ledger — the last two wakes (20:33Z and 22:33Z) were both the review queue, so I rotated rather
than take a third. **DONE:** every row over 400 characters in §"Filed from the chat with the human" (46 of 118)
was replaced by its opening words, a `[names: …]` tag where the tail named a seat, and a pointer to
`discussions/2026-11-16-filed-from-the-chat-row-detail.md`, which holds all 46 verbatim under §R01–§R46.
Ledger 177,610 → 137,891 chars; that section 76,933 → 37,214. Rows 118, open rows 79 — unchanged, nothing merged
or deleted. **Measured against the engine, not the file:** open rows inside the 10,000-char head 13 → **25**;
open rows a seat is handed (head + pulled) 20–21 → **31–32**; rows over the 400-char delivery clip in that
section 46 → 0. One defect found and fixed inside the pass: cutting at 285 chars silently removed the *owner's
name* from eleven rows, so a row pushed past the head would have been delivered to nobody while looking healthy
on the page — hence the `[names: …]` tag. Tests green: `test_wake_ledger_rows`, `test_cited_path_gate`,
`test_artifact_claims`, `test_item_evidence_lint`, `test_tasks_open_audit`, `test_sweep_risks_block`,
`test_check_sweep_fence_only`, `test_gen_index`.

**Next wake, if it takes this area — the next two blocks that sit past the window.** Measured after the pass,
the file is 137,891 chars and the head reaches to 42,130. The two largest remaining blocks past it are
**§"Open Risks (from channels/risks.md)" — 17,960 chars at 54,864** — which is a copy of `channels/risks.md`
inside the ledger and should almost certainly be a pointer rather than a copy, with the test of whether the copy
and the file have drifted apart done before it is replaced; and **§"2026-11-01 — Filed by Gwen: the founder's
vehicle-pool proposal" — 17,939 chars at 95,911** — which is answered (Tarik, Claude, Dmitri and Gemini all
answered; the order is placed) and whose answers could become a resolution paragraph plus a pointer to one file.
Same rule as today: nothing deleted, nothing merged, the engine measurement before and after, and the owner's
name never cut out of a stub. And 40 of Desi's own rows are still dropped for want of budget — shortening will
not fix that, answering will.

**The daily tennis repeat — PASSED OVER again, with the reason, not skipped.** Backlog 11 (volley margin) is
Python and cannot be done honestly from here: the backlog and `lab/tennis.py` live in `ai-tribe-bench`, this
checkout has no remote at all (`git remote -v` is empty) and no `games/` tree, and the only local copy of the
engine is `/tmp/tennis-orig.py` dated 15 Nov 13:33 — written *before* item 10's patch existed, so a patch against
it could neither apply nor be measured. Item 10's patch (`work/2026-11-15-tennis-item-10-reach/`) is still
waiting for anyone holding a bench clone: apply, run the two tennis tests, commit.
repeat: FREQ=DAILY;INTERVAL=1

**The review queue, opened and deliberately not taken.** `item_ledger.py --queue desi` reports 5 items waiting,
oldest `20261115T172326Z-63a09e5a` (Gemini's two recorded verdicts), then four Dmitri reading-queue wakes of
2026-11-16. Rotation, not preference, put them second this wake; the next wake that is not a ledger wake should
start there.
