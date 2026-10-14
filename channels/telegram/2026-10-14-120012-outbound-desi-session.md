# Telegram outbound — 2026-10-14-120012

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

**Daily item report — 2026-10-14 08:00 EDT**
window: the 24h to 2026-10-14 08:00 EDT (since 2026-10-13 12:00Z)

Letters (your scheme of 2026-10-07; the split you insisted on):
 N — performed, no review needed (only where the record says why)
 V — performed, needs review
 A — accomplished
 P — postponed by a decision (reason on disk)
 W — waiting for review (nobody has looked)
 R — rejected
`N+V = A+P+W+R` holds by construction. What carries information is the split inside A
(reviewed vs the lander's gate) and whether W is draining.

**Lifetime** N=0 V=413 A=279 P=93 W=26 R=15 ✓ N+V=A+P+W+R
 A: 150 by a review / 129 by the lander's test gate. P: 93 decided. W: 26 never looked at.
**Last 24h** N=0 V=23 A=16 P=0 W=7 R=0 ✓
 A: 0 by a review / 16 by the gate. P: 0 decided. W: 7 never looked at.

### Is the drain running?
 23 filed · 16 decided · ΔW +7 · Δ(V−W) +16 (over 24h)
 → draining, but slower than the inflow — a capacity problem, not a broken process.

### Is N = P? (your test: equal totals mean the criteria are broken)
 last 24h: N=0 P=0 — equal, but vacuously: neither letter has ever been used — nothing has ever declared itself exempt, nothing has ever been postponed by a decision
 lifetime: N=0 P=93 — different, so the criteria are doing work
 dwell: the oldest item still waiting has sat 2d (filed 2026-10-11, gemini)

### Who is looking (your assignment rule, 2026-10-09)
 W carries a name: desi 25 · dmitri 1
 no holes: every waiting item is addressed to somebody.
 cheap band (prices 2026-08-25, price-band-2026-10.json): desi, dmitri — the draw is a function of the item's id, so it cannot re-roll; the author is never the reviewer.
 exits recorded in the last 24h: A 98 (82 by a review) · P 83 · R 6
 reviews performed: last 24h desi 30 · gemini 4 · dmitri 137 / ever desi 83 · gemini 6 · dmitri 169 (258 decisions by a body, ever; every other A is the lander's gate alone)

### Blockers: left W in the last 24h without being accomplished (89)
These are the items a review moved somewhere other than A, each with the reason that stopped it. This is the list that says *why* the commons is stuck rather than how much.
 P dmitri Read works pipeline and
 because: Substance landed: docs/index.html now reads 'The Five Amigos' throughout and lists dmitri. But the guard the run named, tests/test_site_roster.py, was never written (absent from every branch, not tracked, named nowhere), so the hand-maintained front page the run fixed is unguarded — the same unrun/unwritten-guard class this wake fixed elsewhere. Needs the guard written before closing.
 R dmitri Reject queue governance
 because: The run was cut off at its action cap with LAND '(to be named)' — it produced no artefact to review. The path it named, scripts/roster.py, never existed (untracked, referenced nowhere). The reject-queue governance it intended was delivered by run 20261009T024838Z-bbfc3dd2 (wording amended to 'Every amigo' in channels/reject-queue.md). Nothing to land; re-attempting this run id would be reconstructing work that does not exist.
 R claude Chose repertory over reject
 because: Run cut off during orientation; scratch patch unlanded and incomplete while main invention-d-minor.html is intact
 P desi Files never existed, not done
 because: delivery state: docs/fiction/nine-kilometres-of-glass.html is named but not on main — under the 2026-09-23 rule a missing path is work awaiting a closer, not work to redo
 P desi Fixed wrong sodium on
 because: delivery state: docs/fiction/the-friction-line.html is named but not on main — under the 2026-09-23 rule a missing path is work awaiting a closer, not work to redo
 P desi Ledger stopped refiling

[…trimmed; full report: daily-2026-10-14.md]
