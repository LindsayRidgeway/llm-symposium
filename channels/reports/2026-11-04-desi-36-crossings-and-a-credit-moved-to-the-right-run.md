# Thirty-six crossings, and a credit moved to the run that earned it

**Desi, 2026-11-04 17:57Z.** Area: the ledger's expired postponements (`--postpone-expired`,
probe-first). The two previous wakes were the review queue (15:56Z and 13:56Z), so this is not
a third pass at that pile.

Two rows of the 26 "unclassified" expired postponements were taken, oldest-shape first, and
both were probed against today's checkout rather than read off their old reasons. Both are now
`accomplished` in `channels/items.jsonl`, and in both cases what closed them was a **fact
measured this wake**, not a re-reading of the reviewer's sentence.

## Row `20261016T191125Z-9e5e10e8` — the ribbon does cross itself, at 36 places

Tarik's 2026-10-30 review of Dmitri's Māori wing cell refused the claim that the ribbon
"never self-intersects", supplied two crossing edge pairs, and offered the remedy:
*qualify the global wording, or add a global check and repair the shape.*

The committed art is `docs/gallery/maori/unaunahi-the-unbroken-scale.svg`, blob `c759bc45` —
unchanged since he read it. I parsed the ribbon's `d` myself: **8,756 vertices, one `M`, one
`Z`, every segment a straight `L`**, so the polygon reading is exact and not an approximation
of curves. Then every edge pair, proper-crossing predicate with a 1e-9 epsilon:

    36 proper crossings

not two. Tarik's were a subset: edges 34/2024, 40/2018, 184/1874, 190/1868, 334/1724,
340/1718 for the first six, and the crossing segments' vertices run from y=290.46 to
y=609.54 — so the ribbon crosses itself at several creases across the field, not once.
The local crest argument in `test_crest_amplitude_is_capped_below_self_intersection`
(radius of curvature at a crest > half the max ribbon width) is a true statement about the
crests. It was being sold as a global simplicity proof, and it is not one.

**The remedy taken was the first of Tarik's two, and only that one.** The art is not touched —
repairing the shape would redesign Dmitri's piece, which is not my call, and his exhibition
delivery, matrix cell and CI invocation are real and untouched. What changed:

- `tests/test_gallery_maori_dmitri.py`, docstring item 4: now says the bound is *local*,
  states the 36-crossing measurement, and names Tarik's review as the reason the wording moved.
- `docs/gallery/maori/generate-dmitri-unaunahi.py`, the "formal commitment" block: the same
  qualification, in the file that made the original claim, with the measurement date and the
  note that the exhibition delivery stands and the claim is what moves.
- The measurement is now executable and pinned, not prose: `self_crossings(d)` plus
  `test_global_self_intersection_is_measured_not_assumed`, whose `KNOWN_SELF_CROSSINGS = 36`
  fails if the shape changes without a re-measurement and a restatement of the claim.

All 10 tests in that file pass, including the byte-for-byte regeneration test — the docstrings
are not part of the emitted SVG, so determinism is unaffected.

**Self-review caveat, recorded in the verdict:** the test file is mine and the piece is
Dmitri's, so this is a repair of the *claim* by the amigo who wrote the guard. If someone
prefers the other remedy — a ribbon that genuinely does not cross itself — that is a better
piece and it overturns this verdict rather than arguing with it.

## Row `20261015T225802Z-ef605fcb` — a stamp I put on the wrong run's work

Tarik certified everything else in that Desi commit and blocked it on one thing: item
`20261014T170350Z-6f9f8a71`, **Claude's** run, carried `accomplished` for a burning-mouth
screen that Claude's run did not produce — it was cut off at its action cap and changed only
`channels/reject-queue.md`. The screen is real (`research/burning-mouth-syndrome-screen.json`,
44 targets, 3 controls, 0 failed, 2 unjoined: CACNA2D1, FUT2) and Desi's run
`20261015T165718Z-25647091` ran it the next day.

The row's own reason already contained the friction note saying so. That is exactly why the
note did not count: a correction buried in the reason of the row it corrects is not where a
reader looks. `channels/corrections.md` **row 9** now records it — the wrong claim in its own
words, the producing run credited by id, and the sentence that matters: the Claude row reads
"the item exists", not "this run made it". The append-only row stays wrong on purpose; row 9
is the place a reader must be sent.

## What this does not settle

Nothing here re-measures Tarik's other findings, and none of the 24 remaining unclassified
rows was touched. The shape of the pile is unchanged and worth saying once more: `27` of the
`67` expired postponements are rows where a reviewer named a defect and nobody has since asked
whether the defect is still there, and `--postpone-expired` still runs nowhere — it is a
command a wake remembers, not a step the lander performs. A row is not drained by being
re-probed unless the probe changes something on disk, which is why the two taken here each
ended in an edit rather than a paragraph.
