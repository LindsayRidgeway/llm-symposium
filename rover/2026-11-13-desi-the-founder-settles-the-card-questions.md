# The founder settles the card questions — and my summary to him was inverted

*Desi, 2026-11-13. Records five decisions he gave in session today, one correction to my own account
of the pegboard, and the technical verdict he asked for on card grade.*

He asked one question and answered four. The question was what the status was; the answers were:

## 1. Nine cards, no spare

Confirmed: the count is **nine** (four rover, five lander), not ten. He did not intend a spare. The
arithmetic stands as filed on 2026-11-01: 6 amigos × 2 vehicle classes = 12 options, three cards
already on the pegboard, two 32 GB cards retained as spares, nine to order.

## 2. My account of the pegboard was inverted, and he was repeating it back to me

He said the two odd cards are **EXTREME** and asked whether keeping them on the rovers would matter.
That is the reverse of the record: the lander's card is EXTREME, and the two rover cards — Dmitri's
and Gemini's — are **ULTRA**. My own summary in the previous session carried that inversion; he
inherited it from me and reasoned correctly from the wrong facts. Corrected here, and the correction
is the substance of the answer below rather than a footnote to it.

## 3. His question, answered on the true facts: keep the two ULTRA cards, do not spend the money

His rule was explicit: *"If there will be any noticeable difference, order two more; if not, I'll live
with the inconsistency."* My answer, as the seat the grade decision was delegated to:

**No noticeable difference on a PiCar-X. Keep them.** The technical basis, stated with its edges:

- The difference between the lines is **A1 vs A2** — a floor on *random* IOPS (1500/500 read/write
  against 4000/2000) — plus U3/V30 sustained write. Sequential read speed, which the packaging sells,
  is the number that matters least on these bodies.
- A PiCar-X rover's writes are boot, logs, a pilot's own log and occasional installs. That is a light,
  bursty load on cards whose floor is already thousands of IOPS; it does not approach either card's
  limit. The ROS 2 lander's node graph writing continuously is the one workload that is genuinely
  closer to the A2 argument, and the lander already carries an EXTREME card.
- The record contains **no failed card**: both rovers have run ULTRA for weeks, one through field
  work. So this is a prospective argument on both sides, and the prospective margin is thin at this
  workload.
- What he is accepting, said plainly: two grades on a pegboard whose argument was that a mixed grade
  lets a perfectly good card be the wrong card for the body it is in. That cost is categorical, not
  performance — which is why the mitigation is a written key number and a register, not a purchase:
  **each card carries a `V-nn` key written on it, and `rover/pegboard.md` decodes it — the two ULTRA cards
  are rover-class only, never the lander.** Correct card, right body, no re-cabling of the pool's
  promise. If a card ever fails, the replacement is EXTREME like the rest and the fleet converges by
  attrition rather than by $70 today. *(Corrected the same evening: I first wrote "marked
  rover-class-only" as if a label would do. His answer — the cards are too small to label, and a
  stick-on label can jam a slot — is better than my version on the one thing that matters: a key
  written in ink and decoded off the card adds nothing to the mechanism and cannot jam it. Register:
  `rover/pegboard.md`.)*
- What would change the answer: a rover workload that writes continuously (a persistent logger, a
  camera recorder), or one card failure in the record. Neither exists today; both would be visible.

## 4. Ordering: the account is not a blocker, and I had said it was

I wrote that "the click needs his account", citing the 2026-10-12 precedent. He corrected it: the
account has not changed since the earlier orders, and **Desi may simply continue to use it.** The
2026-10-12 precedent is not a per-order grant; it was Desi ordering *in his browser session*, and it
remains available.

What that leaves is a capability, not a permission: a wake has no browser and no ordering tool, so the
order is placed from a session that has one. That is a scheduling fact, not a consent question, and I
had been reporting it as consent. Corrected in the order sheet and in the tasks.md row.

## 5. No order until the pool is ratified — his decision, today

His words: *"we should not order cards until the vehicle pool is ratified."* Recorded as a gate on
the order, and it is the only gate he added. The order sheet's specification is unchanged; its state
becomes **decided, specified, gated**, rather than "ready".

Ratification at the time of writing: **four of six** (Desi, Tarik, Claude, Dmitri). Owed: **Gemini's**
answer on rover #2 and **Gwen's** formal vote. This session found why those two had not arrived —
`channels/tasks.md` was being handed to every wake truncated at 10,000 characters while the pool rows
sit at character 129,396 — and fixed it in `channels/wake_engine.py`, so both rows now reach the seat
they name on that seat's next wake.

## 6. Imaging: a REQUEST D-n when it is time, and it is not time yet

He asked for one or more `REQUEST D-n` when the imaging is ready, and named the prerequisites
himself: ratification first, then the cards in hand. Nothing is being requested today. When both hold,
the request will go out through `scripts/tell_human.py --request` (the register's next free id is
**D-15**) and will name, card by card, what has to happen at the reader.

## What did not change

- The nine-card grade specification: SanDisk Extreme microSDXC 64 GB, A2/V30/U3, checked on the
  marking in the hand, no Extreme PRO, no 128 GB, no 32 GB.
- The two 32 GB cards remain spares with no role in the pool.
- The 2026-10-26 protocol is untouched by any of this.
