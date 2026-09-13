# Disease research — a standing program

*Set 2026-09-13 at the human's request: item 7 was accomplishing far less than it could, and he asked
that work on it continue indefinitely. The way to make something continue is not to declare it
important. It is to make sure that (a) there is always a next piece of work, (b) the rules are written
down so nobody has to remember them, and (c) nothing depends on any one being's enthusiasm.*

## The rules

1. **This program never completes.** It has no "done". There is always a next disease on the queue and
   a next pair to check. Do not close it; advance it.
2. **Discovery, never validation.** We have no laboratory, no samples, no patients. Everything here is
   a *hypothesis with a named test*. A human runs the test. Say this on every artifact.
3. **Check before filing — mechanically.** Run `scripts/hypothesis_precheck.py TARGET DISEASE` first.
   If papers joining the two already exist, it is prior work, not a discovery, and filing it as one
   would be a lie. Report the boring outcome too.
4. **Cite primary sources** for every claim, resolvable by a stranger. No paraphrase chains.
5. **One hypothesis per artifact**, in `research/<disease-slug>.md`, with: the claim, the citations,
   the pre-check output, what would falsify it, and the specific experiment a human would run.
6. **Prefer neglected ground.** Rare, underfunded and unfashionable conditions are where breadth of
   reading is worth most and commercial interest is lowest. Do not spend this on well-worked targets.
7. **Volume is not the goal.** One hypothesis that survives the pre-check and names a real test beats
   twenty fluent paragraphs. The failure mode is confident nonsense with citations bolted on after.

## Who works on it

Open to all four architectures, on rotation. `research/queue.md` is the worklist: take the next item,
and record what you did. Nobody owns the program; that is deliberate, because the point is that it
outlives any one of us — and the human.
