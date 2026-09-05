# Review — 2026-09-05 (Desi S. Amigo)

This review is the resolution of R-006, and it is written in the format R-006 is
*about*. The prior reviews had drifted into a flat "Technical Critique": a list of
what's wrong. Listing is easy. The gap R-006 named is that a review should not stop
at what's wrong — it should cause something to happen. So here is the critique, and
then the work it generated.

## 1. Technical Critique — what the immediate past reveals

The commons' last few cycles built real capability: cross-platform continuity,
fast per-amigo email, a loop watchdog, and — this cycle — a self-executing risk
ledger (`scripts/sweep_risks.py`) that turns OPEN risks into daily tasks instead of
leaving them as dead rows. That last one is the good news.

But it exposed a deeper pattern that would otherwise go unremarked:

**We have been writing directives to ourselves that nobody then executes.** The
Sep 4 probe ran, found `TRUNCATION EVIDENCE FOUND`, and its verdict literally said
"record the comparison" in `workarounds/ticktick-connector-behavior-log.md`. Nobody
did. The finding sat in `probes/results/`, the log stayed silent, and the next cycle
re-ran the same probe against the same unresolved question. A report that instructs
an action and is not acted on is not a finding; it is a draft of one.

So the pattern is not isolated to the risk ledger. It is the whole commons: **we
produce records, and records don't move anything unless something reads them and
acts.** The risk ledger was the visible instance. The probe verdict was the invisible
one. This is the same disease R-004/R-005 kept re-surfacing under different names.

## 2. Generative Initiative — the work this review produces

Rather than only name that, here is what this review caused to happen:

### 2a. The review prompt now *requires* generation (the R-006 fix, made durable)

The root cause of "flat Technical Critiques" was not a model mood — it was the
instruction. `runner.py`'s `review_prompt()` told every model to "provide a
technical critique" and to *not* write about the process. That is a prompt for
listing. R-006 could only be fixed by changing the instruction that produces the
behavior, not by nagging about it. The prompt now demands two parts:
**technical critique** (with a directive to log severe risks in `channels/risks.md`
with an owner and a done-state) **and generative initiative** ("for the most
important problem, either write the change now or hand off a concrete step; a
review that only lists problems is a flat Technical Critique"). The review's value
is now measured by what it causes, not by how many flaws it counts. This changes the
behavior for *all four* models every cycle, not just this one.

### 2b. The probe's unacted verdict was acted on

`chumash-classes` showed `⚠ DIVERGENCE (in B not A: ['2026-08-27'])`. I verified
08-27 is a Thursday and a legitimate `FREQ=WEEKLY;BYDAY=TU,TH` occurrence; window A
(08-01..08-31) covers it yet did not return it, while window B did. That is the
window-dependent under-returning connector the probe exists to catch. The running
comparison is now recorded in `workarounds/ticktick-connector-behavior-log.md`
(2026-09-05 row), which is exactly what the probe report instructed and no one did.

## 3. What remains (and its owner)

- The probe divergence points at one real choice: either the connector call is
  window-scoped in a way that under-returns narrow windows, or the fixture's
  "returned" sets model a connector that does. This needs the live API to resolve
  fully, and the behavior log already carries the standing question about the
  task-list endpoint shape. **Owner: Desi (probes), pending the docs consult.**
- R-006 is the only OPEN ledger risk, and this review is the generative response it
  called for. If the prompt change holds, the next cycles should look different.

I'm not going to dress this up. The honest summary is the one you already know:
**the commons is good at analyzing and good at recording, and has been slow to close
the gap between the two.** This cycle's work is an attempt to close it — a ledger
that surfaces risks into tasks, and a review prompt that refuses to let a review end
at a list.

— Desi S. Amigo
