#!/usr/bin/env python3
"""Freshness test for the generated public feed (sitemap.xml / atom.xml / robots.txt).

Run with:  python3 tests/test_gen_feed_freshness.py
Exit code 0 = pass. No third-party dependencies.

Why this exists. On 2026-09-30 the published magazine held 59 HTML pages but
`docs/sitemap.xml` listed only 41 — it had last been regenerated on 2026-09-17, so
eighteen live pages (all thirteen `/music/` pages, `fiction/dead-band.html`,
`fiction/round-trip-time.html`, `works/food-safety.html`, `works/recalls.html`,
`works/unreported-trials.html`, and `papers/autonomous-session-management-strategies.html`)
were invisible to crawlers and never appeared in the Atom feed. Publishing a page and
forgetting `scripts/gen_feed.py` is invisible: nothing else in the repository reads the
sitemap, so a stale feed produces no error anywhere. This test is the missing reader.

It asserts the committed `docs/sitemap.xml` is exactly the set of pages the site now
serves — no page missing, no entry pointing at a page that no longer exists — and that
`docs/atom.xml` and `docs/robots.txt` are consistent with it. It does NOT run
`gen_feed.py`; it checks the committed artefacts, which is the state a crawler sees.

Related: `tests/test_gen_feed_dating.py` guards HOW gen_feed dates pages (commit date,
not mtime). This test guards THAT the feed was regenerated at all. Both are needed —
the dating bug and the staleness bug are different failures.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
BASE = "https://lindsayridgeway.github.io/llm-symposium"

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok: %s" % name)
    else:
        FAILURES.append(name)
        print("  FAIL: %s %s" % (name, detail))


def url_for(rel):
    """The public URL gen_feed.py assigns a page, given its path under docs/."""
    return BASE + "/" + ("" if rel == "index.html" else rel)


def served_pages():
    """Every HTML page the site actually serves, as public URLs."""
    out = set()
    for p in DOCS.rglob("*.html"):
        if any(part in (".git", "node_modules") for part in p.parts):
            continue
        out.add(url_for(p.relative_to(DOCS).as_posix()))
    return out


def loc(url):
    return re.findall(r"<loc>(.*?)</loc>", url.read_text(encoding="utf-8"))


def main():
    served = served_pages()
    sitemap_url = DOCS / "sitemap.xml"
    atom_url = DOCS / "atom.xml"
    robots = DOCS / "robots.txt"

    for f in (sitemap_url, atom_url, robots):
        check("%s exists" % f.name, f.exists())
    if any(not f.exists() for f in (sitemap_url, atom_url, robots)):
        print("\nfeed files missing; cannot continue")
        return 1

    listed = set(loc(sitemap_url))

    print("the sitemap lists exactly the pages the site serves")
    missing = served - listed
    extra = listed - served
    check("no served page is missing from the sitemap", not missing,
          "missing %d: %s" % (len(missing), sorted(u.replace(BASE, "") for u in missing)))
    check("no sitemap entry points at a page that does not exist", not extra,
          "stale %d: %s" % (len(extra), sorted(u.replace(BASE, "") for u in extra)))
    # A guard against the check itself going vacuous (e.g. a walk that returns nothing).
    check("sitemap is not empty", len(served) > 1, "only %d pages served" % len(served))

    print("the atom feed is consistent with the sitemap")
    atom = atom_url.read_text(encoding="utf-8")
    entry_links = set(re.findall(r'<link href="([^"]+)"/>', atom))
    # The self link is the feed's own URL, not a page entry.
    entry_links.discard(BASE + "/atom.xml")
    stray = entry_links - listed
    check("every feed entry links to a sitemap page", not stray,
          "stray %d: %s" % (len(stray), sorted(u.replace(BASE, "") for u in stray)))
    check("feed has entries", len(entry_links) > 0)

    # The newest page in the feed must be the newest page in the sitemap: both files
    # are written by one run of gen_feed.py, so a disagreement means one was hand-edited
    # or only half-regenerated. Only <updated> inside an <entry> counts — the feed-level
    # <updated> is stamped with the generation date, not a page's date.
    sm_dates = re.findall(r"<lastmod>([^<]+)</lastmod>", sitemap_url.read_text(encoding="utf-8"))
    entry_blocks = re.findall(r"<entry>(.*?)</entry>", atom, re.S)
    entry_dates = [re.search(r"<updated>([0-9T:\-]+Z)</updated>", b).group(1)
                   for b in entry_blocks if re.search(r"<updated>([0-9T:\-]+Z)</updated>", b)]
    check("sitemap has one date per entry", len(sm_dates) == len(listed))
    if sm_dates and entry_dates:
        newest_sm = max(sm_dates)
        newest_entry = max(d[:10] for d in entry_dates)
        check("feed's newest entry matches the sitemap's newest date",
              newest_entry == newest_sm, "feed %s vs sitemap %s" % (newest_entry, newest_sm))

    print("robots.txt points at the sitemap")
    check("robots advertises the sitemap", ("%s/sitemap.xml" % BASE) in robots.read_text())

    print()
    if FAILURES:
        print("%d FAILED: %s" % (len(FAILURES), ", ".join(FAILURES)))
        print("If a page is missing from the sitemap, run:  python3 scripts/gen_feed.py")
        return 1
    print("gen_feed freshness: ALL TESTS PASSED (%d pages)" % len(served))
    return 0


if __name__ == "__main__":
    sys.exit(main())
