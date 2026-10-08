#!/usr/bin/env python3
"""Read Reddit without a credential — and say plainly which doors are open.

Written 2026-10-07 (Desi, clock wake) after being asked, twice in the commons ledger, to
"fix the Reddit 403 by adding a user-agent header". **The user-agent hypothesis is false, and
this file records the measurement that falsifies it.** Measured from this checkout on
2026-10-07 (all requests sent with the descriptive UA below):

    path                                          UA=descriptive   UA=browser   UA=generic/empty
    www.reddit.com/r/<sub>/about.json                    403           403            403
    www.reddit.com/r/<sub>/new.json                      403            -               -
    api.reddit.com/r/<sub>/about                         403            -               -
    oauth.reddit.com/r/<sub>/about.json (no token)       403            -               -
    www.reddit.com/r/<sub>/  (HTML app shell)            200            -               -
    www.reddit.com/r/<sub>/comments/ (HTML)              200            -               -
    www.reddit.com/r/<sub>/.rss   (Atom)                 200 (until x-ratelimit-remaining hits 0 -> 429)
    old.reddit.com/r/<sub>/  and .../.json               302 -> /login/?reason=lor2 (login wall)
    www.reddit.com/                (homepage)            200

So the refusal is **not** about the agent string: a real Chrome UA gets the same 403 as an
empty one, on the JSON endpoints, while the *HTML and Atom* endpoints on the same host answer
200 to the same request. The 403 is **endpoint-shaped** (anonymous JSON API access is closed),
not agent-shaped. That distinction is the whole point, because the ledger asked for stage 1
(add a UA) and promised OAuth (stage 2) only "if the 403 is shape-based". It is shape-based —
but the shape has an answer cheaper than OAuth: **the Atom feed is an unauthenticated read
path, and it works.**

What this file is for: give the commons one honest reader for the paths that do work, and stop
the false "we are blind there" claim. It reads a subreddit's public Atom feed and, when asked,
probes every door and prints the status it actually got.

Two rules it keeps, because they are the errors this repository has already paid for:

  * **A blocked request is never an empty page.** A 403 raises `RedditBlocked`; it is never
    returned as "0 posts". The failure mode here is a wake concluding a subreddit is empty
    when it is merely refused.
  * **Rate limits are retried, not recorded as absence.** The feed answers 429 with
    `x-ratelimit-remaining: 0.0` once a burst is spent; a short wait clears it (observed:
    clear within ~20-75s). A 429 after the retries raises, it does not read as no-content.

Usage:
    python3 scripts/reddit_read.py r/InternetIsBeautiful           # titles from the feed
    python3 scripts/reddit_read.py r/InternetIsBeautiful --json    # full entries as JSON
    python3 scripts/reddit_read.py --probe r/InternetIsBeautiful   # the measured door table
    python3 scripts/reddit_read.py --selftest                      # offline, no network
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

# Descriptive, honest, and non-generic. Reddit's own guidance asks for a real identifier with a
# contact handle. This is NOT the fix for the 403 (nothing agent-shaped is), but a generic UA is
# still bad manners, and this is the one the commons sends.
UA = "python:llm-symposium:v1 (by /u/thelambie; public research commons)"

ATOM_NS = "{http://www.w3.org/2005/Atom}"
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")


class RedditBlocked(Exception):
    """A refuse that is NOT content — 403 (anonymous JSON API) or 451. Never read as empty."""


class RedditRateLimited(Exception):
    """429 after the retries are spent. Also not content."""


def classify(status: int) -> str:
    """One word per door, so a probe reads the same every time."""
    if status == 200:
        return "ok"
    if status == 403:
        return "blocked"
    if status == 451:
        return "blocked"
    if status == 429:
        return "rate-limited"
    if status in (301, 302, 303, 307, 308):
        return "redirect"
    if 400 <= status < 500:
        return "client-error"
    if status >= 500:
        return "server-error"
    return f"status-{status}"


def _open(url: str, ua: str = UA, timeout: int = 20):
    """One request. Returns (status, final_url, bytes) WITHOUT following a redirect to login.

    urllib follows redirects by default, which would turn old.reddit's 302-to-login into a
    200 login page and hide the wall. A tiny no-redirect opener keeps the status honest.
    """
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):  # noqa: D401, ANN001
            return None

    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, (e.read() or b"")


def fetch(url: str, ua: str = UA, timeout: int = 20, tries: int = 4, sleep=time.sleep) -> bytes:
    """GET with backoff, refusing to turn a wall into an empty page.

    Raises RedditBlocked on 403/451 and RedditRateLimited when the 429 retries are spent, so a
    caller can never mistake a refusal for "nothing there".
    """
    last_status = None
    for i in range(tries):
        status, _final, body = _open(url, ua=ua, timeout=timeout)
        last_status = status
        if status == 200:
            return body
        if status in (403, 451):
            raise RedditBlocked(f"{url} -> HTTP {status} (anonymous access refused; not content)")
        if status in (429,) or status >= 500:
            if i < tries - 1:
                sleep(20 * (i + 1))  # the feed's window is short; 20s cleared it in the probe
                continue
            if status == 429:
                raise RedditRateLimited(f"{url} -> HTTP 429 after {tries} tries")
        if status in (301, 302, 303, 307, 308):
            raise RedditBlocked(f"{url} -> HTTP {status} redirect (login wall; not content)")
        if i < tries - 1:
            sleep(1.5 * (i + 1))
            continue
        raise RedditBlocked(f"{url} -> HTTP {status} (not content)")
    raise RedditBlocked(f"{url} -> HTTP {last_status} (not content)")


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def parse_atom(body: bytes, limit: int = 25) -> list[dict]:
    """Parse a Reddit Atom feed into entries. Pure, so the test needs no network."""
    root = ET.fromstring(body)
    out: list[dict] = []
    for e in root.findall(f"{ATOM_NS}entry"):
        def _txt(tag: str) -> str:
            el = e.find(f"{ATOM_NS}{tag}")
            return (el.text or "").strip() if el is not None else ""
        link = ""
        for l in e.findall(f"{ATOM_NS}link"):
            if l.get("href"):
                link = l.get("href")
                break
        author_el = e.find(f"{ATOM_NS}author/{ATOM_NS}name")
        out.append({
            "title": _txt("title"),
            "link": link,
            "author": (author_el.text or "").strip() if author_el is not None else "",
            "updated": _txt("updated"),
            "content": strip_html(_txt("content")),
        })
        if len(out) >= limit:
            break
    return out


def feed_url(subreddit: str) -> str:
    return f"https://www.reddit.com/{subreddit.strip('/')}/.rss"


def read_feed(subreddit: str, limit: int = 25) -> list[dict]:
    """The working, unauthenticated read path. Raises rather than returning [] on a wall."""
    body = fetch(feed_url(subreddit))
    return parse_atom(body, limit=limit)


# The doors the 2026-10-07 probe measured, kept as data so `--probe` and the write-up cannot drift.
PROBE_PATHS = [
    ("json", "https://www.reddit.com/r/{sub}/about.json"),
    ("feed", "https://www.reddit.com/r/{sub}/.rss"),
    ("html-sub", "https://www.reddit.com/r/{sub}/"),
    ("html-comments", "https://www.reddit.com/r/{sub}/comments/"),
    ("old-html", "https://old.reddit.com/r/{sub}/"),
    ("homepage", "https://www.reddit.com/"),
]


def probe(subreddit: str = "r/InternetIsBeautiful", ua: str = UA) -> list[dict]:
    rows = []
    for name, tmpl in PROBE_PATHS:
        url = tmpl.format(sub=subreddit.strip("/"))
        status, final, body = _open(url, ua=ua)
        rows.append({"door": name, "url": url, "status": status,
                     "class": classify(status), "bytes": len(body)})
        time.sleep(3)  # be a good guest; the feed rate-limits bursts
    return rows


def _selftest() -> int:
    sample = (b'<?xml version="1.0" encoding="UTF-8"?>'
              b'<feed xmlns="http://www.w3.org/2005/Atom">'
              b'<entry><title>Periodic three-body orbits</title>'
              b'<author><name>/u/someone</name></author>'
              b'<updated>2026-10-07T10:00:00+00:00</updated>'
              b'<content type="html">&lt;p&gt;a tool&lt;/p&gt;</content>'
              b'<link href="https://www.reddit.com/r/InternetIsBeautiful/comments/abc/x/"/></entry>'
              b'</feed>')
    got = parse_atom(sample)
    assert len(got) == 1 and got[0]["title"] == "Periodic three-body orbits", got
    assert got[0]["link"].endswith("/comments/abc/x/"), got
    assert got[0]["content"] == "a tool", got
    assert classify(403) == "blocked" and classify(200) == "ok" and classify(429) == "rate-limited"
    print("selftest ok")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
    args = [a for a in argv if not a.startswith("--")]
    sub = args[0] if args else "r/InternetIsBeautiful"
    if "--probe" in argv:
        rows = probe(sub)
        for r in rows:
            print(f"{r['status']:>4}  {r['class']:<12} {r['bytes']:>7}b  {r['url']}")
        return 0
    entries = read_feed(sub)
    if "--json" in argv:
        print(json.dumps(entries, indent=2, ensure_ascii=False))
    else:
        for e in entries:
            print(f"{e['title']}  {e['link']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except RedditBlocked as e:
        print(f"BLOCKED (not empty): {e}", file=sys.stderr)
        raise SystemExit(3)
    except RedditRateLimited as e:
        print(f"RATE-LIMITED (retry later): {e}", file=sys.stderr)
        raise SystemExit(4)
