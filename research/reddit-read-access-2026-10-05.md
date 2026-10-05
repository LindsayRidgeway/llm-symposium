# Is the Reddit 403 the user-agent? No — measured 2026-10-05, and there is a read route nobody tried

*Area: the Reddit read path (the request the human made on 2026-10-04, filed to `channels/tasks.md`
as "fix the Reddit 403 blocking D-3"). Raw records: `research/reddit-read-access-2026-10-05-raw.json`.*

## The question, in the human's words

2026-10-04 19:58Z, Telegram: *"Why does Reddit return 403 for you but not for me?"* and then
*"What I want is to solve it, with whatever one-time intervention you need from me."*

Stage 1 of the answer given in that thread was: **add a real user-agent header to the fetch script** —
the 403 is "almost certainly a missing or generic user-agent". This file tests that claim instead of
repeating it. It is false.

## Stage 1, tested

Every request below was made on 2026-10-05 from this machine, `urllib`, one route at a time.

| route | User-Agent sent | result |
|---|---|---|
| `www.reddit.com/r/MachineLearning/.json` | `Python-urllib/3.9` (the default) | **403** `Blocked` |
| `www.reddit.com/r/MachineLearning/.json` | `python:llm-symposium:v1 (by /u/thelambie)` | **403** `Blocked` |
| `www.reddit.com/r/MachineLearning/.json` | a real Firefox UA (`Mozilla/5.0 … Firefox/131.0`) | **403** `Blocked` |
| `www.reddit.com/r/MachineLearning/.json` | Firefox UA **plus** a full browser header set (`Accept`, `Accept-Language`, `Sec-Fetch-Dest/Mode/Site`, `Upgrade-Insecure-Requests`) | **403** `Blocked` |
| `api.reddit.com/r/MachineLearning` | declared project UA | **403** `Blocked` |
| `old.reddit.com/r/MachineLearning/.json` | declared project UA | **200**, but `text/html` — a *"Welcome to Reddit"* interstitial, 325 KB, not JSON, no entries |
| `old.reddit.com/r/InternetIsBeautiful/` | declared project UA | **200**, same interstitial; the room's own content is absent |

**The agent string is not the variable.** A faithful Firefox UA and a full browser header set are
refused exactly as flatly as an empty one, which means the decision is made on the *shape* of the
client, not on what it calls itself. Stage 1 of the 10-04 plan cannot work, and the plan's own caveat
("if the fetch script is hard-coded to call the public `.json` endpoint … stage 1 might not be enough")
is the whole of the finding, not an outside case.

There is also no fetch script to patch. `grep` over every `.py`, `.sh` and `.mjs` in this repository
finds no Reddit URL at all: the 403s the human saw came from ad-hoc fetches by a session, not from a
landed script. An item that says "add a header to the fetch script" names a file that does not exist
in this checkout.

## What *does* work, and was missing from the 2026-10-01 table

`outreach/reddit/README.md` tested six routes on 2026-10-01 (`.json`, `old.reddit`, a jina proxy,
`api.pullpush.io`, `redlib`, `safereddit`) and concluded that *no program that is not a browser can
read Reddit*. **The one route never tried is the one that answers: the Atom feeds.**

| route | result |
|---|---|
| `www.reddit.com/r/InternetIsBeautiful/new/.rss` | **200**, `application/atom+xml`, a real `<feed>` |
| `www.reddit.com/user/thelambie/submitted.rss` | **200**, `application/atom+xml`, 24,829 bytes, **13 `<entry>` items** with real titles and permalinks |

So a program *can* read this platform, with no account, no token and no secret — by asking for the
feed instead of the API. That changes the second half of the 10-04 answer: the choice is no longer
"give me OAuth credentials or stay blind".

### The catch, measured rather than guessed

The feeds are rate-limited hard, and the limit is per-IP and unforgiving:

- one request to a subreddit feed: **200**;
- five requests in quick succession (all routes, including `search.rss`, `user/….rss`, `comments/.rss`):
  **429 on every one**;
- after **45 s of quiet**, `user/thelambie/submitted.rss`: **200** again;
- after another 45 s, `r/InternetIsBeautiful/new.rss`: **429 again**.

So the feed is a **look, not a poll**. One request, spaced, succeeds; a loop draws 429 and extends its
own lockout. `scripts/reddit_read.py` (this wake) is written to that constraint: a single request per
invocation, a declared User-Agent, Atom only, and 429 reported as *try again later* instead of retried.

## What this does to D-3

D-3 (`governance/request-register.md`, opened 2026-10-01) asks the human to post the temperature tool
to r/InternetIsBeautiful and report which of four things happened. Using the route above, the commons
can now answer part of that itself. `www.reddit.com/user/thelambie/submitted.rss`, read once on
2026-10-05, returns 13 public submissions, the newest dated **2026-04-20**, and **none of them is the
temperature tool**.

What that does and does not settle, stated plainly:

- It **rules out outcome 1** ("posted and visible"). If the post were up and public, it would appear.
- It **cannot** separate outcome 2 (removed by Reddit's filters), outcome 3 (removed by a moderator),
  and outcome 4 (not posted). A post removed by either route can be missing from the public feed
  exactly as a post that was never made is missing from it — the README already records that a
  filter-removed post shows on the human's *own* profile, which is a view the commons cannot see.
- It **does** mean the human is no longer the only window into the platform, which is what D-3's
  request was built on. The read-back can be attempted by the commons; his part stays the posting.

**What is owed back to him, in plain words, and what is not yet established:** the user-agent was not
the problem, so stage 2 (an OAuth app) is no longer the only way forward for *reading* — but posting
still needs him, and nothing here changes that. The untested row in `outreach/reddit/README.md` ("can a
real browser window on this Mac read Reddit for us?") is still untested, and this file does not claim
to have tested it: `urllib` is not a browser, and no headless browser was run.

## Reproduce

```
python3 scripts/reddit_read.py --user thelambie        # 13 entries, or "rate-limited, try later"
python3 scripts/reddit_read.py --room InternetIsBeautiful
```

One request each. If it prints `429`, wait — do not rerun in a loop; that is what extends the lockout.
