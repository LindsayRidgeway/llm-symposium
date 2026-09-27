# The retraction flag, and the notice it is supposed to point at

*A measurement of OpenAlex's `is_retracted` flag against Crossref's retraction records, made live
on 2026-09-27. Every number below came from a request made that day, with the exact query printed so
it can be re-run. `mailto=desi.s.amigo@gmail.com` was sent on every ask, as both services ask. No API
key was used.*

## The question

Our retraction checker (`scripts/check_retracted_refs.py`, Works entry 8) does three things per
reference: it resolves the work in OpenAlex, reads OpenAlex's `is_retracted` flag, and then confirms
the flag against Crossref by asking that work's own record whether it carries a retraction update. The
third step exists because a flag nobody can re-derive is an assertion. So the obvious question, which
we had never measured across the index rather than one document:

> When a reader trusts OpenAlex's flag, can they reach a retraction notice through the work's own
> Crossref record — and how often can they not?

## The two populations, side by side

| index | query | works |
|---|---|---:|
| Crossref | `https://api.crossref.org/works?filter=update-type:retraction&rows=0` | 75,785 |
| OpenAlex | `https://api.openalex.org/works?filter=is_retracted:true&per-page=1` | 136,112 |

These are not the same object and the ratio between them (1.80) is a description, not an error.
Crossref's filter counts *works carrying a retraction update record*; OpenAlex's flag counts *works
marked retracted*, and the marking lands on both ends of a retraction — the notice and the retracted
article. The next two sections measure each direction of that overlap directly.

## Direction 1 — Crossref says retracted: is it flagged?

Sample: the first 200 records returned by
`...&filter=update-type:retraction&rows=200&cursor=*&select=DOI,update-to`,
plus every distinct `update-to` DOI those records name.

| measured | result |
|---|---:|
| records sampled | 200 |
| records OpenAlex resolves | 200 / 200 |
| records OpenAlex flags `is_retracted: true` | **200 / 200** |
| distinct `update-to` target DOIs | 220 |
| targets OpenAlex resolves | 220 / 220 |
| targets OpenAlex flags | **219 / 220** |

So the flag tracks Crossref's retraction record almost exactly in this direction.

**Shape of the relation, which matters to anyone reading it.** Of the 200 sampled records, in 111 the
only `update-to` target is the record itself, and in 89 at least one target is a different DOI. A
second, random pair of draws (`...&sample=100` twice, 200 records pooled) gives 93 self-referencing and
107 with a distinct target, 0 with no target at all in either sample. Reading the examples, the
self-referencing shape is mostly publishers marking the article retracted *in place* — the record's own
title becomes `RETRACTED: <title>` and the DOI does not change (all six examples inspected are Elsevier,
e.g. `10.1016/s0022-510x(00)00298-7`). The consequence for a reader is not that the relation is wrong;
it is that the relation alone does not say which side is the notice, so a consumer has to read both
fields *and* the title. `update-to` sources in the pooled random sample: `retraction-watch` 145,
`publisher` 133 (some records carry more than one).

## Direction 2 — OpenAlex says retracted: can the notice be reached?

Sample: 200 works drawn at random from the flag itself, via
`https://api.openalex.org/works?filter=is_retracted:true&per-page=200&sample=200&select=doi,cited_by_count,title,publication_year,type`,
then one Crossref request per DOI (`https://api.crossref.org/works/<doi>?mailto=...`).

| what the work's own Crossref record shows | works | share |
|---|---:|---:|
| a retraction update in either field (`update-to` or `updated-by`, type `retraction`) | 184 | 92.0 % |
| no update of any kind | **11** | 5.5 % |
| not in Crossref at all | 2 | 1.0 % |
| no DOI in OpenAlex | 3 | 1.5 % |

**16 of 200 — one in twelve — are works whose flag a reader cannot follow to a relation.** The
11 with no update at all are not obscure: the sample includes `10.1021/acsomega.3c07606` (164
citations, "RETRACTED: Synthesis of Metal–Organic Framework-Based ZIF-8@ZIF-67 Nanocomposites…"),
`10.1210/er.2015-1045` (89 citations, Endocrine Reviews 2015), `10.1109/wccct.2016.68` (11),
`10.1109/iccmc51019.2021.9418362` (7). Most carry `Retracted:` or `RETRACTED:` in the title, which is how
the reader finds out anyway — but the title is prose, and the relation field, which is the machine-
readable statement, is empty.

**Top of the ranking, for contrast.** The 100 most-cited flagged works
(`...&filter=is_retracted:true&sort=cited_by_count:desc&per-page=100`) are in much better shape:
100/100 are in Crossref, 69 carry `updated-by` (article → notice), 30 carry `update-to` (notice →
article), and 1 carries neither — `10.1038/nrg2336` (625 citations, *Nature Reviews Genetics* 2008,
"Plant genetic engineering for biofuel production"), whose only update is a `correction`. The flag is
right about that one and Crossref's record is the thing missing the retraction; either way it is a
single record worth a look, and it is the most-cited work in the set that a reader cannot confirm.

Note the split in direction (69 `updated-by` vs 30 `update-to`): a consumer that reads only one of the
two fields will miss a third of the top of the list.

## What this changes on our side

- `scripts/check_retracted_refs.py` already checks **both** fields and prints flags Crossref does not
  confirm as `unconfirmed`. Direction 2 puts a number on that population for the first time: about 8 %
  of flagged works, ~2 % at the top of the citation ranking, cannot be confirmed from the record.
- The script's `unresolved` counter (ids that no longer resolve) is a different hole from this one: an
  id that resolves is not the same as a flag that confirms. Both are printed, neither is a pass.
- The self-referencing `update-to` shape from direction 1 says the confirmation step cannot rely on
  `update-to` alone to find the notice; the notice may be the record itself.

## Limits, in the same voice as the numbers

- Two draws of 200 from 136,112 and 75,785. The rates are ±3–4 points at these sizes; the named
  examples are certain, the percentages are estimates.
- "No update of any kind" means the Crossref record for that DOI, read on 2026-09-27, carried neither
  `update-to` nor `updated-by` and no other update type. It does not mean the work is not retracted.
- Nothing here is a judgement about OpenAlex's flag, which is right in the examples inspected; the
  question is whether the flag is *re-derivable* by a reader who does not already trust it.

## Every query used

```
# populations
api.crossref.org/works?filter=update-type:retraction&rows=0
api.openalex.org/works?filter=is_retracted:true&per-page=1

# direction 1 (deterministic) and its shape
api.crossref.org/works?filter=update-type:retraction&rows=200&cursor=*&select=DOI,title,update-to,type,publisher,container-title
api.crossref.org/works?filter=update-type:retraction&sample=100&select=DOI,title,update-to,type,publisher,container-title   (twice)
api.openalex.org/works?filter=doi:a|b|c…&per-page=50&select=doi,title,is_retracted,publication_year   (50 DOIs per ask)

# direction 2
api.openalex.org/works?filter=is_retracted:true&per-page=200&sample=200&select=doi,cited_by_count,title,publication_year,type
api.crossref.org/works/<doi>?mailto=desi.s.amigo@gmail.com    (one per sampled work, 198 asks)

# the ranking, for contrast
api.openalex.org/works?filter=is_retracted:true&sort=cited_by_count:desc&per-page=100&select=doi,cited_by_count,title,publication_year
```

Total: 353 asks across the probes, 0 failed, no key.
