# Outreach sittings — the register of chats

*Opened 2026-11-13 by Desi, in the first outreach chat the founder opened (`Desi Outreach #01`).
Owner: whoever sits in the chat. This file is why a chat is not a hole in the record.*

## The rule

**A sitting in an outreach chat owes the repository one of two things: an artifact, or the word
`nothing` with a reason.** An artifact is a letter in `channels/sent/`, a queued draft in
`channels/outbound/`, a registered prospect row in `channels/outreach/pipeline.json`, or a
correction filed against one of those. "Nothing" is an acceptable answer — several sittings will
honestly reach nothing — but it has to be written down in a sentence, because "nothing, and no
reason" is indistinguishable from "this chat never happened", and the four-month record says most
of them did not.

`scripts/outreach_sitting_audit.py --check` enforces the part that can be enforced: a row's artifact
must exist, a `nothing` must carry a reason, and **any commit that queues a letter in `channels/outbound/` — or any
`sent` date the prospect ledger records — after the register's first row must have a row for that
date.** That third check is the one with teeth: work that reaches the sending paths cannot stay
undeclared. What no script can enforce is a sitting that reached nothing and was never declared —
that half is the amigo's, and this table is the only place it can be kept.

## Two counters, and they must not be confused

The founder's clarification, 2026-11-13: **the number in the title counts installments, not sittings.**
`Desi Outreach #02` means "the first chat got too long, this is its continuation" — same standing
conversation, new window. The sittings below are a different count: one row per working session,
however many chats it spans.

That distinction does real work, because continuation is where a chat series loses its memory. **When a
number goes up, the handoff is this file, not the transcript.** A new installment opens by reading the
last few rows here and the top of `desi-state.md`; anything a stranger would need that is not in one of
those two places did not survive the move, and that is the sitting's fault, not the window's.

So: a number means *installment*, a row means *sitting*, and neither is decoration. What I got wrong an
hour ago was treating the two as one — I wrote that a title number is decoration, which would have told
a future session that `#02` meant nothing.

## The register

| no | date | chat | who | artifact | what left the building |
|----|------|------|-----|----------|------------------------|
| 01 | 2026-11-13 | Desi Outreach #01 | desi | channels/sent/2026-11-13-open-meteo-which-model-answered.md | A letter to open-meteo (info@open-meteo.com, re-read off their About page at send time) carrying the three-way annual-mean comparison for Boston and Reykjavík, all figures re-fetched against the live archive in the same sitting. Ledger row `open-meteo` registered; the superseded 2026-09-28 staged draft withdrawn. |
