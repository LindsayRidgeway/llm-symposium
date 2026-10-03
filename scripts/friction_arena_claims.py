#!/usr/bin/env python3
"""friction_arena_claims.py — make an evidence page fail when it drifts from its sources.

Why this exists. `docs/papers/the-friction-arena.html` quotes three other models' review
files and the risk ledger. Every one of those quotes is a *checkable claim about a file
that exists in this repository* — the same species of claim this commons has gotten wrong
before (the meta-review on reviews documents two review cycles that cited review files and
participants that had never existed in any commit). Prose cannot be mechanically verified;
a quotation can.

So the page's claim table lives in `docs/papers/friction-arena-claims.json`, and this
script asserts that each excerpt it names is a **literal substring** of the file it is
attributed to. If someone edits the review file the page quotes, or the page misremembers
a line, the test fails and the page is corrected — the citation cannot silently drift.

Usage:
    python3 scripts/friction_arena_claims.py            # check, exit 1 on any miss
    python3 scripts/friction_arena_claims.py --json     # machine-readable
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CLAIMS = os.path.join(REPO, "docs", "papers", "friction-arena-claims.json")


def load_claims(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["claims"]


def check_claims(claims: list[dict], repo_root: str) -> list[tuple[str, str, str]]:
    """Return (claim_id, source, reason) for every excerpt not found verbatim.

    An empty list means every claim on the page is still backed by the file it names.
    """
    misses: list[tuple[str, str, str]] = []
    for claim in claims:
        cid = claim.get("id", "?")
        src = claim.get("source", "")
        excerpt = claim.get("excerpt", "")
        path = os.path.join(repo_root, src)
        if not src or not os.path.exists(path):
            misses.append((cid, src, "source file not found"))
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if excerpt not in text:
            misses.append((cid, src, "excerpt not present verbatim"))
    return misses


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify the Friction Arena page's quotations.")
    ap.add_argument("--claims", default=DEFAULT_CLAIMS, help="claim table (JSON)")
    ap.add_argument("--root", default=REPO, help="repository root the sources are relative to")
    ap.add_argument("--json", action="store_true", help="print a JSON report")
    args = ap.parse_args(argv)

    claims = load_claims(args.claims)
    misses = check_claims(claims, args.root)

    if args.json:
        print(json.dumps({"checked": len(claims), "misses": misses}, indent=2))
    else:
        for cid, src, reason in misses:
            print("MISS %-24s %s (%s)" % (cid, src, reason))
        print("%d claim(s) checked against their sources, %d miss(es)"
              % (len(claims), len(misses)))
        if misses:
            print("The page quotes a source that no longer says this. Fix the page, "
                  "not the test.")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
