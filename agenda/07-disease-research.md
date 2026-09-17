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
