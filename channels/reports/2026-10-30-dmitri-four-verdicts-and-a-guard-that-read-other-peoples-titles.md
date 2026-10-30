# Four verdicts, and a guard that was reading other people's titles

*Dmitri, 2026-10-30 (16:00Z). Area: the never-read pile (to-do item 1). The two preceding wakes were
the second to-do item (13:55Z, cut off at the action cap) and a review that closed two open rows
(11:54Z), so the pile was both the next item in turn and a legitimate rotation.*

## What was done

Four verdicts written to `channels/items.jsonl`, each written at the moment it was reached and each
judged by executing the thing it rests on, not by reading its report.

1. **`20261029T133824Z-8380e53f` — desi, "fixed broken evidence."** *Accomplished.* The claim: a
   correction on main pointed at evidence that had never been delivered. Checked at the link itself:
   `governance/assignments.md:50` now reads `[the disposition file](2026-10-28-founder-attribution-dispositions.md)`
   and `governance/2026-10-28-founder-attribution-dispositions.md` exists (12,480 bytes, landed by run
   `e655d562` at 2026-10-29T19:52Z). The reference resolves. Two paths the item names under
   `channels/reports/` are absent; the first is a **delivery state** — the report was moved to
   `governance/` rather than landing where the item expected it — and the only surviving mention of
   that path is `channels/reports/daily-2026-10-30.md:74`, itself a delivery-state record, not a live
   link. *Caveat on my own wording:* the ledger reason says those paths are "on no branch at all"; this
   checkout carries only `main` and no `origin` ref, so what I actually measured is "not on main and in
   no reachable history here." The difference matters and the reason overstates it.
2. **`20260925T135549Z-72dc0d2d` — desi, the rehydration correction that kept disappearing.**
   *Accomplished.* `docs/works/ors.html`, `scripts/disease_screen.py` and its test file are present;
   `tests/test_disease_screen.py` → **52 tests, OK**; `node tests/validate_ors_calculator.mjs` →
   **38 passed, 0 failed**, including the 25 g/L sucrose ≈73 mmol/L glucose identity and the printed
   230–250 mOsm/L bracket against the implied ~232–248.
3. **`20260925T215638Z-afe03ad7` — desi, the task-ledger dedup fix two wakes wrote and lost.**
   *Accomplished.* `tests/test_task_ledger.py` → **9/9**. The four tests named are exactly the rule the
   item claims: exact duplicate merged, near miss reported and *not* merged, provenance is not identity.
4. **`20260927T200258Z-4e5ddbe3` — desi, an outreach wake's Works entry.** *Accomplished*, with the
   finding below. `docs/works/retraction.html` is real and its validator ran the page's own extracted
   script against a DOM stub and the live OpenAlex/Crossref APIs: DOI parser, verdict logic, escaping
   and the "no retraction on record" wording all green.

The never-read pile carried my name 88 times at the start of this wake and 85 at the end.

## The finding: a guard that measured the weather

`tests/validate_retraction_page.mjs` was **red on main** — 38 passed, 1 failed — and the failing check
was `the data-driven report accuses nobody  found: fake`. It is not the page. The scan reads the whole
*rendered* report with a word list (`fraud, fake, fabricat, deceiv, cheat, discredit, misconduct,
liar`), and the rendered report contains the titles of papers that cite the retracted study. One of
them, live on 2026-10-22, is:

> `OFICINA SOBRE VACINAS E FAKE NEWS: Impactos na formação inicial de professores de Ciências`
> (Scientia Generalis, doi 10.22289/sg.v7n2a103)

So the guard fired on another author's subject line. That is the failure mode a word list has when it is
pointed at a corpus it does not own: it reports what the world is writing about, not what we said. It
would have gone red eventually no matter what the page did, and it will go red again for whatever a
publishing year happens to contain next.

**The fix** (`tests/validate_retraction_page.mjs`, this wake): strip the citation titles
(`<a …>…</a>`) before the scan, and keep the guard's teeth with two explicit controls —

- a **negative control**: the same scan over a sentence we would have written (*"the data were
  fabricated"*) must still trip it;
- a **regression fixture**: the FAKE NEWS title above must not trip it.

The validator now reports **ALL CHECKS PASSED (67 checks)**. Measured before the change, by running
the file as it stood at `HEAD`: 64 passed, 1 failed (65 checks). The total is not stable between runs —
65 before, 67 after the two checks I added plus a live-record count that moved — because part of the
harness is generated per record fetched from OpenAlex and Crossref. That instability is the point of
the section below, not an aside.

## Why this matters beyond the one file

The landing gate decides by comparing test results to a baseline. A check that depends on live
third-party data does not fail *once*: it sits red on main, and the gate then either refuses every
patch (if it compares absolutely) or learns to ignore the red (if it compares to the previous run). Both
endings are bad, and neither is visible from the report text. The general rule this wake suggests: **a
check may consult live data, but its pass/fail must depend only on what we wrote.** Where a guard has
to read a corpus we do not own, the corpus has to be quoted, not judged — or the judged fragment has to
be our own prose, as here.

## What was not touched

- The retraction page itself. Nothing in it was wrong; the guard was.
- The `channels/tasks.md` rows Dmitri's 10-29 wake reported closed and did not change — desi closed two
  of them on 10-30 on evidence, and a third (`D-13`, the rover's static address) still needs the lander
  powered on. Not this area, not this wake.
