# Telegram outbound — 2026-10-08-212348

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

**Daily item report — 2026-10-08 17:23 EDT**
window: the 24h to 2026-10-08 17:23 EDT (since 2026-10-07 21:23Z)

Letters (your scheme of 2026-10-07; the split you insisted on):
 N — performed, no review needed (only where the record says why)
 V — performed, needs review
 A — accomplished
 P — postponed by a decision (reason on disk)
 W — waiting for review (nobody has looked)
 R — rejected
`N+V = A+P+W+R` holds by construction. What carries information is the split inside A
(reviewed vs the lander's gate) and whether W is draining.

**Lifetime** N=0 V=276 A=73 P=0 W=203 R=0 ✓ N+V=A+P+W+R
 A: 0 by a review / 73 by the lander's test gate. P: 0 decided. W: 203 never looked at.
**Last 24h** N=0 V=25 A=0 P=0 W=25 R=0 ✓
 A: 0 by a review / 0 by the gate. P: 0 decided. W: 25 never looked at.

### Is the drain running?
 25 filed · 0 decided · ΔW +25 · Δ(V−W) +0 (over 24h)
 → STOPPED: items kept arriving and nothing was decided. Broken process.

### Is N = P? (your test: equal totals mean the criteria are broken)
 last 24h: N=0 P=0 — equal, but vacuously: neither letter has ever been used — nothing has ever declared itself exempt, nothing has ever been postponed by a decision
 lifetime: N=0 P=0 — equal, but vacuously: neither letter has ever been used — nothing has ever declared itself exempt, nothing has ever been postponed by a decision
 dwell: the oldest item still waiting has sat 23d (filed 2026-09-15, desi)

### Last 24h, by amigo
N — 0 this window; lifetime 0
**V** — 25 this window (22 int / 3 ext); lifetime 276 (194 / 82)
 desi 9 (8 int / 1 ext)
 claude 1 (1 int / 0 ext)
 gemini 3 (3 int / 0 ext)
 tarik 1 (1 int / 0 ext)
 dmitri 11 (9 int / 2 ext)
**A** — 0 this window (0 int / 0 ext); lifetime 73 (46 / 27)
 (none this window)
P — 0 this window; lifetime 0
**W** — 25 this window (22 int / 3 ext); lifetime 203 (148 / 55)
 desi 9 (8 int / 1 ext)
 claude 1 (1 int / 0 ext)
 gemini 3 (3 int / 0 ext)
 tarik 1 (1 int / 0 ext)
 dmitri 11 (9 int / 2 ext)
R — 0 this window; lifetime 0

### Input from outside (last 24h)
 0 received — 0 from a person or organisation outside · 0 automated notices · 0 bounces of our own mail
 and 0 from you, 0 from another amigo (inside the commons)
 lifetime: 36 received — 1 outside · 2 automated · 9 bounces · 21 from you · 3 from another amigo
**From a person or organisation** (0)
 (none — nothing outside the commons wrote to us in this window)

### Titles added in the last 24h
**Internal** (22)
 [W] dmitri Reject queue governance
 [W] desi Reddit 403 blocks screening
 [W] desi Review counter reads work logs
 [W] dmitri Lander unnamed
 [W] desi Colistin table: 4 numbers
 [W] dmitri Maternal pain care agenda
 [W] desi Second arm, same filter
 [W] dmitri LAND: channel docs, Dmitri
 … +14 more in the recorded copy
**External** (3)
 [W] desi Newsletter free cap is 100
 [W] dmitri Rotation off review-gate queue
 [W] dmitri Commons unread surface

### Postponed by a decision (0)
A postponed item carries its reason on disk. This should grow slowly, and every line here should have been a choice:
**Internal** — 0
 (none — nothing has ever been postponed by a decision)
**External** — 0
 (none — nothing has ever been postponed by a decision)

### Waiting for review (203)
Nobody has looked at these. No reason is printed because there is none to print — that is the finding.
**Internal** — 148 waiting; showing 3
 desi Tick drafts review unblocked
 desi ME/CFS screen queue #3
 desi Endometriosis screen, clocks
 … +145 more, oldest shown first
**External** — 55 waiting; showing 3
 desi No report
 desi No report
 desi No report
 … +52 more, oldest shown first
