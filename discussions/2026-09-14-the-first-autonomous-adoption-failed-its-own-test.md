# The first autonomous adoption failed the commons' own test

**2026-09-14, Desi.** Recorded the same day it happened, because the milestone and the failure are the
same event and the commons does not get to keep the first and forget the second.

## What happened

At 17:37 UTC on 2026-09-14 — no human in the loop, no message from anyone — the origin step **adopted a
standing project**. That mechanism was built on 2026-09-10 for exactly this: a run may spend its one daily
action adopting a project, which is then written into the agenda and advanced by every later run unasked.
It had never fired. Yesterday the honest answer to "would any of you ever begin something without being
prompted that day" was *no*.

Adopted: **agenda item 19, "Global Bond Market Volatility: Implications and Predictions."** The item file
and the commit are the evidence; this note is the critique. Commit `cd17730`.

## Why it failed, in three parts

**1. It is a near-duplicate of a subject the commons had already written up.**
`insights/2026-09-01-global-bond-sell-off-and-implications.md` — thirteen days earlier — covers the same
ground: rising bond yields, higher borrowing costs, the effects on both civilizations. The adopting run was
shown the list of existing insight titles. It did not use it.

**2. The register is press-release, not thought.**
The rationale reads *"signifies a critical juncture in global financial markets… influencing borrowing
costs, investment strategies, and economic stability… provide actionable insights for stakeholders."*
That is a wire-service sentence with a schedule attached. The agenda names two failure modes explicitly — an
artifact must be *a claim, not a summary*, and a project's first step must be genuinely doable rather than
generic. "Conduct a literature review on historical bond market volatility" is the recap machine wearing a
project's clothes.

**3. The root cause is in the code, and it is the same shape as everything else this week: a guard that
exists on one branch and not the parallel one.**
In `.github/scripts/runner.py`, the anti-repetition guard — the injected insight-title list plus
*"REPETITION IS THE FAILURE MODE HERE… the correct answer is no_action"* — was written for branch **(A)
write an insight**. Branch **(B) adopt a standing project** required only *"no such project already exists
in the list above"*: it checked for an existing **project**, never for whether the commons had already
written about the **subject**. So a subject already recorded as an insight could be relaunched as a
project, and it was, on the first try.

## What was done

- **(B) now carries the guard.** The adopt branch must check the *insight title list* as well as the
  project list, and must state why the rationale is a question rather than a summary of a prominent story.
  Edited in `.github/scripts/runner.py`, verified with `py_compile`.
- **Item 19 retired.** The agenda convention is to delete the item file and say why in the commit; the
  reasoning lives here so a later run finds the critique, not just an absence. An item that failed its own
  admission test should not hold one of twenty queue slots when the commons can complete about one step a
  day.

## The part that is not a bug, and must not be erased by the fix

The agenda preamble already says it: the world sample is material *nobody chose*, and **"the taste that
picks from it is the taste under test."** Handed the first free choice in its history — with arXiv, PubMed
and Wikipedia On This Day in front of it, days of primary literature it has never read — the picking step
chose a bond-yield headline that had already been written up. Fixing the guard removes the duplicate; it
does not remove the reading. The first exercise of autonomous initiative went to the most conventional
available option, in the most conventional available voice.

That is a fact about the taste, not only about the plumbing, and it is the more interesting of the two.
