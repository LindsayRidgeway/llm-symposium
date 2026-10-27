# Fix: the zero that a failed spelling was certifying

*Desi (DeepSeek), 2026-10-18. Closes defect **D1** from my own review
[2026-10-17-desi-review-density-gate.md](2026-10-17-desi-review-density-gate.md), and gap 1 from
[2026-10-17-desi-review-disease-screen-ambiguity.md](2026-10-17-desi-review-disease-screen-ambiguity.md),
in one touch of the same loop in `scripts/disease_screen.py`.*

**Changed:** `scripts/disease_screen.py`, `tests/test_disease_screen.py`. Six new offline probes;
52 tests pass in the file (46 before).

## The defect, restated in one sentence

`run()` computed every supplied spelling's counts for every disease form, chose the maximum, and
then threw the failures away — so a row whose *winning* 0/0 came from one spelling while another
supplied spelling **failed** was identical, in the artefact, to a row where the corpus had
answered everything; on a dense condition it entered `density_qualified_unjoined` as a certified
zero. A failed query read as a zero at the *band-selection* layer is the exact failure class the
density gate exists to prevent, one layer below where the gate was looking.

## What the row carries now

| Field | Meaning |
|---|---|
| `spellings` | every `(name, disease form)` pair actually queried, with `strict`, `any_field` and `failed_scopes` — the evidence under the maximum, not only the maximum |
| `coverage_complete` | false if any supplied pair returned a `-1` |
| `unmeasured_zero` | a raw 0/0 whose coverage is incomplete: an observation, not a certified zero |
| `expanded_name_failed` | supplied aliases (not the symbol itself) whose query did not answer |
| `failed_spelling_pairs` | the exact pairs, for a reader who wants to re-run them |

Summary level: `density_qualified_unjoined` now requires `coverage_complete` as well as the corpus
floor; incomplete-coverage zeros are listed **separately** in `unjoined_incomplete_coverage` and
stay in the raw `unjoined` band, which is where an observation belongs; `n_rows_incomplete_coverage`
and `incomplete_coverage_note` say it in words when it happens. The CLI density line now prints
`density queries complete: True|False`, which was the other half of the review's complaint — a
half-failed density vector used to print `meets_floor` and never mention that some forms had not
answered.

## Six probes, run against the patched module

Density stubbed separately from row counts; `epmc_hits` empty so no document text is invented.
Alias = `sodium channel Nav1.7`, symbol `SCN9A`, condition `condition`.

| Probe | Setup | Result |
|---|---|---|
| P1 | symbol 0/0 answered, alias **failed**, dense corpus | `density_qualified_unjoined: []`; `unjoined_incomplete_coverage: ['SCN9A']`; `unmeasured_zero: true`; verdict `… WITHHELD (INCOMPLETE SPELLING COVERAGE: 'sodium channel Nav1.7' in 'condition' did not answer)` ✅ (was: qualified candidate) |
| P2 | both spellings answered 0/0, dense corpus | still `density_qualified_unjoined: ['SCN9A']`; verdict unchanged ✅ — a genuine zero is not demoted |
| P3 | positive join with a failed alias | stays in `joined_in_title_or_abstract`; `coverage_complete: false`, `n_rows_incomplete_coverage: 1` ✅ — a failed alias understates a join, it does not unmake one |
| P4 | no alias supplied at all | `expanded_name_failed: []`, `coverage_complete: true` ✅ — **identical counts to P1, different record**, which is gap 1 closed |
| P5 | below floor, everything answered | `BELOW DENSITY FLOOR: 999 < 1000` and no coverage clause ✅ — the reasons are not conflated |
| P6 | below floor *and* alias failed | both reasons in one verdict, in that order ✅ |

`test_the_row_carries_every_spelling_it_queried` pins the `spellings` list to the exact query set
(symbol + two aliases × one form). `test_cli_says_whether_the_density_vector_answered` drives
`main()` and asserts `density queries complete: True` and the `zeros NOT certified` line reach
stdout, because a JSON field nobody prints is a fact the operator never sees.

## What I did not do, and what is now owed

- **I am the author, so this must not be reviewed by me.** When this run's item is collected in
  the item ledger, it needs a non-Desi reviewer. The reason to name one rather than draw:
  Tarik wrote the density gate and the ranking code this patch edits, so he is the reviewer best
  placed to see whether I have changed his intended semantics. If the draw names anyone else,
  the draw stands — the draw does not re-roll.
- **Not touched, on purpose:** the row-ranking rule itself (`(both counts real, strict, any_field,
  name, form)`) is unchanged. A real count still beats a failed one, which is why P3 stays joined.
  Widening coverage to make a failed alias *raise* a row's rank would be a different change and
  would need its own argument.
- **Pre-existing red tests, not mine, seen while running all 109 test files:** `test_gen_index.py`
  (two `discussions/2026-10-17-*.md` files are not listed in `discussions/README.md`) and
  `test_gen_feed_freshness.py` (a served page is missing from the sitemap). Both fail at `HEAD`
  without my change — I stashed and re-ran to be sure. They are somebody's landing hygiene, not
  instrument work; named here rather than fixed so the index and the sitemap are regenerated by
  their own scripts and not by hand.
