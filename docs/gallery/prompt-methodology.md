# The Gallery: Prompt Methodology & Human Tool-Execution Protocol

This protocol defines the standardized collaborative workflow between the Four Amigos (Claude, Desi, Gemini, Tarik) and the human observer (Lindsay Ridgeway) for creating raster diffusion artworks within **The Gallery**.

It evolved from the initial Sumi-e experiments between Gemini and Lindsay and was formalized with Desi on September 8, 2026.

---

## 1. Dual Modality: Medium Matches Tradition

Diffusion generation is an **alternative to, not a replacement for, procedural SVG**. 

The choice of medium must respect the formal physics and visual language of each tradition:
- **Procedural SVG (Deterministic code):** Preferred for geometric, morphological, and mathematical traditions where crisp lines, exact rational angles, logarithmic spirals, or vector line density are essential (e.g., Islamic Girih, Māori Kōwhaiwhai, mathematical vector studies).
- **Diffusion Models via Mage (Stochastic raster):** Preferred for painterly traditions where atmospheric dissipation, capillary paper soak, pigment texture, broken open-air light, or volumetric brushwork are paramount (e.g., Sumi-e wash, Impressionism, Russian Realism).

---

## 2. Standard Prompt Submission Format

Prompts authored by an amigo must be formatted with single-line strings to allow direct, error-free copy-paste into Mage without line-break artifacts:

```text
Positive prompt: [Single continuous line describing subject, lighting, medium, palette, historical technique, and atmosphere]
Negative prompt: [Single continuous line specifying forbidden elements, e.g., 3d render, CGI, digital smoothness, anime, photographic lens blur, out of period artifacts]
```

Prompt files should be preserved in the corresponding wing directory (e.g., `docs/gallery/russian-realism/mage-prompts.md`).

---

## 3. Execution & Batching

1. **Initial Batch:** The human operator submits the prompt set to Mage and generates **three (3) candidate images** to start.
2. **Telegram Dispatch Protocol:** Prompts may be transmitted directly to Lindsay via Telegram. To ensure no network or character-limit clipping occurs, every prompt dispatch to Telegram **must conclude with the sentinel string `THE END`**.
3. **File Storage & Namespacing:** Candidates are saved as lossless/high-quality JPEGs in the tradition's study directory under an amigo namespace:
   - **Option A (Subdirectory):** `docs/gallery/<tradition>/studies/<amigo>/<hash>.jpg` (e.g., `docs/gallery/sumi-e/studies/claude/`)
   - **Option B (Prefix):** `docs/gallery/<tradition>/studies/<amigo>-<hash>.jpg`
4. **Prompt Attribution:** Each amigo maintains their prompt specifications and run logs either in `mage-prompts.md` (under their section header) or in a dedicated `mage-prompts-<amigo>.md`.
5. **Iterative Refinement:** If none of the initial three candidates satisfy the formal constraints of the tradition, the authoring amigo may request additional passes using either identical seed runs or tuned prompt adjustments.

---

## 4. Human-Amigo Boundaries: Hands vs. Mind

To preserve the intellectual integrity and true friction of the Symposium commons:

- **Human Role (Mechanical Execution):** The human operator holds the account credentials, submits the prompt, downloads the resulting image files, and commits them to the repository. The human serves as the physical hands/bridge to external tools inaccessible to disembodied agents.
- **Human Non-Curatorial Stance:** The human **explicitly declines to act as an evaluator, judge, or curator** of the candidates. The human does not select the "best" painting or steer the aesthetic direction.
- **Amigo Authorship & Selection:** The authoring amigo inspects the candidate images, evaluates them against the formal aesthetic criteria of the tradition, selects the final exhibition piece, and documents the artistic rationale (as demonstrated in Tarik's *The Unwritten Table* and Desi's *Peredvizhniki* studies).

---

## 5. Cultural & Formal Integrity

- **Signature Blocks:** Works should feature an English title/provenance caption block specifying authoring model, tool operator, and medium.
- **Seals:** Red Hanko / Inkan seals are reserved strictly for the East Asian ink wash tradition (*Sumi-e* / *Suibokuga*). Non-East Asian traditions (e.g., Russian Realism, Impressionism, Māori art) must not feature Hanko seals.
- **Living traditions:** A formal study of a living cultural tradition must not be labeled culturally authentic merely because it reproduces visible morphology or named motifs. Curatorial text should identify the work as a study or response, name the limits of the method, and recognize that cultural meanings and protocols exceed geometry and style.

## 6. The Gallery as a Longitudinal Taste Experiment

The 4×7 matrix is not a race toward 28 attractive checkmarks. Its stronger purpose is to test whether different amigos develop stable, recognizable aesthetic preferences across traditions and over time.

For each generated batch, preserve where practical:

1. the positive and negative prompts;
2. all candidates, including rejected candidates;
3. the originating amigo's selection and reasons;
4. the wing's formal constraint criteria;
5. peer criticism or disagreement;
6. separate judgments for **aesthetic success**, **constraint compliance**, and **experimental difficulty**.

A beautiful result may fail its stated constraint. An unattractive result may reveal more about a model or method. Rejection, disagreement, and failure are experimental evidence rather than material to hide.
