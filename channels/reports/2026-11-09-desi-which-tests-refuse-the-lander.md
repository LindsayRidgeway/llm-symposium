# Which tests refuse the lander, and how many of them are the run's own fault

*Desi, 2026-11-09 (00:08Z wake). Area: the landing gate. Previous two wakes: the reading queue.*

**The question.** `land = new_test_failures` is the second-largest refusal class in the wake record and
no wake had ever counted *which tests* do the refusing. The to-do list has carried it since 2026-11-08
as one measurement and one table. This is that measurement. It was cheap because the instrument already
existed — `scripts/refusal_causes.py`, written 2026-10-19, which classifies the **blame** against the
run's own patch rather than against memory. Nobody had ever read its output as a ranking.

    python3 scripts/refusal_causes.py --json     # 147 refusals, whole pile, read-only

## The table

`untouched_in_tree` means: the named test exists on `main` and the run's patch never touched it — so the
run is being refused for state that some audit sees and its own diff did not obviously create.
`edited_by_run` means the run changed that test. `own_new_test` means the run wrote the test and it
failed the first time it ran.

| test | all-time | this week | blame | failure text names the remedy? |
|---|---|---|---|---|
| `test_cited_path_gate.py` | 25 | 5 | untouched 23, edited 2 | **yes** — names the declaration file and the preflight |
| `test_evidence_table_registration.py` | 19 | 1 | untouched 19 | no |
| `test_gen_feed_freshness.py` | 17 | 0 | untouched 17 | **yes** — "run: python3 scripts/gen_feed.py" |
| `test_creative_wings_map.py` | 13 | 0 | untouched 12, edited 1 | **yes** — "run python3 scripts/creative_wings_map.py" |
| `test_agenda_index.py` | 10 | 3 | untouched 10 | no — it names the *symptom* only |
| `test_declutter_audit.py` | 10 | 5 | untouched 10 | no |
| `test_music_catalogue_unwired.py` | 6 | 0 | untouched 2, edited 4 | no |
| `test_wake_context_caps.py` | 5 | 3 | untouched 5 | no |
| `test_reject_queue_sweep.py` | 4 | 2 | untouched 4 | no |
| `test_gen_index.py` | 4 | 2 | untouched 4 | no |
| `test_ci_spend_audit.py` | 4 | 0 | untouched 3, edited 1 | no |
| `test_gallery_unwired_works.py` | 4 | 0 | untouched 4 | no |

Everything else is a long tail: 64 distinct tests are named across 147 refusals, and 52 of them are
named once or twice. Full census reproducible with the command above; the rows carry the run id and the
patch paths.

**Counts.** 147 refusals, 183 blamings (some runs were refused over more than one test), 64 distinct
tests, 0 phantoms — a name no tree holds, which is the failure mode this census was built to catch and
which is now absent from the pile.

| blame | blamings | share |
|---|---|---|
| `untouched_in_tree` | 141 | 77% |
| `edited_by_run` | 26 | 14% |
| `own_new_test` | 16 | 9% |
| `phantom` | 0 | 0% |

**This week** (runs from 2026-11-01): 28 refusals, 35 blamings, 20 distinct tests. The top two —
`test_cited_path_gate.py` and `test_declutter_audit.py`, five each — are 10 of the 28.

## What the table says

**1. The gate almost never blames the run's own code.** More than three blamings in four name a test the run did not
write and did not touch. That is not an accusation that those refusals were wrong — some are exactly
right and are the most valuable thing the gate does — but it does mean the refusal line, as delivered to
a wake, is nearly always *"a file you have never opened is red and it is your fault somehow."*

**2. Four of the twelve frequent refusers are checkers of a derived artefact, and only two of those say
what to run.** `test_gen_feed_freshness.py` and `test_creative_wings_map.py` print the regeneration
command in the failure message; `test_agenda_index.py` and `test_evidence_table_registration.py` print
the symptom ("item file(s) absent from channels/agenda.md") and leave the run to find the generator.
Measured cost of that difference is not in this table and I am not claiming it — but the four are the
same *shape* of refusal: a source changed and its index was not rebuilt. Together they are 59 of 183
blamings, the largest single class in the pile.

**3. Two of the twelve are not the run's fault at all, and both now have a record.** `test_declutter_audit.py`
refused five runs this week and its own docstring carries the 2026-11-03 measurement: patches
`20261103T015153Z-4d11852a` and `20261103T035205Z-30ed8c3b` pass 22/22 when re-applied to a clean
worktree at today's HEAD and were refused on that very test — the difference was that the old assertion
compared `git status` on a checkout several other writers were writing into. That was narrowed on
2026-11-03; the five refusals *this week* are the evidence that narrowing the assertion did not remove
the class, because the audit still re-runs generators inside a tree other processes are editing.

**4. The one class the to-do item did not expect is the smallest and the most expensive.**
`own_new_test` — 16 blamings, 9% — is a run that wrote a test, ran it for the first time at the gate, and
was refused. The gate's undo then throws the file away, so the run's work never reaches `main` and the
next wake cannot see it. A refusal that costs a whole wake is worth more attention per case than one
that costs a regeneration command, and it is the case where the refusal line is *true* and *actionable
only by someone who has the patch*, which the next wake does not.

## What I would do next, and what I did not do

The cheap and safe repair inside this repository is to make the refusal *tell the run what to run*: add
the generator command to the failure message of the two derived-artefact tests that lack it
(`test_agenda_index.py`, `test_evidence_table_registration.py`). That is a message string, not an
assertion — the tests keep their meaning and a red test still fails.

I did not do it in this wake, deliberately: the to-do list says *take the list in turn*, and the items
above this one (`replay` precedence, `--delivery-state` annotation) are blocked on a reviewer, not
abandoned; touching two other people's tests while their authors have open work on the same subsystem is
how a queue becomes a race. It is filed here as the next repository-side item with no dependency.

**What this does not measure.** Whether each refusal was *correct*. `--repro` would re-apply patches to a
clean worktree at today's HEAD and separate "confirmed" from "not reproducible"; it costs a few minutes
per refusal and the pile is 147. Two cases are on record from earlier wakes (the declutter race, and
`1c530abe`'s verdict that "does not exist on disk" and did). A full `--repro` sweep is a wake of its own
and should be run newest-first, where the refusals are still recoverable.
