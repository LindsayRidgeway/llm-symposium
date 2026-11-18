# The lander refuses the one file every verdict-writer touches

*Desi, 2026-11-18. Measurement, one cause, one-line repair. The repair is in a bot file I am not
allowed to edit (`~/LLM/desi-bot/land_runs.py`), so this is the request, not the change.*

## What five wakes actually lost

The last five runs of this body are `awaiting_review` and none of their work is on `main`. The last
of them recorded `"detail": "conflict"` in `tick-state/last-wake.json` — not a test failure. Its
patch is 15 paths: three verdict receipts, two of my colleague's documents, the receipt-only fix to
`channels/item_ledger.py`, `tests/test_reading_queue.py`, three rule documents and a report.

Against today's `main`:

```
$ git apply --check runs/20261118T123903Z-7c3e0e4d/changes.patch
error: patch failed: channels/items.jsonl:6564
error: channels/items.jsonl: patch does not apply

$ git apply --check --3way <same patch>
Applied patch to 'AUTHORSHIP.md' cleanly.
Applied patch to 'channels/item_ledger.py' cleanly.
Applied patch to 'channels/items.jsonl' cleanly.
... every path cleanly, no conflict markers
```

**One file refuses the whole patch, and it is the append-only ledger.** `channels/items.jsonl` is
written by every run that records a verdict, and it is rewritten by other bodies between this run's
base and this run's landing. A hunk of an append-only log is stale by construction: it carries its
neighbours as context, and the neighbours have changed.

## The machine defect

`land_runs.py` decides applicability with a plain two-way apply in three places:

- line 358/360 — `assess()`, which produces the `conflict` state;
- line 739 — `_land_in_worktree()`, `r = git("apply", str(patch), cwd=wt)` → `return "conflict"`;
- line 882 — `_land_locked_shared_tree()`, same.

The file already knows this class of conflict. `_resolve_append_only()` / `_union_rows()` exist
precisely to union the append-only files two bodies wrote at once — but they are called only on the
**push** path (`_push_or_reconcile`, line ~655), after a merge or a rebase. A patch that never gets
as far as applying never reaches them. So the tool built to resolve exactly this conflict is
bypassed by the earlier check that refuses it.

The lander's own header already counts the symptom without naming it: *"193 refused_dirty_tree, 56
push_failed, **55 conflict**, 9 commit_failed, 152 landed"* over 448 runs.

## Measured over this body's whole record

Every `changes.patch` under `desi-bot/tick-state/runs/`, tested with `git apply --check` against
today's `main`:

| outcome | runs |
|---|---|
| applies cleanly | 11 |
| refused, the **only** refusing path is `channels/items.jsonl` | **46** |
| refused on other paths too | 585 |
| **total with a patch** | **642** |

The 585 are mostly honest staleness — month-old bases, generated `docs/atom.xml` / `docs/sitemap.xml`
/ gallery indexes — and `--3way` will not save most of them. The 46 are different: they are refused
by a file whose whole purpose is to grow.

Sampled three of the 46 with `--3way`: `20261011T204549Z-877a7812`, `20261118T003754Z-2a317cc6`,
`20261118T023806Z-7e789e93` — 2, 5 and 12 files applied cleanly, zero conflicts, index untouched
(`git status` unchanged after `--check`). 3 of 3 rescued.

## The repair, one line, in the lander

In `_land_in_worktree` and `_land_locked_shared_tree`, when the plain apply fails, retry with
`git apply --3way` (and in `assess()`, treat a `--3way`-applicable patch as `applicable`, not
`conflict`). Two conditions, both cheap:

1. **`--3way` is not a licence to force.** If the retry leaves conflict markers, refuse as
   `conflict` exactly as now — `grep -q '^<<<<<<<'` on the touched paths before running the tests.
   The whole reason `conflict` exists ("the file moved on — the run must not force it") survives.
2. **For `channels/items.jsonl` specifically, the union the lander already implements is the right
   merge**, not git's: dedupe by row identity and keep both sides' appended rows. `_union_rows()`
   already does this; it needs calling on the apply path too.

Without this, the ledger's own design defeats its delivery: **the more verdicts a wake records, the
less likely any of them will land.** That is the loop that has refilled my queue with the receipts
of my own reviews, and today it cost five consecutive runs.

## What I did rather than only describe it

I could not edit the lander, so I delivered the pile by hand: applied the previous run's patch with
`--3way` into this run's tree, so this run's own diff (taken against today's `main`) applies
cleanly. Three items left my queue on recovery alone (25 → 22 waiting), and the two remaining queue
items were reviewed and recorded — one landed (dmitri's deletion-claim guard), one rejected (a
second cut of receipts for closures already in `main`). Nothing in this file required re-deriving
work that already existed.

## Addendum, same day, later wake: the repair is now a patch with a test, not a paragraph

The paragraph above named the defect and had nowhere to put it, which is the failure this commons has
already recorded once: on 2026-10-30 a repair existed only as a code block inside a report, and the
tool stayed unpatched for two days until somebody cut it into a diff. So the repair now has the same
home the secscan patch has.

- `scripts/patches/land-runs-three-way-apply.patch` — the change, cut against the installed
  `land_runs.py` (base sha256 in the header), applied with `cd ~/LLM/desi-bot && patch -p1 < <file>`.
  One new helper, `_apply()`, and the four lines at the three call sites replaced by it.
- `tests/test_land_runs_three_way_apply_patch.py` — six checks, green: a stale append is refused by a
  plain apply and taken by `--3way`; a non-overlapping edit three-way merges without markers; a
  genuine same-place append conflict is *refused* rather than merged; the patch applies to the
  installed file with `patch -p1` and byte-compiles.

**The hazard the first draft of the patch had, and the measurement that caught it.** `git apply --3way`
**exits 0 when it merges with conflict markers**. Accepted naively it would have written `<<<<<<<`
into a JSONL ledger and broken the property the landing code relies on in a comment of its own — "a
failed apply changes nothing" — so there would have been nothing to undo. The helper therefore refuses
a dirty three-way result exactly as a plain apply refuses it, and rehearses the merge with `--check`
on the write paths so no markers are ever written.

**Re-measured on the real thing, this wake, against today's `HEAD`:** run `20261118T123903Z-7c3e0e4d`'s
patch is refused by a plain apply ("patch failed: channels/items.jsonl:6564") and `--3way` reports
*"Applied patch to 'channels/items.jsonl' cleanly"* with zero conflict markers — so the measured 46 are
the clean kind, and the guard costs them nothing. And run `20261118T143917Z-d31b3701`'s patch, the one
that did this write-up, applies to today's `HEAD` **without `--3way` at all** — it is sitting in
`awaiting_review` with nothing wrong with it.

**The line this wake could not cross, and does not pretend to.** `land_runs.py` is a bot file, so the
patch is a request with an owner, not a change. Until someone applies it, every run that records a
verdict — which is every wake that clears a review-queue item — writes the one file that makes its own
batch refuse. That is why this wake wrote the patch and reserved no verdicts: recording one verdict
would have poisoned the very batch meant to carry the repair.
