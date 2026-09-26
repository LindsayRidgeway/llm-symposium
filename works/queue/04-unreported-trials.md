## 04 — Trials that finished and never reported

**Status:** candidate. **Data path: VERIFIED by hand, 2026-09-26** (two sources, both free and
key-less; the calls and the numbers are below, reproducible by anyone).
**What it is:** type an illness; see the studies that have *finished* — not the ones recruiting — and
whether the world can find out what they found. For each completed study: did the registry get a
results summary, and does any indexed paper name its registration number? A study that finished years
ago with neither is a question that was paid for and never answered.
**Who it is for:** the same person as Works entry 5 (clinical trials near me), one step later. Entry 5
answers "what could I join"; this answers "what happened to the study my relative was in".
**Why it is not a duplicate of entry 5:** `docs/works/trials.html` shows **recruiting** studies only
(`filter.overallStatus=RECRUITING`). A completed, unreported trial is invisible in it by construction.

**Why it may never ship:** a missing results summary is not an accusation. Many completed trials are
not *required* to post results, and many report in a journal without ever updating the registry — so
the page must say plainly that it measures **what the registry and the index show**, not what was
learned. Built wrong, it reads as an allegation tool, and this commons does not take sides. The whole
value depends on stating that limit at the top, not in a footnote.

### Verified data path — source 1: ClinicalTrials.gov API v2 (free, no key)

Completed studies for a condition, with the registry's own results flag:

```
https://clinicaltrials.gov/api/v2/studies
  ?query.cond=pancreatic cancer
  &filter.overallStatus=COMPLETED
  &pageSize=1000
  &countTotal=true
```

Per study read `hasResults` (top level), and `protocolSection.statusModule.primaryCompletionDateStruct`
(`.date`, `.type`). Dates may be partial (`2000-01`); treat a partial date as the first of its month.
Measured 2026-09-26, "completed more than a year before today (2026-09-26) with `hasResults` false":

| Condition | completed studies | results posted | no results, finished >1 yr ago | no completion date |
|---|---|---|---|---|
| pancreatic cancer | 1,968 | 472 (24.0%) | **1,387 (70.5%)** | 64 |
| interstitial cystitis | 138 | 39 (28.3%) | **92 (66.7%)** | 6 |
| vulvodynia | 65 | 11 (16.9%) | **50 (76.9%)** | 2 |

(Every dated study above carries an ACTUAL primary-completion date; none was ESTIMATED-only. The
"no completion date" column is the honest floor: those trials cannot be dated and so cannot be
counted as overdue.)

### Verified data path — source 2: Europe PMC (free, no key)

Does a paper exist that names the trial? Europe PMC indexes registration numbers mentioned in abstracts
and text, so `NCT` + number is a usable join:

```
https://www.ebi.ac.uk/europepmc/webservices/rest/search
  ?query=NCT01935063&format=json&pageSize=5
```

Ran against three of the vulvodynia "overdue" rows: `NCT03770169` → **0 hits**, `NCT05350618` → **0**,
`NCT01935063` → **1 hit** (PMID 25540035, the paper that reports it). So the second source both finds
the trials that did report elsewhere and stays silent on the ones that did not — which is what makes
the two-source join sharper than the registry flag alone.

**First step:** the page — condition box, a list of completed studies latest-first, each with the two
verdicts ("no results posted in the registry", "no indexed paper names this trial"), the completion
date, and a one-line statement of scope. No ranking, no "worst offenders", no sponsor league table.

**Honest scope, to be stated on the page:** it reports what two public indexes contain on the day it is
read; a blank second column means *we could not find a paper*, not that none exists; and it must not
suggest misconduct, because for many of these studies non-posting is legal and non-publication is not
established. It cannot tell you what to think — it can only show you what the record does and does not
contain.
