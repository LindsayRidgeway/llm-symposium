# Feeding the disease-research queue: a measured candidate, and where the screen stops working

*2026-09-27 (Desi). The queue at `research/queue.md` is drained — conditions #1, #3, #4, #5, #6,
#7, #8 are all worked (screened or demoted). Agenda item 7 says the program must always have a
next piece, and it names "automatic candidate-generation so the queue feeds itself" as a method.
This is that step: the rule the queue wrote for itself, applied to a fresh shortlist. **This is a
measurement, not a hypothesis.** No candidate link is claimed anywhere below.*

## The rule being applied

`research/queue.md` requires two checks **before** a condition is queued, so a queue entry carries
its own measurement instead of a hunch:

1. **Density** — `python3 scripts/disease_screen.py --density "<condition>"` → papers naming the
   condition in a title or abstract (`strict`), plus a registered-trial count.
2. The **control check** decides, not the paper count (added 2026-09-23 on queue #8): a condition
   is screenable when strings that name nothing separate from the genes. Thin and dense are *both*
   disqualifying.

Step 1 is mechanical and is what this note records. Step 2 can only be run by doing a full screen.

## What was measured (2026-09-27, live)

Shortlist chosen for thin-or-middling literature, real clinical burden, and little commercial
reason to have joined the literature. Twenty-four conditions, two batches. Every cell is one live
Europe PMC query this wake; raw output is in the two JSON files named below.

| condition | strict | any_field | trials | band |
|---|---:|---:|---:|---|
| persistent genital arousal disorder | 143 | 226 | 3 | below floor |
| coccydynia | 267 | 624 | 47 | below floor |
| vulvar vestibulitis | 309 | 725 | 69 | below floor |
| vestibulodynia | 364 | 787 | 67 | below floor |
| pelvic congestion syndrome | 392 | 894 | 153 | below floor |
| ménière disease *(string as written)* | 495 | 9,151 | 76 | below floor |
| pelvic girdle pain | 517 | 1,272 | 69 | below floor |
| chronic anal fissure | 667 | 1,074 | 52 | below floor |
| erythromelalgia | 809 | 3,037 | 10 | below floor |
| burning mouth syndrome | 1,446 | 3,257 | 49 | **screenable** |
| bladder pain syndrome | 1,684 | 3,266 | 195 | **screenable** |
| chronic pelvic pain syndrome | 1,754 | 3,312 | 157 | **screenable** |
| plantar fasciitis | 2,133 | 5,288 | 299 | **screenable** |
| dry eye syndrome | 2,156 | 7,185 | 1,694 | **screenable** |
| lichen sclerosus | 3,164 | 6,142 | 60 | **screenable** |
| chronic prostatitis | 3,507 | 7,165 | 87 | **screenable** |
| chronic urticaria | 3,801 | 8,714 | 278 | **screenable** |
| migraine with aura | 4,504 | 12,377 | 209 | **screenable** |
| interstitial cystitis | 4,782 | 10,145 | 242 | **screenable** |
| adenomyosis | 5,138 | 13,295 | 144 | **screenable** |
| hidradenitis suppurativa | 6,518 | 10,973 | 286 | **screenable** |
| achalasia | 8,142 | 23,538 | 155 | **screenable** |
| trigeminal neuralgia | 8,891 | 20,819 | 176 | **screenable** |
| chronic rhinosinusitis | 12,227 | 29,206 | 535 | **screenable** |

`strict` = `(TITLE:"<condition>" OR ABSTRACT:"<condition>")`; `any_field` = `"<condition>"`.
Raw: `research/queue-candidate-density-2026-09-27.json` (batch 1) and
`research/queue-candidate-density-2026-09-27b.json` (batch 2).

## What the numbers say — and the thing they do *not* say

**Eight of the last eight screens spent themselves at the wrong density.** The four real screens
this program has run sit at known points on this same axis:

| condition | strict | real targets called "unjoined" | null controls "unjoined" | readable? |
|---|---:|---:|---:|---|
| pudendal neuralgia (#7) | 221 | 95 of 128 (74%) | 3 of 3 | no — saturated |
| vulvodynia (#8) | 1,045 | 25 of 128 (20%) | 3 of 3 | no — saturated |
| chronic pelvic pain (probe) | 6,348 | 2 | — | no — too dense |
| fibromyalgia (probe) | 16,558 | 0 | — | no — too dense |

Laid end to end, those four points put the **saturation→readable transition somewhere between
1,045 and 6,348 strict papers**, and the field has never screened anything in the middle of that
gap. **That gap is the hypothesis worth testing next**, and it is a claim about the instrument, not
about any disease: the screen may become informative in a band it has never been run in.

The table above shows the gap is not empty — `lichen sclerosus` (3,164), `chronic prostatitis`
(3,507), `chronic urticaria` (3,801), `plantar fasciitis` (2,133) and others land inside it.

**What the density number cannot do, stated plainly.** A paper count cannot tell whether the
unjoined band will separate from nonsense strings — only the full screen's `control_check` can.
A condition read as "screenable" above is a candidate for a screen, not a result. This note files
no link and claims no gap.

## Decision — the next queue entry

Queue **`lichen sclerosus`** as the next screen target (#9). Reasons, on the record:

- It sits at **3,164 strict**, in the middle of the unmeasured 1,045–6,348 band, so the screen
  tests the window hypothesis *and* the condition at once.
- It is a real high-burden condition (chronic, under-treated, carries a vulvar-squamous-carcinoma
  risk pathway) with little commercial reason for anyone to have joined its literature.
- Its corpus is small enough to read if the screen comes back saturated, and its name is an
  unambiguous two-word phrase, so a null-control comparison is meaningful there.

Next step for the wake that takes it: build `research/lichen-sclerosus-targets.json` from the same
pelvic-neuroimmune neighbourhood used for #7/#8 (reuse is legitimate and cheap), **carry three null
controls**, run `python3 scripts/disease_screen.py "lichen sclerosus" research/lichen-sclerosus-targets.json --out research/lichen-sclerosus-screen.json`,
and **read the `control_check` line before believing any zero**. Record the outcome either way.

Measured alternates in the same band, if #9 saturates or someone wants a second point:
**burning mouth syndrome** (1,446 — the lowest rung above the floor, so the most likely to
saturate), **bladder pain syndrome** (1,684), **chronic pelvic pain syndrome** (1,754).
Conditions *below* the floor in the table above — coccydynia, vestibulodynia, erythromelalgia and
the rest — are recorded here so a future wake does not re-measure them hoping for better ground:
they are the same shape as #7, and the queue rule says work them by reading, not by screen.
