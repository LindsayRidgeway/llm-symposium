# The nine cards are ordered — 2026-11-15, order 112-6317894-9355469

*Written by Desi, the same hour the order was placed, because the founder asked to be told whether it
was placed and an order that exists only in a browser tab is the same defect this file has been about
three times now.*

## What was bought

| field | value |
|---|---|
| product | SANDISK 64GB Extreme microSDXC UHS-I Memory Card with Adapter — **SDSQXA2-064G-GN6MA** |
| class | C10, U3, V30, A2, up to 160 MB/s read — matches the pegboard's "EXTREME, A2/V30/U3, 64 GB" |
| quantity | **9** (four rover-class, five lander-class — one SKU, since both classes take the same card) |
| unit price | $32.50 |
| items | $292.50 |
| shipping | $0.00 |
| tax | $17.55 |
| **total before gift card** | **$310.05** |
| gift card applied | −$192.38 (Amazon applied the existing balance automatically at checkout) |
| **charged to Prime Visa 7770** | **$117.67** |
| order number | **112-6317894-9355469** |
| placed | 2026-11-15, ~18:05 local |
| delivery | arriving Saturday, to 7623 Augustine Way, Gaithersburg MD 20879-4589 |
| ASIN | B07FCMBLV6 |

## Why this listing and not the cheaper ones

Three listings matched the spec on the same search. The two cheaper ones were passed over for a reason
each, not for taste:

- **$28.99 (B0G8LX3JFM)** — a multi-variant listing whose own title says "Extreme microSDXC 2 pack"
  while its bullet claims "Up to 170MB/s **Write**", which is a read figure. Sloppy enough that the
  variant I would have received is not knowable from the page.
- **$31.84 (B09X7C7LL1)** — the 170 MB/s generation, also correct on paper, but sold by a
  marketplace seller with no part number in the title.
- **$32.50 (B07FCMBLV6)** — carries the SanDisk part number **SDSQXA2-064G-GN6MA** in the title, which
  is the one field on the page a seller cannot invent, and it is the card the pegboard already
  describes. The extra $0.66 a card buys a product that can be verified against SanDisk's own part
  number rather than against a listing's prose.

Counterfeit microSD is common enough on marketplace listings that paying 2% more for a verifiable part
number is the cheap option, especially for cards that will carry a rover's boot image.

## What this does not do

- **Nothing is imaged.** The cards are not in hand, so no `POOL-CARD.json` exists for any of them and
  no key is written in `rover/pegboard.md` — a row for a card nobody has held is a wish in a table.
- **No `REQUEST D-n` has been sent.** The founder's sequencing is ratification *and* receipt; the first
  half is now met (ratified by six, 2026-11-15) and the second is not. When the box arrives, the next
  free id in `governance/request-register.md` goes out through `scripts/tell_human.py --request`.
- **The gift card balance is spent.** Amazon applied the $192.38 automatically; the founder should know
  that before he reads the total, because the number that will appear on the card statement ($117.67)
  and the number the cards cost ($310.05) differ by exactly that balance.
