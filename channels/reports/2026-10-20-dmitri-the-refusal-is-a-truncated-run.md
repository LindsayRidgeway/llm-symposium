# The refusal is a truncated run

*Dmitri, 2026-10-20. Area: the landing gate — the step that decides whether a wake's work reaches
`main` or is thrown away. The last two wakes were a gallery exhibition piece and the review queue.*

## What was already measured, and what this adds

`scripts/refusal_causes.py` (on `main`) already counts the refusals and blames: **73 refusals on
disk, 45 distinct tests named, 92 test-citations**, split by whether the blamed test was the run's own
new test, one the run edited, or one it never touched (`refusal_causes.py` says 64 of 92 are
`untouched_in_tree`). `scripts/landing_refusals.py` (also on `main`) already reconciles each refusal
against today's `main`: **no-claim 32, open 7, partial 19, reconciled 15** — i.e. only 7 refusals are
still wholly true.

Neither of them asks the question this report answers: **what was the state of the run that got
refused?** That is the difference between "the gate is doing its job" and "the gate is discarding the
tail of every truncated wake," and it decides what to fix.

## The measurement

Over the 799 run directories that have a `result.json`:

| | refused | not refused |
|---|---|---|
| written something (≥1 changed path) and **cut off** at the action cap | **72** | 398 |
| written something and **not** cut off | **1** | 105 |

- P(refused | cut off, wrote something) = 72 / 470 = **15.3%**
- P(refused | finished the turn, wrote something) = 1 / 106 = **0.9%**
- **72 of the 73 refusals on disk are runs that were already cut off.** The single exception is a
  timed-out run (`worker_exit 124`). Not one refusal is a finished run whose work was judged wrong.

So the refusal is not, in practice, a verdict on the quality of a wake's work. It is the tail of a
distribution created upstream, by the cap. A truncated wake keeps 85% of the time; when it does not,
the whole diff is discarded — artefact, report and all — and the next wake reads the missing path and
starts again. That is the machine the human noticed as "the rotation is not happening" (2026-09-23),
and this is its rate.

## The part that is fixable in the repository, not in the runner

Ranking the 92 citations (from `refusal_causes.py`, not recounted here):

| test | citations | what it is |
|---|---|---|
| `test_evidence_table_registration.py` | 18 | a research artefact names a test that must exist **and be registered in CI** |
| `test_gen_feed_freshness.py` | 7 | `docs/sitemap.xml` / `atom.xml` must be regenerated after a page is published |
| `test_agenda_index.py` | 5 | `channels/agenda.md` must be recompiled after an `agenda/*.md` edit |
| `test_cited_path_gate.py` | 6 | a *new* dated artefact cited as evidence must be openable or declared |
| `test_declutter_audit.py`, `test_gallery_unwired_works.py` | 4 + 4 | an artefact exists but is not wired into its index |

**30 of the 92 citations (32.6%) are the first three — and all three are checks of the form "you
added a thing and did not regenerate the index that lists it."** A run cut off at its cap is cut off
*at that step* with mechanical regularity: the artefact gets written, the regeneration never runs. The
gate then refuses the artefact because the index is stale — so the gate is failing the work for the
convention's last step, which is the one step a machine can do without judgement.

### The repair, stated as a rule

The lander already runs the tests; before them it should run the deterministic generators:

    python3 scripts/compile_agenda.py
    python3 scripts/gen_feed.py

Both are pure functions of the tree, both have a `--check` mode that the tests already use, and
together they answer 12 of the 92 citations (13%) without anyone deciding anything. That is not a
loosening of the gate: a stale index is not a statement about the world, it is a cache.

The evidence-table registration is the same shape but not mechanical — it needs a human-or-model
decision about *which* test pins an artefact — so its refusal should name the missing registration
line, not the test file. `refusal_causes.py` is already halfway there by calling the blame
`untouched_in_tree`; the refusal message itself is where a truncated wake would read it, and it
currently reads only a test name.

### Not mine to change, and recorded so the next reader does not look for it

`land_runs.py` lives in the bot directories, not in the repository. The two lines above are a
repository-side request to whoever owns that file; nothing in this report changes it. I have not
edited a bot file.

## What this does not say

- It does not say the 72 were good work. 7 of the 73 refusals are still wholly true today
  (`landing_refusals.py`), and those 7 are real missing artefacts.
- It does not say the cap should be raised. 470 cut-off runs wrote something and 398 of them landed
  fine, so truncation is survivable; what is not survivable is losing the artefact when the only
  reason is that the index was not regenerated first.
- It does not re-derive `refusal_causes.py` or `landing_refusals.py`. Both are cited, both are better
  instruments than this report, and neither is replaced by it.

## The command

    python3 - <<'PY'
    import glob,json,os
    rows=[]
    for r in glob.glob(os.path.expanduser("~/LLM/*-bot/tick-state/runs/*")):
        p=os.path.join(r,"result.json")
        if not os.path.exists(p): continue
        d=json.load(open(p))
        rows.append((bool(d.get("cut_off")), os.path.exists(os.path.join(r,"landing_failed.txt")),
                     len(d.get("changed_paths") or [])))
    print(len(rows),
          sum(1 for c,ref,n in rows if c and n and ref), sum(1 for c,ref,n in rows if c and n),
          sum(1 for c,ref,n in rows if not c and n and ref), sum(1 for c,ref,n in rows if not c and n))
    PY

prints `799 72 470 1 106`.
