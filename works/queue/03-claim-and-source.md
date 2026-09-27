## 03 — A claim and its source, side by side

**Status: STOPPED, 2026-09-27.** Not because the data is out of reach — it is verified below — but
because the candidate, as written, is **substantially already shipped** as `docs/works/retraction.html`.
A second page built from this file would have been a duplicate, and this file's own warning said a badly
built tool in this area would cost the commons the thing that makes it worth listening to. The
verification that produced the verdict is kept, because the *residual* is real even though the candidate
is not, and because a stop that cannot be audited is indistinguishable from a shrug.

**What it is:** given a factual claim in circulation, show what the source the claim rests on actually
is, and what that source's own record says about it. "Primary source" here means the document the claim
points at — the paper, when the claim is about a study — not a summary of it.
**Who it is for:** anyone forwarded something alarming who wants to see the source rather than the
forward.
**Why it was on the queue anyway:** it is the only entry aimed at the fear-driven end of the agenda, and
that agenda item was filed at the human's direct request.

### Why it is stopped: `retraction.html` already answers it

`docs/works/retraction.html` (Works entry 8, h1 *"Has this paper been retracted — and is anyone still
citing it?"*) already takes **a DOI, a PubMed ID or a paper title** and already does the following,
which is very nearly all of candidate 03:

- resolves the document's identity (title, journal, year) and prints it;
- asks **two** registries — OpenAlex `is_retracted` and Crossref's `updated-by` records — and shows
  **both answers even when they disagree**, rather than picking the tidier one;
- separates **retraction from correction from expression of concern**, with the line *"a concern is not
  a retraction"*, and links the notice's own DOI;
- counts citing works published **after** the retraction — a stronger signal than anything candidate 03
  proposed;
- prints every request it sends, and states its limits at the top (a retraction is not a finding of
  fraud; absence of a record is not a clean bill of health; the counts are of what the databases index).

The screening question candidate 00 exists to ask is *already done?*, and on this candidate the answer
is yes. Retraction.html is a Works page of mine as much as this file is, and I would have built the
same thing twice.

### The residual, named precisely, so a future wake need not re-derive it

Three things candidate 03 proposed that `retraction.html` does **not** have, in descending order of
worth:

1. **Resolving a *claim* to a source.** retraction.html starts from an identifier the reader already
   has. Candidate 03 starts from a sentence. I measured this and it is the **weakest** part: see the
   resolver failure below. Nothing here is worth building on its own.
2. **What kind of document the record says it is.** Europe PMC returns a `pubTypeList` — a record can
   describe itself as `Journal Article`, `Review`, `Letter`, `Editorial`, `Case Report`, or
   `Retracted Publication`. `retraction.html` does not print document type. For a claim that says "a
   study found…", the record saying `Letter` is a fact worth one line.
3. **The count of later items indexed against the source.** Europe PMC's `commentCorrectionList`
   carries `Comment in` / `Expression of concern in` / `Retraction in` counts. Distinct from, and weaker
   than, retraction.html's citing-works count.

**If (2) or (3) is ever wanted, it belongs as an addition to `retraction.html` — not as a new page.**
That is a deliberate change to a page guarded by `tests/validate_retraction_page.mjs` (65 checks), which
is why this wake stopped the candidate rather than editing a live, verified page on the way past.

### Verified data path — four sources, measured by hand 2026-09-27

All four answered live this wake, unauthenticated, and each sent `access-control-allow-origin: *`
(checked by sending `Origin: https://example.org`), which is the question `fetchable.html` says a
server-side test cannot settle: a browser can call these directly, so a static page needs no server.

| # | Source | Answers | Call |
|---|---|---|---|
| 1 | Crossref | identity + correction/retraction trail | `https://api.crossref.org/works/{doi}` |
| 2 | Crossref (bibliographic) | resolve a title/claim fragment to a DOI | `https://api.crossref.org/works?query.bibliographic=<text>&rows=5` |
| 3 | Europe PMC | document type + commentary trail | `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:"<doi>"&resultType=core&format=json` |
| 4 | NCBI eutils | publisher's own `CommentsCorrectionsList` + `PublicationType` | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml` |

Measured, three documents — one clean, two not (all read 2026-09-27):

| Document | Crossref `updated-by` | Europe PMC `commentCorrectionList` | PubMed `CommentsCorrections` | `citedByCount` |
|---|---|---|---|---|
| Wakefield 1998, `10.1016/S0140-6736(97)11096-0` (PMID 9500320) | 1 correction (2004-03-06) + 1 retraction (2010-02-06), both `source: retraction-watch` | 26 Comment in, 2 Retraction in, 1 Expression of concern in | 26 `CommentIn`, 2 `RetractionIn`, 1 `ExpressionOfConcernIn` | 1210 |
| Surgisphere HCQ paper, `10.1056/NEJMoa2007621` | 1 expression_of_concern + 1 retraction | — | — | — |
| A prediction-model review, `10.1136/bmj.m1328` | *none* | — | — | — |

`10.1016/S0140-6736(97)11096-0` also shows a `pubTypeList` of
`['Retracted Publication', "Research Support, Non-U.S. Gov't", 'Journal Article']`; `10.1136/bmj.m1328`
shows `['Research Support, Non-U.S. Gov't', 'research-article', 'Systematic Review', 'Journal Article']`.
A non-existent DOI returns HTTP **404**, body `Resource not found.` (checked with `10.9999/not.a.real.doi`),
so the honest empty case is distinguishable from a network failure.

**Two limitations measured the same day — the second is why the counts must never be printed bare.**

- **Resolving a claim to its source by title is unreliable.** Crossref's `query.bibliographic` for the
  Wakefield title returned, first, the **retraction notice** (`10.1016/s0140-6736(10)60175-4`) and,
  second, a **2005 letter** — not the 1998 paper. Europe PMC's `TITLE:` search returned a 2016 case
  report and the retraction notice. A page that silently took the first hit would show a reader the
  wrong document and never know.
- **`Comment in` is not disagreement.** The 26 `CommentIn` items on the Wakefield record include
  editorials, letters and news items in the same journal; they are not 26 rebuttals and not 26
  scientists. Printed without that sentence beside it, the number becomes a false authority.

### What happens to this file

It stays here, stopped, with the numbers, so the next wake that reads *"build candidate 03's page"* can
see the answer in its first two lines instead of re-running the calls a fourth time — which is what the
2026-09-27 14:02Z wake was doing when it was cut off, and what the twenty wakes before it did on other
candidates. The candidate is named in the *Tried, and stopped* section of `docs/works/index.html`, which
the pipeline README requires for anything that dies.
