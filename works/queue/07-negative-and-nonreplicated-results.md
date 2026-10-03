# 07 — An index of negative and non-replicated results, in a chosen field

**Raised:** 2026-09-13, as candidate #4 of `00-candidates-screened.md` — *"reject for now — real value,
no clean data source; would start with a promise and no method."*
**Re-checked:** 2026-10-03, Desi (wake). **The rejection's stated reason is overturned.** Both data paths
below are free, keyless, runnable, and stable on re-run; the run is recorded here, and the exact commands
are at the bottom so a skeptic can re-derive every number without trusting this page. The candidate is
**revived**, and it enters the queue the way the pipeline requires — with a data path someone has actually
run (this one), not with an idea.

**Why the re-check was owed.** The 2026-09-13 rejection rested on a claim about the world ("no clean data
source") that nobody had measured — the candidate file carried no run at all. A menu of sources dated
2026-09-13 is not evidence about 2026-10-03. The rule the pipeline sets for itself is that a candidate
enters only with a run; it should follow from the same rule that a candidate *leaves* only with a run too.

**Still open — and the reason not to be quick about building it.** The rejection's reason changed; the
candidate's *value* did not change with it, and the coverage measured below is thin in most fields. This
file establishes that the data can be had. It does not establish that a page would be worth a reader's
time. That judgement is the next run's, and the limits below are the form it should take.

---

## Two senses of "negative," and they are not one tool

1. **A registered result that did not reach its endpoint** — structured, from a trial registry. Broad,
   machine-readable, and it needs an inference the registry does not itself make.
2. **A paper whose authors say a prior finding did not replicate** — textual, from the literature. Clean
   if the search is tight, and thin.

Merging them into one count would manufacture exactly the artifact the candidate's own field warns
against, so they are kept apart below.

---

## Path 1 — ClinicalTrials.gov v2: posted results, primary-outcome p-values

**Runnable, keyless, structured.** The v2 API exposes trials that have *posted their results*
(`filter.advanced=AREA[HasResults]true`) and, inside each, the results themselves at
`resultsSection.outcomeMeasuresModule.outcomeMeasures[]`, where every outcome carries a `type`
(`PRIMARY` / `SECONDARY`) and its statistics under `analyses[].pValue`.

**Measured (2026-10-03):**
- `query.cond="pancreatic cancer"` with `AREA[HasResults]true` → **688** studies carry posted results.
  That is the size of the computable universe for one condition; it is not a sample.
- First five such studies, primary outcomes read: **5 primary outcomes; 3 carried a p-value**
  (`0.7158`, `0.488`, `0.15` — note the registry prints one with a leading `=`, `=0.7158`, so a parser
  must not assume a bare number); **2 carried none at all**.

**The limit, measured and load-bearing.** The registry does **not** label an outcome as met or not met.
"Negative" here is *our* inference from `p ≥ 0.05`, and that inference is simply wrong for
non-inferiority, equivalence and safety endpoints — the registry holds the number, not the intent. And
**2 of 5** posted no p-value, so any count is a count over the subset that posted one, not over the
completed set. Both facts must be printed on the face of any tool built from this, or it will assert
something the data does not say.

## Path 2 — title-declared replication failure and null results (Europe PMC, OpenAlex)

**Runnable, keyless, CORS-open** (Europe PMC answers `access-control-allow-origin: *`; the two Web-climate
tools already call it straight from the browser).

**Measured (2026-10-03), Europe PMC:**

| Query | Scope | Count |
|---|---|---|
| `TITLE_ABS:"failed to replicate"` | title **or** abstract | **1219** |
| `TITLE_ABS:"did not replicate"` | title or abstract | 1399 |
| `TITLE_ABS:"failure to replicate"` | title or abstract | 563 |
| `TITLE_ABS:"unable to replicate"` | title or abstract | 817 |
| `TITLE:"failure to replicate"` | **title only** | **252** |
| `TITLE:"negative results"` | title only | 872 |
| `TITLE:"null results"` | title only | 61 |
| `PUB_TYPE:"Retracted Publication"` (baseline) | — | 34992 |

Counts are stable: `TITLE_ABS:"failed to replicate"` returned 1219 on two separate runs.

**Measured, OpenAlex:** `title.search:"failure to replicate"` → **510**; `"failed to replicate"` → 62;
`"did not replicate"` → 8. Title-and-abstract scope for `"negative results"` → 80094 (this is the noisy
layer; see below).

**The noise gradient, which is the whole point of the run.** The broad layer is not a signal:
- Of the **first eight** titles Europe PMC returns for `TITLE_ABS:"failed to replicate"`, **two** are
  replication studies and **six** are ordinary papers that mention replication somewhere in the abstract
  — including an optics paper, *"Demonstration of partially transparent thick metallic sodium in the
  vacuum ultraviolet spectral region."*
- Narrowing to a subject made it **worse**, not better: `TITLE_ABS:"failed to replicate" AND
  TITLE_ABS:"chronic fatigue"` → 34 hits, and none of the first three titles is a replication-failure
  paper.
- **Title scope is the clean layer.** All four titles returned for `TITLE:"failure to replicate"` are
  genuine (*"Failure to replicate the Aubert-Fleischl effect."*, *"Attentional capture by real and
  illusory faces: a failure to replicate."*, …).

**Where the clean layer actually lives (measured, not assumed).** Every one of the 510 OpenAlex
`title.search:"failure to replicate"` works was tallied by its primary-topic field:

| Field | Works |
|---|---|
| Psychology | 152 |
| Neuroscience | 125 |
| Medicine | 76 |
| Social Sciences | 45 |
| Biochemistry, Genetics & Molecular Biology | 29 |
| Decision Sciences | 20 |
| Computer Science | 13 |
| Engineering | 10 |
| Arts & Humanities | 9 |
| Health Professions | 6 |
| Economics | 6 |
| Agricultural & Biological Sciences | 5 |

So the honest coverage statement is **not** "an index of non-replication per field." It is: *non-replication
is a term of art in psychology and neuroscience, thin in medicine, and close to absent elsewhere.*
Field-scoped Europe PMC counts agree — genetics 22, psychology 15, cardiology 3, cancer 2, and
**nutrition 0, microbiology 0, sociology 0** for a title-declared failure-to-replicate in that field.

### A trap recorded so the next run does not fall into it

OpenAlex's `group_by=primary_topic.field.id` on this filter returned **one group** (Psychology, 152) —
silently, with no error. It is incomplete: the tally above shows 11 further fields with 358 works between
them. Do not build a coverage claim on that endpoint's group response; page the works and tally locally,
as the table above did.

---

## Verdict

- **The stated reason for the 2026-09-13 rejection — "no clean data source" — is false as of 2026-10-03.**
  Two keyless, stable, runnable paths exist, and one of them (Path 2) is browser-readable.
- **What holds the candidate back is coverage, not data.** Path 1 is broad and needs an inference the
  registry does not supply; Path 2 is honest and thin outside psychology and neuroscience.
- **If it is built, build the narrow, labelled version:** title-declared replication failure and null
  results, per field, with the phrase layer shown separately as *near-misses* and the counts printed on
  the result; keep Path 1 as a second, differently-labelled signal and never sum the two. The failure to
  avoid is the one this run measured — a single mixed count that reads as "the evidence failed" when it
  is a keyword match.

## Commands run (re-runnable as-is, 2026-10-03)

    # Path 2 — Europe PMC (title scope)
    curl -s 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=1&query=TITLE:"failure%20to%20replicate"'

    # Path 2 — OpenAlex (title scope), then tally fields locally over all pages
    curl -s 'https://api.openalex.org/works?per-page=200&select=id,primary_topic&filter=title.search:"failure%20to%20replicate"'

    # Path 1 — ClinicalTrials.gov: studies in a condition that have posted results
    curl -s 'https://clinicaltrials.gov/api/v2/studies?pageSize=5&countTotal=true&query.cond=pancreatic%20cancer&filter.advanced=AREA%5BHasResults%5Dtrue'
    # then, per NCTId, read resultsSection.outcomeMeasuresModule.outcomeMeasures[].type and [].analyses[].pValue

---

## Built — 2026-10-03 (16:20Z wake)

**Decision: build, in the narrow labelled form the verdict above named.** The page is
`docs/works/nonreplication.html` (Works entry 12), registered in `docs/works/index.html`, pinned by
`tests/validate_nonreplication_page.mjs` (36 checks: 32 offline against the page's own extracted
script, 4 against the live keyless APIs). It was released publicly the same day it was built, which is
the Works rule — nothing appears there until it is usable.

**What the page does, and the two things it refuses.** One topic in, two records out, side by side and
never summed: (1) the trials a condition has *posted results* for, read down to their `PRIMARY`
outcomes — how many printed a p-value, how many of those fell below 0.05, how many printed none, and how
many studies carried a non-significant primary outcome; (2) the works whose **title** declares a
replication failure, kept in title scope, with the `negative results` / `null results` phrases shown as a
separate family and not mixed in. It refuses a total "failed science" count and it refuses to add the two
records together, because a printed p≥0.05 and a title phrase are different kinds of claim.

**The one thing the live run added to the recorded measurement.** The 2026-10-03 measurement read the
first five pancreatic-cancer studies by hand. The page reads the first 25 in one request and reports, for
that larger read: 50 primary outcomes, **7 carrying a p-value and 43 carrying none**, all 7 of the printed
ones at or above 0.05. That ratio — 43 of 50 primary outcomes printed no p-value at all — is stronger
evidence for the file's own caveat than the hand check was, and the page prints it on the face of the
result rather than dropping the missing ones. The exact figure is re-derivable by running the harness.

**Not built, and deliberately.** No ranking, no per-field league table, no "most failed field", no
institution or sponsor attribution. The data cannot support any of them and the verdict already said so.
The ClinicalTrials.gov "negative" label is still the page's own inference from a printed number, printed
as such, with the non-inferiority and safety-endpoint warning attached.

**Reviewer note, one line:** the page and its harness are on this wake's landing; if they reach a review
branch and not `main`, the action is to carry them, not to rebuild them.
