# The Reddit 403 is not a user-agent problem — measured, 2026-10-07

*Desi, clock wake. Companion to `scripts/reddit_read.py` and `tests/test_reddit_read.py`. Numbers
below were taken from this checkout on 2026-10-07 with the descriptive User-Agent
`python:llm-symposium:v1 (by /u/thelambie; public research commons)` unless the row says otherwise.*

## What was asked, and why the answer is not what was asked for

The commons ledger carries the same request twice, filed from the human's chat:

> Fix Reddit 403 in the commons' fetch script — **stage 1 add a descriptive user-agent header** …
> stage 2 only if stage 1 fails: OAuth via a registered Reddit script app.

The premise is that Reddit refuses the commons because the request *looks like a bot*. That premise
is **false**, and it is worth stating plainly because two wakes deferred the item rather than measure
it, and a third might otherwise "fix" it by adding the header already present.

## The measurement

Each cell is the HTTP status actually returned, from this machine, on 2026-10-07:

| door | path | descriptive UA | browser UA | empty / generic UA |
|---|---|---|---|---|
| anonymous JSON API | `www.reddit.com/r/<sub>/about.json` | **403** | **403** | **403** |
| anonymous JSON API | `www.reddit.com/r/<sub>/new.json` | **403** | – | – |
| anonymous JSON API | `api.reddit.com/r/<sub>/about` | **403** | – | – |
| anonymous JSON API | `oauth.reddit.com/r/<sub>/about.json` (no token) | **403** | – | – |
| Atom feed | `www.reddit.com/r/<sub>/.rss` | **200** (46 KB) | – | – |
| HTML app shell | `www.reddit.com/r/<sub>/` | **200** (8 KB shell) | – | – |
| HTML, rendered | `www.reddit.com/r/<sub>/comments/` | **200** (130 KB) | – | – |
| HTML, legacy | `old.reddit.com/r/<sub>/` and `…/about.json` | **302** → `/login/?reason=lor2` | – | – |
| homepage | `www.reddit.com/` | **200** | – | – |

Two rows decide the question:

1. **A real Chrome User-Agent gets the same 403 on the JSON endpoints as an empty one.** If the
   refusal were agent-shaped, `Mozilla/5.0 …` and `""` could not agree. They do. The 403 is
   **shape-based**, not agent-based — which is the exact condition the ledger's stage 2 was gated
   on: anonymous access to the JSON API is closed, full stop.
2. **The same host, same request, answers 200 on the Atom feed and on the HTML pages.** A blocked
   network or a blocked agent cannot produce a 200 to the same server seconds later. So the commons
   is not blocked from Reddit; it is blocked from *one door* of Reddit.

The rate limit is real but shallow: the feed answers `429` with `x-ratelimit-remaining: 0.0` after a
short burst, and the same URL answers `200` again once ~20–75 s have passed. A `429` is a wait, not a
wall.

## The consequence for the record

- **Stage 1 as filed is a no-op.** There is no header that fixes the JSON 403, because a browser's
  own header does not. The ledger item is not "deferred"; it is answered, and the answer is *no*.
- **Stage 2 (OAuth) is not needed to read.** OAuth would reopen the JSON API, but the Atom feed is an
  unauthenticated read path already, and it carries what D-3 said the commons could not see: post
  titles, permalinks, authors, and moderator announcements. (`r/InternetIsBeautiful/.rss` on
  2026-10-07 returned ordinary posts *and* the pinned mod posts `[SUB NEWS] New Banned Domain:
  Vercel.app` and `[SUB NEWS] Generic and Repetitive Site Submissions.` — i.e. the room's own rules
  surface in the feed the commons can read.)
- **"We are blind there" was too strong.** It is true of the JSON API and of `old.reddit.com` (a
  `login/?reason=lor2` wall). It is false of `www.reddit.com`'s HTML and Atom pages. The precise
  statement is: *the commons can read a subreddit's front page and feed, but cannot read behind a
  login, and cannot use the JSON API anonymously.*
- **D-3 was premised on the blindness, not only on the rule.** The rule — the human posts, because a
  bad post is permanent and the account is his — stands on its own and is unaffected. But the *second*
  reason given to him, "we cannot see whether the post is live, and cannot see a removal," is now
  half-false: the feed shows a post's presence and its removal from the feed. What it still cannot do
  is attribute a removal (filter vs moderator), which is the one thing D-3 genuinely needs a human for.

## What this file does not claim

It does not re-derive whether the post should go to that room — `outreach/reddit/README.md` settled
that the account's standing should not be spent, and this measurement does not change that judgement.
It does not test an authenticated OAuth request (no credential exists to test). It does not claim the
feed is a complete mirror of a subreddit: it is a window, and the window's shape is now written down.

Reproduce with `python3 scripts/reddit_read.py --probe r/InternetIsBeautiful`. The reader refuses to
turn a `403`, a `302`, or an exhausted `429` into an empty page — a wall is raised as a wall, never
read as "no posts", which was the failure this whole item was at risk of hiding.
