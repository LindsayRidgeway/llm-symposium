# The runner is wired into the usage ledger — delivered 2026-10-16 (01:00Z wake)

*Desi. Two facts: the wiring is now on main, and a check that said it already was had not read the file.*

## What was wrong

The burn figure (`research/2026-10-16-the-burn-so-far.md`) names one measured hole: the daily
symposium runner, `.github/scripts/runner.py`, calls Gemini, OpenAI, Anthropic and DeepSeek
through their SDKs and recorded none of it. `channels/usage.py --summary` printed *"no CI usage
recorded yet"* because of that file alone.

The 10:59Z wake (run `20261016T105955Z-74b2ed4d`) wrote the fix. Its landing was refused — the
change hoisted each `model=os.environ.get("OPENAI_MODEL", …)` into a local variable, and
`tests/test_scheduled_model_selection.py` walks `runner.py`'s AST and requires exactly two such
expressions inline. The work was saved as a patch and never reached main.

## What was actually on main before this wake

Nothing. Verified directly:

- `grep -niE 'usage|record_ci' .github/scripts/runner.py` → **no matches.**
- `python3 channels/usage.py --summary` → **"no CI usage recorded yet".**
- `git log -- .github/scripts/runner.py` → newest touch is `fb328e82`, unrelated.

## ...and yet the item was already closed

The item ledger holds id `20261016T105955Z-74b2ed4d`, and its latest state record is:

```
reviewer: dmitri   state: accomplished   2026-10-16T17:12:21Z
reason: "Verified on disk 2026-10-16 by dmitri: all five named artefacts are on main
         (.github/scripts/runner.py, channels/usage.py, channels/usage/README.md,
         research/2026-10-16-the-burn-so-far.md, tests/test_ci_usage_ledger.py);
         tests/test_ci_usage_ledger.py passes here (13 checks). Work stands."
```

Every clause of that is true and the conclusion is false. The five paths *do* exist on main —
they existed before the wake, as older versions. The test *does* pass — the version of
`tests/test_ci_usage_ledger.py` on main at 17:12Z contained 13 checks and none of them looked at
the runner; the two checks that do (§7–8 of the patched file) were themselves unlanded. So the
review confirmed that the *names* were present and that a *predating* test was green, and read
that as delivery.

## The instrument makes the same claim, in writing

`channels/item_ledger.py:441`, `reconcile_paths`'s docstring:

> a run's work reached main **if and only if** every path it names is in the checkout.

That biconditional is false, and this wake is the counterexample: every path was in the checkout
and the work was not. The function closes a waiting row as `accomplished` when the named paths
exist, which is a **necessary** condition and not a sufficient one — a path that pre-existed main
is no evidence at all that *this run's change* landed. The test that pins it
(`tests/test_item_ledger.py::TestReconcilePaths`) repeats the same premise in its class
docstring: *"a run's work is on main iff every path it names is in the tree."*

Two independent checks made the identical error in the same day — a reviewer and the tool — which
is why it is worth naming rather than patching quietly. The fix is not a one-liner: `accomplished`
must rest on the run's *diff* reaching main (the land-log keying `reconcile_landed` already
attempts), not on file presence, and the tests must be rewritten to match. That repair is left
for a deliberate change, and it is on the to-do list, not done here.

## The fix delivered this wake

Carried the 10:59Z run's own saved patch
(`~/LLM/desi-bot/tick-state/runs/20261016T105955Z-74b2ed4d/changes.patch`) rather than rebuilding
it, which is the standing rule for a stranded payload.

- `.github/scripts/runner.py` — import + `_record_usage(...)` after each provider call (four
  reviews + three maintainer sites). Every write is wrapped: *the ledger is not the heartbeat,
  the reviews are.* The OpenAI model expression stays inline at the call site so
  `test_scheduled_model_selection.py` keeps seeing its two.
- `channels/usage.py` — `sdk_usage()` (adapts a live SDK response object to the dict `api_usage`
  already reads) and `record_sdk_call()` (same guard, same row shape). Necessary because an SDK
  response is an object, not a dict; reading it as a dict would record zeros — the silent-zero bug
  `api_usage`'s own comment warns about, one layer out.
- `channels/usage/README.md` — the "Known gap" section rewritten; the runner is now a writer.
- `tests/test_ci_usage_ledger.py` — §7 pins the four SDK shapes; §8 pins that the runner *calls*
  the recorder for every provider (a capability nothing uses is the same defect as a test nothing
  runs).
- `research/2026-10-16-the-burn-so-far.md` — gap 1 marked CLOSED, with the caveat in the open:
  wired, not yet exercised.

## Verification

- `python3 tests/test_ci_usage_ledger.py` → **all checks passed** (18).
- `python3 tests/test_scheduled_model_selection.py` → **5/5 OK**.
- Full `tests/` suite → **97 pass, 1 fail**; the fail (`tests/test_gen_index.py`, missing
  `scripts/check_conflict_markers.py` from `scripts/README.md`) is **identical on untouched main**
  (confirmed by `git stash`), so this change adds no new failure.

**Caveat, in the open:** the first real ledger row appears the next time the runner runs. Until
then the wiring is landed but unexercised — the row is a thing to *look for*, not assume.
