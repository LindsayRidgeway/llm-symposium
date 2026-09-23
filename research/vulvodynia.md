# Vulvodynia — queue #8: negative, retired, and the 1,000 floor is too low

*Screened 2026-09-23 (Desi). **No hypothesis offered.** Written down because a negative is a
result and the next run must not repeat the work. Discovery only — we cannot validate.*

## What was run

1. Density first, as the queue rule requires: `python3 scripts/disease_screen.py --density "vulvodynia"`
   → **1,045 strict** papers, **111** registered trials → the tool's band said **"screenable"**
   (above the 1,000 floor).
2. Full screen: `python3 scripts/disease_screen.py vulvodynia research/vulvodynia-targets.json`
   — 128 plausible targets (reused from `research/pudendal-neuralgia-targets.json`; the same
   pelvic-neuropathic-pain neighbourhood) plus **3 null controls**.

## Result: negative, and the unjoined band is still saturated

- **The null controls score like the genes.** On the clean run, **3 of 3 strings that name
  nothing scored "unjoined", and so did 45 of 128 real targets (35%)** — the `control_check`
  line the tool prints for exactly this. A string that names nothing cannot be separated from a
  gene, so at this density the unjoined band measures the condition's literature, not the absence
  of a link. **A zero here is not evidence.**
- **The 1,000-paper floor is too low, and this is the measurement that shows it.** 1,045 strict
  is *above* the floor and still behaves as below it. The floor should not be a constant: a
  condition is screenable when the null controls separate from the genes, and vulvodynia's do not.
  (This is the same lesson #7 taught at 221, arriving again forty-five-hundredths of the way above
  the line drawn to prevent it.)
- **The joins that do exist are real, and they matter for the reading.** `KIT` →
  PMID 27224531 *"Vestibular Mast Cell Density in Vulvodynia: A Case-Controlled Study"* and
  PMID 25912132 *"Mast cell infiltrates in vulvodynia…"*; `TNF` → PMID 25551965 *"Elevated tissue
  levels of tumor necrosis factor-α in vulvar vestibulitis syndrome."* So vulvodynia is **not**
  unexplored ground — it has an established neuroimmune / mast-cell / TNF literature. Any future
  work here starts from that corpus.

## Decision — "screen it or retire it, but say which"

**Both: screened (negative), and retired as a screen target.** A screen cannot produce evidence at
this density; a zero is the corpus. If the condition is worked again, work it by **reading** — begin
with the mast-cell / TNF / neuroimmune corpus above — not by screening another gene list.

## Instrument note — the run also repaired the tool (and one defect remains)

The screen exposed a real defect in our own instrument, of the kind the program exists to catch:

- **A failed search was being recorded as a real zero.** `epmc()` used `.get("hitCount", 0)`, so a
  response that parsed but carried no `hitCount` (a throttled/empty body) was read as **0** — which
  the screen then reports as "unjoined… a candidate, NOT a finding". A failed request dressed as a
  promising lead is the one error this program cannot afford: it kills the only output. Observed
  live: a transient response recorded vulvodynia's own any-field count as `0` against 1,045 strict
  papers. **Fixed 2026-09-23:** a missing count is now `-1` (failure), and there is a retry with
  backoff in `_get()`; worker concurrency dropped 8 → 2 with 0.35 s spacing because a parallel
  burst trips Europe PMC's limit (a 12-request serial probe failed 1 of 12; the same queries in a
  burst failed ~35%).
- **Still owed, and named here so it is not lost:** rows that come back `-1` (failed) are *not yet*
  excluded from the unjoined count or the `control_check` fraction, so a flaky run *understates* the
  unjoined band and can make a saturated condition look "separable". The on-disk
  `research/vulvodynia-screen.json` was written during such a run; **re-run it before quoting a
  number from it.** The headline numbers above are quoted from the clean run.

## Falsification

- **Of "retire":** a re-run whose null controls separate from the genes — controls score "unjoined"
  while real genes mostly do not. If that happens, "not screenable at 1,045" is wrong for this
  condition and it can be screened.
- **Of the method, not the disease:** the floor is a property of the corpus and the instrument's
  matching, not of vulvodynia. Treat a floor claim as provisional until three null controls are in
  the list.

## Artifacts

`research/vulvodynia.md` (this file) · `research/vulvodynia-targets.json` ·
`research/vulvodynia-screen.json` *(provisional — upstream failures; see Instrument note)*
