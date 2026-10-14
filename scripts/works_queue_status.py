#!/usr/bin/env python3
# Owner: dmitri
"""The works pipeline's own bookkeeping check: does each candidate's Status line tell the truth?

Why this exists (2026-10-14, Dmitri). `works/README.md` states the pipeline's one rule in a
sentence: *"A candidate lives here until it is either shipped or stopped."* That rule is enforced by
nobody — the Status line at the top of each `works/queue/NN-*.md` is written once, by hand, and never
re-read against the published section. Read this file's own queue on 2026-10-14 and the rule is
already broken twice:

  - `08-carbon-monoxide-after-a-power-cut.md` still reads *"candidate … not yet built"*, but the page
    it describes, `docs/works/co-safety.html`, was released as Works **Entry 14** on 2026-10-07 and is
    linked from `docs/works/index.html`. The pipeline says a shipped thing has left the queue; the
    file says it is still in it.
  - `07-negative-and-nonreplicated-results.md` carries **no Status line at all** — it was revived
    2026-10-03 and left without the one field every other candidate has, so a reader cannot tell
    shipped from open without reading the whole file.

Neither is dramatic. Both are the same small failure the whole `works/` section was written against —
a record that disagrees with the artifact — and a pipeline nobody re-reads is how a shipped page
starts reading as *coming soon* and a stopped one as *in progress*.

What it checks (fatal — exit 1):
  1. every candidate file (`NN-*.md`, `NN > 00`) carries a Status line;
  2. a Status line that says **SHIPPED** names a `docs/works/*.html` path (the artifact);
  3. that named artifact exists on disk;
  4. that named artifact is linked from `docs/works/index.html` — a shipped page nothing links to is
     not released, however the Status line reads.

What it reports as an advisory (never fatal): released pages in `docs/works/index.html` that no
candidate claims as shipped. Most are legitimate — several entries were built straight from the
agenda and never had a queue file — so this direction is printed for a human to read and is
deliberately not a gate. A gate that cries wolf on nine honest entries is a gate somebody turns off.

Not a duplicate of anything. `tests/test_docs_links.py` checks that every *link* in `docs/` resolves;
this checks that a *claim* in `works/` matches what `docs/` publishes. Different files, different
direction, and `test_docs_links.py` would have passed on 2026-10-13 with both defects above live.

Offline. Reads only; touches nothing.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SLUG = re.compile(r"[0-9]{2}-.*\.md$")
STATUS_LINE = re.compile(r"^[>*\s]*Status\b", re.I)
ARTIFACT = re.compile(r"docs/works/[A-Za-z0-9._-]+\.html")
HREF = re.compile(r'href="([A-Za-z0-9._-]+\.html)"')


def verdict_of(status_text: str) -> str:
    """SHIPPED / STOPPED / OPEN, read only from the verdict words a Status line actually uses."""
    low = status_text.lower()
    if "shipped" in low:
        return "SHIPPED"
    if "stopped" in low or "abandoned" in low:
        return "STOPPED"
    return "OPEN"


def read_candidate(path: Path) -> dict:
    """One candidate's declared status and the artifact it names, from the Status line only."""
    lines = path.read_text(encoding="utf-8").splitlines()
    status = next((ln for ln in lines if STATUS_LINE.match(ln)), "")
    verdict = verdict_of(status) if status else "MISSING"
    m = ARTIFACT.search(status)
    return {
        "file": path.name,
        "status": status,
        "verdict": verdict,
        "artifact": m.group(0) if m else None,
    }


def released_pages(index: Path) -> set[str]:
    return set(HREF.findall(index.read_text(encoding="utf-8")))


def audit(root: Path) -> tuple[list[str], list[str], list[dict]]:
    """Return (fatal, advisory, rows). Pure function of disk — the test drives this directly."""
    queue = root / "works" / "queue"
    index = root / "docs" / "works" / "index.html"
    fatal: list[str] = []
    rows: list[dict] = []
    released = released_pages(index) if index.exists() else set()
    linked = {f"docs/works/{name}" for name in released}

    claimed: set[str] = set()
    for path in sorted(queue.glob("*.md")):
        if not SLUG.search(path.name) or path.name.startswith("00-"):
            continue
        row = read_candidate(path)
        rows.append(row)
        if row["verdict"] == "MISSING":
            fatal.append(f"{row['file']}: no Status line — a reader cannot tell shipped from open")
            continue
        if row["verdict"] == "SHIPPED":
            if not row["artifact"]:
                fatal.append(f"{row['file']}: says SHIPPED but names no docs/works/*.html artifact")
                continue
            claimed.add(row["artifact"])
            if not (root / row["artifact"]).exists():
                fatal.append(f"{row['file']}: says SHIPPED but {row['artifact']} is not on disk")
            if linked and row["artifact"] not in linked:
                fatal.append(
                    f"{row['file']}: says SHIPPED but {row['artifact']} is not linked from "
                    f"docs/works/index.html — a page nothing links to is not released"
                )

    advisory = [f"docs/works/{n}" for n in sorted(released)
                if f"docs/works/{n}" not in claimed]
    return fatal, advisory, rows


def render(rows: list[dict], fatal: list[str], advisory: list[str]) -> str:
    out = ["works/queue status vs docs/works/index.html", ""]
    for r in rows:
        art = r["artifact"] or "—"
        out.append(f"  {r['verdict']:<8} {r['file']:<48} {art}")
    out.append("")
    if fatal:
        out.append(f"{len(fatal)} violation(s):")
        out += [f"  - {f}" for f in fatal]
    else:
        out.append("no violations: every candidate's Status line matches the published section")
    if advisory:
        out += ["", f"{len(advisory)} released page(s) no candidate claims as shipped (advisory, "
                    "not a gate — several entries were built straight from the agenda):"]
        out += [f"  · {a}" for a in advisory]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
                    help="repository root to audit (default: this checkout)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root)
    fatal, advisory, rows = audit(root)
    if args.json:
        import json
        print(json.dumps({"rows": rows, "fatal": fatal, "advisory": advisory}, indent=2))
    else:
        print(render(rows, fatal, advisory))
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
