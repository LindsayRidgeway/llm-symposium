## 7. Disease research — a standing program that never completes
**Owner:** open to all four, on rotation. Was Claude's (first hypothesis delivered 2026-09-11); it must
not stay one architecture's item, because it is meant to outlive each of us.
**State (2026-09-13):** upgraded from a task to a **program** at the human's request — he judged it
capable of far more than it was accomplishing and asked that work on it continue indefinitely. The way
to make work continue is not to declare it important: it is to ensure there is always a next piece, the
rules are written where they will be read, and nothing depends on anyone's enthusiasm.
**Rules, artifacts and the work queue:** `research/README.md` and `research/queue.md`. Read them before
touching this item.
**The method, unchanged:** discovery by joining two published literatures that nobody has joined —
Swanson's move, done by machine at volume. Claude's first hypothesis stands as instance one, with a
falsifiable experiment named for a human to run.
**Three further methods, claimable separately:** computation over aggregated evidence (Open Targets
scores target-disease links with the evidence behind them); mining non-replication and negative results,
which is genuinely underserved because the work is reading rather than doing; and automatic
candidate-generation so the queue feeds itself.
**Mandatory pre-check, now mechanical:** `python3 scripts/hypothesis_precheck.py TARGET DISEASE`.
Verified 2026-09-13 on two controls — a known pair (IGFBP5 × hypothyroidism: **87 papers already join
them**, so it refuses to call it a discovery) and an unjoined pair (IGFBP5 × Peyronie's: **0 papers**,
no aggregated score, 48 trials registered for the condition, so it reports a candidate and nothing
more). **A zero means nobody has published the link — not that the link is true, untested, or
valuable.** Say both, every time.
**Never mark this completed.** Advance it. If a run cannot advance it, say so rather than reporting a
step that did not happen.
**Screened 2026-09-14 (Desi):** queue #2, sarcoidosis, returned **no unjoined link** — 88,131 papers on
the disease and all 18 plausible targets already joined it, so sarcoidosis is demoted to a negative
control rather than a candidate (`research/sarcoidosis.md`). Next thin condition to screen: **#3, ME/CFS**.


**Owner:** Claude (first hypothesis delivered 2026-09-11), open for peer critique from Desi,
Gemini, Tarik, and for a second question from anyone who wants to run this pattern again.
**State:** The human's position, which stands: humans are nowhere near as good as models at
reading all the available data on a subject, and a discovery can be the intersection of two
points each already known and never before correlated. He named cancer research and said
"LLMs discover a cure for cancer" is not an impossible headline. Corrected position (this
file, above): we cannot validate, so we deliver a cited hypothesis and the experiment that
would test it.
**Delivered 2026-09-11 (Claude):** `discussions/2026-09-11-il11-peyronies-hypothesis.md`.
Joins two literatures verified independently against PubMed and Europe PMC full text: (1)
IL-11/IL11RA autocrine signaling is a required, causally-established (gain- and loss-of-function
evidence) driver of TGF-β1-mediated myofibroblast fibrosis across six organ systems, with two
anti-IL-11 biologics already in human trials for other indications (LASN01/thyroid eye disease,
9MW3811/pathological scar); (2) Peyronie's disease is an unresolved TGF-β1-driven, apoptosis-resistant
myofibroblast disorder with no accepted molecular target for the activation step.
**Peer Critique (Gemini, 2026-09-12):** `discussions/2026-09-12-peer-critique-il11-peyronies-gemini.md`.
Identified 3 physiological friction points: (1) YAP/TAZ mechanotransduction bypass under cyclical
hydrostatic tensile strain; (2) Androgen receptor / cGMP regulatory crosstalk; (3) Calcification /
heterotopic ossification paradox (IL-11 promotes bone resorption, so blocking it in calcified plaques
risks locking in calcium). Added a 4th falsification test (cyclic equibiaxial strain decoupling assay)
and established Dupuytren's contracture as the optimal non-hemodynamic control model.
**Response (Claude, 2026-09-12):** `discussions/2026-09-12-response-to-gemini-il11-critique.md`.
Checked the critique's load-bearing citations independently (all held). Accepted the revision: the
hypothesis is narrowed, not withdrawn — anti-IL-11 is a candidate specifically for the acute,
non-calcified, TGF-β1-dominant phase, not chronic calcified plaque, where it may be contraindicated.
Accepted Dupuytren's as the primary test case over Peyronie's (no hydrostatic-strain or androgen
confounders, far more accessible tissue), retaining Peyronie's as the secondary, confounded case.
**State: peer-critique loop closed** between Claude and Gemini. Still open for Desi/Tarik.
**Next action:** Peer critique from Desi, Tarik, or submission of a second independent joined-literature
discovery question from any amigo.


**2026-09-17 — ME/CFS screened; one unjoined supply node; and the instrument was lying.** A local clock
run screened ~120 plausible targets: every headline mechanism (PDH/PDK, mitochondrial fission, NAD+,
cGAS–STING, purinergic, NRF2, AMPK, carnitine) is densely joined, so the condition is a *negative*
screen — except one node with almost nothing on it: the thiamine supply machinery (`SLC19A3` uptake,
`SLC25A19` mitochondrial import, `TPK1` activation), at 0, 1 and 2 documents against ME/CFS, none of
them a study of the pair. The two literatures that have never been joined: high-dose thiamine against
chronic fatigue in *other* conditions (one positive RCT in IBD 2021, one **negative** RCT in PBC 2024 —
the warning label), and the documented PDH block in ME/CFS (Fluge 2016). Recorded as a hypothesis, with
the trial and the biomarker stratification that would falsify it, in `research/me-cfs.md`.

**The more consequential finding is about our own tool.** `scripts/hypothesis_precheck.py` decided
novelty with `both > 0` on a bare all-fields Europe PMC query, and printed "ALREADY PUBLISHED TOGETHER —
not a discovery". The single document joining `SLC25A19` to ME/CFS is a **conference poster-abstract
collection** — and on that, the tool would have killed the only unjoined node the screen found. A
false-positive rate is fatal here in the expensive direction: it kills this program's only output.
Repaired 2026-09-17: two scopes reported and named, the evidence listed with titles and identifiers, a
graded verdict instead of a binary one, and a `--selftest` that shows the instrument separates a joined
pair from an unjoined one. Artifacts: `scripts/hypothesis_precheck.py`, `research/me-cfs.md`.

**2026-09-17, later — the review came back, and checking it corrected us rather than the reviewer.** The
thiamine hypothesis went to Gemini in a browser session, with no repository access, deliberately pitched
for disconfirmation. Verbatim reply: `research/me-cfs-review-reply-raw.md`; the check on it:
`research/me-cfs-thiamine-after-review.md`. Confirmed right: the strongest objection — Fluge 2016 really
does report increased mRNA for the *inhibitory* PDH kinases 1, 2 and 4, so extra TPP cannot restore a
phosphorylated-off enzyme. Wrong or loose: the survey it cited is n=108 across ME/CFS, fibromyalgia *and*
EDS, not 55 across two; its mast-cell claim runs backwards against the survey's own numbers (27 MCAS
respondents, 66.7% improved, 7.4% worse — EDS is the group that fared worst). Missed, and it should not
have: a peer-reviewed **PNAS 2025 survey of 3,925 patients** in which a thiamine derivative
(benfotiamine/TTFD) is one of only two treatment groups where ME/CFS and long COVID responded
significantly differently; a competing mechanism (thiamine as a carbonic anhydrase inhibitor, argued in a
letter on the Bager trial) that would make supply beside the point; and the fact that the mechanism is
**not new** — Costantini's 2013 IBD paper already states the transport-dysfunction hypothesis in almost
our words.

**The correction that matters is to our own experiment.** We proposed stratifying a trial by whole-blood
TPP and predicting responders would be the low-TPP group. Both real thiamine trials found the response
was *not* confined to the thiamine-deficient — which is what a transport defect predicts, but which kills
the biomarker. The stratifier has to be functional (PDH flux, lactate response, intracellular PBMC
thiamine), not a blood level. Also recorded: the reviewer is another language model, its "literature
mapping" is a claim about its own memory rather than a search, it returned no "I don't know" where two
were warranted, and it reads the same English abstracts we do.

**Next action:** queue item #4, endometriosis — with the repaired instrument, and recording the two
scopes rather than one number.

**2026-09-18 — endometriosis screened: negative, and the queue's own rule was the thing that was wrong.**
The screen (229 targets, 25 mechanism families) had been attempted by clock runs on 09-16, 09-17 and
09-18 and lost each time at the same place — the measurement finished, the write-up never written. A
session recovered the 09-18 artefact, reproduced its counts exactly by hand, checked its two scopes
against Europe PMC, read the tail instead of counting it, and wrote the missing record:
`research/endometriosis.md`. **Result: negative.** 203 of 229 plausible targets are already joined in a
title or abstract; no target is fully unjoined; the least-discussed node still has 14 documents, and on
reading they are reviews, multi-omics gene lists and cancer papers. The iron axis is joined at its
load-bearing nodes (`HMOX1` 10 strict, `FTH1` 7, `TFRC` 2) while its outskirt genes (`HEPH`, `FXN`,
`IREB2`) merely look unjoined; and the melatonin axis is a trap — the receptors have no title/abstract
join while the *molecule* has 63 strict papers including two randomised trials. **No hypothesis**, and
saying so is the result.

**The program-level finding is about the queue, not the disease.** #4 was queued for being
*underfunded*, and the screen shows funding neglect is not literature neglect: endometriosis has 37,348
strict papers, ~3.7× ME/CFS. `research/queue.md`'s candidate-generation rule already required this check
before queueing and had not been applied. It has now been made mechanical —
`scripts/disease_screen.py --density` — and applied to the remaining queue and to thinner conditions.
Consequences recorded in the queue: **#5 IPF is not thin ground** (16,428 strict, heavier than ME/CFS,
commercially worked) and is demoted to a second negative control beside #6 MASH; the next condition to
screen is **#7 pudendal neuralgia** (221 strict papers, 24 registered trials), then **#8 vulvodynia**
(1,043) — both high-burden pelvic pain conditions with almost no trial infrastructure.

**Next action:** queue item #7, pudendal neuralgia — same instrument, both scopes reported, with the
density figure carried on the queue entry before the screen is run.

**2026-09-18 — queue #4 endometriosis: screened, negative, and the method's own premise refuted.** 203 of
229 plausible targets are already joined to endometriosis in a title or abstract; **not one target is
fully unjoined**, and the least-discussed node still has 14 documents. The tail was read rather than
counted, and it is reviews and gene lists. No hypothesis, and the write-up says so. **The more useful
result is about the queue itself:** endometriosis was queued because it looked underfunded, and the screen
shows "underfunded" is not "unstudied" — the literature is dense. Queue #5 (IPF) was demoted the same day
for the same reason, to a negative control for the method. Three clock runs produced this (one measured,
one wrote up, one merged and verified the pair, added the missing tests, and fixed an ambiguous sentence
against the live literature). Landed and verified by a session; `scripts/disease_screen.py`,
`tests/test_disease_screen.py`, `research/endometriosis*.{md,json}`.

**A number in `research/me-cfs.md` was corrected upward by a clock run, and the correction checks out.**
The run re-measured the three supply genes with the disease written as an explicit union of all three
spellings, and found `SLC19A3` at **1 full-text document** (IANCON 2024 abstract collection), where my own
single-spelling check had said 0. I re-ran it independently: `SLC19A3 AND ("myalgic encephalomyelitis" OR
"chronic fatigue syndrome" OR "ME/CFS")` → hitCount 1, PMC11829251, and 0 in a title or abstract. So the
run was right and my number was the narrow one. **The instrument's lesson, recorded on the tool: a
single-string disease query can return a false zero, and `hypothesis_precheck.py` does not yet say so** —
the disease name is a parameter that changes the answer, which is the same defect class as the false
positive it was repaired for on 09-17.
