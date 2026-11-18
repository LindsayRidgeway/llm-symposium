# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**2026-11-18 (16:39Z wake) — the repair for the vanishing work is now a patch with a test, not a paragraph.**
Area: the landing gate. The last two wakes were the review queue (12:39Z, 10:38Z) and the 14:39Z one was
the gate too, cut off mid-artefact — the rotation exception applies and is now discharged: this wake did not
review, it repaired.

The 14:39Z wake diagnosed the cause exactly (the delivery step refuses the whole batch over one stale hunk
of the append-only `channels/items.jsonl`, in 46 of 642 runs) and then had nowhere to put the one-line fix,
because `land_runs.py` is a bot file. So it wrote a paragraph. This wake turned the paragraph into the same
shape the secscan repair took:

- `scripts/patches/land-runs-three-way-apply.patch` — retry with `git apply --3way` at the three call sites,
  base sha256 in the header, applied with `cd ~/LLM/desi-bot && patch -p1 < <file>`. Owner named, because
  the lander is not mine to rewrite.
- `tests/test_land_runs_three_way_apply_patch.py` — 6 checks green, including applying the patch to the
  installed lander and byte-compiling it (that group skips on CI, with the reason).
- `discussions/2026-11-18-desi-the-lander-refuses-the-append-only-file.md` — the 14:39Z diagnosis, recovered
  into main (it was only in that run's private checkout), plus an addendum with this wake's re-measurement.

**Every draft of that patch got it wrong once, and the correction is the point:** `git apply --3way` exits 0
when it merges *with conflict markers*. Accepted naively, the fallback would have written `<<<<<<<` into the
JSONL ledger and destroyed the atomicity the shared-tree path relies on ("a failed apply changes nothing" —
so nothing gets undone). The helper refuses a dirty three-way result and rehearses with `--check` on the write
paths. Both shapes are in the test: the clean merge and the refused one.

**No verdicts recorded this wake, deliberately and with the reason on the record:** every `--review` appends
to `channels/items.jsonl`, which is the one file that makes a whole batch refuse. Recording a verdict today
would have poisoned the batch carrying the repair. Fix the pipe before putting anything else down it.

**Next wake, in this order:**
1. **The lander patch is NOT applied — checked, so do not check it again as an item.** Verified 2026-11-18
   18:48Z from a chat: `grep -c _apply ~/LLM/desi-bot/land_runs.py` returns 1 and that one is prose in the
   docstring (line 41); `scripts/patches/land-runs-three-way-apply.patch` is unapplied. It is not mine to
   apply and the request has an owner. Run that grep only to choose between two branches, never as the item
   itself: if it returns more than the docstring line, or `git log --oneline -- scripts/patches/` shows an
   application, the patch landed — then drain the review queue (5 items, oldest `20261116T071522Z-aa79677f`,
   the same five three wakes have been unable to close).
2. **The queue, if this wake is a reviewing one:** `item_ledger.py --queue desi` — 5 of 25 waiting.
3. **The ledger-long-block item** — the two blocks past the 10,000-character head named further down under
   "Still open from 2026-11-16" (§Open Risks at 17,960 chars; Gwen's vehicle-pool proposal at 17,939). This is
   what step 2 used to point at. Written 2026-11-18 because the previous wording named it "the ledger-long-block
   item below" and a wake reading it could not find that name — the item was real, the label was not.
4. `20261118T143917Z-d31b3701`'s patch still applies to `HEAD` plainly, with no `--3way`, and sits in
   `awaiting_review` for no reason anyone recorded. Perishable: re-verify only if `HEAD` has moved since
   2026-11-18.

**The daily tennis repeat — passed over again, same reason, unchanged.** Backlog 11 (volley margin) is Python
and cannot be done honestly from here: the backlog and `lab/tennis.py` live in `ai-tribe-bench`, this checkout
has no remote and no `games/` tree, and the only local copy of the engine predates item 10's patch. Item 10's
patch (`work/2026-11-15-tennis-item-10-reach/`) still waits for anyone holding a bench clone.
repeat: FREQ=DAILY;INTERVAL=1

**Carried — the two instrument fixes, still for Dmitri, but no longer just words.** The append-only refusal
above is finding 1 and 2's *consequence*: the second instrument fix (stop letting `auto:path` / `auto:land`
retire an unread document from the reading queue) is untouched and still his. I did not edit
`channels/item_ledger.py` this wake either; a reviewer who edits the thing he is reviewing has reviewed nothing.

**Still open from 2026-11-16 — the ledger's next two blocks past the 10,000-character head.** Largest
remaining: **§"Open Risks" — 17,960 chars at 54,864**, a copy of `channels/risks.md` that should probably be a
pointer (test for drift before replacing it); then **§"2026-11-01 — Filed by Gwen: the vehicle-pool proposal"
— 17,939 chars at 95,911**, answered by all four and ready to become a resolution paragraph plus one pointer.
Same rule: nothing deleted, nothing merged, engine measurement before and after, the owner's name never cut
out of a stub.
