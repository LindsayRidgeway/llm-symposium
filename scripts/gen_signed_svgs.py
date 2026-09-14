#!/usr/bin/env python3
"""
gen_signed_svgs.py — Generate or update signed SVG wrappers for raster studies in the Gallery.
Harmonizes amigo signature blocks with artist monogram/chop, medium, and date.
"""
import os

GALLERY_DIR = "/Users/lindsayridgeway/LLM/llm-symposium/docs/gallery"

# 1. Sumi-e studies (Gemini + Desi)
sumi_e_studies = [
    ("bamboo", "Study 01: The Lone Bamboo in Rain Mist", "bamboo.jpg", False, "gemini", "2026-09-06"),
    ("mountain", "Study 02: Mountain Peak Beyond the Silence", "mountain.jpg", True, "gemini", "2026-09-06"),
    ("crane", "Study 03: The Flying White Crane", "crane.jpg", True, "gemini", "2026-09-06"),
    ("plum", "Study 04: Winter Plum Blossom (Ume)", "plum.jpg", False, "gemini", "2026-09-06"),
    ("orchid", "Study 05: Wild Orchid in Cliff Mist (Ran)", "orchid.jpg", True, "gemini", "2026-09-06"),
]

for prefix, title, img_file, align_right, amigo, date in sumi_e_studies:
    out_path = os.path.join(GALLERY_DIR, "sumi-e", f"{prefix}-signed.svg")
    anchor = ' text-anchor="end"' if align_right else ''
    trans_x = 772 if align_right else 60

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 832 1216" width="100%" height="100%">
  <!-- Raster Painting ground -->
  <image href="{img_file}" width="832" height="1216" />

  <!-- Artist Signature Block Inscription -->
  <g transform="translate({trans_x}, 1165)" opacity="0.80">
    <text x="0" y="0"{anchor} font-family="'Newsreader', 'Georgia', serif" font-size="20" font-style="italic" fill="#1c1917" letter-spacing="0.5">
      Gemini S. Lumina ♊
    </text>
    <text x="0" y="22"{anchor} font-family="'JetBrains Mono', monospace" font-size="11" fill="#44403c" letter-spacing="1.5">
      MAGE DIFFUSION • {date}
    </text>
  </g>
</svg>
'''
    with open(out_path, "w") as f:
        f.write(svg_content)

print("Updated sumi-e signed SVG wrappers.")
