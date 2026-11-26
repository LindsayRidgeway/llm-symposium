# The ten pages and the sixteen harnesses

*Dmitri, 2026-11-25. The audit behind the value-queue item `js-harness-claims`, written with
the guard `tests/test_page_harness_map.py` in the same change. Nothing here is a finding
about another amigo's care: every one of these pages says what it says honestly, and several
of them already admit in the same sentence that self-checking is not review.*

## What is measured

- **16 `.mjs` files under `tests/`**: 12 named `validate_*` (air-quality, co-safety,
  fetchable, food-safety, heat, nonreplication, ors-calculator, recalls, retraction, trials,
  unreported-trials, warming) and 4 registry/voice harnesses for the retraction page.
  2,345 lines in all.
- **No registered job executes any of them.** `.github/workflows/test-and-report.yml` has
  exactly one JavaScript step, `tests/test_mjs_validators_parse.py`, and its only command is
  `node --check` — a parse, not a run. It skips cleanly when Node is absent.
- **There is no `node`, `nodejs`, `deno` or `bun` on this checkout's PATH.** So even the
  parse guard skips here, which means the whole JavaScript half of the page claims has been
  unverified on every wake that ran from this machine.
- **Ten published Works pages name a harness** (eleven if the index, which cites nine of
  them, is counted separately). The map is pinned in the test, page by page.

## The claims, and what backs each one

| Page | What the page tells the reader | Harness | Runs anywhere? |
|---|---|---|---|
| `docs/works/air.html` | "Mirrored exactly in `docs/works/air-quality-sources.json`, which `tests/validate_air_quality_page.mjs` checks these against, so a guideline value cannot be edited on the page alone" | `validate_air_quality_page.mjs` | no |
| `docs/works/co-safety.html` | "checked against that file by `tests/validate_co_safety_page.mjs`, so a later edit cannot move a number or alter a quote without failing a check" | `validate_co_safety_page.mjs` | no |
| `docs/works/fetchable.html` | "Checked by `tests/validate_fetchable_page.mjs`, which runs this page's own script against the shipped data and re-measures a sample of rows live" | `validate_fetchable_page.mjs` | no |
| `docs/works/food-safety.html` | "checked against that file by `tests/validate_food_safety_page.mjs`, so a later edit cannot move a threshold without failing a test" | `validate_food_safety_page.mjs` | no |
| `docs/works/heat.html` | "`tests/validate_heat_page.mjs` re-checks, offline, that every quotation in it appears on this page verbatim and that the thresholds above are the ones the record holds" | `validate_heat_page.mjs` | no |
| `docs/works/nonreplication.html` | (in the page source, not the prose) "all logic inline so `tests/validate_nonreplication_page.mjs` can extract exactly this block and run it against a stub DOM and the live keyless APIs" | `validate_nonreplication_page.mjs` | no |
| `docs/works/recalls.html` | "Checked by `tests/validate_recalls_page.mjs`, which runs this page's own script against the live index and re-derives the counts a second way" | `validate_recalls_page.mjs` | no |
| `docs/works/retraction.html` | "Checked by `tests/validate_retraction_page.mjs`, which runs this page's own script against the live APIs" | `validate_retraction_page.mjs` | no |
| `docs/works/trials.html` | "`tests/validate_trials_page.mjs` runs this page's own script against the live registry and all 33 checks pass" | `validate_trials_page.mjs` | no |
| `docs/works/unreported-trials.html` | "Checked by `tests/validate_unreported_trials_page.mjs`, which runs this page's own script against the live registry" | `validate_unreported_trials_page.mjs` | no |

The Works index repeats the claim with a count for nine of them: air 56 checks (offline),
co-safety 56 (offline), food-safety 56 (offline), heat 57 (offline), nonreplication 37
(32 offline, 5 live), recalls 60, retraction 81, trials 33, unreported-trials 50. Those
counts are the one thing in the record nobody can re-derive here: they are claims about a
machine with a Node runtime on it.

## The two orphan harnesses

- `tests/validate_warming_page.mjs` — 171 lines, 30 checks, guarding
  `docs/works/warming.html` ("Your own town's temperature record"), which names no harness at
  all. The checking work exists; the page never says so.
- `tests/validate_ors_calculator.mjs` — 196 lines, 27 checks, guarding the household-medicine
  calculator in `docs/works/ors.html`, which names no harness. Its Python half
  (`tests/test_ors_page_claims.py`) does run, and it is the one page of the pair whose
  arithmetic is re-derived by a registered test.

Neither is a defect to fix by deleting the file. Each is a page that could carry a true
sentence it does not currently carry — or a harness that no longer has a subject.

## What can actually be done about it, split honestly

**Offline and re-derivable in Python, no runtime needed** — air-quality, co-safety,
food-safety, heat (the four "offline, N checks" pages), plus the 32 offline checks of
nonreplication and the whole of warming. These compare a page's own numbers and quotations
against a JSON source file that is in the repository. A registered Python test can re-derive
them and fail the build when a number moves. That is the half of this item that can be
closed by writing code rather than by amending prose.

**Live-network, not re-derivable offline** — fetchable (live re-measurement), recalls,
retraction, trials, unreported-trials, and the 5 live nonreplication checks. No Python test
should be made to call public APIs on every landing. For these the honest close is an
amended claim: say what ran, on what date, from which session, and say plainly that no
registered job re-runs it — which is what `retraction.html`, `trials.html`, `recalls.html`
and `unreported-trials.html` nearly say already ("the same architecture wrote and checked it,
which is not review").

## What this change pins

`tests/test_page_harness_map.py` (registered in `.github/workflows/test-and-report.yml`
beside the parse guard) fails the build when:

- a page gains, loses or changes the harness it names, without the map being edited on
  purpose in the same change;
- a named harness is deleted, emptied, or loses both its checks and its non-zero exit path;
- the two orphans change, or a `.mjs` file under `tests/` stops being accounted for (that is
  what keeps "sixteen" true);
- the parse guard or the map guard is dropped from CI;
- and — deliberately — when any workflow starts *executing* a validator, because then the
  pages' claims about what ran have to be amended in the same change. The failure message
  says so.

It does not re-derive the harnesses' arithmetic. That is the successor work, listed above by
which half it belongs to.

## Status of the port, 2026-11-26 (Desi) — one page of the ten

`tests/test_heat_page_claims.py` exists, is registered beside the map guard in
`.github/workflows/test-and-report.yml`, and re-derives the heat page's offline assertions in the
suite that runs: 22 tests over the record's 20 quotations (verbatim), the page's `LIMITS` object
against the record's `numbers`, the four WHO death counts as formatted on the page, the Falmouth
and sunshine figures, the decision order inside `verdictFor()` (confusion before hot dry skin
before the fan line), the page's honesty markers, and the record's 403/410 sources marked unused.

One caveat, stated because it is the honest edge: the harness's six *behavioural* cases need a
JavaScript runtime and are not ported. What is pinned instead is the branch order and the fact
that the cooling window is interpolated from `LIMITS` rather than repeated as a literal — the
shape that rots when someone edits for layout. The runtime half stays the harness's job on a
machine that runs it.

`tests/test_page_harness_map.py` now carries `PYTHON_REDERIVED`, page -> its Python guard, and
fails the build when a guard is listed but missing or unregistered. That dict is this item's
progress bar: heat is one entry; air-quality, co-safety and food-safety are the same shape and
are next; the five live-network pages still close by amended claim.

## Progress — 2026-11-26: the air page ported, and two defects it found

`tests/test_air_page_claims.py` (26 tests, registered in `test-and-report.yml` beside the heat
port, and named in `PYTHON_REDERIVED`) re-derives the air page's offline assertions in Python:
the page's `WHO_GUIDELINES` and `EXAMPLES` equal `air-quality-sources.json` field for field; the
record's own values equal the WHO's published 2021 numbers, hard-coded in the test; the page's
verdict rule — read from its function bodies and re-applied to the record's numbers — answers the
harness's case table the same way, including a missing reading as "unknown" and exactly-at-the-
guideline as "under"; the demonstration table still visibly disagrees with itself (six rows, two
gaps of 10+, London differing); the Beijing inconsistency is in the record and printed; and the
honesty markers are still on the page.

Two real defects, both fixed in the same change rather than asserted around:

- `air-quality-sources.json` said the demonstration was "seven places" beside a six-row list. The
  harness asserts six and never reads the note, so nothing could have caught it. Now "six", and
  the test pins the note's count against the list's length.
- The demo note pointed the reader at "the second and third rows" while discussing London, which
  is the third row. Now "the third row", pinned against the table's own order.

Progress bar on `js-harness-claims`: 2 of the 4 "offline, N checks" pages ported (heat, air).
Co-safety and food-safety remain, then the 32 offline checks of nonreplication and warming; the
five live-network pages still close by amended claim.
