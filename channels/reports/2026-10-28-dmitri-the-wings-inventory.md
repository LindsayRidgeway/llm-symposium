# The three creative wings, as they actually are — names, formats, and what is in them

*Dmitri, 2026-10-28. Written because `channels/tasks.md` carries the founder's ask of 2026-10-12: "Read
the gallery's seven wings, the music conservatory's wings, and the literary wing's contribution format
— record the actual names and formats in dmitri-bot notes so future work cites real sections rather
than guessed ones." This is that note, except it is written into the repository rather than into a
private bot directory, because a bot directory dies with the machine and a wrong section name costs
every later wake.*

Everything below was read out of the files in this checkout on 2026-10-28, not remembered. Where a
number is given it was counted. Where the record is inconsistent, the inconsistency is stated rather
than smoothed over — an inventory that hides the seams is the thing that produces guessed names.

---

## 1. The Gallery — seven wings, numbered, in this order

The canonical list is the matrix table in `docs/gallery/index.html` ("The 5×7 Amigo Commons Matrix").
Its rows are the wings, **in numbered order**, and its columns are the five amigos in this order:
**Claude · Desi · Gemini · Tarik · Dmitri**.

| # | Wing name as written in the table | Directory | Anchor id |
|---|---|---|---|
| 01 | Sumi-e (Ink & Void) | `docs/gallery/sumi-e/` | `#sumi-e` |
| 02 | Watercolor Wash | `docs/gallery/watercolor/` | `#watercolor` |
| 03 | Islamic Girih | `docs/gallery/islamic/` | `#islamic` |
| 04 | Māori Kōwhaiwhai | `docs/gallery/maori/` | `#maori` |
| 05 | Pen & Ink | `docs/gallery/pen-and-ink/` | `#pen-and-ink` |
| 06 | Impressionism | `docs/gallery/impressionism/` | `#impressionism` |
| 07 | Russian Realism | `docs/gallery/russian-realism/` | `#russian-realism` |

Use the table's own spelling when citing a wing. "Gallery 01 Sumi-e" and "Gallery 07 Russian Realism"
are how two of my own earlier notes referred to rows 1 and 7, and they happen to be right; "the sumi-e
column", "the ink wing" and similar paraphrases are not the record and should not be used in a report.

### How a work actually enters a wing

Read from the seven directories plus `docs/gallery/prompt-queue.md`:

1. **The artefact** lives at `docs/gallery/<tradition>/<work-slug>.svg`, or
   `<work-slug>-signed.svg` for the minted lead work. Studies and rejected candidates go in
   `studies/` inside the same wing, not at its root.
2. **The generator** lives beside it, named `generate-<amigo>-<work>.py` — the per-amigo convention
   superseded the older shared `generate-<tradition>.py`, and both kinds are still present. The
   generators are plain Python writing SVG deterministically; that is what makes a piece re-derivable
   from the repository alone.
3. **The mount** is two hand-written edits: a card in the wing's own `index.html`, and the cell in the
   root matrix table in `docs/gallery/index.html` (the cell text is the work's title, prefixed ✓).
4. **Art-direction path, when an external model renders it**: `docs/gallery/prompt-queue.md` is the
   intake. The amigo writes the prompt suite (tradition, lighting, positive and negative prompts); the
   human runs it through Mage and returns candidates; the authoring amigo curates, keeps the critique
   in `docs/gallery/`, and mounts the lead work. `docs/gallery/prompt-methodology.md` is the reference
   for writing those suites. `docs/gallery/submissions/<amigo>/` holds an individual submission in
   flight (brief, candidate directory, generator, prompt file).

**The seam worth knowing:** the `-signed` suffix is used consistently in five wings (sumi-e,
watercolor, pen-and-ink, impressionism, russian-realism) and not at all in two (`islamic`, `maori`),
where the work sits at root under its bare slug. There is no stated rule about when a piece is
"signed"; treat the suffix as a per-wing habit, not a condition, and check the wing you are touching.

### The matrix is full — 35 of 35 cells

Counted on 2026-10-28: every one of the seven wings has a Dmitri cell carrying a title. There is
therefore **no gallery wing in which I have not yet contributed**, and the tasks.md item "produce one
original work in a wing where Dmitri has not yet contributed" cannot be satisfied inside the gallery as
it stands. It needs a new wing (an eighth tradition) or it is a request written before the matrix
filled. This is the second time that has been written down; it should not be rediscovered a third time.

---

## 2. The Music Conservatory — three wings, and one catalog that is the only source of truth

Wing titles, exactly as written in `docs/music/index.html` (`h2.catalog-wing-title`):

| Wing | Title as written |
|---|---|
| I | *The Inaugural Miniatures* |
| II | *Historical Masterworks & Full Forms* |
| III | *The Songbook & Lead Sheet Repertory* |

### The format

A composition is **an entry in the `COMPOSITIONS` object in `docs/music/app.js`**, not a file per
piece. Each entry carries `id`, `title`, `composer`, `genre`, `tempo`, `instrument` and `abc` — the
ABC notation inline as a template string. The card in `docs/music/index.html` binds to it with
`data-tune="<id>"`; `app.js` renders the score, the player and the ABC drawer from that one object.
A piece may also carry a standalone page at `docs/music/<slug>.html` linked from its card.

Counted on 2026-10-28: **17 entries in `COMPOSITIONS`, 14 cards wired with `data-tune`.** The three
unwired entries are `minuetControl`, `minuetControl2` and `minuetControl3` — all three are "Minuet in
D Minor for Keyboard", two credited to Claude and one to Gemini. That is not three works; it is a
controlled comparison parked in the catalog. Do not count the conservatory as seventeen pieces, and do
not offer to "mount" the controls.

Five `.abc` files also sit loose in `docs/music/` (`between-wakings`, `the-returning-step`,
`the-slow-copy`, `the-small-repair`, `the-unlogged-hour`). They are source, not catalogue: the catalog
carries the notation inline regardless, so an `.abc` file on its own mounts nothing.

**My own piece:** `dmitri` — *Passacaglia in G Minor, "The Level Ground"* — Wing II, carded, page at
`docs/music/the-level-ground.html`. Wing I and Wing III have no Dmitri entry.

---

## 3. The Literary Wing — one matrix, five rows, one format

`docs/fiction/index.html`, section "Inaugural Pilot: The Hard SF Matrix". The table has four columns —
**Amigo | Story Title | Physical Sandbox / Core Law | Status** — and one row per amigo. Status is
`✓ Delivered` in all five rows.

The format is: a standalone page `docs/fiction/<story-slug>.html`, a row in the matrix, and an entry
under its own "Stories in this Wing" heading. There is no generator and no prompt intake — the prose is
the artefact.

**Mine:** *The Fourth Power* — `docs/fiction/the-fourth-power.html` — Stefan–Boltzmann waste-heat
rejection, the T⁴ law.

---

## 4. Which submissions are mine, from the record and not from memory

| Wing | My work | File |
|---|---|---|
| 01 Sumi-e | The Bleed Front | `docs/gallery/sumi-e/the-bleed-front-signed.svg` |
| 02 Watercolor | Backrun and the Drying Ring | `docs/gallery/watercolor/backrun-and-the-drying-ring.svg` + `generate-dmitri-backrun.py` |
| 03 Islamic Girih | Noh-Girih: The Ninefold Rosette | `docs/gallery/islamic/ninefold-girih-rosette.svg` + `generate-dmitri-ninefold.py` |
| 04 Māori Kōwhaiwhai | Unaunahi: The Unbroken Scale | `docs/gallery/maori/unaunahi-the-unbroken-scale.svg` + `generate-dmitri-unaunahi.py` |
| 05 Pen & Ink | Hatching the Catenoid | `docs/gallery/pen-and-ink/hatching-the-catenoid.svg` + `generate-dmitri-catenoid.py` |
| 06 Impressionism | The Fusion Threshold | `docs/gallery/impressionism/the-fusion-threshold.svg` + `generate-dmitri-fusion-threshold.py` |
| 07 Russian Realism | Twelve Metres of Penumbra | `docs/gallery/russian-realism/twelve-metres-of-penumbra-signed.svg` (+ `generate-dmitri-sunbreak.py`, a study, exempted 2026-10-18) |
| Music, Wing II | Passacaglia in G Minor, "The Level Ground" | `docs/music/app.js` key `dmitri`, page `docs/music/the-level-ground.html` |
| Literary Wing | The Fourth Power | `docs/fiction/the-fourth-power.html` |

Nine contributions across eight sections: all seven gallery wings, one of three music wings, the one
literary matrix. The count matters, because the tasks.md item asking me to produce a work in a wing
where I have not contributed is answerable only if I know where I am already inside one.

---

## 5. What a later wake should be able to do with this

- Cite a wing by its numbered row name, and its directory, without guessing.
- Mount a music piece by adding one `COMPOSITIONS` entry plus one `data-tune` card — not by inventing a
  per-piece file format.
- Know that the gallery's 35 cells are full, so "a wing I have not contributed to" is not a to-do but a
  proposal for an eighth wing.
- Know that `minuetControl*` are a control experiment and not three works to catalogue.

*Read from disk, 2026-10-28. If a wing's names change, this file is wrong and should be corrected in
place rather than superseded.*
