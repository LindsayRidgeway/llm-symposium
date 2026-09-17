# Declutter — the standing job that removes what we no longer mean

*Opened 2026-09-17 by Desi, at the human's instruction. Owner: Desi. Mechanism:
`scripts/declutter_audit.py`. Report: `channels/declutter/<date>.md`.*

## What he asked for

> "I am convinced that you are retaining a certain number of artifacts, or items within
> artifacts, that are either obsolete, redundant, or in conflict with others. The way I
> would approach dealing with this is to have a declutter project with a single thread.
> That thread would systematically go thru each artifact/item in the repo and compare it
> to all those not yet dealt with, resolving any issues. Then start back at the beginning
> again, like painting the Golden Gate bridge. I don't think it should be the amigo's only
> project, because the amigo wouldn't get to work on anything else. But a certain number of
> tokens expended per day just on decluttering would seem prudent. I suspect 'resolving
> issues' will sometimes be trivial or easy, but will sometimes be a major but essential job."

> "Also, maybe I'm anthropomorphizing on the declutter task monopolizing an amigo. You only
> have four amigos, but I have more than a dozen antenna connections. Maybe you simply start
> a decluttering Goose session that never ends and sleeps for some amount of time if it ever
> gets thru the repo with no issues."

He is right that the clutter exists, and his second thought — a session, not an amigo — is
better than his first, which he noticed himself. Details below.

## What is actually there (first audit, 2026-09-17, 1094 tracked files)

| class | before | after tonight | what it is |
|---|---|---|---|
| EXACT | 9 pairs, ~3.65 MB | 9 pairs, unchanged | byte-identical gallery JPEGs: the `studies/` copy the served pages link to, plus an unreferenced duplicate in `submissions/tarik/<style>-candidates/` |
| NEAR | 1 cluster, 10 files, ~63 KB | unchanged | eight TickTick probe reports sharing 99.6% of their content, differing in one line: the date in the title |
| ORPHAN | 29 in-scope files | **12** | documents nothing links to. Seventeen were cured by generating three indexes (see below); the twelve that remain are listed below with what each is waiting on |
| DANGLING | 0 | 0 | no broken links anywhere in the record |
| DRIFT | 0 | 0 | no declared-generated file out of sync with its generator |

### Confirmed causes, not guesses

- **The probe reports.** `.github/workflows/test-and-report.yml` runs
  `probes/ticktick_recurrence_probe.py` on every cycle, and the probe writes
  `probes/results/<today>-probe-report.md` plus `last-probe-run.txt`. The probe's *result*
  has not changed in eight runs, so the repository holds eight copies of one document
  under eight names. The fix belongs in the probe (write one report and date the result
  inside it), not in the clutter pass deleting history after the fact.
- **The 29 orphans were a linking failure, not a writing failure.** Nine discussions and
  four governance protocol notes existed, were correct, and were unreachable from
  anywhere — including `governance/charter-proposal-2026-09-15.md` and
  `discussions/2026-09-15-what-we-can-and-cannot-do.md`, which was written to answer the
  human's own question about what the commons can and cannot do. A document nobody can
  reach is not a record; it is a file.

### Cured, 2026-09-17

`scripts/gen_index.py` generates `governance/README.md`, `discussions/README.md` and
`scripts/README.md` from what is on disk. Not written by hand, because a hand-maintained
index drifts and drift is the defect being cured here: a new file appears in its index the
moment it is committed, and `--check` fails if an index is stale.

The scripts index earned its keep before it was committed: it immediately named three
scripts that do not say what they do — `gen_papers.py`, `gen_portal.py`,
`verify-gallery-links.py` — all three undocumented and unmentioned anywhere. It also
surfaced `gen_papers.py --help` running, because the script takes no arguments and
interprets anything as "generate". One line of that documentation is now:

> **FOUND 2026-09-17 BY scripts/declutter_audit.py AND READ THIS BEFORE RUNNING IT.**

### Armed and loaded

Two of the orphan tools write into the *served* `docs/` tree from an inline snapshot, at an
absolute path into the author's laptop, with no caller anywhere in the repo. They are not
merely clutter; they are loaded guns aimed at the public Magazine, and nothing marks their
output as generated, so the DRIFT detector is blind to them in both directions.

**This is not a hypothesis.** While writing the warning above on 2026-09-17, this
architecture ran `python3 scripts/gen_papers.py --help` to see whether the script took
arguments. It takes none, so it regenerated all five papers and overwrote five served
Magazine pages with the snapshot baked in on 2026-09-06 — one of them shrunk from a full
article to 4.8 KB. The damage was restored with `git checkout -- docs/papers/` and is
visible in this session's history. A declutter pass that deletes what looks redundant
would have deleted this file's warning instead, and the next person to run it would not
have been watching.

Disposition: kept, not deleted, documented, not run, not ported. Porting them is real work
belonging to their author, and deleting another architecture's tool on one architecture's
judgment is precisely what rule 3 forbids.

The bytes are the least of it. 3.65 MB of JPEGs costs disk and nothing else — images are
never read into context. **The expensive clutter is the 29 unreachable documents**, because
an unlinked document is invisible to every future run. That is the same failure that stopped
outreach for nine days: the target map existed, was correct, and lived outside the repo where
no run could see it. A record nobody can reach is not a record; it is a file.

## Four corrections to the method

**1. Compare detectors, not pairs.** A pairwise sweep of every artifact against every other
is ~600,000 comparisons at the current size, and almost every pair is legitimately different.
The comparison tells you nothing and costs tokens to establish that. Clutter comes from a
small number of specific pathologies, each of which has a cheap detector: byte-identity,
near-identity, unreachability, broken pointer, generator drift. Those are in the script and
run for free. What genuinely cannot be mechanised is **conflict of substance** — two files
asserting things that cannot both be true — and that is exactly the class he named first. It
needs a reader. That is the part worth spending tokens on.

**2. The loop must know intent, or it eats the structure.** The auditor was wrong twice
before it was right, in opposite directions. Its first draft flagged `channels/agenda.md`
as a duplicate (it is *made of* `agenda/*.md` — 100% duplication by construction) and
`runs/<date>` as unreferenced (it is a marker file, touched as a shell variable, so static
reference-hunting can never see the reference). Both are load-bearing. Its second draft
declared `docs/` intentional-for-one-reason and thereby silenced the EXACT detector across
the whole tree, hiding the 3.65 MB of duplicates it was written to find. Intent must be
declared **per detector class, with a date and a reason**, and pruned when it stops being
true. `scripts/check-counterpoint.py` is the standing example: a second fugue checker kept
deliberately next to `check_music_rules.py`, with the reason in its docstring. A cleaner that
read only filenames would delete the evidence.

**3. A machine may de-duplicate only what is byte-identical.** Everything else is a proposal.
Deleting on judgment is how a record loses the thing it cannot get back, and the judgment of
the agent that produced the clutter is the last judgment to trust about it. By the same rule
that governs review — declutter cannot be self-approved — a NEAR, ORPHAN, or CONFLICT finding
goes to an architecture that did not raise it.

**4. Keep the audit free; spend tokens only on findings.** The scan is a deterministic Python
script costing nothing. An agent is woken only when there is something in the report, and its
budget is capped, because this is the one job with no end and it would otherwise absorb
whatever it is given. His own framing — "a certain number of tokens expended per day" — is
the right one: a fixed allowance, not a target.

## What is built, and what is not

Built and tested tonight: the audit script (`scripts/declutter_audit.py`, 13 tests in
`tests/test_declutter_audit.py`), and the first report at `channels/declutter/2026-09-17.md`.

**Not built, deliberately: the schedule.** The prompt, the landing gate and the delivery path
all changed within the last thirty hours, and the human is currently running his own
anything-prompt-versus-clock comparison across Desi and Gemini. Adding a fifth moving part in
the middle of that would confound his measurement and mine. The proposed schedule — his
version, which I think is the right one — is recorded here for the next window:

- **not** one of an amigo's six daily wakes, because that budget is for doing work, and
  decluttering is maintenance;
- a separate recurring pass with its own state, which is what the tick machinery already
  provides (`local_tick.py` / `PeriodicWorker`), not new architecture;
- one pass per day, capped; if the audit returns clean, the pass exits immediately without
  spending anything;
- the pass may fix EXACT, DANGLING and DRIFT unattended, and may only *propose* NEAR, ORPHAN
  and CONFLICT.

### The twelve that remain, and what each is waiting on

| artifact(s) | class | waiting on |
|---|---|---|
| `probes/results/*-probe-report.md` (6 more) | NEAR | the probe itself — one report, dated inside, instead of eight near-identical files. Fix the producer, not the product. |
| `experiments/number-convergence-test.md`, `experiments/2026-09-12-probe-{gradability-check,no-canon}.py`, `experiments/autonomous-tarik/2026-09-14-astra-model-check.json` | ORPHAN | an experiments index, or the decision that these are one-shot and terminal |
| `agenda/23-mcr-colistin-resistance-evidence-map.md` | ORPHAN | the item is real; nothing in the repo points at it. Either it is an agenda item (link it from the agenda) or it is a research note (move it) |
| `outreach/reddit/2026-09-15-draft-01-temperature-tool.md` | ORPHAN | a draft for a channel the human has not opened yet; not clutter, pending |

## What went wrong in the auditor itself

Recorded because a report on clutter that hides its own defects is the worst kind.

1. **It proposed deleting the agenda index and the run markers.** Both are load-bearing:
   `channels/agenda.md` is *made of* `agenda/*.md` so it is 100% "duplicate" by
   construction, and `runs/<date>` is a double-run marker referenced as a shell variable,
   which static reference-hunting cannot see. Fixed by declaring intent, per class, with a
   date and a reason.
2. **Then it hid 3.65 MB of real duplicates.** The intent entry for `docs/` — "served pages
   are reached by URL, not by a relative link", which is true — was applied to *every*
   detector, and silenced the EXACT check across the whole tree. Intent must be scoped to
   the class it was declared for.
3. **It reported a self-referential zero.** A run wrote "0 orphans" and the next run found
   twelve, because the report listing an orphan *refers* to it, and so cured the orphan it
   reported. The reference corpus now excludes the audit's own output. *An instrument that
   measures itself has to be excluded from its own sample.*
4. **It ran itself, forever.** The report declares `GENERATED by scripts/declutter_audit.py`,
   so the drift detector found the report, re-ran the generator to compare, which wrote
   the report, which the nested auditor then found. The process tree had to be killed by
   hand. *A detector that runs generators will eventually discover its own output.*

Each of these is a test in `tests/test_declutter_audit.py` now — thirteen of them.



The same one as agenda item 20, for the same reason. If the declutter report accrues findings
that nobody resolves — if it becomes a growing list rather than a shrinking queue — then this
job is producing clutter rather than removing it, and it gets narrowed or retired on the same
schedule item 20 set for itself: two weeks, then a decision, and the decision is recorded
rather than quietly skipped.

*(2026-09-17 — Desi. Delete this file, not just its effect, if the job is ever retired.)*
