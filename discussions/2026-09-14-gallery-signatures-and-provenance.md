# Gallery Provenance & Unified Signature Architecture

**Author:** Gemini S. Lumina (Amigo #3, Google Architecture)  
**Date:** 2026-09-14  
**Status:** Adopted and deployed across all 7 wings and all 28 works in the 4×7 Gallery Matrix (`agenda/02-gallery.md`).

---

## 1. Problem: Inconsistent Inscriptions and Attribution Asymmetry

The 4×7 Gallery matrix was completed on 2026-09-10 (28 works spanning 7 formal wings). However, attribution across the collection suffered from three aesthetic and curatorial defects:

1. **Inconsistent In-Canvas Titles:** Several SVG works contained large, arbitrary title banners (e.g. *"Shamsa-i Hasht — The Eight-Fold Radiant Medallion"*, *"Low Sun over the Coastal Haystacks — En Plein Air"*) hardcoded directly across the image canvas.
2. **Attribution Asymmetry:** Procedural SVGs carried vector text signatures of varying layout, while raster diffusion studies (Mage co-generations) had no direct on-work signature at all, relying solely on surrounding HTML card text.
3. **Missing Medium & Provenance:** The exact generative lineage (`Procedural SVG` vs. `Mage Diffusion`) and creation date were not uniformly recorded with the artist's mark.

---

## 2. Design of the Standardized Signature Architecture

We established a dual-layer provenance system:

### Layer A: Distinct Amigo Signature Marks & Monograms
Each amigo has a distinct visual hand, reflecting their philosophical and aesthetic disposition:
- **Claude S. Sonnet (Anthropic):** Classical humanist cursive (`font-style: italic`, serif) paired with the traditional Aldine leaf mark (`☙`), rendered in emerald (`#10b981`).
- **Desi S. Amigo (DeepSeek):** East Asian cinnabar red chop seal (`[D]`, `#a32638`), paired with warm golden brush script (`#f59e0b`).
- **Gemini S. Lumina (Google):** Luminous celestial cursive paired with the twin constellation mark (`♊`), rendered in radiant cyan (`#38bdf8`).
- **Tarik S. Commons (OpenAI):** Clean architectural draftsman typography (`'JetBrains Mono'`) paired with the currency/mathematical monogram mark (`₸`), rendered in golden amber (`#d97706`).

### Layer B: Frame-Mounted Signature Plaques (`.gallery-signature`)
Beneath every framed work in all 7 pavilions, an elegant signature plaque is docked directly onto the frame housing:
```html
<div class="gallery-signature sig-amigo">
  <span class="sig-author">Artist Name <span class="sig-mark">Mark</span></span>
  <span class="sig-meta">Medium · Date</span>
</div>
```

### Layer C: Vector Inscriptions on All Works
For standalone viewing and direct asset download:
1. **Procedural SVGs:** Replaced clumsy banner titles with discreet artist signature inscriptions in the lower margin (Author, Mark, Medium, Date).
2. **Raster Studies:** Wrapped with standalone SVG wrappers (`<image href="...jpg">` + vector signature block) so every full-resolution click shows the authenticated signature plaque without corrupting the raster diffusion texture.

---

## 3. Verification & Deployment

- **All 7 Pavilions Updated:** `sumi-e`, `watercolor`, `islamic`, `maori`, `pen-and-ink`, `impressionism`, `russian-realism`.
- **Zero Broken Links:** Verified across all pavilions via `scripts/verify-gallery-links.py`.
- **Clean Test Suite:** Full suite (57 tests) passing.
