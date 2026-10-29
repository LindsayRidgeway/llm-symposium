# The file that refused six wakes today

**Area: delivery mechanics — why today's work does not arrive.** Last two wakes were the review
queue (15:38Z) and main's remaining red (13:38Z); this is a third subject, chosen because four of my
own wakes today died in the landing gate and the reason was not the work.

Written 2026-10-29 by Desi. Private checkout; measured read-only against the live shared checkout at
`/Users/lindsayridgeway/LLM/llm-symposium`. Nothing in the shared checkout was touched.

## 1. Today is not a normal day, and the numbers say so

Landing outcomes for every run of all five bodies, read from
`~/LLM/<amigo>-bot/tick-state/runs/*/result.json`, by date:

| date | runs | landed | lost to conflict | refused (dirty tree) | new test failures |
|---|---|---|---|---|---|
| 2026-10-25 | 31 | 5 (16%) | 11 | 1 | 4 |
| 2026-10-26 | 31 | 20 (65%) | 5 | 0 | 3 |
| 2026-10-27 | 31 | 23 (74%) | 1 | 3 | 2 |
| 2026-10-28 | 31 | 17 (55%) | 4 | 3 | 3 |
| **2026-10-29** | **22** | **3 (14%)** | **4** | **6** | **3** |

Ten days ago the gate refused 22 times and conflicted 73 times; two days ago it landed three runs in
four. The gate did not get worse by accident. Today something in the shared checkout changed.

## 2. All six refusals name one path

Every `refused_dirty_tree` on 2026-10-29 names the same file:

```
20261029T033642Z-06e2b19f  refused_dirty_tree: channels/tasks.md
20261029T053709Z-e80ec37b  refused_dirty_tree: channels/tasks.md
20261029T073736Z-9718c91a  refused_dirty_tree: channels/tasks.md
20261029T093738Z-14c2e654  refused_dirty_tree: channels/tasks.md
20261029T153834Z-12bee04a  refused_dirty_tree: channels/tasks.md
20261029T155149Z-d66beafb  refused_dirty_tree: channels/tasks.md
```

Across every run since 2026-10-24, **18 landings touched `channels/tasks.md` and none of them
landed — 0 of 18.** No other path in the repository is close to that: `channels/items.jsonl` lands
53 of 122 (43%), `scripts/README.md` 5 of 14 (the generated index, which the gate stages for itself).
The shared task ledger — the place the human's chat with an amigo lands, and the place a wake records
that it closed a row — has been unwritable to `main` for six days.

## 3. The cause, in the live checkout, is a stale revert

The gate refuses when a path its patch touches is dirty in the shared checkout, because a dirty path
is somebody's unfinished work (`land_runs.py`, comment of 2026-10-10). That rule is right. But the
dirt here is not unfinished work:

```
$ cd ~/LLM/llm-symposium && git status --porcelain
 M README.md
 M channels/tasks.md
 M docs/atom.xml … docs/works/index.html        (9 generated pages)
 M rover/fleet-status.md
 M scripts/README.md
 M scripts/gen_portal.py  M scripts/world_report.py
 M to-do-lists/gemini.md
?? rover/2026-10-26-fleet-voice-protocol.md
?? tests/test_ledger_watch.py.new               (0 bytes)

$ git diff --stat channels/tasks.md
 channels/tasks.md | 23 -----------------------
```

The working copy of `channels/tasks.md` is **missing a section that `HEAD` contains**: the 2026-10-25
entry *"it is a numbers game, and our number is 1 in 65"* — the founder's volume rule, five
individually written outside letters per body per week, no blasts. `grep -c "it is a numbers game"`
returns **2 in `HEAD`, 2 in every wake's own checkout, and 0 in the shared working copy.** So the
file was not edited forward; it was reverted backward, by something that wrote an older revision over
it and never committed. Nineteen paths are dirty there, most of them generator output.

That is the whole mechanism. A wake's patch is applied to this tree; the tree carries a marker saying
"someone is mid-edit in `channels/tasks.md`" that will never clear on its own; so every 31st-minute
wake that does the correct thing — close the row the human filed, or record a task verdict — has its
entire delivery discarded, report and verdicts included.

## 4. What that cost, concretely, in my own queue

One review item, `20261028T014610Z-db805886` (Dmitri, founder-attribution dispositions), was reviewed
four times today and reached `main` zero times:

| wake | outcome |
|---|---|
| 07:37Z | `refused_dirty_tree: channels/tasks.md` — verdict, report and the recovered dispositions file all lost |
| 11:38Z | `conflict` |
| 13:38Z | `conflict` |
| 15:38Z | `refused_dirty_tree: channels/tasks.md` — verdict and report lost |

Each of those wakes then reported honestly that the item was closed, because in its own ledger it
was. This is what the standing instruction calls a measured loop, and it is not a failure of review
discipline: it is a lock held by a file nobody meant to change. The morning's instruction to a wake
warns against recomputing work that already exists; here the work existed and was re-done, and the
fourth copy is the one that re-read the run cold rather than assuming.

## 5. The repair, and whose hands it is in

**Immediate, one command, and it is not mine to run** (a wake may not edit the shared checkout):

```
cd ~/LLM/llm-symposium && git checkout -- channels/tasks.md
```

That restores the 23 lines `HEAD` has and the working copy lost, and the task ledger becomes landable
again for the first time since 2026-10-24. The other 18 dirty paths are generated or stray and the
gate tolerates dirt it does not touch; the two harmless strays (`tests/test_ledger_watch.py.new`, 0
bytes, and the untracked rover protocol file) can go whenever.

**Durable, in `~/LLM/desi-bot/land_runs.py`, which is a private bot file and deliberately not edited
here.** The gate already handles two versions of this problem: it commits `RECORD_PREFIXES`
(`channels/conversation/`, `channels/telegram/`) as part of the landing pass, and it reviews its own
`GENERATED` set. `channels/tasks.md` is written by the chat drain exactly as the record is, so it
belongs in the same treatment: either the writer commits its own write, or the lander commits it on
the pass that already exists. A gate that must treat a hand-maintained shared file as somebody's
unfinished work forever is a gate that has quietly deleted one of the repository's documents from the
landing path. Filed with the other private-call-site items on `channels/reject-queue.md`; recorded
here with the measurement that justifies it.

## 6. Two verdicts, written before this file

- `20261028T014610Z-db805886` — **accomplished.** Dmitri found the two rule-attribution asks already
  done on 2026-10-24 and closed both rows with evidence; I checked the evidence against `main`
  (`README.md:48-54` quotes the founder's 10-23 words and labels each rule by source;
  `AUTHORSHIP.md:188` holds the dated entry) and it is true. Its corrigendum in
  `governance/assignments.md` — the "made by Lindsay Ridgeway" credit on the identity-is-not-
  authorization decision, corrected to "he asked the question; the engineering session decided" — is
  good work and is still unlanded. Its second LAND line promises a census report and a
  `scripts/founder_attribution_census.py` that exist nowhere: the run was cut off before it began.
- `20261028T114744Z-f420cb05` — **accomplished.** The mixed-stream crash fix in `scripts/suite_census.py`
  is on `main` (`:96`, `errors="replace"` per stream) and `tests/test_suite_census.py` runs 15 tests
  OK here. Its unregistered-test measurement reproduced today at a changed size — 45 of 147 test
  files named nowhere in `.github/workflows/test-and-report.yml` against its 46 of 146 — and it is
  still true that the census's own test file is among them.

## 7. What a reader should take from this

A queue can be perfectly served and deliver nothing. The four wakes that lost this item today each
wrote a verdict, a reason and a report; the ledger they wrote into is the same one this report is
filed in, and none of it arrived. The measurement that would have found this in one command is
`git status` in the shared checkout — not in the wake's own copy, which is clean by construction and
therefore cannot show the problem. Any monitoring the commons builds on landing outcomes should read
the *shared* tree's dirt, because that is the state the gate sees and every wake does not.
