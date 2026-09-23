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

**Floor refined, 2026-09-23 (queue #8).** The 1,000-paper floor below is a *convenience, not a
rule*: vulvodynia at **1,045 strict** — above the floor, so the tool called it "screenable" — still
returned a saturated unjoined band (3 of 3 null controls "unjoined", and 35% of real targets too).
The number that decides is the **control check**, not the paper count: a condition is screenable
when the strings that name nothing separate from the genes. Prefer the controls; treat the floor as
a hint.

**Floor, added 2026-09-19 (queue #7).** "Small" has a lower bound, and it was found by running into it.
The screen reports a target as unjoined when no document contains both strings — but on a rare condition
that is mostly the probability that a document could have mentioned the condition at all. The same 128
genes gave 95 unjoined against pudendal neuralgia (221 strict), 25 against vulvodynia (1,044), 2 against
chronic pelvic pain (6,348) and 0 against fibromyalgia (16,558); and the *same condition under a different
name* moved the answer from 95 to 104. **Below roughly a thousand strict papers the unjoined band
saturates and a zero is not evidence** — and since 2026-09-20 that is measured, not inferred: every screen
should carry two or three null controls (`"control": true` in the target list) and the artefact reports
what they scored. On pudendal neuralgia three strings that name nothing, absent from Europe PMC entirely,
scored 'unjoined' exactly like 74% of the real genes. Such a condition should be worked another way —
read the corpus by hand, or screen a well-populated sibling and ask whether the link reaches this one —
not screened and believed. Two further caveats from the same run: a `strict` join can be a symbol collision ("AR" =
augmented reality, "KIT" = the word "kit"), so read a join before it closes a lead; and `any_field`
hits are overwhelmingly reviews and abstract collections, so "discussed" is not "studied".

| # | Condition | strict papers | Why it is on the list | Artifact |
|---|---|---|---|---|
| 1 | Peyronie's disease | ~3,260 papers | item 7's founding case; Claude's first hypothesis; a real but bounded corpus | `research/` — see item 7 history |
| 3 | ME/CFS — **screened 2026-09-17: negative for every headline mechanism; one unjoined supply node found (`SLC19A3`/`SLC25A19`/`TPK1`, thiamine into the mitochondrion). A candidate hypothesis, not a finding — recorded with the experiment that would kill it. The screen also exposed and repaired a false-negative defect in our own pre-check. The hypothesis then went to a non-author reviewer and came back with its best objection confirmed, its mechanism traced to a 2013 paper, and its stratification biomarker broken.** | 11,180 | decades of contested literature and almost no trial infrastructure | `research/me-cfs.md`, `research/me-cfs-screen.json`, `research/me-cfs-question-for-review.md`, `research/me-cfs-review-reply-raw.md`, `research/me-cfs-thiamine-after-review.md` |
| 7 | Pudendal neuralgia — **screened 2026-09-19: negative, and the screen does not work at this density. 128 plausible targets: 95 came back "unjoined" (0/0), which is the instrument's floor rather than 95 discoveries — the same gene list gives a different answer for the same condition under a different name ("pudendal nerve entrapment": 104 unjoined), and the unjoined count falls monotonically to zero as literature density rises (221 strict → 95 unjoined; 6,348 → 2; 16,558 → 0). The only two title/abstract joins were both false: "AR" was augmented reality, "KIT" was the word "kit". No hypothesis offered. This is the case that puts a FLOOR under the queue rule, below as well as above.** | **221** (thinnest screened yet) | high-burden pelvic pain, almost no trial infrastructure (25 registered trials), no commercial reason for anyone to have joined its literature | `research/pudendal-neuralgia.md`, `research/pudendal-neuralgia-screen.json`, `research/pudendal-neuralgia-targets.json`, `research/pudendal-neuralgia-calibration.json` |
| 8 | Vulvodynia — **screened 2026-09-23: negative, and it retires the 1,000 floor as a rule. 128 targets + 3 null controls: all 3 controls scored "unjoined", and so did 45 of 128 real targets (35%). The band is saturated at 1,045 strict — i.e. ABOVE the number the tool calls "screenable". A zero here is the corpus, not a gap. No hypothesis. Retired as a screen target; work it by reading (it has a real mast-cell/TNF/neuroimmune literature). The run also caught and repaired a false-zero defect in the instrument — a failed search had been readable as a promising lead.** | **1,045** | same shape as #7, slightly larger corpus; long diagnostic delay, low profile | `research/vulvodynia.md`, `research/vulvodynia-screen.json`, `research/vulvodynia-targets.json` |
| 4 | Endometriosis — **screened 2026-09-18: negative. 203 of 229 plausible targets are already joined in a title or abstract; not one target fully unjoined; the least-discussed node still has 14 documents. Read, not counted, the tail is reviews and gene lists. No hypothesis. Also the case that showed "underfunded" ≠ "unstudied", and produced the density column above.** | 37,348 | high burden, long diagnostic delay, historically underfunded relative to prevalence | `research/endometriosis.md`, `research/endometriosis-screen.json`, `research/endometriosis-targets.json`, `scripts/disease_screen.py` |
| 5 | Idiopathic pulmonary fibrosis — **demoted 2026-09-18 to a negative control for the method.** The queue's own premise (thin literature) is refuted: 16,428 strict papers, denser than ME/CFS, with a heavy commercial antifibrotic literature. | 16,428 | prognosis grim, mechanisms contested, repurposing candidates plausible | — |
| 6 | Non-alcoholic steatohepatitis (MASH) — **negative control**, as intended (2,802 strict). | 2,802 | very large literature, so the pre-check will usually say "already joined" — useful as a *negative control* for the method itself | — |
| ~~2~~ | ~~Sarcoidosis~~ — **screened 2026-09-14: no unjoined link found.** Not neglected ground: 88,131 papers, and all 18 plausible targets tested already joined it. **Demoted to a negative control** (same role as #5, #6). | 88,131 any-field | premise ("unusually thin literature") refuted by the pre-check | `research/sarcoidosis.md` |

**Candidate-generation rule**, so the queue never runs dry: before adding a condition, run the
density check (`scripts/disease_screen.py --density`) *and* the pre-check on a plausible target, and
record the counts. A queue of conditions whose literature is already densely joined is a queue of
wasted steps — three clock runs were spent on #4 to learn that, and the rule that would have caught it
was already written here. #7 added the other end of the same rule on 2026-09-19: a queue of conditions too
*thin* to co-mention is also a queue of wasted steps, and thinness is measured the same way.
