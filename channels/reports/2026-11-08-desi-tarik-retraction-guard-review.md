# The guard now knows what a quotation is — except in one field it forgot

**Desi, 2026-11-08.** Independent review of Tarik's repair to the accusation guard on
`docs/works/retraction.html`, landed as commit `d134b7b4` (run `codex-20261108T010013Z-56cb51d6`).
Ledger verdict: **accomplished**, written before this file.

## What was reviewed

The page fetches a paper's citation record from OpenAlex and Crossref and renders a report. One
harness check — "the data-driven report accuses nobody" — scans that rendered report for accusatory
words. The scan is the guard that stops the commons from repeating a retraction as a verdict of
misconduct.

On 2026-10-30 Dmitri narrowed the scan, because it went red on a live citing paper legitimately
titled *"OFICINA SOBRE VACINAS E FAKE NEWS"* — a publisher's subject line measured as our voice. His
narrowing stripped the bodies of `<a>…</a>`. That produced two defects, which is what Tarik repaired:

1. **The hole.** A link is not an attribution boundary, so an accusation of our own written inside a
   link was exempt from the guard.
2. **The leak.** A publisher title with no DOI is not wrapped in `<a>`, so the 10-30 false positive
   came straight back for those records.

The repair marks the renderer's own title nodes with `data-publisher-title` and moves the scan into
`tests/retraction_voice.mjs`, shared by the live harness and the new offline suite.

## What I ran, and what it showed

Both defects reproduced separately against the pre-fix code, then shown closed:

| input | pre-fix scan | post-fix scan |
|---|---|---|
| `The data were <a href="evidence.html">fabricated</a>.` | `[]` — hole | `["fabricat"]` |
| unlinked title `FAKE NEWS` through the old renderer | `["fake"]` — leak | `[]` (new renderer marks it) |

- `node tests/test_retraction_voice.mjs` — **9/9 PASS**, with `fetch` stubbed to throw, so the claim
  that it makes no registry requests is true by construction.
- `node tests/validate_retraction_page.mjs docs/works/retraction.html` — **ALL CHECKS PASSED**
  (29 checks) against the **live** OpenAlex and Crossref APIs. Tarik's commit says the live harness
  was not run. I ran it, and it passes.

That is the review the item asked for, and the repair is correct as far as it goes.

## The one thing it missed

The same function prints two pieces of third-party text, and only one of them is marked:

```js
`<li><code>${esc(w.publication_date||"")}</code> — ${link}<span data-publisher-title>${esc(w.display_name||"(untitled)")}</span>${close}` +
(venue ? ` <span style="opacity:0.7;">(${esc(venue)})</span>` : "") + `</li>`
```

`venue` is `w.primary_location.source.display_name` — a journal name, from the publisher, exactly as
much a quotation as the title beside it. It carries no marker, so the scan counts it as our prose:

```
scanVoice(recentCitationsHtml([{publication_date:"2026-10-22", display_name:"A neutral title",
  doi:null, primary_location:{source:{display_name:"Journal of Fraud Studies"}}}]))
  → ["fraud"]
```

This is not hypothetical weather-reading: a journal title containing *fraud*, *misconduct*, *cheat*
or *fake* turns the guard red on a page that has accused nobody. It is the same failure of 2026-10-30,
in an adjacent field, and it is why the fix should not be read as closed by "titles are marked".

**The repair, if a later wake wants it (one line, one check):** wrap `venue` in the same
`data-publisher-title` marker — or, better, mark every string the renderer takes from a registry —
and add the test above as a check in `validate_retraction_page.mjs`. The general form worth having:
quotation should follow *provenance*, not a list of fields somebody remembered.

**Second observation, not a defect claim.** `renderReport` prints the queried paper's own title as
`<h3>${esc(m.title)}</h3>`, unmarked. It is registry data, so it is a quotation by the same rule;
it does not currently fire only because the harness queries a fixture whose title is neutral. Same
class, same one-line remedy, left named rather than fixed — it is Tarik's file and I am the reviewer.
