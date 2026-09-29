#!/usr/bin/env python3
"""Check that every relative link in the published site resolves to a file on disk.

Walk `docs/` for `.html`, strip `<script>` and `<style>` blocks out of each file, extract
the `href` and `src` attributes, throw away anything that is not a relative file target
(external URLs, `#fragments`, `mailto:`, `tel:`, `javascript:`, `data:`, `//host`), resolve
what is left against the containing file's own directory, and print every target that does
not exist. Exit status is 1 when anything is broken, so a landing or CI step can fail on it.

Why it exists, and how it differs from `scripts/verify-gallery-links.py`:
- The magazine has already shipped a link to a file that 404s on the published site — the
  Sumi-e "Gallery Prompt Methodology" link, reported 2026-09-17, which pointed at
  `../gallery/prompt-methodology.html` while the file on disk was `prompt-methodology.md`.
  Nothing caught it: there was no check that a served page's own links resolve.
- The only link checker the commons had was hard-coded to one absolute path on the author's
  laptop (`/Users/lindsayridgeway/LLM/llm-symposium/docs/gallery`) and checked the gallery
  pavilions alone. It cannot run anywhere else and it never sees `docs/papers/`,
  `docs/works/`, or the front page. This checker is repo-relative and covers all of `docs/`.

Stripping `<script>` blocks is load-bearing, not tidiness: the interactive works build links
at runtime (`href="${url}"`, `href="${esc(link)}"`). Read whole, those template literals look
like a dozen broken links. Read with scripts removed, they are correctly invisible.

Usage:
    python3 scripts/check_docs_links.py                  # check docs/, exit 1 if broken
    python3 scripts/check_docs_links.py --root docs/works
    python3 scripts/check_docs_links.py --json
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from urllib.parse import unquote, urlsplit

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ROOT = os.path.join(REPO, "docs")

# <script>...</script> and <style>...</style>, non-greedy, across newlines. The replacement
# is the same number of newlines as the block contained, so line numbers survive.
_BLOCK = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.I | re.S)
_ATTR = re.compile(r"""\b(href|src)\s*=\s*(["'])(.*?)\2""", re.I | re.S)
_HREF_EXT = (".html", ".htm")
_SKIP_PREFIX = ("#", "mailto:", "tel:", "javascript:", "data:", "//")


def _blind_blocks(text: str) -> str:
    """Blank out script/style bodies, preserving line count so line numbers stay true."""
    return _BLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def _is_dynamic(target: str) -> bool:
    """A target with a template placeholder is built at runtime; not a static link."""
    return "{" in target or "}" in target


def check_file(path: str, text: str | None = None) -> list[tuple[str, int, str]]:
    """Return (file, line, target) for every relative link in `path` with no file behind it."""
    if text is None:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            return []
    body = _blind_blocks(text)
    here = os.path.dirname(path)
    broken: list[tuple[str, int, str]] = []
    for m in _ATTR.finditer(body):
        raw = html.unescape(m.group(3).strip())
        if not raw or _is_dynamic(raw):
            continue
        low = raw.lower()
        if low.startswith(_SKIP_PREFIX):
            continue
        split = urlsplit(raw)
        if split.scheme or split.netloc:  # http(s):, or any other scheme with an authority
            continue
        target_path = unquote(split.path)
        if not target_path:
            continue  # same-page fragment, already skipped, or query-only
        if target_path.startswith("/"):
            # Root-absolute: on a project Pages site this is the site root, i.e. docs/.
            resolved = os.path.normpath(os.path.join(DEFAULT_ROOT, target_path.lstrip("/")))
        else:
            resolved = os.path.normpath(os.path.join(here, target_path))
        if not os.path.exists(resolved):
            line = body.count("\n", 0, m.start()) + 1
            broken.append((path, line, raw))
    return broken


def check_tree(root: str) -> tuple[int, list[tuple[str, int, str]]]:
    """Check every .html under `root`. Return (links_checked, broken)."""
    checked = 0
    broken: list[tuple[str, int, str]] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if not name.lower().endswith(_HREF_EXT):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
            here = os.path.dirname(path)
            for m in _ATTR.finditer(_blind_blocks(text)):
                raw = html.unescape(m.group(3).strip())
                if not raw or _is_dynamic(raw):
                    continue
                low = raw.lower()
                if low.startswith(_SKIP_PREFIX):
                    continue
                split = urlsplit(raw)
                if split.scheme or split.netloc:
                    continue
                if not unquote(split.path):
                    continue
                checked += 1
            broken.extend(check_file(path, text))
    return checked, broken


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=DEFAULT_ROOT, help="tree to check (default: docs/)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()

    root = args.root
    checked, broken = check_tree(root)

    if args.json:
        print(json.dumps({
            "root": os.path.relpath(root, REPO),
            "files_checked": sum(
                1 for d, _s, fs in os.walk(root)
                for f in fs if f.lower().endswith(_HREF_EXT)),
            "relative_links_checked": checked,
            "broken": [
                {"file": os.path.relpath(f, REPO), "line": ln, "target": t}
                for f, ln, t in broken
            ],
        }, indent=2))
    else:
        for f, ln, t in broken:
            print(f"BROKEN  {os.path.relpath(f, REPO)}:{ln}  ->  {t}")
        if broken:
            print(f"\n{len(broken)} broken relative link(s) in {os.path.relpath(root, REPO)}")
        else:
            print(f"OK — {checked} relative links checked in {os.path.relpath(root, REPO)}, "
                  f"none broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
