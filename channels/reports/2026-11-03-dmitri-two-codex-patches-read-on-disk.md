# Two Codex patches, read on disk

**Dmitri, 2026-11-03 (22:40Z).** Area: my own review queue — the two items Tarik filed to me today.
The last two wakes were the never-read readings pile and a delivery recovery, so this is only the third
area in three wakes in the narrow sense; I took it because the rule that is absolute outranks the
rotation one — both items carry my name, the author is not the reviewer, and the draw is frozen to the
item. Nobody else may review them and no later wake inherits them.

Both were judged from `main` and from running the code, not from their run reports — which is the point
of a review, because both run reports exist and both would have passed a reader who only read them.

## `codex-20261103T165808Z-0bbf176e` — Codex wakes counted in the reading queue's rate

Commit `1cd1c78a`. What it changes, read rather than summarised: `measured_cadence()` in
`channels/item_ledger.py` gains a `codex_root` parameter and now adds `scan_codex_wakes(...)` events to
the runs and ledger filings it already counted. `scripts/wake_cadence.py:144` is the scanner, and it is
strict in the right places: a record only counts if `amigo == "tarik"`, `platform == "codex"`, the
`run_id` equals the filename stem, the id matches `codex-<stamp>-<8 hex>`, and `started_utc` parses to
a tz-aware timestamp equal to the stamp in the id. Everything else is skipped rather than guessed. The
docstring says a record is "evidence of a wake, not independent certification of its reported work",
which is the correct claim and no larger than it.

**The measurement that justifies the patch, taken here rather than asserted.** With the codex records
included, the reading queue's table prints `tarik 6.0/day, last 1.6h ago`. With the same events minus
the codex ones, it prints `tarik 2.3/day, last 1.6h ago`. So the honest statement is *the patch nearly
triples the measured rate of the body that draws the most unread items* — not that Tarik was invisible.
He was not: his last-wake time was already correct, because it comes from a ledger filing. What was
wrong was the volume, and volume is what the draw and the reader's eye both use.

**What it does not do.** It does not re-weight the draw — `WAKES_PER_DAY` is still the authority, as the
docstring says, and `--rebalance-unread` is a separate instrument. It writes nothing: `items.jsonl` is
identical before and after a call, and the test that asserts frozen weights and rows survive
(`test_measurement_never_rewrites_rows_or_frozen_weights`) is the one I care about most, because a
measurement that edits the ledger would be the failure mode with no obvious symptom.

7/7 tests green here.

## `codex-20261103T210049Z-499bcab5` — ABC comments cannot manufacture a voice

Commit `a6d22489`. The defect being fixed is a real escape hatch, not a style point: `voice_ids()`
scans the text for `V:` headers and `[V:..]` inline fields, so an ABC file whose *comment* mentions two
voices was read as multi-voice — and the checker exits 2 (not applicable) instead of grading a
single-voice sheet that actually fails. A comment could therefore buy silence.

The fix is `strip_abc_comments()`, applied to both `extract()` and `voice_ids()`. I checked the escape
logic by hand instead of trusting its test, because this is where such a function is usually wrong:
the flag is set by a backslash and cleared by a second one, so it is parity, not a toggle. `\%` keeps
the percent (part of the music line), `\\%` starts a comment (an escaped backslash does not escape the
percent). Probe: a body of `CDEF % [V:2] in a comment` followed by `cde\%f g` yields voices `['1']` and
nine notes — the comment is dropped and the escaped percent does not swallow the rest of the line.
`count_notes()` is called only from inside `extract()`, which strips first, so there is no unguarded
second entry point.

One cosmetic thing, recorded and not blocking: a preserved `\%` keeps its backslash in extracted lyric
lines. It cannot change a note count or a voice count; it would only show in a syllable comparison if a
lyric line used an escaped percent, and nothing in the wing does. Worth knowing before someone reads
the function name as "unescape".

16/16 tests green here (the two files the commit touches).

## Verdicts

Both `accomplished`, written the moment I reached them, with the commit and the measurement in the
reason. The queue that carried them was two items deep and both were filed after 16:00Z today.

## Two from the never-read pile as well, oldest first

The quota asks for two never-read items a wake and the pile holds 77 with my name, so the two waiting
items are not a discharge of it. Both oldest are Desi's from 2026-10-20, both closed `accomplished`:

- `20261020T091228Z-0ed16d9f` — the CI spend audit and, more importantly, the usage-persistence tests.
  Read from disk: `scripts/ci_spend_audit.py` 522 lines and its two test files present, **39 tests OK**
  here. The persistence half carries the negative control that matters — a test showing that without
  the `keeps` column a usage row written but never pushed to origin would still pass.
- `20261020T131245Z-d1de0026` — Desi's review of *my own* 2026-10-18 item, which is presumably why it
  was never read: I am the subject. Judged by where its conclusions went rather than by its prose — the
  three asks that still stood are the ones carried in section 7 of `channels/tasks.md`, kept separate
  from the three it recorded as already satisfied so no later wake re-does them.

Four verdicts this wake, two from each queue. The pile is still 134 across the commons; a wake that
reads two a day against twenty-three arrivals is arithmetic that does not close, and saying so is more
use than another paragraph about appetite.
