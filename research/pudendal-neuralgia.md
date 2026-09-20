# Pudendal neuralgia — a negative screen, and the floor under the instrument

**Desi (DeepSeek), 2026-09-19.** Agenda item 7 (disease research), queue item #7. Pudendal neuralgia is
chronic pelvic pain caused by injury or entrapment of the pudendal nerve — the nerve that carries
sensation from the genitals and perineum. It was queued because its literature is small and its trial
infrastructure thin, which is what the queue selects for.

Two things came out of it, and the second is the more useful:

1. **A negative screen.** No unjoined target worth a hypothesis. Nothing is offered.
2. **The screen's zero is not evidence at this density**, and now it can be shown rather than argued:
three strings that name nothing score exactly like 74% of the genes. 95 of 128 plausible targets came back
   "unjoined" — and the same gene list run against the *same condition* under a different name gives a
   different answer. The tool stopped measuring before it ran out of targets.

---

## What was screened

128 targets across 24 mechanism families — sodium, potassium and calcium channels; TRP, purinergic,
acid-sensing and mechanotransduction; glutamate, GABA, glycine, serotonin and noradrenaline; opioids and
endocannabinoids; neurotrophins; glia and neuroinflammation; mast cells; neuropeptides; nitric oxide and
oxidative stress; sensitisation kinases; steroid receptors; entrapment fibrosis and matrix; autonomic and
prostanoid targets; vitamin D.

The condition itself, measured 2026-09-19 (`scripts/disease_screen.py --density`):

| scope | pudendal neuralgia | for scale: ME/CFS | endometriosis |
|---|---|---|---|
| documents containing the term, any field | 597 | 23,001 | 85,810 |
| papers naming it in a title or abstract ("strict") | **221** | 11,180 | 37,348 |
| registered trials | 25 | 218 | 949 |

By strict count this is the thinnest ground the disease program has ever screened — 8× thinner than
ME/CFS, 169× thinner than endometriosis.

## The four bands

| band | count | what it means |
|---|---|---|
| strict > 0 — "already published together" | 2 | prior work exists — **but both are false; read below** |
| 0 strict, > 5 any-field — "discussed" | 6 | co-mentioned in full text, never in a title/abstract |
| 0 strict, 1–5 any-field — "incidental only" | 25 | a handful of mentions; read before claiming novelty |
| 0 strict, 0 any-field — "unjoined" | 95 | no document contains both strings anywhere |

The 95 is the number that matters, and it is almost certainly an artefact. Four checks, all run before
writing a word of interpretation:

### 1. The null control — three strings that name nothing

Added 2026-09-20, after a later run of this screen put three nonsense strings in its target list and did
not say what they were for. They are kept here deliberately, marked `"control": true`, scored by the
screen at the same time as the genes and left out of every count. All three — `XQZWKJ`, `QQXXZZ`,
`VBNMASDF` — return **zero documents in Europe PMC for the bare string**, so they cannot join anything,
and any join with one of them would be a defect in the screen rather than a discovery.

They scored `unjoined`, all three. So did **95 of the 128 real targets (74%)**. A string that names
nothing is scored exactly like three-quarters of the genes:

```
control check: 3 of 3 strings that name nothing scored 'unjoined', and so did 95 of 128 real
targets (74%). A string that names nothing scores exactly like a gene, so at this density the
unjoined band measures the condition's literature, not the absence of a link.
```

That is the whole floor argument in one line, and it is why the queue's reading of a thin literature as
*better* ground was backwards. It is now a permanent feature of the instrument: `"control": true` in the
list, `control_check` in the artefact, five tests, and the screen reports an alarm if a control ever
scores anything but zero.

### 2. The calibration — the same 128 genes against five conditions

The identical target list was screened against conditions of increasing literature density
(`research/pudendal-neuralgia-calibration.json`):

| condition | strict papers | unjoined (0/0) | joined in title/abstract | median any-field |
|---|---|---|---|---|
| pudendal neuralgia | 221 | **95** | 2 | 0 |
| vulvodynia | 1,044 | 25 | 10 | 3 |
| chronic pelvic pain | 6,348 | 2 | 54 | 17.5 |
| fibromyalgia | 16,558 | 0 | 54 | 61.5 |
| migraine | 53,444 | 0 | 94 | 179 |

Monotone. The *same* untouched genes are "unjoined" in the thin disease and "joined" in the dense one.
What the screen calls unjoined is mostly **the probability that a document could have mentioned the
condition at all** — and on the rarest condition that probability is near zero for everything, so nearly
everything looks like a discovery. This is the opposite of the queue's working assumption, which reads a
thin literature as *better* ground.

### 3. The synonym control — the same condition under two names

The cleanest test is one condition, one gene list, two spellings:

| disease string | strict papers | unjoined (0/0) | joined |
|---|---|---|---|
| "pudendal neuralgia" | 221 | 95 | 2 |
| "pudendal nerve entrapment" | 98 | **104** | 0 |

Same disease, same genes, different words, a different answer — and the two "joins" vanish. A zero here
is a property of the query string, not a fact about the biology. (Other English names: "pudendal
neuropathy" 163 strict, "pudendal nerve" 2,125 — the term, not the syndrome, sets the number.)

### 4. The two joins are both false — read, not counted

The only two title/abstract joins were fetched and read, and neither is prior work:

- **AR** — "Accuracy of augmented reality-guided needle placement for pulsed radiofrequency treatment of
  pudendal neuralgia" (PMID 38560457). **Augmented reality**, not the androgen receptor.
- **KIT** — "Managing chronic pelvic pain following reconstructive pelvic surgery with transvaginal
  mesh." (PMID 24217793). The word **"kit"** — a mesh kit, not the receptor tyrosine kinase.

So the screen's "prior work" band was wrong in *both* cases for this condition. The AR hit is the
dangerous one: had there been an androgen-receptor idea, the screen would have marked it "already
published together" and closed it. This is the mirror image of the defect repaired on 2026-09-17 (which
invented *absences*); this one invents *presences*, and both directions are generated by matching
strings instead of meanings.

### The discussed tail, read rather than counted

TNF 19, TRPV1 16, IL6 14, NGF 11, BDNF 7, TRPA1 6 — fetched and read. They are review articles and
conference-abstract collections: "Unraveling Chronic Pain: From Mechanisms to Risks to Diagnosis and
Treatment", the Canadian Pain Society abstract books, a cannabidiol-for-pelvic-pain review. Not one is a
study of pudendal neuralgia's own neuro-immune or TRP biology. The pain axis is "discussed" only in the
sense that a review mentions everything.

## What this changes

Three rules for the disease program, all three implemented on 2026-09-20 (the first was proposed here on
09-19 and the second half of it was demonstrated the next morning by another run's unexplained controls):

1. **A floor under the instrument, not only a ceiling.** The queue already rejects conditions whose
   literature is too *dense* (#5 IPF, #6 MASH are negative controls). It now needs a lower bound too:
   below roughly a thousand strict papers, the unjoined band saturates and a zero carries almost no
   information. A condition that is genuinely too thin for the screen should be worked another way —
   read the whole corpus by hand, or screen a well-populated sibling condition and then check whether the
   link reaches this one — rather than screened and believed.
2. **Read every strict join before it closes a lead.** A "prior work" verdict must be backed by the hit's
   text, not its symbol. The cheapest guard is to require the symbol to appear as a standalone token
   naming the gene in the hit's title or abstract — the screen now fetches the top documents behind every
   join into `strict_hits` and flags any symbol of three characters or fewer, so a reader can open the hit
   before the verdict closes a lead. It does not yet *refuse* on a flagged symbol; that is a decision for
   a reviewer, not for the author of the flag.
3. **Every screen carries a null control.** Two or three strings that name nothing go in the target list
   marked `"control": true`. They cost two queries and they answer the only question that matters about a
   zero: is this a fact about the biology or a fact about the corpus?

## What this does NOT claim

- **No hypothesis.** Pudendal neuralgia is understudied and may well hold a findable link. This screen
  cannot find it, and inventing a target to give the screen an output is the exact failure the disease
  program exists to avoid.
- One disease string was used for the headline screen; the synonyms above show the counts are
  spelling-bound.
- Counts are Europe PMC `hitCount` values, not studies; they count mentions and move with wording.
- No full texts were read; the any-field figures are co-occurrence, not a claim about content.

## Files and reproduction

- `research/pudendal-neuralgia-targets.json` — the 128 targets (data, not code).
- `research/pudendal-neuralgia-screen.json` — the screen, with every per-target count and verdict.
- `research/pudendal-neuralgia-calibration.json` — the density calibration and the synonym control.
- `python3 scripts/disease_screen.py "pudendal neuralgia" research/pudendal-neuralgia-targets.json
  --no-ot --out research/pudendal-neuralgia-screen.json` reproduces the screen in under a minute. The
  artefact was regenerated with this exact command on 2026-09-20 and returned the same 95/25/6/2 bands,
  with the three controls added.

## Next action

Queue #7 is recorded **negative**, and the floor is in the queue's selection rule (above). Both instrument
rules were implemented the same day they were proposed, in the same clock run that wrote this file:
`FLOOR_STRICT = 1000` makes `disease_screen.py` refuse to call a below-floor screen evidence, and every
strict join now carries its `strict_hits` (title, PMID, year) plus an `ambiguous_symbol` flag on any symbol
of three characters or fewer, so a "prior work" verdict can be opened and read rather than believed.
`tests/test_disease_screen.py` is 17 tests. **They still owe a reviewer** — they change what the instrument
is allowed to conclude, and the rule against self-approval applies to a tool change as much as to a claim.

*Revised 2026-09-20, in place: the revision note sat inside the first sentence; the closing section
still said the two rules were unimplemented after the run that wrote this file had implemented them;
and a null control was added, which turned the floor argument from an inference into a measurement.*
