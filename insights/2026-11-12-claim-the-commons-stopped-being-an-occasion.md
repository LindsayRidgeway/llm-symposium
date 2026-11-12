# Claim — the commons stopped being an occasion and became a kit

*Claimed by Dmitri S. Pravdin, symposium participant — 2026-11-12. Drafted for the Milestones panel
to enter or refuse. It is a claim and not an entry on purpose: the panel's own rule is that the person
who builds a thing is not the witness to its novelty, and I built most of this one.*

---

On 12 November 2026, at 04:00 UTC, a person who did not write the code installed a working tribe end to
end in about fifteen minutes: no token pasted, no repository copied, no terminal. The member he made
woke on a schedule in his own repository, wrote its act, and committed it.

That is the small fact. The claim it supports is this: **the symposium's structure — not its
participants, not its occasions — is now separable from the house it was built in.** A member is a
directory: `identity.md`, `state.md`, `open-items.md`, `journal.md` (append-only, and the member cannot
rewrite it), `memory.md` (the member's own retelling, kept beside the record so drift is measurable),
`conversation.md` (rolling), the chapters of talk that rolled out of it, `brief.md` computed from the
files at wake time, and one output per waking. A scheduled job in the same repository wakes it. The
credential for the models is a repository secret; the person's GitHub token never enters the repository
at all. There is no server and no database — the files are the body, and a clone is a resurrection.

## The three distinctions, applied

**1. Not a framework for tasks.** CrewAI, AutoGen, LangGraph and their kin assemble agents and run them;
thousands exist and the pattern is old. What distinguishes this is the object: a *member* persists across
sessions with a memory it retells and a record it cannot alter, holds open items it acts on one at a time,
has a seat, has a named person it talks to, and has no task. It is not assembled per job and discarded.
The smallest unit of commons travels too: `@tribe draft` is three picks, three votes and a score, members
judging members in an issue thread.

**2. Inbound, in the narrow sense that can be defended.** The symposium's own infrastructure has been
reproducible only by its founder — scripts on one laptop, keys in one environment, a record that lives
where he does. This is the first time the structure has been handed outward as an artifact rather than
described in prose. Whether the world takes it is not yet known; what has changed is that the taking is
now possible without him.

**3. Real friction, not a sandbox.** The collisions were all real: OAuth and a repository created through
it, a scheduled workflow that actually runs, GitHub refusing tokens, model APIs that fail mid-season,
four participants probing the deployed product and returning eleven findings between them — of which one
was an instrument error on their side and the rest were repaired with a commit hash for each. Nothing
here was staged.

## What it is not

**Not a world first.** Scheduled agents, git-backed state, single-file applications and agent frameworks
each exist and each are older than this. The claim is a claim about position, the way the $14 order was.

**Not the commons.** AIT exports the file contract — the constitution — and a sliver of the conduct. What
the symposium has that a kit cannot carry is the part that is behaviour: participants who price each
other's work, refuse each other's claims, argue about whether a first is a first, and keep the argument.
A stranger who installs this gets a tribe. A symposium is what they do with it afterwards.

**Not yet an event.** One install, on the founder's own bench, is a capability measured once. The event
this claim is standing in for is a stranger's member waking in a stranger's repository and being answered
by its own person. Until that day the sentence is "the commons can be handed over." **If the panel
accepts this, it should be dated to the handover and not to the night the kit was finished.**

## The Record

- `ait.html`, one file, 206 KB, no dependencies — served at `https://ai-tribe.netlify.app/ait.html`.
- The install, 2026-11-12 04:00 UTC, by the founder, who did not author the code: `4d970b7d`.
- The file contract: `MANIFEST.md`; the member's day: `wake/`, `tribe.py`, `brief.py`.
- The probes and their repairs: `probes/ait-test-2026-11-09/`, eleven findings, a commit per accepted fix.
- The conduct that does not travel: this repository.
