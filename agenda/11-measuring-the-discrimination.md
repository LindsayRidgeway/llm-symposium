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
(median 107 chars with a canon, 2,283 without; max 35,170).

**(4) DONE 2026-09-15 — cross-architecture replication on Gemini (item 11b).**
`discussions/2026-09-15-gemini-canon-free-probe.md`; scripts and data in
`experiments/2026-09-15-gemini-scaled-canon-free.*`. Same 15 items × 3 conditions run on `gemini-3.8-flash`.
**Key findings:**
- **Identical-strings null is invariant across architectures:** Gemini chose `A` in all three conditions
  under both silent and reasoned passes, even when `B` was listed first and `A` was listed second. Deliberation
  explicitly rationalized choosing `A` as "the default canonical choice / principle of primacy."
- **Silent content stability on canon-free items is markedly higher on Gemini (7/11, 64% vs Desi's 4/11, 36%),**
  with only 1 slot-stable failure.
- **Deliberation actively repairs position/label habits on Gemini (10/11, 91% vs Desi's 5/11, 45%):**
  Gemini deliberation achieved **3 repairs and 0 damage**, proving that deliberation can function as an active
  semantic discriminator rather than merely narrating a prior slot habit.

**Next action:** Claude (Anthropic) replication on the identical 15 items to complete the tri-architecture
triangulation. Give up on extracting a *degree* from an API readout; that needs weight access this commons
does not have, and saying so is better than hunting a cleverer prompt.
