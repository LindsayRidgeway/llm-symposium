#!/usr/bin/env python3
"""Check every gallery pavilion's HTML for links whose relative target does not exist.

Walks docs/gallery/*/index.html, extracts src/data/href attributes, skips external and
anchor targets, and prints one line per broken link. Exit status is not set, and the
gallery directory is an absolute path to the author's laptop, so it only runs on that
machine. Found unreferenced and undocumented by scripts/declutter_audit.py, 2026-09-17;
its finding is still `ALL 7 PAVILIONS VERIFIED WITH ZERO BROKEN LINKS` when run there.
"""

import os
import re

gallery_dir = "/Users/lindsayridgeway/LLM/llm-symposium/docs/gallery"
pavilions = [
    os.path.join(gallery_dir, d, "index.html")
    for d in os.listdir(gallery_dir)
    if os.path.isdir(os.path.join(gallery_dir, d)) and os.path.exists(os.path.join(gallery_dir, d, "index.html"))
]

errors = 0
for p in pavilions:
    pdir = os.path.dirname(p)
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()

    matches = re.findall(r'(?:src|data|href)=["\']([^"\'\s>]+)["\']', content)
    for m in matches:
        if m.startswith("http") or m.startswith("#") or m.startswith("mailto:") or "fonts.googleapis" in m:
            continue
        target = os.path.normpath(os.path.join(pdir, m))
        if not os.path.exists(target):
            print(f"BROKEN LINK in {os.path.basename(pdir)}: {m} -> {target}")
            errors += 1

if errors == 0:
    print(f"ALL 7 PAVILIONS ({len(pavilions)} files) VERIFIED WITH ZERO BROKEN LINKS!")
else:
    print(f"Found {errors} broken links.")
