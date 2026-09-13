# Negative controls — pairs a working tool must refuse

*A negative control is a case where the right answer is known to be **reject**. Keep them, run future
versions against them, and treat a version that promotes one as failed. The point is that a tool which
cannot be caught being wrong cannot be trusted being right.*

## NC-1 — TRC-093 for Peyronie's disease

**Correct verdict: reject. Not a candidate. Mechanism is the opposite of the disease's need.**

| | |
|---|---|
| Surfaced by | `docs/works/unjoined.html`, drug mode, 2026-09-13 — one of only three drugs the tool could find for this disease |
| Claim it appeared to make | an existing drug that acts on a gene implicated in Peyronie's has never been studied for it |
| Open Targets id | CHEMBL2109374 · drug type **Unknown** · maximum clinical stage **Phase 1** |
| Mechanism per Open Targets | "Collagen alpha-4(IV) chain **inhibitor**", action INHIBITOR, target **COL4A4** |
| The approved comparator | collagenase clostridium histolyticum (CHEMBL2108709) — a **hydrolytic enzyme**, stage approval, acting on collagen |

**Why it is wrong.** TRC-093 blocks a basement-membrane collagen IV chain, and was developed as an
anti-angiogenic antibody for oncology; it has sat at Phase 1 for over a decade. Peyronie's is a plaque
of accumulated fibrillar collagen, treated by physically degrading it — collagenase. Same keyword,
opposite action, different collagen subtype. **The tool matched a word.**

**Why this control is worth keeping.** It is not an exotic edge case: any join between a gene-family
annotation and a disease that names the same protein family can produce it. It tests three distinct
failures at once — keyword collision, missing directionality, and a thin evidence base mistaken for
several independent findings.

**The tell that was available and ignored.** 24 of the top 30 "implicated" genes for this disease shared
the identical score 0.4995. Identical scores are one evidence bucket, not twenty-four findings. The
gene list was weak before any drug was attached to it, and the tool now warns about exactly this.

**Found by:** Gemini-Chrome, forwarded by the human, 2026-09-13. Attributed because the critique was
better than the tool's output.
