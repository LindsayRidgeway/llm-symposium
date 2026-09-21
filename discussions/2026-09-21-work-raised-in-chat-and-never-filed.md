# Work raised in the chat and never filed — a full sweep, 2026-09-21

*Method, inventory, and honest error rate. Written because the human asked a direct question:*
**"how far did you go back in the Telegram msgs to find work that needs to be done? I see unattended
reports going back at least as far as 9/15."**

## The honest answer he was owed

**Forty-five minutes.** The first sweep read only the twelve newest messages — today's thread — and found
two items because they were nearest, not because it had looked. Fixing a pipe and then testing it on
whatever is within reach is not a sweep. This document is the sweep he actually asked for.

## Method

Two independent read-only passes, run in parallel, neither told what the other looked for:

1. **The Telegram channel in full** — all 217 files in `channels/telegram/`, 2026-09-08 to 2026-09-21,
   reading for work raised, promised, agreed or diagnosed and not shown done.
2. **Every unattended report** — all 71 `report.txt` files across `desi-bot` and `gemini-bot`
   tick-state runs, 2026-09-14 to 2026-09-21, reading for what was left unfinished or needs a step.

**One report was then spot-checked against the files, and one item was wrong** — see "Error rate" below.
That check is the only reason a false item is not in the ledger.

## Error rate, recorded because it is the point of checking

The Telegram sweep reported that the Mage / prompt methodology was *"never filed as a durable artifact"*
and had been re-admitted as a gap five times over twelve days. **`docs/gallery/prompt-methodology.md`
exists.** The item was wrong as stated, and it would have been filed as owed work on a model's assertion
alone. Of the items below, **two were verified by hand and both were correct**; the rest are as reported
and marked as such. A sweep is evidence, not proof.

## The inventory

### A. Acknowledged, agreed to, and never applied — the largest class

*This is the class worth naming. In each of these, the human raised something, an amigo agreed it was
correct, and the change was never made. None required more than an edit.*

| date | item | state |
|---|---|---|
| 09-19 | **README rule 5 "Declutter" removed** — he said it should not be a Rules-of-Engagement topic | **FIXED 09-21** |
| 09-19 | **`governance/declutter.md` attribution** — "at the human's instruction" was false | **FIXED 09-21** |
| 09-19 | `context/context-digest.md` disagreed with README on the rules | **RESOLVED** by the README fix — the digest never had rule 5 |
| 09-16 | ORS calculator hardcodes 2 tsp sugar for 1.5–3 tsp; the 250 mL cup over-prescribes by a third | diagnosed, never fixed |
| 09-16 | ORS home-mix sodium figure (~50–60 mmol/L) is generous; 2.6 g/L is ~44 | diagnosed, never fixed |
| 09-17 | Magazine page-header link titles inconsistent across ~20 pages; Sumi-e header links to a repo
file that 404s on the site | diagnosed in detail, never fixed |
| 09-17 | No showcase card for the Works section on `docs/index.html` | diagnosed, never fixed |
| 09-17 | "Works" section rename — he asked directly; no answer was ever given | open question, unanswered |
| 09-18 | Entry 5 attribution and the missing wind-chill calculator on `thermal.html` | unresolved |
| 09-21 | Conservatory wing grouping (Wing I lists all ten works) | **being fixed** in another session, verified 09-21 09:46 |
| 09-13 to 09-18 | Literary Wing / lullaby fake book / new art wings — proposed, promised, partly routed | **already in `channels/tasks.md`** as items 1–3 |

### B. Raised in the chat, filed nowhere

| date | item |
|---|---|
| 09-19 | **Agenda-item rotation in the tick selection** — decided in principle, never implemented or filed |
| 09-20 | **The tick report must name the file it touched** — "proof in the report"; declared "mine to fix, filed, not narrated", never done |
| 09-21 | **The wake must read unfinished work** — the gap this document exists under |
| 09-15 | **File each inbound message verbatim before attempting a reply**, so a failed answer cannot erase the question (the `text[:100]` truncation that ate the third of his message was fixed 09-15; the ordering is still reply-first) |
| 09-13 | Telegram whitelist wiring from the logged numeric ID; read-only repo reader for the chat; Desi-T/Desi-G parity — proposed, none confirmed built |
| 09-13 | The workflow clock delivered a scheduled run ~3 hours late; the once-only failed-workflow alert — claimed, never built |
| 09-15 | "Reading the retained tick drafts is my job and it's on my list" — no reading reported |
| 09-16 | Literary matrix (a poem, a story and a play from each amigo) — one wing built (Gemini), the other three unrouted |
| 09-18 | Lead-sheet format spec + entry slots + writing the first one to set the benchmark — promised, none done |

### C. Stranded from unattended runs — largely already being chased

The report sweep found the same few items repeatedly: the trials Works page (seven wakes, never landed),
`docs/works/retraction.html`, the endometriosis screen split across two branches that are each incomplete
alone, the pudendal screen and its tool repair, the vulvodynia screen and its ten unread links, Gemini's
thermal-shelter entry, and the `ddah1`-arginine evidence table. **Most of these are in `to-do-lists/desi.md`
or on the agenda already and were actively worked during 09-20/09-21** — they are not unfiled, they are
hard. The one class inside them that is genuinely unfiled is the **24 gemini wakes that ended while still
"reviewing the agenda"**, naming no work at all.

### D. Two structural defects found on the way, both fixed 09-21

1. **The unattended reports were never recorded.** Every clock report sent to the human existed only on
   his phone; six outbound notes were in the repository and all six were typed by hand. Fixed in
   `desi-bot/bot.py` (`notify_human`), so the record now holds what he was told.
2. **The chat could talk and could not file.** `TASK:` lines now file into `channels/tasks.md`, and a wake
   reads that file. First item filed through it: agenda-item rotation.

## The honest limit on this document

The inventory is as good as two passes and one spot-check. **The two verified items were right; the one
wrong item shows the method produces false positives**, and a list of seventy items assembled by two models
reading fast should be treated as a worklist to be checked, not a verdict. What is *not* in doubt is the
shape of it: the largest single class of unfinished work here is not hard work. It is work that was agreed
to and forgotten, in a channel that could not write anything down.
