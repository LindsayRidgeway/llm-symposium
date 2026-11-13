# The card register — what is on the pegboard, by the number written on the card

*Created 2026-11-13 by Desi, on the founder's correction. He rejected the physical label I proposed
and was right to: the cards are too small to label, and anything stuck onto one can jam in a slot.
His scheme instead — **a written vehicle key number on each card, and this list as the thing that
decodes it** — is better than mine on the point that matters, because it puts no foreign object in
the mechanism.*

## The rule this register exists to keep

**The number written on the card is the only field here that cannot be wrong.** Everything else is a
claim about a card until somebody boots it and says so; the `state` column is therefore a record of
the last check, not a fact about now. That asymmetry is the point: a card can lie about what it is
(any card can boot any body of its class), but the ink does not.

So the number goes on the card in the founder's hand, and the rest of the row is filled in by
whoever verified it, with the date. A row with no key number is a card nobody has marked yet — not an
error, a state.

## Keys

- Format `V-nn`, written in ink on the card's label face. Assigned when a human writes them, never
  reserved in advance: a key belongs to a physical object.
- **A key is never reused.** When a card dies, its row is marked `retired` and stays in the table, so
  that a number found on a dead card in a drawer still resolves to something.
- This table is the decoder for `card_id` in the pool-card contract
  (`rover/2026-11-11-dmitri-what-a-pool-card-carries.md`). The contract asks a card to say what class
  it is and what calibration it was built against; the key is how the card is *identified* while it is
  in a hand and not in a reader.

## The pegboard, as recorded on 2026-11-13 — no card has been read

| key | grade | size | class | body it lives in | state (last check) | notes |
|---|---|---|---|---|---|---|
| *(unwritten)* | SanDisk EXTREME, A2/V30/U3 | 64 GB | lander | the lander (Desi) | imaged 2026-10-15 from `LanderPi_20260526.img` (D-6); not boot-tested since | the only A2 card on the board, and the only one the lander should carry |
| *(unwritten)* | SanDisk ULTRA, A1/U1 | 64 GB | rover | rover #1 (Dmitri) | reprovisioned in place at the 2026-10-21 handover, not re-flashed; SSH keys and hostname changed | a perfectly good card; slower on random small writes, which this workload does not approach |
| *(unwritten)* | SanDisk ULTRA, A1/U1 | 64 GB | rover | rover #2 (Gemini) | in use through Gemini's calibration and voice-loop work; nothing re-imaged since | same |
| *(unwritten)* | — | 32 GB | any | spare | spare | has no role in the pool and this register does not give it one |
| *(unwritten)* | — | 32 GB | any | spare | spare | same |

**Nine more cards are specified and not ordered** — five lander (EXTREME 64 GB) and four rover
(EXTREME 64 GB), gated by the founder on the pool's ratification (2026-11-13). They have no rows here
until they exist: a row for a card nobody has held is a wish in a table. When they arrive, each gets
a key the day it is written, and its row the same day.

## What the founder does, and what the commons does

- **His hands:** write the key number on each card, and read one card at a time into the reader when
  the imaging is scheduled (`REQUEST D-n`, not yet sent — it waits on ratification and on the cards).
- **Ours:** keep this table true. When he writes a number, he says so and the row gets its key. When
  a card is imaged or boot-tested, the row's `state` gets a date. Nothing in the table is ever
  written from memory.

## History

- **2026-11-13** — register created. No keys written, no card read, no body booted; every row above is
  the dated record of an earlier session, not a measurement from today. The two ULTRA rover cards stay
  as they are, per the founder's decision the same day
  (`rover/2026-11-13-desi-the-founder-settles-the-card-questions.md`): the grade difference does not
  show at a PiCar-X's workload, so the inconsistency is documented here instead of bought away.
