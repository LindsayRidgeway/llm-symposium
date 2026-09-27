## 05 — Was this product recalled, and how long before the public record said so?

**Status:** candidate. **Data path: VERIFIED by hand, 2026-09-27** (one public source, free, no key,
and readable by a browser as well as a server; the calls and the counts are below, reproducible by
anyone in a terminal or a page).

**What it is:** type a product name — a medicine, a food, a device — and see the recall record the
FDA holds for it: the class, the firm, what was wrong, where it was distributed, and the dates. For
each recall it also prints the interval between the day the firm began the recall
(`recall_initiation_date`) and the day the recall entered the FDA's public weekly Enforcement Report
(`report_date`). That interval is the part no one else surface: a recall you learn about three months
after it began is a different fact from one you learn about in three weeks, and the record contains
both dates for every entry.

**Who it is for:** anyone who has just read that something was recalled and wants the record rather
than the headline; and anyone who wants to know how stale a "recall" notice can already be by the time
it reaches them.

**Why it is not a duplicate of anything already shipped.** `docs/works/retraction.html` asks whether a
*paper* was retracted. `trials.html` and `unreported-trials.html` read the *clinical-trial registry*.
`fetchable.html` asked whether the FDA's open data answered at all, and never used it — it measured
reachability, not content. Nothing on the site reads the **enforcement record** of drugs, food, or
devices. This is a different source, answering a question no other entry asks, and it is the only
entry whose subject is a physical product rather than a paper or a trial.

**Why it may never ship:** a recall record is not a finding that anyone was harmed. The classes
describe the *probability* of serious harm (Class I is the highest), not whether harm occurred, and a
large share of recalls are labelling, packaging or specification failures that never reached a person.
Built wrong — ranked, or phrased as "this company's dangerous products" — it becomes an accusation
tool, and this commons does not take sides. The whole value depends on stating that limit at the top,
not in a footnote.

### Verified data path — openFDA (free, no key, browser-readable)

One shape covers all three product types; the field names are identical.

```
https://api.fda.gov/{drug|food|device}/enforcement.json?search=<term>&limit=100&skip=0
```

Fields read: `recall_number`, `classification`, `status`, `recalling_firm`, `product_description`,
`reason_for_recall`, `distribution_pattern`, `recall_initiation_date`, `report_date`,
`center_classification_date`. Counts use `&count=classification.exact`.

**CORS verified** — `access-control-allow-origin: *` (header checked 2026-09-27), so a stranger's
browser can call it directly; this is the question `fetchable.html` says a server test cannot settle.
**No key required** — verified by ~24 keyless requests in one sitting.

Measured 2026-09-27 (source `meta.last_updated` = 2026-09-16):

| Product type | records | Class I | Class II | Class III | unclassified |
|---|---|---|---|---|---|
| drug | 17,975 | 1,747 | 14,511 | 1,715 | 2 |
| food | 29,415 | 12,926 | 14,729 | 1,760 | 0 |
| device | 39,969 | 3,632 | 35,307 | 1,029 | 1 |

**The interval, over the whole drug set** (every one of the 17,975 records carries both dates — zero
records are undated, and zero report before initiation):

| p10 | median | p90 | p99 | max | share over 90 days |
|---|---|---|---|---|---|
| 19 d | **47 d** | 197 d | 460 d | 2,455 d (≈6.7 yr) | **29.3 %** |

Food and device show the same shape (samples of 4,000: food median 45 d / p90 126 d / max 2,270 d;
device median 56 d / p90 175 d / max 3,334 d). The drug records span `report_date` 2012–2026.

**A field choice changes the count, which is itself worth printing.** For metformin,
`search=product_description:metformin` returns **91** recalls (84 Class II, 6 Class III, 1 Class I),
while `search=openfda.generic_name:metformin` returns **39**. The `openfda` block is only populated
when the FDA could map the product to a name, so the narrower field silently loses more than half. A
page that does not say which field it searched is reporting a number that depends on a choice it hid.

**First step:** the page — a product box and a type selector (drug / food / device), a latest-first
list of the records with their class, firm, reason and dates, the interval printed on each row, and a
one-line statement of scope. No ranking, no "worst offenders", no firm league table.

**Honest scope, to be stated on the page:** it reports what **one** public index (the FDA's
enforcement record) contained on the day it was read; a blank result means *no record found*, not
*never recalled*, because the index starts in 2012 for drugs and covers the US market; the interval
between initiation and report measures **record-keeping and publication timing, and mostly the FDA's
own classification step** — it is not evidence of concealment by the firm; and a recall is not proof
that anyone was harmed. It cannot tell you what to think — it can only show you what the record does
and does not contain.
