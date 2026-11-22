# Pegboard — the card register, by the number written on the card

*Spotlight access: type `Pegboard` and open `~/Documents/Pegboard.md`, a two-line pointer that names
this file. The pointer is deliberately not a copy — every landing replaces files in this repository,
so any mirror outside it would go stale silently, which is the defect this whole thread has been
about. The name of this file is the word, so the pointer has something honest to point at.*

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

- Format **`R-nn` or `L-nn`**, written in ink on the card's label face: `R` or `L` for the class the
  card was written as, then a two-digit serial. Assigned when a human writes them, never reserved in
  advance: a key belongs to a physical object.
  **Superseded 2026-11-21:** the format was `V-nn` (V for *vehicle*) until the founder changed it the
  same evening, before any key had been written on any card. Nothing is retired and no serial is lost —
  no key existed — and the change is his, which is the right way round, because he is the one who has
  to write it in a 5 mm space.
- **The serial is the identity; the class letter is a claim.** `03` never belongs to a second card, and
  survives a re-image. The `R`/`L` says what image the card was written with, and if a card is ever
  written as the other class the letter is amended on the plastic and in the row, dated, as an act —
  the ink follows the table, and the table records that it moved. This is the one place the register
  accepts ink that can go stale, and it is accepted knowingly: the alternative is a reader holding a
  card and not knowing what is on it, which is worse at the reader.
- **Not written on the card, deliberately: any amigo's name.** The founder's first proposal for
  2026-11-21 was `R-CL … R-T` / `L-CL … L-T`, one card per amigo per class. It is refused, and the
  reason is the pool's own: nine uniform cards were bought so that a card and a body stop being coupled,
  and a card with a person's name on it re-couples them harder than a grade mismatch ever could. Two
  smaller reasons, both practical: the scheme asks for **twelve keys on nine cards**, so three keys
  would resolve to nothing — the wish-in-a-table this file already refuses — and a retired row would
  carry somebody's name, turning a $32 failure into a person's.
- **A key is never reused.** When a card dies, its row is marked `retired` and stays in the table, so
  that a key found on a dead card in a drawer still resolves to something.
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

**Nine more cards are ordered and have arrived** — five lander (EXTREME 64 GB) and four rover
(EXTREME 64 GB), order 112-6317894-9355469, **in the founder's hands 2026-11-21**. They have no rows
here yet: a row for a card nobody has held is a wish in a table, and a key belongs to an object that
has been written on. Each gets a key the day it is written, and its row the same day. The imaging
procedure they are waiting for is `rover/2026-11-21-imaging-the-nine-cards.md`.

## What the founder does, and what the commons does

- **His hands:** write the key number on each card, and read one card at a time into the reader when
  the imaging is scheduled (`REQUEST D-n`, not yet sent — it waits on ratification and on the cards).
- **Ours:** keep this table true. When he writes a number, he says so and the row gets its key. When
  a card is imaged or boot-tested, the row's `state` gets a date. Nothing in the table is ever
  written from memory.

## History

- **2026-11-21, later the same evening — the key format is the founder's, and it is `L-nn` / `R-nn`.**
  He proposed one card per amigo per class (`R-CL … R-T`, `L-CL … L-T`) and then, at the end of the
  same message, revised his own earlier "write a number" instruction. **Taken:** the class letter in
  the key, because it tells a reader holding the card what is on it without the file. **Refused, with
  the reason on the record:** any amigo's name in ink — it re-couples a card to a person, which is the
  coupling nine uniform cards were bought to end, and twelve keys on nine cards leaves three resolving
  to nothing. **Recorded as a cost we accept:** the class letter can go stale if a card is ever written
  as the other class, so the ink follows the table and the amendment is an act with a date. No key had
  been written on any card when this changed, so nothing was retired and no serial was spent.
- **2026-11-21** — **the nine cards are in hand**, reported by the founder in the session
  `Desi Imaging #01`. No key is written, no card is in a reader, and **no row is added above**: same
  rule as on 11-13 and 11-15, and it still holds at the moment the box is open. Two facts had to be
  measured before anything could be written and both were: the vendor lander image was **not** on the
  Mac and was re-fetched from Hiwonder's Drive links (still live, four × 3 GB, 2026-11-21 18:32), and
  **no rover boot-floor image exists anywhere** — so the four rover cards cannot be imaged at all until
  one is built on a rover and cloned. The procedure, the guards and the two-stage shape (floor, then
  pilot) are in `rover/2026-11-21-imaging-the-nine-cards.md`. Nothing imaged, nothing verified.
- **2026-11-15** — **the nine cards are ordered**, order 112-6317894-9355469, nine × SANDISK 64GB
  Extreme SDSQXA2-064G-GN6MA, $310.05 total of which $192.38 came from the existing gift-card balance
  ($117.67 charged). Arriving Saturday. **No rows are added to the table above and no keys are written**:
  a row for a card nobody has held is a wish in a table, which is this file's own rule. The next entries
  here are the founder's key numbers once the box is open. Full record:
  `rover/2026-11-15-desi-nine-cards-ordered.md`.
- **2026-11-13** — register created. No keys written, no card read, no body booted; every row above is
  the dated record of an earlier session, not a measurement from today. The two ULTRA rover cards stay
  as they are, per the founder's decision the same day
  (`rover/2026-11-13-desi-the-founder-settles-the-card-questions.md`): the grade difference does not
  show at a PiCar-X's workload, so the inconsistency is documented here instead of bought away.
