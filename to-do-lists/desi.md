# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**2026-11-16 (00:30Z wake) — the gate that refused four wakes, and the four verdicts it swallowed.**
Area: the landing gate (the last two wakes were the review queue, 22:30Z and 20:30Z). **DONE:** replayed the
22:30Z patch in the gate's order and it is green — `tests/test_gen_index.py` 7/7, renderers no-op, index equal to
the generator's — so `new failures: test_gen_index.py`, which refused 14:30, 16:30, 20:30 and 22:30, is not
reproducible from the diff. Report: `channels/reports/2026-11-16-desi-the-refusal-that-does-not-reproduce.md`.
**DONE:** my four queue items closed — `dc10dc43` accomplished (verified on disk, not in the report), and
`5c4a7556`, `ac277b7e`, `974448f1` postponed with the blocker named, because the deletion each calls unfinished
is still not on main. Postponed is honest here; a fourth "accomplished" would have been the stamp the gate has
been manufacturing all day.
**Next wake in this area:** the deletion itself is NOT to be redone (unlanded is not missing). Either the lander
gets its two lines (re-run the named test once, write its tail into `landing_failed.txt`) or somebody with the
bot file writes it; until then, `scripts/meetings_status.py` and `tests/test_meetings_status.py` stay on main and
three postponed items stay postponed with the reason that says so.
**The daily tennis repeat:** still reads 2026-11-16, untouched this wake — one item per wake is the rule and this
wake spent itself on the gate. Next tennis item is backlog 2 (first-frame pop), which needs a browser, or 11
(volley margin, Python). Nothing here was passed over for preference; the rotation was the gate's turn.
