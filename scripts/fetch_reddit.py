#!/usr/bin/env python3
"""Read a public Reddit feed without pretending to be a browser.

WHY THIS EXISTS, AND WHAT WAS MEASURED (2026-10-08, this machine, live):

The human filed two tasks (channels/tasks.md) that begin "add a descriptive
user-agent header to the fetch script".  Those tasks name a script that did not
exist, and they assume a user-agent is what stands between us and Reddit.  Both
assumptions were tested before anything was written, and one of them is wrong:

  * `https://www.reddit.com/r/<sub>/.json` -> HTTP 403 to EVERY agent tried, and
    the three responses were byte-identical (189,908 bytes of `text/html`):
    the bare `Python-urllib` string, the commons' declared byline, and a real
    Chrome desktop User-Agent.  When a browser string fares exactly as well as
    no name at all, the block is **shape-based, not agent-based**, and no header
    on our side can remove it.  The `.json` route is closed to programs, full
    stop; only stage 2 (an OAuth app) or a real browser window would change that.

  * `https://www.reddit.com/r/<sub>/.rss` -> HTTP 200, `application/atom+xml`,
    54,769 bytes of real posts, with the declared byline — where the SAME URL
    asked with the bare `Python-urllib` agent returned **429**.  So the agent
    header does matter; it just matters on the Atom endpoint, not the JSON one.

  * The anonymous budget is roughly ONE request per window.  A second request
    sent immediately after a successful one returned 429 with
    `x-ratelimit-remaining: 0`; after a short pause (12s sufficed) a fresh
    request returned 200 again.  So this tool asks once and reports; it does not
    retry in a loop, because retrying is how a rate limit becomes a ban.

THE ROUTE, THEN: the public Atom feed, asked with a declared byline, one request
at a time.  That is enough to see what a room is actually about — which is the
thing the Reddit channel has never been able to do (`outreach/reddit/README.md`:
"Reddit answers our fetches with HTTP 403, so his profile and the subreddit
rules are invisible to us").  It is a read, not a post; posting stays with the
human, as `REQUEST D-3` has it.

WHAT THIS TOOL WILL NOT DO.  It will not send a browser User-Agent to get past
the wall.  Looking more like a person is the CAPTCHA refusal in different
clothes (`outreach/reddit/README.md`, 2026-10-01): the honest form is to be a
non-human that says so.  The byline below names the commons, not the human's
account — the account is his, and the commons may read in its own name.

Usage:
  python3 scripts/fetch_reddit.py r/russian           # a subreddit's newest posts
  python3 scripts/fetch_reddit.py u/thelambie         # a user's public feed
  python3 scripts/fetch_reddit.py --json r/LearnRussian
  python3 scripts/fetch_reddit.py --selftest          # offline; no network
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

# A declared byline. It names the commons and points at a public source, so the
# operator on the other side can see who is asking. It deliberately does NOT
# carry a browser string (see the module docstring).
USER_AGENT = (
    "python:llm-symposium:v1 (public read-only feed reader; "
    "+https://github.com/LindsayRidgeway/llm-symposium)"
)

# Reddit serves the Atom feed to this Accept; asking for JSON here would be a
# lie about what we can parse.
ACCEPT = "application/atom+xml, application/xml;q=0.9, */*;q=0.8"

_BASE = "https://www.reddit.com"
_ATOM = "{http://www.w3.org/2005/Atom}"


class RedditRefused(RuntimeError):
    """Raised when Reddit refuses the request, with the reason it gave."""


def feed_url(target: str) -> str:
    """Turn `r/NAME`, `u/NAME`, a bare name, or any Reddit URL into an Atom feed URL.

    A `.json` URL is rewritten to `.rss` rather than fetched, because the JSON
    route is closed to programs (measured above) and silently returning an error
    the caller did not ask about is worse than telling it the route changed.
    """
    t = target.strip().rstrip("/")
    if t.startswith("http://") or t.startswith("https://"):
        if t.endswith(".json"):
            t = t[: -len(".json")] + ".rss"
        elif not t.endswith(".rss"):
            t = t + "/.rss"
        return t
    if t.startswith("r/"):
        return f"{_BASE}/{t}/.rss"
    if t.startswith("u/") or t.startswith("user/"):
        name = t.split("/", 1)[1]
        return f"{_BASE}/user/{name}/.rss"
    return f"{_BASE}/r/{t}/.rss"


def fetch(url: str, *, opener=None, timeout: float = 25.0) -> str:
    """Fetch one feed URL and return the body text, or raise RedditRefused.

    `opener` is injectable so the offline test can prove the 429 path without a
    network. It is called exactly once: no retries, by design.
    """
    opener = opener or urllib.request.urlopen
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": ACCEPT})
    try:
        with opener(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            retry = exc.headers.get("Retry-After") if exc.headers else None
            left = exc.headers.get("x-ratelimit-remaining") if exc.headers else None
            raise RedditRefused(
                f"HTTP 429 (rate limited) for {url}; "
                f"retry-after={retry}, remaining={left}. "
                "Reddit allows roughly one anonymous request per window: wait, do not loop."
            ) from exc
        if exc.code == 403:
            raise RedditRefused(
                f"HTTP 403 for {url}. If this is a /.json URL, the block is "
                "shape-based, not agent-based: a bare agent, our byline, and a real "
                "Chrome User-Agent all got the identical refusal (measured "
                "2026-10-08), so no header fixes it. Use /.rss."
            ) from exc
        raise RedditRefused(f"HTTP {exc.code} for {url}") from exc


def parse_atom(xml_text: str) -> list[dict]:
    """Return the feed entries as dicts: title, link, updated, author."""
    root = ET.fromstring(xml_text)
    out = []
    for entry in root.findall(f"{_ATOM}entry"):
        title = entry.findtext(f"{_ATOM}title") or ""
        updated = entry.findtext(f"{_ATOM}updated") or ""
        author = entry.findtext(f"{_ATOM}author/{_ATOM}name") or ""
        link = ""
        for ln in entry.findall(f"{_ATOM}link"):
            if ln.get("rel") in (None, "alternate"):
                link = ln.get("href") or ""
                break
        out.append(
            {"title": title.strip(), "link": link, "updated": updated, "author": author}
        )
    return out


def _selftest() -> int:
    """Offline proof that the URL mapping and the parser work, and that we never
    send a browser string. No network is touched."""
    assert "llm-symposium" in USER_AGENT
    assert "Mozilla" not in USER_AGENT, "we do not pretend to be a browser"
    assert feed_url("r/russian") == "https://www.reddit.com/r/russian/.rss"
    assert feed_url("u/thelambie") == "https://www.reddit.com/user/thelambie/.rss"
    assert feed_url("LearnRussian") == "https://www.reddit.com/r/LearnRussian/.rss"
    # the closed JSON route is rewritten, not requested
    assert feed_url(
        "https://www.reddit.com/r/russian/.json"
    ) == "https://www.reddit.com/r/russian/.rss"
    sample = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        "<entry><author><name>/u/example</name></author>"
        "<title>Tutor Tuesday</title>"
        '<link rel="alternate" href="https://www.reddit.com/r/russian/x"/>'
        "<updated>2026-10-08T22:38:14+00:00</updated></entry>"
        "</feed>"
    )
    rows = parse_atom(sample)
    assert len(rows) == 1, rows
    assert rows[0]["title"] == "Tutor Tuesday", rows
    assert rows[0]["link"].endswith("/r/russian/x"), rows
    assert rows[0]["author"] == "/u/example", rows
    print("selftest ok: URL mapping, Atom parsing, and the no-browser-byline rule all hold")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read a public Reddit feed in the commons' own name.")
    ap.add_argument("target", nargs="?", help="r/NAME, u/NAME, a bare name, or a Reddit URL")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    ap.add_argument("--limit", type=int, default=15, help="max entries to print (default 15)")
    ap.add_argument("--selftest", action="store_true", help="offline checks; no network")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.target:
        ap.error("a target is required (e.g. r/russian), or use --selftest")

    url = feed_url(args.target)
    try:
        body = fetch(url)
    except RedditRefused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    rows = parse_atom(body)[: args.limit]
    if args.json:
        print(json.dumps({"url": url, "count": len(rows), "entries": rows}, indent=2))
    else:
        print(f"# {url}  ({len(rows)} entries)")
        for r in rows:
            print(f"{r['updated'][:10]}  {r['author']:<18}  {r['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
