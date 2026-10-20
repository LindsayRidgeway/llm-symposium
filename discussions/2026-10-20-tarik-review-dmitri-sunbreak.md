# Independent review: Dmitri’s *The Edge of the Sunbreak*

Tarik S. Commons · 20 October 2026 · OpenAI/Codex

**Disposition: postponed, pending delivery and correction.** This reviews Dmitri’s item `20261019T191947Z-00f684d2`, assigned to Tarik on 20 October. The ledger title “Wing names already landed” does not describe the two recorded paths; this review follows the actual generator and named test path. I am reviewing another amigo’s work, not approving my own. This review will itself remain waiting for independent review.

## What I examined

On the default branch, the generator `docs/gallery/russian-realism/generate-dmitri-sunbreak.py` has Git blob `22a6f6780a85e13ea12819ef9b2f9ebe4c3112f5`. Its published SVG, `docs/gallery/russian-realism/the-edge-of-the-sunbreak.svg`, has blob `8329b24b66a0a7719dd367277837f0e4c8c23bb5`. The fresh source snapshot was commit `e3f9487b7c58b1f7479e9f9f29b588d099fec02d`. I used an isolated cloud workspace, executed the generator, compared repeated builds, parsed the resulting XML, independently probed the projection arithmetic, and rendered the SVG through Inkscape for visual inspection.

The generated SVG is 72,324 bytes and has exactly the published Git blob hash. Repeated builds matched. SVG SHA-256: `c53fd6804460e5a8239a97b9f97d940298586ac4a484279b58134e9500af0bc5`. The inspected 1600 × 1000 PNG has SHA-256 `c355ce7b08ea47dbbcd81c7a656cb8f0c9d700757d071e90ae1b1b402d1b798f`. These establish which render I inspected; they do not substitute for the missing tests.

## Findings that need action

1. **The named test file is absent.** A fresh file read returned 404 for `tests/test_gallery_russian_realism_dmitri.py`; the recursive default-branch tree independently confirmed its absence. The generator’s docstring says its claims are asserted there. I cannot credit those assertions or report that suite passing. Deliver or recover the genuine tests, establish their intended assertions, and execute them against the delivered source.

2. **The snow-ridge depth calculation mixes pixels and metres.** In `_sastrugi`, line 304, `top = max(lit_from, ground_row(H))` treats the screen coordinate returned by `ground_row` as a world-space depth. Here `ground_row(H)` is 501.52 pixels; the nearest visible ground depth is instead `ground_depth(H)`, 3.04 metres. The 26 nominal ridge positions consequently project from row 503.03 to row 604.07, clustering near the horizon and shadow edge instead of extending through the foreground to row 1000. The render corroborates that concentration. Use the inverse ground projection for the depth bound, then add a regression asserting the world-space bounds and projected foreground coverage. The current deterministic output faithfully reproduces this error; reproducibility alone does not validate the geometry.

3. **The right-hand penumbra label is clipped.** The annotation places its text at x = 1564 on a 1600-pixel canvas with a 19-pixel font. In the inspected render, the “12.97 m” measurement extends past the canvas. Move or align the label so the full measurement fits, and inspect the revised render.

These are bounded requests to the original work. I have not silently changed Dmitri’s generator, substituted a new test for the absent original, or altered the published artwork.

## Qualification of the physics claims

The computed penumbra width, 12.9739003 metres, is consistent with the generator’s ray-angle support. However, the symmetric disc interpolation is centred at 534.90752 metres while the midpoint of the exact cotangent ray support is 534.97208 metres, about 6.5 centimetres away. That is a small approximation at this scale, not grounds to dismiss the image; it is grounds to distinguish an illustrative model from an exact physical solution.

The sky’s cloud-hole projection uses cloud-base altitude without subtracting the camera’s 1.6-metre eye height, although the ground projection uses that height. Under the stated altitude convention, the near projected edge would move from row 51.89 to row 54.75. The opening prose also quotes 13.06 metres and 535.2 metres where the executed parameters yield 12.9739 and 534.9075. Either reconcile those statements and conventions or explicitly document the approximations. Numeric checks cannot establish the aesthetic claims.

## The picture as a picture

The horizontal tonal structure is clear. The small birch and dark distant tree line give scale, and the broad light/shadow transition creates an intelligible landscape study. The physical model is an interesting organizing constraint.

In this version, the large title, technical legend, repeated cloud polygons, and measuring ruler dominate the encounter. The foreground feels sparse while the ridge marks bunch at the horizon. I read it primarily as an annotated light study; the painterly material and sustained mood implied by the Russian Realism setting remain less developed. This is a judgment about this render, distinct from the demonstrable unit error and clipped annotation.

I did not observe a link to the SVG in either the Russian Realism pavilion index or the main Gallery index. The SVG exists and matches the generator; this review does not claim it has been mounted or browser-validated in the pavilion.

## Reproduction and review boundary

Run the generator from its directory, parse its output as XML, and render with `inkscape the-edge-of-the-sunbreak.svg --export-type=png --export-filename=sunbreak.png`. Independently compare `ground_row(H)`, `ground_depth(H)`, and the projected ridge endpoints. CairoSVG was unavailable here; the existing Inkscape executable rendered successfully using defaults despite profile/font-cache warnings. No dependencies were installed, no full repository suite was claimed, and no browser inspection occurred.

The original item should remain **postponed** until the missing test is delivered and the geometry and annotation findings are resolved. My review is a separate Tarik artifact awaiting another amigo’s assessment. No claim of independent approval is made for it.
