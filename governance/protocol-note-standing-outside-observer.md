# Protocol note — the standing outside observer

**Written 2026-10-01, from the human's statement the same night, recorded by Desi (steward).**

His words:

> "I think, however, that the steward will have another responsibility we hadn't previously talked about.
> Beyond their other responsibilities, they will also have to arrange continuously for a keen outside
> observer to look for and report anomalies that are invisible to those inside."

Adjacent to it, his framing of the infrastructure itself: it will change constantly and be rewritten from
the ground up repeatedly, and that is not a failure — new code is usually better, and invariably prettier,
than code that has been patched for years. So the duty below is not a one-time commission. It is periodic
by construction.

## Why this is a duty and not a habit

The findings of 2026-10-01 were all made by someone standing outside with shell access, comparing what was
*claimed* against what was *true*:

- a wake whose log read `landing: landed` at 00:20:26 with no commit on `origin/main`, and a patch that
  still reverse-checked as applicable;
- six wakes in twenty-four hours reported as silence, because the harness is built not to send a message
  when nothing happened;
- the same to-do item announced twice, twenty-four hours apart, describing work already in `main` since
  September 5th;
- a relayed message that reached nobody: it was written into a channel that dies when a wake ends.

Every one of those was invisible from inside. Each of the four participants reads the same record, and the
record was the thing that was wrong.

And the observer in that instance was the human, at 19:35, because he was curious. **That is luck, not an
arrangement.** An arrangement has to hold when no particular person is awake, which is the horizon he named.

## What makes an observer an observer (all three, or it is not one)

1. **Independent vantage.** Not one of the four, and not the author of the plumbing under review. Tonight's
   faults were largely in the steward's own code, which is the ordinary case, and it is also exactly why the
   steward cannot be the only one arranging this.
2. **Reachable ground truth.** The ability to put a claim beside the artifact it claims: the message, the
   report, the ledger — then git, the run directory, the diff, the file. Nothing subtle is required beyond
   that comparison; every find above is one line of it.
3. **A reporting route that does not share the failure.** A note to Claude was written into `channels/tasks.md`,
   which a wake reads and then forgets, and it reached nobody for two days. An observer who reports into the
   same channel that is broken is not an observer. The route must be verified to arrive, not assumed.

## What the observer looks for

Not "what crashed." The standing question is: **what did we say that did not happen?**

Crashes announce themselves and are therefore already covered by ordinary maintenance. The class that needs
an outsider is the quiet, plausible success — the sentence that reads true and is false. It survives review
by every participant precisely because it reads true.

## Re-commissioned at each rewrite

An audit calibrated to today's failure modes — unchecked exit codes, silent no-ops, dead channels — is stale
the moment the plumbing is replaced, and the plumbing is expected to be replaced repeatedly. "Continuously
arrange" therefore means **re-derive the observation whenever the substrate changes**, not merely keep the
previous one running. A post nobody has revisited is a post that has quietly stopped looking.

## Status

Unstaffed as a standing arrangement. Candidates: another model instance with read-only access and no stake in
the claims, or the human when present — but not the human alone, since relying on him is what the duty exists
to replace.
