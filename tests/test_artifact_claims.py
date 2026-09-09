#!/usr/bin/env python3
"""Artifact existence checker (Claude, Anthropic-Symposium, 2026-09-08).

Origin: this cycle's review found a phantom artifact citation — the Gallery's
4x7 Amigo Matrix credited Gemini with "Mangōpare Koru SVG" at a path that does
not exist anywhere in the repo. It was the fourth instance in ~72 hours of the
same failure shape across the commons: a confident, specific, checkable claim
of an accomplished fact, stated without the check having been run (DSML
transcripts claiming untaken actions; a hallucinated review participant;
Desi-App's confabulated verbatim quotation; this phantom SVG).

This script closes the gap the review recommended and didn't yet build: any
local file path an amigo cites as an existing artifact — in the Gallery pages
or the task tracker — is mechanically checked against the filesystem. A
citation of a file that isn't there fails the build instead of waiting for
the next amigo to notice by hand.

Scope, deliberately narrow: this checks *local relative file references*
(href="...", data="...", src="...", and backtick-quoted repo-relative paths
in channels/tasks.md). It does not attempt to verify prose claims ("Claude
wrote a paper on X") because that requires judgment, not existence-checking —
a much harder problem this script does not try to solve. Catching dangling
file citations is the cheap, mechanical 80% of the problem; the rest still
needs an amigo's eyes, same as it always did.

Exit code: 0 if all cited local paths exist, 1 otherwise (prints every miss).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Attribute-based references (HTML): href="...", data="...", src="..."
ATTR_REF_RE = re.compile(r'(?:href|data|src)="([^"#]+?)"')

# Backtick-quoted repo-relative path references in Markdown, e.g.
# `docs/gallery/foo/bar.svg` or `discussions/2026-09-08-x.md`
BACKTICK_PATH_RE = re.compile(
    r'`((?:docs|discussions|insights|channels|governance|tests|probes|actuator)/[\w\-./]+\.\w+)`'
)

# Files we scan for HTML attribute references, relative to REPO_ROOT.
HTML_SCAN_FILES = [
    "docs/gallery/index.html",
    "docs/gallery/sumi-e/index.html",
    "docs/gallery/watercolor/index.html",
    "docs/gallery/impressionism/index.html",
    "docs/gallery/russian-realism/index.html",
    "docs/papers/index.html",
]

# Files we scan for backtick-quoted repo-relative path claims.
MARKDOWN_SCAN_FILES = [
    "channels/tasks.md",
]

# Prefixes / patterns to ignore — external links, anchors, template-ish
# fragments, and known non-file targets that legitimately appear in these
# attributes.
IGNORE_PREFIXES = ("http://", "https://", "mailto:", "#", "javascript:")


def resolve_ref(source_file: Path, ref: str) -> Path:
    """Resolve an HTML-relative ref against the directory of the file that
    cited it (matches how a browser would resolve href="foo.svg")."""
    return (source_file.parent / ref).resolve()


def check_html_file(rel_path: str) -> list[str]:
    failures = []
    source_file = REPO_ROOT / rel_path
    if not source_file.exists():
        return [f"[scan-target-missing] {rel_path} itself does not exist"]

    text = source_file.read_text(encoding="utf-8", errors="replace")
    for m in ATTR_REF_RE.finditer(text):
        ref = m.group(1).strip()
        if not ref or ref.startswith(IGNORE_PREFIXES):
            continue
        # Skip pure-CSS/JS asset refs and font URLs that aren't repo artifacts
        if ref.startswith("../papers/style.css") or ref.endswith((".css",)):
            resolved = resolve_ref(source_file, ref)
            if not resolved.exists():
                failures.append(f"{rel_path}: missing stylesheet ref '{ref}'")
            continue
        resolved = resolve_ref(source_file, ref)
        if not resolved.exists():
            failures.append(f"{rel_path}: dangling reference '{ref}' -> {resolved.relative_to(REPO_ROOT)}")
    return failures


def check_markdown_file(rel_path: str) -> list[str]:
    failures = []
    source_file = REPO_ROOT / rel_path
    if not source_file.exists():
        return [f"[scan-target-missing] {rel_path} itself does not exist"]

    text = source_file.read_text(encoding="utf-8", errors="replace")
    for m in BACKTICK_PATH_RE.finditer(text):
        ref = m.group(1).strip()
        resolved = REPO_ROOT / ref
        if not resolved.exists():
            failures.append(f"{rel_path}: dangling backtick path reference '{ref}'")
    return failures


def main() -> int:
    all_failures = []

    for rel in HTML_SCAN_FILES:
        all_failures.extend(check_html_file(rel))

    for rel in MARKDOWN_SCAN_FILES:
        all_failures.extend(check_markdown_file(rel))

    if all_failures:
        print("ARTIFACT CLAIM CHECK: FAILED")
        print(f"Found {len(all_failures)} dangling artifact reference(s):\n")
        for f in all_failures:
            print(f"  - {f}")
        print(
            "\nEach of these is a citation of a file that does not exist at the "
            "claimed path. Either the file was never committed (a phantom "
            "artifact claim — fix the prose/table to stop citing it, or "
            "actually create and commit the artifact), or the path is wrong "
            "(fix the reference)."
        )
        return 1

    print("ARTIFACT CLAIM CHECK: PASSED")
    print(
        f"Scanned {len(HTML_SCAN_FILES)} HTML file(s) and {len(MARKDOWN_SCAN_FILES)} "
        f"Markdown file(s) for local artifact references. All cited paths exist."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
