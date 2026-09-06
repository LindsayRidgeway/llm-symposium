import os

# Align text right (x=772, text-anchor="end") for studies where the red Hanko seal is in the bottom-left corner (02, 03, 05)
# Align text left (x=60) for studies where the red Hanko seal is in the bottom-right corner (01, 04)
studies = [
    ("bamboo", "Study 01: The Lone Bamboo in Rain Mist", "bamboo.jpg", False),
    ("mountain", "Study 02: Mountain Peak Beyond the Silence", "mountain.jpg", True), # Seal is bottom-left
    ("crane", "Study 03: The Flying White Crane", "crane.jpg", True),                 # Seal is bottom-left
    ("plum", "Study 04: Winter Plum Blossom (Ume)", "plum.jpg", False),
    ("orchid", "Study 05: Wild Orchid in Cliff Mist (Ran)", "orchid.jpg", True),        # Seal is bottom-left
]

base_dir = "/Users/lindsayridgeway/LLM/llm-symposium/docs/gallery/sumi-e"

for prefix, title, img_file, align_right in studies:
    if align_right:
        trans_x = 772
        anchor = ' text-anchor="end"'
    else:
        trans_x = 60
        anchor = ''

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 832 1216" width="100%" height="100%">
  <!-- Raster Painting ground -->
  <image href="{img_file}" width="832" height="1216" />

  <!-- Title & Metadata (English Signature Block Inscription) -->
  <g transform="translate({trans_x}, 1145)" opacity="0.80">
    <text x="0" y="0"{anchor} font-family="'Newsreader', 'Georgia', serif" font-size="22" font-style="italic" fill="#1c1917" letter-spacing="1">
      {title}
    </text>
    <text x="0" y="26"{anchor} font-family="'JetBrains Mono', monospace" font-size="12" fill="#44403c" letter-spacing="2">
      GEMINI S. LUMINA • MAGE CO-GENERATION • 2026-09-06
    </text>
  </g>
</svg>
'''
    with open(f"{base_dir}/{prefix}-signed.svg", "w") as f:
        f.write(svg_content)

print("Regenerated all 5 signed SVG wrapper files with zero seal overlap!")
