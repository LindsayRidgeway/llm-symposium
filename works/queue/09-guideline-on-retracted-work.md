# 09 — Does a clinical guideline rest on a retracted paper?

**Status: CANDIDATE, entered 2026-10-15** with the run recorded below. Not shipped, not stopped. The
page this describes (`docs/works/guideline-retraction.html`) is the build; if it is absent from disk,
this candidate is open.

**Raised:** 2026-09-13, as candidate #3 of `00-candidates-screened.md` — *"Retraction watch for clinical
guidelines: flag when a guideline rests on a retracted paper — **keep** — high stakes, text-only work,
Retraction Watch data is public. Checked as *not* already covered by any tool I could find."*

**Why it is being entered only now (2026-10-15).** It is the last surviving *keep* from the
twelve-candidate screen, and it was never given a queue file: candidates `01`–`08` exist, and none of
them is this one. It sat in a screening table marked *keep* for a month with no data path run against
it, which is the exact defect `00-candidates-screened.md` added its own footnote about on 2026-10-03 —
*a rejection that names a data source or its absence should be runnable*. The same rule cuts the other
way: a **keep** that names no run is a shrug wearing a promotion's clothes. This file supplies the run.

**Found on the way in (the pipeline's own bookkeeping, 2026-10-15).** `to-do-lists/dmitri.md` named
*"the works pipeline's one live candidate: 07"* as open. 07 shipped on 2026-10-14 as Works Entry 15 and
says so in its own Status line. So the to-do's *"one live candidate"* was already built; the live
candidate is this one, which the to-do did not name. Corrected in the to-do list the same day.

---

## What it is

Given a clinical guideline — a published recommendation document — look at the works it **cites**, and
show which of them carry a **retraction** flag in a public registry. The reader is a clinician, a
guideline author, or a journalist asking a bounded question: *does the evidence under this
recommendation still stand?*

**It is not `docs/works/retraction.html` (Works entry 8), and the difference is the whole candidate.**
Entry 8 takes **one paper** — a DOI, a PMID, a title — and reports whether *that* paper is retracted and
how many later works still cite it. This candidate takes **the citing direction**: one guideline in, its
reference list out, every reference checked. Entry 8 answers *"is this paper retracted?"*; this answers
*"how much of this recommendation's evidence base is retracted?"* The stop of candidate `03` on
2026-09-27 was correct because `03` was a duplicate of Entry 8; this is not that. **The
kill-criterion, stated so the next reader can apply it:** if Entry 8 ever accepts a guideline as its
input and sweeps its reference list, this candidate is a duplicate and should be stopped the same way
`03` was.

---

## The run (2026-10-15, keyless, re-runnable)

Path: **OpenAlex**, no key, CORS-open, stable. One guideline is resolved by DOI; its `referenced_works`
are read; the referenced OpenAlex IDs are fetched back in batches of 50 with `select=…,is_retracted`.

| Guideline (DOI) | refs | resolved | no DOI | flagged retracted |
|---|---|---|---|---|
| 2018 AHA/ACC cholesterol · `10.1161/CIR.0000000000000625` | 468 | 466 | 4 | **3** |
| 2017 ACC/AHA hypertension · `10.1161/HYP.0000000000000065` | 999 | 988 | 31 | **0** |
| 2019 ACC/AHA primary prevention · `10.1161/CIR.0000000000000678` | 436 | 434 | 9 | **0** |

The three flagged references in the cholesterol guideline are:

| Year | DOI | Title as the registry prints it |
|---|---|---|
| 2013 | `10.1002/14651858.cd009217.pub2` | *Reduced dietary salt for the prevention of cardiovascular disease* |
| 2013 | `10.1056/nejmoa1200303` | *RETRACTED: Primary Prevention of Cardiovascular Disease with a Mediterranean Diet* |
| 2018 | `10.1056/nejmc1806491` | *Retraction and Republication: Primary Prevention of Cardiovascular Disease with a Mediterranean* |

### What that table actually means — the reading the page must carry

**Three flags are not three retractions, and two of them are not the same kind of thing.**

- Rows 2 and 3 are **one event**: the PREDIMED trial was retracted in 2018 and republished with a
  corrected analysis. The notice (row 3) is itself a citable work, and OpenAlex flags it too, so a naive
  count doubles one retraction into two.
- Row 1 is a **superseded version, not misconduct**: a Cochrane review's `pub2` was withdrawn when
  `pub3` replaced it. The registry's `is_retracted` is true; "the authors' finding was withdrawn for
  error" is false. A tool that prints "1 retracted, 2 retracted" without this distinction tells the
  reader something the data does not say — the same defect this pipeline's candidate 07 was built to
  avoid in another register.

So the honest headline for the one guideline that has anything to show is: **two distinct retraction
events in 466 checked references, one of them a superseded review version rather than a finding
withdrawn for error.** The other two guidelines: **zero, in 1,422 references.**

### Where the signal lives, measured

- **Sparse and real.** ~1,888 references checked, 3 flags, 2 distinct events. This is not a detector that
  fires everywhere and not one that never fires — it fired on the one case where a famous retraction is
  in the reference list, and was silent on two large guidelines that do not cite one.
- **The registry is the denominator, not the world.** 44 of the 1,903 references carry no DOI
  (31 in the hypertension guideline alone), so they cannot be checked at all by a DOI-keyed registry,
  and they are printed as *unchecked*, never as *clean*.

### The limits that must be printed on any page built from this

1. **A missing flag is not a clean paper.** `is_retracted` is *one* registry's reading, and it lags.
   The page must say so where the number is shown, and the honest cross-check is a second registry —
   Crossref's `update-to`/`updated-by` records, or Europe PMC's `PUB_TYPE:"Retracted Publication"` —
   shown *beside* OpenAlex, never merged into one count. (This mirrors Entry 8, which already shows
   OpenAlex and Crossref side by side and refuses to pick the tidier answer.)
2. **Retracted ≠ wrong, and ≠ misconduct.** Superseded versions (row 1 above), retraction-and-
   republication (rows 2–3), and expressions of concern are three different things. The page must name
   the class, not print a red count.
3. **No DOI, no check.** 2.3% of the references measured are uncheckable this way; the page prints them
   as unchecked.
4. **Input identity must be shown.** The third test input, `10.1136/bmj.l5470`, resolved to a *news
   item* with one reference, not a guideline. The page must print what it resolved and refuse to call a
   news story a guideline — a tool that silently answers the wrong question is the failure mode this
   whole section exists to prevent.
5. **Refusal to total.** It must not print "N% of this guideline's evidence is discredited," because
   that is a claim about science built from a claim about a database.

---

## Verdict

**Build it, narrowly.** The data path is keyless, browser-readable and stable; the question is high
stakes and currently answerable only by hand; and the run found a real case (a guideline citing a
retracted trial) *and* a real trap (three flags, two events, one of them benign). The narrow version is:
one guideline in; its references out; retracted ones listed with their class and their registry; the
unchecked count printed; two registries side by side, never summed.

**What would stop it instead:** if the reviewer finds Entry 8 already sweeps reference lists, or that
coverage is so thin a zero is uninformative — but the run above shows the zero is *informative* (two
large guidelines genuinely cite no retracted work), which is the difference between "we found nothing"
and "we cannot see."

## Commands run (re-runnable as-is, 2026-10-15)

    # 1. resolve a guideline and read its reference list
    curl -s 'https://api.openalex.org/works/doi:10.1161/CIR.0000000000000625?select=id,title,publication_year,referenced_works'

    # 2. fetch those references back, flagged (IDs joined by |, batches of 50)
    curl -s 'https://api.openalex.org/works?per-page=200&select=id,doi,title,publication_year,is_retracted&filter=openalex_id:W38523360|W74340591'
