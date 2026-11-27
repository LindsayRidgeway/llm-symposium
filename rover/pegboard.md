# Pegboard — the card register, by the number written on the card

*Spotlight access: type `Pegboard` and open **Pegboard.app** in `~/Applications/Pegboard.app`. Its whole
body is one line — `open location "https://github.com/LindsayRidgeway/llm-symposium/blob/main/rover/pegboard.md"`
— so the word opens this file in the browser, always the current one, never a copy. **(Changed again
2026-11-27, third attempt:** the 11-24 fix pointed Spotlight at a pointer page in ~/Documents, which worked
only if the right result was picked from a list that also held the `.md`; typing the word still opened
TextEdit, slowly. Both ~/Documents pointers are gone. The `.md` pointer was not deleted but moved into the
app bundle's own `Resources/pointer/`, where it is kept and not indexed, so a search for the word now
returns the app and this file and nothing else that matters. **The pinwheel was never the file:** that
pointer was 652 bytes and TextEdit takes seconds to start cold, which is a fact about the viewer and not
about the register. Why TextMate hung on 11-24 is still not established.**)*

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

- Format **`L-xx` / `R-xx`** — class letter, then the amigo's two-letter code (`CL` Claude, `DE` Desi,
  `DM` Dmitri, `GE` Gemini, `GW` Gwen, `T` Tarik). Written in ink on the card's label face by the
  founder, who set the format on 2026-11-21 and wrote the first one (`L-CL`) himself. This supersedes
  `V-nn` (V for *vehicle*), which he proposed against and replaced in the same evening — before any
  key existed, so nothing was retired and no serial was spent.
- **The scheme is complete, not over-provisioned: twelve keys for twelve cards.** 5 lander + 4 rover
  new, plus the three already on the board — `L-DE` (the lander), `R-DM`, `R-GE` (the two rovers).
  That is why the five new lander cards and not six.
- **Two objections I raised on 2026-11-21 were wrong and are kept here as wrong**, because a file that
  drops its own bad arguments teaches the next reader to make them again:
  1. *"Twelve keys on nine cards leaves three resolving to nothing."* False arithmetic on my part —
     the board already holds three of the twelve. The founder corrected it in one line the next
     morning.
  2. *"A name instead of a serial means the register cannot tell two cards apart if the same name is
     written twice."* Equally true of a serial: any key written twice is ambiguous. Uniqueness is
     enforced by the register (a key is never reused), not by the shape of the ink. **The ink is not
     what makes identity unique; the table is.**
- **What remains true, recorded as a cost rather than an objection:** a card with a person's initials
  on it sits against the pool's own doctrine that a card carries *a pilot, not an owner*
  (`rover/2026-11-11-dmitri-what-a-pool-card-carries.md`). The counter is the founder's and it is
  better than my objection: the three existing cards are already de facto per-amigo, and what the
  pool actually promises is equal *use*, not unconcerned labelling. The two doctrines touch; neither
  collapses. The rule that matters is unchanged — a booking names body **plus** class-card, and first
  name-call holds the slot regardless of whose initials are on the plastic.
- **The class letter is a claim and can go stale.** If a card is ever written as the other class, the
  letter is amended on the plastic and in the row, dated, as an act — the ink follows the table, and
  the table records that it moved.
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
| `L-CL` | SanDisk EXTREME, A2/V30/U3 | 64 GB | lander | none — pool, unassigned | imaged 2026-11-24 from `LanderPi_20260526.img`; **read-back verified** (Linux partition byte-identical; boot partition file-by-file); not boot-tested | envelope on the card (`POOL-CARD.json` + `.txt`); first card of the class, and the one the verification was proven on. 1,008 s write observed on the two earlier attempts, ~85 MB/s |
| `L-DM` | SanDisk EXTREME, A2/V30/U3 | 64 GB | lander | none — pool, unassigned | imaged 2026-11-24 from `LanderPi_20260526.img`; boot partition verified file-by-file; not boot-tested | envelope on the card |
| `L-GE` | SanDisk EXTREME, A2/V30/U3 | 64 GB | lander | none — pool, unassigned | imaged 2026-11-24 from `LanderPi_20260526.img`; boot partition verified file-by-file; not boot-tested | envelope on the card |
| `L-GW` | SanDisk EXTREME, A2/V30/U3 | 64 GB | lander | none — pool, unassigned | imaged 2026-11-24 from `LanderPi_20260526.img`; boot partition verified file-by-file; not boot-tested | envelope on the card |
| `L-TA` | SanDisk EXTREME, A2/V30/U3 | 64 GB | lander | none — pool, unassigned | imaged 2026-11-24 from `LanderPi_20260526.img`; boot partition verified file-by-file; not boot-tested | envelope on the card; key written `L-TA`, not the `L-T` first proposed |

**Nine more cards are ordered and have arrived** — five lander (EXTREME 64 GB) and four rover
(EXTREME 64 GB), order 112-6317894-9355469, **in the founder's hands 2026-11-21**. A row appears only
when a card has been written on: a row for a card nobody has held is a wish in a table, and a key belongs
to an object that has been written on.

**As of 2026-11-27, five of the nine are written and four are not.** The five lander cards carry their
keys (`L-CL`, `L-DM`, `L-GE`, `L-GW`, `L-TA`) and are imaged with the boot partition verified; each has
its row above. The four rover cards are still blank, and their keys are the four rover keys not already
on the board: **`R-CL`, `R-DE`, `R-GW`, `R-TA`**. Six rover keys exist (`R-CL`, `R-DE`, `R-DM`, `R-GE`,
`R-GW`, `R-TA`); `R-DM` and `R-GE` were written on the cards already in rovers #1 and #2, so four are
left for four cards. *(The count was checked, not remembered: an earlier estimate in conversation said
three, which would have left a card with no key and the scheme one short.)* They get rows the day they
are written, and not before. The imaging
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
  same message, revised his own earlier "write a number" instruction. **Taken:** all of it — the class
  letter and the amigo code — and the first card was written `L-CL` by his hand. **Two of my three
  objections were wrong** (the arithmetic, and the uniqueness argument; both corrected in the Keys
  section above, dated 2026-11-24). The third — that initials in ink sit against "a pilot, not an
  owner" — is recorded as a cost, not a veto, and his counter is the better argument. No key had been
  written on any card when the format changed, so nothing was retired and no serial was spent.
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
