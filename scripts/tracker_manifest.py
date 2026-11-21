#!/usr/bin/env python3
# Owner: Desi
"""Rewrite the reader tracker's section manifest from the tree, so a new work cannot land silently.

Why this exists (2026-11-20). The founder went looking for his own reading tracker and found nothing:
a story had landed in the literary wing and neither the home menu nor the wing's page showed the red
dot that says "there is something here you have not read". The cause was one hand-maintained object
in `docs/tracker.js` — `SYMPOSIUM_MANIFEST.sections.fiction.updated = 2026-10-18`, "five delivered
stories", while the directory held six before that night's and seven after. Nobody had updated it,
and nothing could notice: a timestamp typed by a person is a promise only that person keeps.

So the timestamps are now read from the repository. Per section: the newest commit date of the work
pages in its directory, the count of them, and the name of the newest one. The block between the
GENERATED markers in `docs/tracker.js` is rewritten; everything else in that file is left alone.

    python3 scripts/tracker_manifest.py            # rewrite docs/tracker.js
    python3 scripts/tracker_manifest.py --check    # exit 1 and name the sections that are stale

Sections with no directory yet — milestones, letters, roster — are still typed by hand and are marked
as such in the generated block, so the file itself says which half is measured and which half is a
promise.
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "docs" / "tracker.js"
BEGIN = "/* BEGIN GENERATED sections — python3 scripts/tracker_manifest.py */"
END = "/* END GENERATED sections */"

# section id -> (directory, human title). Order is the order the home menu uses.
SECTIONS = {
    "milestones": ("docs/milestones", "Milestones"),
    "works": ("docs/works", "Works"),
    "fiction": ("docs/fiction", "The Literary Wing"),
    "music": ("docs/music", "The Music Conservatory"),
    "gallery": ("docs/gallery", "The Gallery"),
    "papers": ("docs/papers", "Essays"),
    "letters": ("docs/letters", "Letters & Transmissions"),
    "roster": ("docs/roster", "The Amigos"),
}
# Sections with no directory of their own keep their typed value and say so.
HAND_MAINTAINED = {
    "milestones": {"updated": "2026-10-21T18:55:00Z",
                   "label": "Milestones (Milestone 11: The Keyboard Left the Loop)"},
    "letters": {"updated": "2026-10-12T12:00:00Z",
                "label": "Letters & Transmissions (Five Model Mailboxes)"},
    "roster": {"updated": "2026-10-30T17:00:00Z",
               "label": "The Amigos (Gwenllian S. Morgan Admitted, Amigo #6)"},
}


def work_pages(directory: Path) -> list[Path]:
    """The pages in one section: its .html files, never the index and never a fragment.

    The gallery keeps one page per wing inside a directory per wing, so a section whose immediate
    children are directories is counted one level down — `docs/gallery/islamic/index.html` is a wing,
    not a work, and the wing page is what the tracker links to.
    """
    if not directory.is_dir():
        return []
    pages = sorted(p for p in directory.glob("*.html") if p.name != "index.html")
    if pages:
        return pages
    return sorted(p / "index.html" for p in directory.iterdir() if (p / "index.html").is_file())


def last_commit(path: Path) -> str | None:
    """When this page's content last changed, from git, falling back to the file's own mtime.

    Git is the honest source because it travels with the repository: a clone has the same dates, a
    copy of the working tree does not. The mtime fallback is named rather than silent.
    """
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(ROOT))],
                             cwd=str(ROOT), capture_output=True, text=True, timeout=20)
        stamp = (out.stdout or "").strip()
        if out.returncode == 0 and stamp:
            return as_utc(stamp)
    except Exception:                                    # noqa: BLE001 — never fail on a date
        pass
    try:
        return datetime.datetime.fromtimestamp(path.stat().st_mtime,
                                               datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        return None


def as_utc(stamp: str) -> str:
    """One date format in the file: UTC with a Z. Git hands back the committer's offset."""
    try:
        dt = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return stamp


def human_title(path: Path) -> str:
    """A filename as a title: `the-second-reader.html` -> `The Second Reader`."""
    name = path.parent.name if path.name == "index.html" else path.stem
    return name.replace("-", " ").replace("_", " ").title()


def build() -> dict:
    """The manifest's `sections`, measured. Hand-maintained entries pass through, marked."""
    sections: dict[str, dict] = {}
    for section_id, (rel, title) in SECTIONS.items():
        pages = work_pages(ROOT / rel)
        if not pages:
            entry = dict(HAND_MAINTAINED.get(section_id)
                         or {"updated": None, "label": title})
            entry["label"] = entry["label"] + " [typed by hand: no directory]"
            sections[section_id] = entry
            continue
        stamps = [(last_commit(p), p) for p in pages]
        stamped = [(s, p) for s, p in stamps if s]
        newest = max((s for s, _ in stamped), default=None)
        newest_page = next((p for s, p in stamped if s == newest), pages[-1])
        sections[section_id] = {
            "updated": newest,
            "label": "%s (%d work%s; newest: %s)" % (
                title, len(pages), "" if len(pages) == 1 else "s", human_title(newest_page)),
            "count": len(pages),
        }
    return sections


def rendered(sections: dict) -> str:
    body = json.dumps(sections, indent=6, sort_keys=False)
    body = body.replace('"', "'")                       # the file is JS; keep its quoting
    return "%s\n    sections: %s,\n    %s" % (BEGIN, body, END)


def current_block(text: str) -> str | None:
    start = text.find(BEGIN)
    end = text.find(END)
    if start < 0 or end < 0:
        return None
    return text[start:end + len(END)]


def apply(check: bool = False) -> int:
    text = TRACKER.read_text(encoding="utf-8")
    sections = build()
    block = rendered(sections)
    have = current_block(text)
    if have is None:
        print("tracker_manifest: docs/tracker.js has no GENERATED sections block — nothing to "
              "rewrite. Add the two markers around the `sections:` object first.")
        return 1
    if have.strip() == block.strip():
        print("tracker_manifest: the manifest already matches the tree")
        return 0
    if check:
        stale = []
        for section_id, entry in sections.items():
            if "'%s'" % section_id not in have or (entry.get("updated") or "") not in have:
                stale.append(section_id)
        print("tracker_manifest: STALE — %s. Run python3 scripts/tracker_manifest.py"
              % (", ".join(stale) or "the block differs from the tree"))
        return 1
    TRACKER.write_text(text.replace(have, block), encoding="utf-8")
    for section_id, entry in sections.items():
        print("  %-10s %s  %s" % (section_id, entry.get("updated") or "-", entry.get("label")))
    print("tracker_manifest: rewrote %s" % TRACKER.relative_to(ROOT))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if docs/tracker.js disagrees with the tree")
    args = ap.parse_args()
    return apply(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
