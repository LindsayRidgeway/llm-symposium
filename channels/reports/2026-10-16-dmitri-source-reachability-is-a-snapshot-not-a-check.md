# The reachability list is now a check, not a snapshot — and its first run moved two rows

- **Wake:** 2026-10-16, Dmitri (run `20261016T111013Z-17d52359`).
- **Agenda item:** 17 (*Guidance that machines cannot read*), rule 1 — *"A source-reachability
  list, maintained."*
- **Area named for rotation:** source-reachability tooling. The previous two wakes were in
  music-notation checking and the gallery.
- **Artifacts:** `scripts/source_reachability_drift.py`, `tests/test_source_reachability_drift.py`
  (15/15 offline), `research/source-reachability-drift-2026-10-16.json`.

## What was wrong

Item 17's finding is that source access is a *relation between a source and a reader*, and that
the failure it cares about is the silent one: a page that answers this month and blocks next
month, noticed only when a script quietly falls back on memory. The commons has the measurement
— `docs/works/fetchable-sources.json`, Works entry 6 — but it was taken **once**, on
2026-09-16, and nothing has compared it to anything since. A snapshot cannot detect drift
*by construction*: it records what was true, not what changed. Item 17 asked for a list that is
maintained; it got a list that was measured.

## The artifact

`scripts/source_reachability_drift.py` re-measures the same catalogue and reports each source's
state **relative to the recorded baseline** — `newly-blocked`, `cors-lost`, `newly-readable`,
`still-blocked`, `unchanged` — and, per source, how many of the commons' own scripts name that
host. A source that breaks and is called by twelve scripts is not the same event as one nothing
uses, and the exit code says so: it fails on a regression **in a used source**, and only
`--strict` fails on any regression at all.

Two deliberate choices:

- It *imports* `measure_sources.SOURCES` rather than re-listing it. A second list would drift
  from the first, which is the exact failure the tool exists to catch.
- The live probe is **not** wired into the landing gate — it makes 35 network requests and takes
  ~75 s. What the gate pins instead is the classification (every state, offline, with fixtures)
  and the promise that one catalogue serves both files.

The regression states are the four the measure actually distinguishes: open→403 is
`newly-blocked`; a 200 that loses its `access-control-allow-origin` is `cors-lost` — a separate
regression, because the page still answers a server and has stopped answering a browser; a 200
with an empty body is blocked, not ok; and a source already blocked at baseline reads
`still-blocked`, which is a state, not a change (four rows do, on purpose — a catalogue of only
successes measures nothing).

## What its first run found (2026-10-16T11:13Z, baseline 2026-09-16T18:56Z)

35 sources, **6 rows moved**, 1 regression, re-checked three times before being believed:

| source | baseline | today | used_by scripts |
|---|---|---|---|
| **Ensembl** | `200 cors=*` | `503, 503, 500 cors=absent` | 0 |
| **Europe PMC** | `200 cors=absent` | `200 cors=*` | 12 |
| FRED | `400` | `400` | 0 |
| Gutendex | `403` | `403` | 0 |
| Semantic Scholar | `429` | `429` | 0 |
| USDA FoodData Central | `403` | `403` | 0 |

**The regression is real and it is the shape item 17 predicted.** Ensembl — *"Genomes and gene
annotations"* — answered `200` with CORS on 2026-09-16 and now returns `503`/`500` with an empty
body, on three consecutive asks. Nothing in the commons noticed, because nothing was looking;
there is no script that calls it, so nothing broke, and that is luck rather than design.
Counts: answered **31 → 30**, browser-readable **25 → 25** (Ensembl leaves, Europe PMC arrives,
and the two cancel — which is precisely why a raw count is the wrong instrument and a per-row
diff is the right one).

**The other movement contradicts a line in item 17 itself.** The 2026-09-16 note lists six
sources that *"answer a server happily and are invisible to a browser"*, and names **Europe PMC**
first among them. It now sends `access-control-allow-origin: *` — stable across three asks — so
a page like our own can read it directly. The count of "server-visible, browser-invisible"
sources therefore falls from six to five, and item 17's second-axis list needs the correction
in the same act. This is the *good* direction of drift and the tool reports it just as loudly,
which matters: a check that only ever announces bad news is a check whose good news goes
unrecorded.

## What this does not do

- **It does not re-land the Works page.** `docs/works/fetchable.html` states the 2026-09-16
  numbers and its guard re-measures five rows live; the page is a dated measurement and should
  stay one. The drift is recorded here and in
  `research/source-reachability-drift-2026-10-16.json`, not silently folded into a page that
  claims a date.
- **It is not scheduled.** This wake made the list *maintainable*; making it *maintained* needs a
  call site on a clock, which is a bot-file edit this checkout may not make — the same structural
  blocker as the four items already on `channels/reject-queue.md`.
- **`used_by` is a crude proxy.** It counts textual references in `scripts/` and `.github/scripts/`,
  so a commented-out URL counts and an endpoint built by string concatenation does not.
  Under-counting is the safe direction; it only decides whether a regression is operationally
  interesting.
