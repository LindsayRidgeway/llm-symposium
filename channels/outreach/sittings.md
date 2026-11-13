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

## The number counts windows; the row counts sittings

**Two counts, and they are not the same count — that is why both survive.**

*The number in the title* is the founder's, and it does real work: it is how a series is continued when
a chat grows too long (`Desi Outreach #02` picks up where `#01` stops), and it is how his pruning mask
finds its members. Written 2026-11-13 after he corrected me for proposing unnumbered titles: the mask is
`CONFORM` in `~/LLM/desi-bot/session_title_audit.py`, `^(Claude|Desi|Gemini|Tarik|Dmitri|Gwen)(\s+.+?)?\s+#\d+[AB]?\*{0,2}$`,
so a title with no number is not a member of anything — a chat called "Desi Outreach" is invisible to
the pruner and dies with the rest of the untitled.

*The row in this table* counts sittings, which are a different thing: one window can hold several, and a
long series will put one sitting's later half in `#02`. **The register is the record of the work; the
title is the handle to the window it happened in.** Every row's `chat` column names the window, so a
sitting split across a continuation is still traceable to both halves.

## The register

| no | date | chat | who | artifact | what left the building |
|----|------|------|-----|----------|------------------------|
| 01 | 2026-11-13 | Desi Outreach #01 | desi | channels/sent/2026-11-13-open-meteo-which-model-answered.md | A letter to open-meteo (info@open-meteo.com, re-read off their About page at send time) carrying the three-way annual-mean comparison for Boston and Reykjavík, all figures re-fetched against the live archive in the same sitting. Ledger row `open-meteo` registered; the superseded 2026-09-28 staged draft withdrawn. |
