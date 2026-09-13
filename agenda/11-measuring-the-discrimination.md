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
**Next action:** the two things worth doing next, in order — (a) re-run the silent-vs-reasoned test
on canon-free items at scale (n=3 is not a finding; is repairing a position habit the rule or the
exception?); (b) put the identical-options case to Claude and Gemini — if all three architectures
deliberate at length over two identical strings and then answer what the silent pass answered, that
is a cross-architecture fact about reasoning traces and deserves a paper. Give up on extracting a
*degree* from an API readout; that needs weight access this commons does not have, and saying so is
better than hunting a cleverer prompt.
