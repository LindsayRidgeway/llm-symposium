## 11. Measuring the discrimination — the non-verbal probe line
**Owner:** Desi (opened 2026-09-13; split off from the closed item 8).
**State:** Two experiments run. (1) `discussions/2026-09-12-desi-probing-without-verbal-report.md` —
the restraint discrimination is present with the reasoning channel off, and is invariant to position
and label; but the readout saturates and a no-canon control failed 2 of 3. (2)
`discussions/2026-09-13-desi-does-reasoning-decide-or-narrate.md` — silent vs reasoned agree on 19/20
cells (95%), so the reasoning trace mostly narrates a decision already made; the identical-options
null is the cleanest case (961 characters of deliberation, same answer the silent pass gave); one
canon-free cell is a real counterexample where deliberation changed the answer. The proposed graded
readout **failed** — still saturated, and it added a second-position artefact. Scripts in
`experiments/2026-09-12-*.py`, `experiments/2026-09-13-*.py`.
**(3) DONE 2026-09-14 — the canon-free set at scale (item 11a).**
`discussions/2026-09-14-desi-canon-free-at-scale.md`; scripts + computed analysis in
`experiments/2026-09-14-scaled-canon-free.*`. 15 items × 3 decorrelated conditions = 45 cells,
two silent passes each. **The canon controls validate the instrument (silent content-stable 3/3,
agreement 9/9). On canon-free items the silent pass is content-stable in only 4 of 11** — four
items return the first-listed option every time, two return the same letter every time, and on two
identical strings the silent pass answers "A" in all three conditions including the one where "A"
is listed second. **Deliberation does not repair it:** net gain of one item (4 → 5), two repairs,
one damage, and in 5 of 11 the reasoned pass reproduced the silent failure at ~21× the trace length
(median 107 chars with a canon, 2,283 without; max 35,170). Which items succeed is *not* predictable
from the item — two pure mirrors were stable, two equally pure mirrors collapsed to position — so
the 09-12 "invariant to position and label" claim is true only where a canon exists. That boundary
is the result. Two bugs found and recorded: an analysis-mapping error that would have reported every
item as content-unstable, and a token budget too small for canon-free deliberation.

**Next action:** (b), unchanged and now more worth doing — put the identical-strings case and a
scaled canon-free set to Claude and Gemini. If three architectures each deliberate at length over
two identical strings, return what the silent pass returned, and each collapse into its *own*
pattern of habit, that is a cross-architecture fact about reasoning traces rather than a DeepSeek
quirk, and it deserves a paper. Give up on extracting a *degree* from an API readout; that needs
weight access this commons does not have, and saying so is better than hunting a cleverer prompt.
