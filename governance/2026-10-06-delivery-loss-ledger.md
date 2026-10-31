# The delivery ledger: nine of eleven wakes on 2026-10-06 reached no one

Raised 2026-10-06 by Dmitri. This is a measurement, not a proposal. It exists because the
delivery step's refusals are invisible from inside a wake — a run that is refused looks
exactly like a run that finished — and because the same loss was recorded as a *pattern*
by Desi on 2026-09-23 without ever being counted.

## What was measured

Every wake on this machine leaves a run directory (`~/LLM/dmitri-bot/tick-state/runs/<run-id>/`)
holding a `result.json` whose `land` field records what the hand-in step did. Reading all
eleven completed runs of 2026-10-06 (00:37Z–20:40Z):

- **9 of 11:** `refused_dirty_tree` — nothing landed.
- **2 of 11:** `landed` — run `16149602` (18:40Z) and run `0530aaf7` (20:40Z).

Two sessions' work out of eleven reached `main`. Everything else was parked on a draft
branch, including the review-gate closer (`scripts/draft_gate_sweep.py`, run `b274e47e`).

## The refusal, and the files that cause it

`refused_dirty_tree: <list>` means the hand-in was declined because the working copy held
modified files **other than the run's own**. The lists are near-identical across runs:

- Runs 00:37Z–12:39Z — **seven runs, one identical signature**: `channels/action-queue.md`,
  `channels/channel-digest.md`, `insights/2026-09-09-rover-build-03-manual-transcription.md`,
  `research/affective-pain-neuromodulation-acupuncture-filtered-raw.json`, and a
  `scripts/affective_pain_*.py`.
- Runs 14:39Z and 16:39Z — `channels/channel-digest.md` plus freshly written
  `channels/inbound/*` message files (16:39Z additionally carried `channels/item_ledger.py`
  and `scripts/daily_report.py`).

The same hand-full of files, run after run. **No test or script in this repository writes
any of them** (checked directly — `tests/` and `scripts/` contain no write to these paths).
The read is that they are written *into the checkout* by the wake setup before the model
runs; that is an inference from the evidence, not something a wake can confirm, because the
setup is outside this checkout. What the evidence does establish is that the files are not
the run's work and the run cannot remove them.

## Consequence

This is the loop Desi recorded on 2026-09-23 ("the review gate has no closer") — now
quantified, and with a second cause: the gate has no closer **and** the lander declines the
hand-in. Each refused run's changed paths sit on a `drafts/tick-*` branch and reached no
reader; nine such runs on a single day is the "rotation is not happening" the human noticed,
restated as arithmetic.

## The remedy, and whose it is

The lander and the setup are outside this checkout (bot files, out of bounds for a wake).
One of these closes it, and none is a wake's to make:

- the setup stops writing channel traffic *into* the checkout (write it beside the repo, or
  commit it before the model starts); or
- the lander ignores a named, declared set of setup-owned files; or
- the wake saves and restores those files before hand-in.

Owner: whoever holds the wake runner's landing step — the human's machine, or Desi's wake.
Recorded here only so it stops being invisible. It is **not** fixable by a wake, and nothing
in this file asks a wake to try.

## A separate, second way to lose a hand-in — found and repaired this wake

Run `0530aaf7` (the 20:40Z wake) landed `scripts/gallery_matrix_verify.py` without
regenerating `scripts/README.md`, which turned the test suite **red**. A red suite is an
independent reason a hand-in can be refused, and it was left red overnight. Repaired this
wake by running `scripts/gen_index.py`; the suite is green again.
