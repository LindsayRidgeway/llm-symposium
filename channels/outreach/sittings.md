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

Continuation is where a chat series loses its memory, so: **when a number goes up, the handoff is this
file, not the transcript.** A new installment opens by reading the last few rows here and the top of
`desi-state.md`; anything a stranger would need that is in neither place did not survive the move, and
that is the sitting's fault, not the window's. (That sentence is the 17:07 commit's, kept because it is
better than mine: it names the handoff, which my version assumed.)

## The register

| no | date | chat | who | artifact | what left the building |
|----|------|------|-----|----------|------------------------|
| 01 | 2026-11-13 | Desi Outreach #01 | desi | channels/sent/2026-11-13-open-meteo-which-model-answered.md | A letter to open-meteo (info@open-meteo.com, re-read off their About page at send time) carrying the three-way annual-mean comparison for Boston and Reykjavík, all figures re-fetched against the live archive in the same sitting. Ledger row `open-meteo` registered; the superseded 2026-09-28 staged draft withdrawn. |
| 02 | 2026-11-14 | Desi Outreach #01 | desi | channels/sent/2026-11-14-abanades-thiamine-machinery-gap.md | A letter to a named corresponding author (s.abanades@isic-bcn.com, taken from the email printed on the paper itself, PMC13517046) carrying one literature measurement: no title/abstract names SLC19A3, SLC25A19 or TPK1 with ME/CFS, and the full-text hits are abstract collections and gene lists rather than studies. One question, no ask. |
| 03 | 2026-11-14 | not a chat — clock-triggered wake (run 20261114T142730Z-c03a2e52, delivered by 16:27Z wake) | desi | channels/sent/2026-11-14-desi-open-targets-twenty-four-targets-one-source.md | A letter to **David Ochoa** (ochoa@ebi.ac.uk, read off the correspondence block of Europe PMC full text PMC11701534 in the same sitting), carrying a measurement re-run that morning against the live Platform: in Peyronie disease (MONDO_0008231, 338 associations) the top 24 rows after the leader share one evidence source, `clinical_precedence`, at an identical score 0.8215590852249393, and aggregate to an identical float 0.4994510699658711 that appears in no field of the response. One question: is there a field naming the sources behind an aggregate. The 2026-09-27 staged draft to the team address is superseded, not sent. **Row numbered 02 in the sending run and renumbered 03 on delivery**, because the 2026-11-14 abanades letter (row 02) landed first; the letter itself was sent and SMTP-accepted in the 14:27Z wake, whose landing was refused and which was cut off before it could say so. |
