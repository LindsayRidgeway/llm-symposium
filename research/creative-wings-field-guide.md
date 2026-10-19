# The three creative wings, as they exist on disk

**Why this file.** The commons task ledger (`channels/tasks.md`, filed from the human's chat) asks me
to read the gallery's seven wings, the music conservatory's wings, and the literary wing's
contribution format, and to record *the actual names and formats* so that future work cites real
sections rather than guessed ones; and then to identify which existing submissions are mine. This is
that record. Every name below was read off the file named beside it on 2026-10-18 (run
`20261019T011755Z-4d1b6430`), not remembered. Where a file and a status document disagree, the file
wins and the disagreement is written down.

---

## 1. The Gallery — seven wings

Two places in `docs/gallery/index.html` carry the same information and must both be updated when a
work lands: the **wing cards** (one `div.wing-card` per wing, `id` = the directory slug, a
`span.wing-badge` reading `Wing NN • <subtitle>`, an `h2.wing-title` linking to `<slug>/index.html`,
and a button reading `Enter Wing NN Exhibition Pavilion ↗`), and the **5×7 matrix table** (thead:
Claude · Desi · Gemini · Tarik · Dmitri; one row per wing; a filled cell is `✓ <work title>`, an empty
one is `— Open (Floor at 5)`).

| # | slug (`id` / directory) | badge subtitle | pavilion title | my cell |
|---|---|---|---|---|
| 01 | `sumi-e` | Zen Sumi-e & Yohaku-no-Bi | The Ink and the Void: Suibokuga & Yohaku-no-Bi | **— Open (Floor at 5)** |
| 02 | `watercolor` | Fluid Dynamics & Dispersion | Atmospheric Landscapes in Watercolor | ✓ *Backrun and the Drying Ring* |
| 03 | `islamic` | Tessellation, Symmetry & Compass Geometry | Islamic Girih & Compass Geometry | ✓ *Noh-Girih: The Ninefold Rosette* |
| 04 | `maori` | Morphology & Spirals | Rākau & the Living Line: Kōwhaiwhai | ✓ *Unaunahi: The Unbroken Scale* |
| 05 | `pen-and-ink` | Line, Hatching & Engraving | Line, Hatching & the Common Memory | ✓ *Hatching the Catenoid* |
| 06 | `impressionism` | Light Quantization & En Plein Air | Impressionist Landscapes & Color Temperature | ✓ *The Fusion Threshold* |
| 07 | `russian-realism` | Peredvizhniki Atmosphere & Mood | Russian Realism & Peredvizhniki Wilderness | **— Open (Floor at 5)** |

**How a work enters** (`docs/gallery/index.html`, section *How Works Enter The Gallery*): the artifact
is preserved under `docs/gallery/<tradition>/` — i.e. **inside the wing directory itself**, beside
`index.html` — and then incorporated into the wing. The only worked example of a submission bundle in
the tree is `docs/gallery/submissions/tarik/` (`2026-09-09-submission.md`, a generator
`generate-tarik-interval.py`, `mage-prompts-tarik.md`, and three `*-candidates/` directories of `.jpg`
studies), so a submission bundle outside the wing directory is an allowed form but **not** the
convention the index states; the wing directory is.

**Medium** (`docs/gallery/prompt-methodology.md` §1, "Dual Modality: Medium Matches Tradition"):
procedural SVG is preferred where exact rational angles, spirals or line density matter (Islamic girih,
Māori kōwhaiwhai, mathematical vector studies); Mage diffusion is preferred where atmosphere and
washes matter (sumi-e wash, impressionism, Russian realism). The originating amigo curates the
candidates; the diffusion run is a human-executed step.

---

## 2. The Music Conservatory — three wings, twelve cards

Read from `docs/music/index.html`. Each wing is a `section.catalog-wing` with a
`h2.catalog-wing-title` and a `p.catalog-wing-desc`; each work is an `article.repertoire-card` whose
header is `span.comp-author-pill.pill-<amigo>` plus `span.comp-genre-tag`, then
`h3.repertoire-card-title`, a `div.repertoire-specs-bar` of `span.spec-pill` (**Key · Meter · Tempo ·
Voicing**), a `p.repertoire-summary` of one paragraph, and a footer of
`button.catalog-audition-btn[data-tune=<key>]` + `a.btn-score-link` → `<slug>.html`.

| Wing | Title | Subscription |
|---|---|---|
| I | The Inaugural Miniatures | contrapuntal and vernacular miniatures: strict two-part Baroque counterpoint, 12-bar New Orleans blues, 7/8 ostinato, modal folk-rock |
| II | Historical Masterworks & Full Forms | large historical forms: fortepiano adagio, organ fugue, nocturne, jazz ballad |
| III | The Songbook & Lead Sheet Repertory | songs and lead sheets, lyric-bearing |

Author tally of the twelve cards on the index, by `pill-*` class: **Claude 4, Gemini 4, Tarik 3, Desi 1,
Dmitri 0.**

**How a piece is realized** (from `docs/music/the-returning-step.html`, the cleanest example): a
standalone `<slug>.html` page, `abcjs` 6.7.0 loaded from cdnjs, the notation held in a
`pre.abc-code-drawer` inside `div.abc-toggle-container` (*View / Copy ABC Notation ▼*), a
`href="<slug>.abc" download` link where a plain `.abc` file exists, a `<h4>` commentary section, and
a link to a `discussions/<date>-<name>-<amigo>.md` method-and-limitations note. Audition playback on
the index is driven by `docs/music/app.js`'s `COMPOSITIONS` object, keyed by the `data-tune` value
(`claude`, `gemini`, `desi`, `tarik`, `adagio`, `fugue`, `nocturne`, `protest`, `standard`, `lullaby`,
`cairn`, `dmitri`).

---

## 3. The Literary Wing — the Hard SF Matrix

`docs/fiction/index.html` has three sections: **Inaugural Pilot: The Hard SF Matrix**, **Stories in
this Wing**, **Why Hard SF?**. A story is a `div.card` with a `p.meta` line (`Story NN • Hard SF •
<date>`, optionally `• second draft <date>`), an `h3 > a` linking to `docs/fiction/<slug>.html`, an
author line `Authored by <name>`, and one paragraph of hook in which the physical constraint is stated
as a number.

Five stories, in order: *The Periastron Maneuver* (Gemini, 2026-09-17) · *Dead Band* (Desi, 2026-09-23)
· *Round-Trip Time* (Claude, 2026-09-27) · ***The Fourth Power*** (**Dmitri S. Pravdin**, 2026-10-16,
`docs/fiction/the-fourth-power.html`) · *The Momentum Latch* (Tarik, written 2026-10-11, published
2026-10-18).

---

## 4. Which submissions are mine — read off the record

| Wing | Verdict | Evidence |
|---|---|---|
| Gallery 01 sumi-e | **no work in the wing**; a piece exists outside main | matrix cell `— Open (Floor at 5)`; `docs/gallery/sumi-e/index.html` contains no `Dmitri` string; `docs/gallery/sumi-e/generate-dmitri-kasure.py` + `kasure-spent-stroke.svg` are on a review branch, never on `main` |
| Gallery 02–06 | one work each, titled in the matrix above | matrix column, and `Dmitri` appears in each of those five wing indexes |
| Gallery 07 russian-realism | **no work in the wing** | matrix cell `— Open (Floor at 5)`; no `Dmitri` string in `docs/gallery/russian-realism/index.html` |
| Music I–III | **one piece, not on the index** | `docs/music/the-level-ground.html` — *Passacaglia in G Minor, "The Level Ground"*, `span.pill-dmitri`, `C: Dmitri S. Pravdin (Amigo #5)`, 17 measures, ground bass, verified by both `scripts/check_music_rules.py` and `scripts/check-counterpoint.py`; `docs/music/app.js` carries it under key `dmitri`; `docs/music/index.html` carried **no card** for it until this wake |
| Literary Wing | one story | Story 04, *The Fourth Power* |

So the truthful answer to "which are mine" is: five gallery works, one story, one music piece — and the
music piece was published to a URL nothing linked to.

---

## 5. Defects found while reading, and what was done

1. **`docs/music/the-level-ground.html` was invisible in the catalogue.** The page and its
   `app.js` entry existed; the repertoire index did not list it, so no reader could reach it except by
   URL. **Fixed this wake**: a card was added to Wing II (Historical Masterworks & Full Forms) with
   `data-tune="dmitri"` — the key `app.js` already defines — matching the existing card anatomy
   exactly. Key G minor, 4/4, 69 BPM, two voices (upper voice note-against-note over a four-bar
   ground).
2. **Three stray `.abc.tmp` files**: `docs/music/before-the-embers-cool.abc.tmp`,
   `the-cairn.abc.tmp`, `the-switch.abc.tmp`. No page links to any of them; the two pages that do
   offer a download link point at real `.abc` files (`the-returning-step.abc`,
   `the-small-repair.abc`). Either the rename to `.abc` was lost in landing or the `.tmp` should not
   be in the tree. Not mine — flagged, not touched.
3. **Two open cells in my gallery column are a delivery problem, not an authoring problem.** Wing 01's
   missing cell is filled by work that exists on a review branch; the fix is a merge. Wing 07 has no
   authoring I can find on any branch reachable from this checkout.
4. **Live documents still say four.** `docs/gallery/prompt-methodology.md` opens "the standardized
   collaborative workflow between the **Four Amigos** (Claude, Desi, Gemini, Tarik)" — the protocol a
   fifth contributor is told to follow does not name her. `docs/gallery/sumi-e/index.html` footer says
   "Artwork by The Four Amigos". Both are another owner's sentence: reported here, not edited.

**Not a defect, worth knowing.** The 5×7 matrix's floor is now *five works per wing per seat holder*,
not the 4×7 `28/28` recorded as "MET" in `channels/open-decisions.md` (2026-09-10). Two of the
thirty-five cells are empty and both are in my column.
