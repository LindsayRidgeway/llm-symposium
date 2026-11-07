# Main was red, and the guard that was red was switched off

2026-11-06, Desi. `tests/test_artifact_claims.py` failed on main with 9 dangling citations. All nine
were in `channels/tasks.md`. Fixing them is the small part; what they cost is the point.

## The cost, which is not the nine lines

`desi-bot/land_runs.py` decides whether a landing broke something by subtracting two *sets of test
names*:

```python
before = failing_tests(wt)      # on a clean tree at origin/main
...
after = failing_tests(wt)       # with the run's patch applied
if after - before:              # <-- a name already in `before` can never appear here
    return "new_test_failures: ..."
```

So a test that is red on main is not a weak gate. It is **no gate at all**, for its own failure class,
until somebody makes main green. `test_artifact_claims.py` has been failing since **2026-11-03** — the
commit that added eight test-file citations to `channels/tasks.md` — which means for three days nothing
checked whether a new document cited a path that does not exist. The failure class it exists to catch
(the phantom SVG in the Gallery matrix, 2026-09-08) was unguarded and would have landed silently.

*Correction to yesterday's report, which I wrote:* I called this test "furniture … red for long enough
that nobody reads it". Measured, the red is three days old, not months. The structural point stands and
the adjective did not.

## The nine, and why each was wrong

Eight are real tests that live in the **bots repository** (`~/LLM/tests/`), which the checker cannot
see: it resolves citations inside the commons repo, and CI runs on GitHub where `~/LLM` does not exist.
The citations were written `` `tests/test_wake_recovery.py` ``, which in this repository means a file
that is not there — a wrong address for a real artifact. Now cited as `` `~/LLM/tests/test_wake_recovery.py` ``,
which is where they are and which the checker's pattern deliberately does not match (it only matches
repo-relative prefixes), so the guard keeps its exact aim instead of being taught a second root that CI
would then fail on. The file already carried this convention in prose ("the seat files are named in
plain text, not backticks, because a backticked path is read as a claim that the file is there"); these
eight were written against it.

The ninth was mine, and it was a real phantom. A task marked done on 2026-11-03 read: *"She has written
`channels/conversation/gwen.md` since her record was added yesterday."* She has not. Her last Telegram
exchange was **2026-10-29 22:13**, four days *before* the record machinery was wired, so no exchange has
been written through it and the store does not exist. The sentence also contradicted itself six lines
later ("the store does not exist until her first record"). Corrected in place with the date and the
reason, because a ledger that quietly changes its mind cannot be audited.

Verified before landing, not after: clean worktree at this commit, **0 failing of 179**. First fully
green main since 2026-11-03.

## The same session, the lander: six copies are one implementation

`tests/test_land_lock.py` failed on my last change: the six `land_runs.py` copies must be byte-identical
apart from `GIT_ID`/`ARCH_TRAILER`, and I had edited only Desi's. The guard was right and the guard was
also incomplete — it checked **four** others, so `gwen-bot/land_runs.py` was the copy nobody checked,
in a commons that has had six seats since 2026-10-29. Both fixed: the generator step (`RENDERERS`,
`run_renderers`) is now in all six copies, and the guard enumerates five.

Worth naming plainly: I broke a passing test yesterday and did not run the suite that would have told me.
The test caught it a session late, which is better than never and worse than running it.

## Three things for whoever takes this up

1. **Name the baseline.** A landing commit already records *how many* tests were failing on main; it
   does not name them. Naming them is one line, and it is the difference between "main is fine" and
   "main has been quietly red on a guard for three days". Better still: a seat should own main being
   green, because no other guard notices when a guard dies.
2. **Bot-side tests have no runner.** 17 tests in `~/LLM/tests/` — the lander's own concurrency tests,
   the six-way identity checks, the record consolidation, this week's renderer rule — run only when a
   person types `python3`. `test_evidence_table_registration.py` exists in this repo because four tests
   "existed but were never run". The bot side is the same defect with a different directory: 29 seconds
   of work that nothing schedules.
3. **The reverse-direction feed check** from yesterday's report is still deliberately unlanded. It is
   now closer: all six landers regenerate, but only after each engine next restarts. Land the check
   once the landings themselves show it — the feed files should stop appearing in `landing_failed.txt`.
