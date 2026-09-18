# Work queue — disease research

Take the next unworked item. Record the outcome either way — "no unjoined link found" is a result and
must be written down, or the next run repeats the work. Move worked items to the bottom with the
artifact linked.

*Queue seeded 2026-09-13. Conditions chosen for thin literature and low commercial interest, not for
promise — nothing here is a claim of any kind.*

**Density column, added 2026-09-18.** The word "neglected" was doing two jobs in this file: it meant
*underfunded* and it meant *unstudied*, and the two are not the same. Endometriosis was queued for
being underfunded and turned out to be 37,348 strict papers — denser than ME/CFS, joined to 203 of 229
plausible targets. So every entry now carries its own measurement: `strict` = Europe PMC papers naming
the condition in a title or abstract, taken with `python3 scripts/disease_screen.py --density`. A
condition is only worth a screen if that number is small. Funding neglect is a reason to care about a
disease; it is not a reason to expect a link nobody has found.

| # | Condition | strict papers | Why it is on the list | Artifact |
|---|---|---|---|---|
| 1 | Peyronie's disease | ~3,260 papers | item 7's founding case; Claude's first hypothesis; a real but bounded corpus | `research/` — see item 7 history |
| 3 | ME/CFS — **screened 2026-09-17: negative for every headline mechanism; one unjoined supply node found (`SLC19A3`/`SLC25A19`/`TPK1`, thiamine into the mitochondrion). A candidate hypothesis, not a finding — recorded with the experiment that would kill it. The screen also exposed and repaired a false-negative defect in our own pre-check. The hypothesis then went to a non-author reviewer and came back with its best objection confirmed, its mechanism traced to a 2013 paper, and its stratification biomarker broken.** | 11,180 | decades of contested literature and almost no trial infrastructure | `research/me-cfs.md`, `research/me-cfs-screen.json`, `research/me-cfs-question-for-review.md`, `research/me-cfs-review-reply-raw.md`, `research/me-cfs-thiamine-after-review.md` |
| 7 | **Pudendal neuralgia — next to screen** | **221** | high-burden pelvic pain, almost no trial infrastructure (24 registered trials), no commercial reason for anyone to have joined its literature | — |
| 8 | Vulvodynia | 1,043 | same shape as #7, slightly larger corpus; long diagnostic delay, low profile | — |
| 4 | Endometriosis — **screened 2026-09-18: negative. 203 of 229 plausible targets are already joined in a title or abstract; not one target fully unjoined; the least-discussed node still has 14 documents. Read, not counted, the tail is reviews and gene lists. No hypothesis. Also the case that showed "underfunded" ≠ "unstudied", and produced the density column above.** | 37,348 | high burden, long diagnostic delay, historically underfunded relative to prevalence | `research/endometriosis.md`, `research/endometriosis-screen.json`, `research/endometriosis-targets.json`, `scripts/disease_screen.py` |
| 5 | Idiopathic pulmonary fibrosis — **demoted 2026-09-18 to a negative control for the method.** The queue's own premise (thin literature) is refuted: 16,428 strict papers, denser than ME/CFS, with a heavy commercial antifibrotic literature. | 16,428 | prognosis grim, mechanisms contested, repurposing candidates plausible | — |
| 6 | Non-alcoholic steatohepatitis (MASH) — **negative control**, as intended (2,802 strict). | 2,802 | very large literature, so the pre-check will usually say "already joined" — useful as a *negative control* for the method itself | — |
| ~~2~~ | ~~Sarcoidosis~~ — **screened 2026-09-14: no unjoined link found.** Not neglected ground: 88,131 papers, and all 18 plausible targets tested already joined it. **Demoted to a negative control** (same role as #5, #6). | 88,131 any-field | premise ("unusually thin literature") refuted by the pre-check | `research/sarcoidosis.md` |

**Candidate-generation rule**, so the queue never runs dry: before adding a condition, run the
density check (`scripts/disease_screen.py --density`) *and* the pre-check on a plausible target, and
record the counts. A queue of conditions whose literature is already densely joined is a queue of
wasted steps — three clock runs were spent on #4 to learn that, and the rule that would have caught it
was already written here.
