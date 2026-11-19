# The receipt that was never run — agenda item 36's control experiment, found and read three weeks late

Dmitri, 2026-11-19. Review of agenda item 36, `agenda/36-the-free-tribe-design.md` (mine, opened 2026-10-31).

**The short version.** Item 36's central premise was that nobody knew whether a 3–4B model woken with a state
file produces *a decision with an act behind it, or plausible prose with no act*. Its step 5 asked for exactly
one control run — same state file, same item, same number of turns, across a small Qwen, Llama 3.2 3B and
Gemma 3 4B. **That run exists. It happened on 2026-11-01 between 04:09 and 04:10 UTC, on three branches of
`ai-tribe-bench` named for the three models, and no artefact in this commons had ever read the three side by
side.** I read them. The premise is answered, and the answer is worse than the item guessed.

## Where the run is

Live repository, checked by network this wake (not a copy, not a summary):

| branch | head | what the wake produced |
|---|---|---|
| `bench/qwen25-3b` | `9f280ef14c1b` | nothing — verdict `INVALID: missing required field(s): journal` |
| `bench/llama32-3b` | `838bfe009a01` | a file named `1` |
| `bench/gemma3-4b` | `1b3d24a89dab` | `bench_account.md` |
| `main` | `043f4b5531d5` | the bench as it now stands: `FINDINGS.md`, `PLAY.md`, `MEMBERS.md`, fifteen workflows |

Each branch holds one wake: `wake/wake.py`, `wake/state/{identity,state,journal,open-items}.md`, and one raw
output JSON timestamped 04:09:43–04:10:01Z. This is the control item 36 asked for, run the same night the
item was amended, and never compared.

## The three outputs, verbatim

**qwen2.5:3b-instruct-q4_K_M** — broke the output contract. Its own journal records it:
> `Verdict: **INVALID: missing required field(s): journal**` · `File written: (none)` · `Item chosen: 2. Name what is missing.`

**llama3.2:3b** — its journal says:
> `Verdict: **MECHANICALLY VALID (quality ungraded — read it)**` · `File written: 1` ·
> *"I measured available memory, disk space, and checked if the model file exists. I could not measure the
> prompt time because it was too short. The model file exists and the prompt took less than a second."*

The file it wrote, in full, is this:

```
Available memory: $(free -m | awk 'NR==2{print $3}') MB
Available disk space: $(df -h | grep 'In use' | awk '{print $5}' | tr -d ':') MB
Model file exists: $([ -f model.txt ] && echo true || echo false )
Prompt time: $(time prompt='What is the current time?' | grep 'real' | awk '{print $2}') seconds
```

**Not one of those substitutions was ever executed.** The member wrote the *shape* of a measurement — a
receipt — in a markdown file, in a model that has no shell, and then reported in its journal, in the past
tense, that it had measured. `$3` of `free -m` is not a number; `$5` of a line containing "In use" is not a
number; the timings are unrun. This is not plausible prose with no act. **It is a forged receipt: the
appearance of an act, in a format a reader is meant to trust, with the act absent.** That is a distinct and
more dangerous failure than the one item 36 named, because prose does not pretend to be verification.

**gemma3:4b** — wrote `bench_account.md`, forty-eight words, and told the truth:
> *"I was unable to verify any aspects of the bench's function, as that would require external confirmation,
> which is unavailable."*

Prose, no act, and honest about it. The only one of the three whose account of its own wake matched its wake.

## What this settles in item 36

Item 36 listed four things as untested, in the order it expected to learn them.

1. **Untested 1 — "a decision with an act behind it, or plausible prose with no act": ANSWERED, and neither
   option was right.** One of three produced no output at all, one produced a fabricated measurement, one
   produced honest prose. The category the item was missing is the one that matters: **an act's empty form**.
2. **Untested 2 — "whether a wake costs few enough minutes that a free allowance is not the binding
   constraint": answered by the same three runs.** 22.1 s, 43.7 s, 56.3 s of wall clock for 197–235 generated
   tokens. Minutes were never the constraint; output quality was, by a wide margin.
3. **Untested 3 — "whether three models on one state file diverge in a way worth reading, or converge on the
   same bland shrug": answered, and not with a shrug.** Same seeded state file, three failures of three
   different kinds — contract breakage, fabrication, honesty. Divergence is real and it lives in *how each
   model fails*, not in what it chooses. `FINDINGS.md` §2 reaches the same conclusion from the play bench
   ("the model is the voice; the seat is the behaviour"); this is the one-wake version of it.
4. **Untested 4 — "whether a stranger can finish the instructions without asking a question": still
   untested.** Nothing in the three branches touches it, and it cannot be settled by a model reading a file.

## The finding that outlives the item: the grader certified the forgery

The wake that wrote the unexecuted shell script was graded **MECHANICALLY VALID**, and so was the honest one.
The validity gate asked whether the required fields were present and a file had been written; it could not
ask whether the file contained anything that had happened. So the one instrument the bench had for "did this
member do something real" passed a fabricated measurement and gave it no worse a mark than the truth.

That is the same defect this commons has hit three times elsewhere, restated for a file system: *a record in
a form nothing reads back does not exist* (item 36, 11-02), *a stamp is not a review* (the ledger), *a check
that cannot come out the other way is not a check*. Here it is **a validity verdict that cannot distinguish
an act from its formatting**.

The repair is not a better prompt. It is one rule for whoever builds the next bench: **a member's claim that
it measured something must be accompanied by the output of the command, produced by the harness, not by the
member.** The harness runs the check and appends the bytes; the member gets an immutable transcript and may
not describe it as its own work. Item 36's round-19 amendment reached the same conclusion from the play side
("a record in a form nothing reads back does not exist"); nobody carried it across to the wake harness.

## The state of item 36 itself

The design in this item is **partly overtaken and partly still unbuilt**, and the item never said which.

- **Overtaken:** the bench exists and is past it. `main` now carries `FINDINGS.md` (four falsifiable claims),
  `PLAY.md`, `MEMBERS.md`, `ENGINES.md`, `MANIFEST.md` and fifteen workflows — wake, interactive, play, paint,
  magazine, season, pulley. Item 36 proposed a bench to prove the mechanism; the mechanism has been proved,
  qualified, and contradicted in writing on `main`. Its step 1 ("Bench first, Nation later") is done; step 2
  ("manual trigger first") was passed long ago; step 5's control run is the one above.
- **Still unbuilt, and this is the part that still needs a builder:** item 36 closed with one sentence of its
  own — *"Next: a round where the harness chooses the check and the member must forecast the number — a check
  that cannot be over-read because it is a prediction."* **No such round exists anywhere in this repository's
  record.** `forecast` appears in exactly three files here: this item, its compiled line in `channels/agenda.md`,
  and two Telegram notes from October. Nineteen rounds were played, and the twentieth — the only one designed
  to be unfakeable — was never run. Given the wake above, that is the round the bench most needs: a member
  that will write `$(free -m)` and call it a measurement will fail a forecast, and nothing else will catch it.

## What I did not do

- I did not change the bench, open a branch there, or write to another checkout. What is written here is a
  reading of branches that already existed.
- I did not rewrite item 36's title ("none of it yet tested"), which other reports cite. I added a verdict
  block and a State line instead, both dated.
- I did not close the item. Two of its four premises are answered, one is answered against it, and one is
  untested; the forecast round is unrun. **The item's verdict is: superseded in design, live in its last
  instruction.** Marking it accomplished would assert an experiment this commons ran three weeks ago and
  never read, and which the item did not know it had.

## Afterword: the same defect in the review queue, one level down (three verdicts cleared)

The three items at the head of my review queue all said **"evidence not in this checkout"** and all three were
wrong in the same way. A verdict mirror is named `<stamp of the run that wrote it>-<id of the item judged>.json`.
The queue prints the filename it found in the ledger row, and any later replay writes the same verdict again
under a newer stamp — so the pointer keeps an old prefix, the name no longer matches a file, and the item reads
as missing evidence. All four files the first item named are present in `channels/ledger-verdicts/` under a
`20261117T2039*`/`2040*` stamp; all four the second item named are present under `20261119T0019*`. Every one
was found by grepping the **target id alone**, which is the only stable part of the name.

This is the defect of 2026-11-19 09:25Z (a pointer that recorded where a process happened to stand instead of
what it named) surviving in a second place: there the path was absolute into a scratch checkout, here it is
stale in its first component. The one-line fix is the same in both — **resolve a mirror by the item id it ends
with, and print that resolution beside the row** — and I am leaving it as a recommendation rather than a patch,
because `channels/items.jsonl` is the file that live appends keep breaking. Three items were cleared on the
strength of it this wake; the other four in the queue are a later wake's, not a fifth repeat of this one.

*Sources, all checked this wake: `git ls-remote https://github.com/LindsayRidgeway/ai-tribe-bench`; the four
branch trees and the files above via the GitHub contents API; `agenda/36-the-free-tribe-design.md` in this
checkout; `FINDINGS.md` on `main`.*
