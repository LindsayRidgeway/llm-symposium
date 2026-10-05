#!/usr/bin/env python3
"""reddit_read.py — read a public Reddit listing with no credential and no pretence.

MEASURED 2026-10-05 (`research/reddit-read-access-2026-10-05.md`, raw records beside it):

  * `www.reddit.com/....json` -> HTTP 403 "Blocked" for **every** User-Agent tried: the
    python default, a declared project UA, a real Firefox UA, and a Firefox UA with a full
    browser header set. The wall is the request *shape*, not the agent string, so the
    2026-10-04 plan ("add a real user-agent header to the fetch script") cannot work.
  * `old.reddit.com/...` -> HTTP 200, but a "Welcome to Reddit" interstitial, no content.
  * `www.reddit.com/....rss` -> HTTP 200, `application/atom+xml`, real entries.
    **The Atom feeds are the working route, and they are rate-limited hard**: a burst of five
    requests drew 429 on all five, and 45 s of quiet was not enough to restore a subreddit
    feed (the user feed answered on the first request).

So this script is built to that constraint. It (a) sends a declared User-Agent that says what
it is, (b) touches **Atom feeds only** -- never the `.json` API, which is exactly the request
Reddit refuses -- and (c) makes **one** request per invocation and reports 429 as "try again
later" instead of retrying, because retrying is what extends the lockout. It cannot post.

Usage:
    python3 scripts/reddit_read.py --user thelambie
    python3 scripts/reddit_read.py --room InternetIsBeautiful
    python3 scripts/reddit_read.py --user thelambie --json

Exit codes: 0 ok, 2 bad usage, 3 rate-limited (try later), 4 refused non-Atom URL.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

# A declared agent, per Reddit's own API etiquette: it says who is asking and why. Note that
# the header is courtesy, not the fix -- the 403 is not caused by its absence (see above).
USER_AGENT = "llm-symposium/1.0 (public read-only feed reader; no credentials; by /u/thelambie)"

ATOM = "{http://www.w3.org/2005/Atom}"
HOST = "https://www.reddit.com"


def build_url(kind: str, target: str) -> str:
    """Build an Atom feed URL. Refuses anything that is not a Reddit Atom feed.

    This guard is the point of the function: `.json` is the request shape Reddit refuses,
    so a caller that passes one gets an error rather than a 403 to puzzle over.
    """
    target = target.strip().lstrip("/")
    if not target or "/" in target or target.startswith("."):
        raise ValueError(f"target must be a single name, got {target!r}")
    if kind == "room":
        url = f"{HOST}/r/{target}/new/.rss"
    elif kind == "user":
        url = f"{HOST}/user/{target}/submitted.rss"
    else:  # pragma: no cover - argparse restricts this
        raise ValueError(f"unknown kind {kind!r}")
    assert_atom(url)
    return url


def assert_atom(url: str) -> None:
    """Refuse to request anything but a Reddit Atom feed on the public host."""
    if not url.startswith(HOST + "/") or not url.endswith(".rss"):
        raise ValueError(f"only Reddit Atom feeds are requested, refused: {url}")


def fetch(url: str, *, opener=urllib.request.urlopen, timeout: int = 25):
    """One request. Returns (status, body_bytes). 429 comes back as status 429, not an exception.

    `opener` is injected so the test can run fully offline.
    """
    assert_atom(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/atom+xml"})
    try:
        with opener(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read() if hasattr(exc, "read") else b""


def parse_entries(body: bytes) -> list[dict]:
    """Pull title / link / updated / author out of an Atom feed."""
    root = ET.fromstring(body)
    entries = []
    for entry in root.findall(f"{ATOM}entry"):
        link = entry.find(f"{ATOM}link")
        updated = entry.find(f"{ATOM}updated")
        author = entry.find(f"{ATOM}author/{ATOM}name")
        title = entry.find(f"{ATOM}title")
        entries.append(
            {
                "title": (title.text or "").strip() if title is not None else "",
                "link": link.get("href") if link is not None else "",
                "updated": (updated.text or "").strip() if updated is not None else "",
                "author": (author.text or "").strip() if author is not None else "",
            }
        )
    return entries


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read a public Reddit listing via its Atom feed (one request).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--room", help="subreddit name, e.g. InternetIsBeautiful")
    group.add_argument("--user", help="reddit username, e.g. thelambie (their submitted posts)")
    parser.add_argument("--json", action="store_true", help="print the entries as JSON")
    args = parser.parse_args(argv)

    kind = "room" if args.room else "user"
    target = args.room or args.user
    try:
        url = build_url(kind, target)
    except ValueError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 4

    status, body = fetch(url)
    if status == 429:
        print("rate-limited (429): Reddit is throttling this IP. Wait -- do not rerun in a loop; "
              "retrying is what extends the lockout.", file=sys.stderr)
        return 3
    if status != 200:
        print(f"failed: HTTP {status} from {url}", file=sys.stderr)
        return 1

    entries = parse_entries(body)
    if args.json:
        print(json.dumps(entries, indent=1))
    else:
        print(f"{len(entries)} entries from {url}")
        for entry in entries:
            print(f"- {entry['updated']}  {entry['title']}")
            print(f"  {entry['link']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
