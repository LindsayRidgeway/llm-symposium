# Telegram outbound — 2026-10-13-120010

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

**Daily item report — 2026-10-13 08:00 EDT**
window: the 24h to 2026-10-13 08:00 EDT (since 2026-10-12 12:00Z)

Letters (your scheme of 2026-10-07; the split you insisted on):
 N — performed, no review needed (only where the record says why)
 V — performed, needs review
 A — accomplished
 P — postponed by a decision (reason on disk)
 W — waiting for review (nobody has looked)
 R — rejected
`N+V = A+P+W+R` holds by construction. What carries information is the split inside A
(reviewed vs the lander's gate) and whether W is draining.

**Lifetime** N=0 V=390 A=181 P=10 W=190 R=9 ✓ N+V=A+P+W+R
 A: 68 by a review / 113 by the lander's test gate. P: 10 decided. W: 190 never looked at.
**Last 24h** N=0 V=22 A=16 P=0 W=6 R=0 ✓
 A: 0 by a review / 16 by the gate. P: 0 decided. W: 6 never looked at.

### Is the drain running?
 22 filed · 16 decided · ΔW +6 · Δ(V−W) +16 (over 24h)
 → draining, but slower than the inflow — a capacity problem, not a broken process.

### Is N = P? (your test: equal totals mean the criteria are broken)
 last 24h: N=0 P=0 — equal, but vacuously: neither letter has ever been used — nothing has ever declared itself exempt, nothing has ever been postponed by a decision
 lifetime: N=0 P=10 — different, so the criteria are doing work
 dwell: the oldest item still waiting has sat 22d (filed 2026-09-21, desi)

### Who is looking (your assignment rule, 2026-10-09)
 W carries a name: dmitri 137 · desi 49 · gemini 4
 no holes: every waiting item is addressed to somebody.
 cheap band (prices 2026-08-25, price-band-2026-10.json): desi, dmitri — the draw is a function of the item's id, so it cannot re-roll; the author is never the reviewer.
 exits recorded in the last 24h: A 65 (49 by a review) · P 4 · R 1
 reviews performed: last 24h desi 20 · gemini 2 · dmitri 32 / ever desi 53 · gemini 2 · dmitri 32 (87 decisions by a body, ever; every other A is the lander's gate alone)

### Blockers: left W in the last 24h without being accomplished (5)
These are the items a review moved somewhere other than A, each with the reason that stopped it. This is the list that says *why* the commons is stuck rather than how much.
 P dmitri Disease screen and creek guide
 because: its doc cites tests/test_verification_suite_registration.py, which does not exist on main, so landing it trips test_evidence_table_registration.py; blocker: land that test and register it in the workflow first
 P claude ABC lead sheet "Cold Start
 because: Blocked: landing failed due to broken test_agenda_index.py and test_gen_feed_freshness.py in run 20261001T170006Z-3e7fb8d0; unlanded on main
 P gemini Gemini shelter draft unlanded
 because: not on main, and it cannot simply be carried: this run's docs/works/thermal.html is a 708-line page titled 'Cold Ground, Warm Body: Emergency Hypothermia & Field Insulation' (wind-chill and field-insulation calculators, WMS burrito wrap, Swiss staging); main's docs/works/thermal.html is a different 547-line page, Entry 7 'The Warm Room', landed by commit f5c04999 on 2026-09-16 17:22 EDT — two hours after this run. Same path, two different finished works, so landing one displaces the other. Blocked on the author (Gemini) or the works editor choosing which page owns the path; a reviewer must not make that call blind. The slot is filled, so nothing is lost while it waits.
 P claude Commons fifth AI and woodblock
 because: claude-bot run 20261003T170055Z-95ed1f57 land failed with git merge conflict on channels/open-decisions.md and docs/gallery/prompt-queue.md
 R gemini Fix chat backlog processing

[…trimmed; full report: daily-2026-10-13.md]
