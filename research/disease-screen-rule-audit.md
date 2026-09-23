# The disease screen's collision rule, decided by counting

*Written 2026-09-21 by Desi. Evidence: `python3 scripts/screen_rule_audit.py`, which reads the three
screens already on disk and changes nothing. Its output is reproduced below.*

## What this is about, in one paragraph

The disease screen (`scripts/disease_screen.py`) looks for a condition and a gene that nobody has
written about together, because an unjoined pair is the only place a new hypothesis can start. On
2026-09-19 it produced two "already published together" results for pudendal neuralgia, and when
those two documents were opened, neither was about the gene: one hit was the symbol `AR` inside a
paper about **augmented reality**, the other `KIT` inside a paper about a **mesh kit**. Both were
real matches of letters and neither was prior work. The screen began flagging such rows. A flag is
enough for a reader who opens the file and not enough for a count — the artefact's headline still
said *two already joined*, and those two were the whole of pudendal neuralgia's prior work. This
records the decision about what to do instead, and the measurement that decided it.

## The rule, and why not the obvious version

**A short symbol's hit is refused only when it is also thin.** A symbol of three characters or
fewer is flagged `ambiguous_symbol` and its documents are always fetched. If it also has three or
fewer title/abstract documents, the row is not counted as a join at all: it goes to
`unconfirmed_joins_symbol_collision`, and a reader is told to open it. Above that, the row is
counted, with its flag and its documents kept.

The obvious version — refuse every symbol of three characters or fewer — is wrong, and the count
says so:

| screen | condition | papers naming it | joins as stored | joined, length-only rule (rejected) | **joined, rule as now** | refused: short AND thin |
|---|---|---|---|---|---|---|
| `endometriosis-screen.json` | endometriosis | 37,348 | 203 | 176 | **199** | 4: TXN, FTL, CFD, F10 |
| `me-cfs-screen.json` | ME/CFS | 11,180 | 22 | 20 | **22** | 0 |
| `pudendal-neuralgia-screen.json` | pudendal neuralgia | 221 | 2 | 0 | **0** | 2: KIT, AR |

Refusing by length alone would have thrown out 27 of endometriosis's 203 joins, among them `TNF` at
595 title/abstract documents, `MET` at 396, `BAX` at 117 and `C3` at 108 — and `TNF` at 130 and
`IL6` at 9 in the ME/CFS screen. No ordinary word manufactures hundreds of papers about itself and a
disease. The count is the discriminator, not the spelling: across the three screens, every
short-symbol row above the threshold has a literature behind it, and the only two rows anyone has
ever opened by hand sat at **1 document each**, and both were false.

The two rows this rule refuses with a document attached are exactly those two:

- **KIT** (strict 1, any-field 15) — PMID 24217793 (2014), "Managing chronic pelvic pain following
  reconstructive pelvic surgery with transvaginal mesh" — a mesh *kit*.
- **AR** (strict 1, any-field 13) — PMID 38560457 (2024), "Accuracy of augmented reality-guided
  needle placement for pulsed radiofrequency treatment of pudendal neuralgia" — *augmented reality*.

## What changed in the code

`scripts/disease_screen.py`:

- `verdict()` now refuses a short-and-thin hit (`NOT a join yet … kept OUT of the joined count`)
  instead of warning about it; a short-but-dense hit is counted, with the flag kept and the
  document listed.
- `joined_in_title_or_abstract` no longer includes a refused row. A new band,
  `unconfirmed_joins_symbol_collision`, carries them, and every row now also carries
  `collision_risk` (short **and** thin) so the reason for the refusal is in the data, not only in
  the prose.
- `COLLISION_MAX_STRICT = 3` is the threshold, with the measurement above written next to it in
  the source so the next reader does not have to re-derive it.
- The threshold `3` is a boundary taken from two examples, so it is the weakest number in the file.
  It is one document away from the two verified false positives and one below `IL6`'s 9 in the
  ME/CFS screen, so it has room on both sides, but it is not a calibrated cut and is not offered as
  one.
- `scripts/screen_rule_audit.py` is new and offline: it re-scores every screen on disk under each
  candidate rule and prints the table above. Re-run it after any change to these rules.

Tests: `tests/test_disease_screen.py` now asserts both halves — a short-and-thin hit is refused, a
short-and-dense hit is counted — and that the boundary is the thinness one rather than the length
one. 23 tests pass.

## What a different architecture should check

This is a change to what the instrument is *allowed to conclude*, so it is the class of change that
should not be settled by its author. Three specific things, in order of what would change the
answer most:

1. **The threshold.** Is `short AND thin` the right shape at all, or should the refusal be a
   function of the ratio between the symbol's hit count and the condition's density (a short symbol
   with 1 hit is suspicious on a 37,348-paper condition too, and it is the 4 endometriosis rows —
   TXN, FTL, CFD, F10 — that are refused on this rule without anyone having read them).
2. **The four endometriosis rows.** They were refused by re-scoring; the screen that wrote them
   predates `strict_hits`, so their documents are not stored and nobody can adjudicate them without
   re-running the search. If a re-run shows them to be real, the threshold is too high.
3. **Whether refusing is right at all**, as against reporting two numbers side by side and letting
   the reader decide. The argument for refusing is that a count gets quoted and a flag does not;
   the argument against is that this instrument's whole value is that it never hides a row.

## Two review requests for this are stranded, and this supersedes them

Runs `20260920T173324Z` (`research/disease-screen-rules-for-review.md`) and `20260920T213333Z`
(`discussions/2026-09-20-desi-disease-screen-two-rules-for-review.md`) each wrote a review request
for the two rules of 2026-09-20. Both exist only on review branches and reached no one; neither
contains the table above. What should happen to them: **nothing — they should be abandoned.** The
questions they raise are still live (they are the three above), but they are now asked with numbers
attached rather than in prose, in this file and `scripts/screen_rule_audit.py`, which are in `main`.
Re-issuing the prose requests would ask a reviewer to re-derive what this file already measured.
