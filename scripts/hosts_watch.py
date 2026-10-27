#!/usr/bin/env python3
"""Watch the four model hosts for the two things that can reach us unannounced:
a *model this commons actually runs* going away, and a published price that is
about to change.

Why this exists. The standing duty "watch the hosts" was set 2026-10-15 and had
never been done; the first reading (`research/hosts-watch.md`, 2026-10-16) found
that Claude's daily route (`claude-sonnet-4-5`) retires 2026-11-30 and Gemini's
(`gemini-3.8-flash`) doubles in price 2027-01-01. Those facts were sitting on the
vendors' own pages the whole time. Reading four pages by hand is a thing a wake
does once and never again; this turns it into one command.

Design, and why it is split this way:
  * `ROUTES` is the yardstick — the model identifiers this commons *sets*. It is
    read from `governance/model-settings.md`; keep the two in step.
  * Everything that touches the network is inside `fetch()`; everything that
    judges is pure. A test that needs a vendor's site to be up is a test that
    fails for the wrong reason, so the default run is offline and deterministic.
  * It reports *mentions and dates*, not verdicts. Deciding whether a mention
    means "dying" is for the reader who can see the sentence.

Usage:
    python3 scripts/hosts_watch.py            # offline: print routes + URLs
    python3 scripts/hosts_watch.py --fetch    # live: fetch and report
    python3 scripts/hosts_watch.py --fetch --json
"""
from __future__ import annotations

import argparse
import datetime
import html as _html
import json
import re
import sys
import urllib.request
from pathlib import Path

# The model identifiers the commons actually sets, and which page would announce
# their death. Source of truth for the names: governance/model-settings.md.
ROUTES = [
    ("Claude", "daily runner + maintainer", "claude-sonnet-4-5", "anthropic"),
    ("Claude", "mail replies", "claude-sonnet-4-6", "anthropic"),
    ("Tarik", "daily runner + maintainer", "gpt-5.6-sol", "openai"),
    ("Tarik", "autonomous worker", "gpt-6-astra", "openai"),
    ("Gemini", "daily review", "gemini-3.8-flash", "google"),
    ("Desi", "daily runner + maintainer", "deepseek/deepseek-chat", "openrouter"),
    ("Desi", "direct fallback", "deepseek-chat", "deepseek"),
    ("Desi", "mail replies", "deepseek-v4-flash", "deepseek"),
]

# Where each host says what it is retiring. Read 2026-10-16.
PAGES = {
    "anthropic": "https://docs.anthropic.com/en/docs/about-claude/model-deprecations",
    "openai": "https://platform.openai.com/docs/deprecations",
    "google": "https://ai.google.dev/gemini-api/docs/deprecations",
    "deepseek": "https://api-docs.deepseek.com/updates",
    "openrouter": "https://openrouter.ai/api/v1/models",
}

# ...and where each host says what it charges. Half this duty is "a published price that is about to
# change", and the baseline found both price events (OpenAI's promo end, Gemini's doubling) by reading
# these pages *by hand* — they were absent from PAGES, so the automated watch could not see the half of
# the job its own docstring promised. Added 2026-10-16. OpenRouter is not repeated here: its /models
# call above already carries each model's price, which is why the DeepSeek routes read their price there.
PRICING_PAGES = {
    "anthropic": "https://www.anthropic.com/pricing",
    "openai": "https://platform.openai.com/docs/pricing",
    "google": "https://ai.google.dev/gemini-api/docs/pricing",
    "deepseek": "https://api-docs.deepseek.com/quick_start/pricing",
}


def pricing_key(provider: str) -> str:
    """Namespace a pricing page so it cannot collide with the deprecations page for the same host."""
    return f"price:{provider}"

ISO_DATE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")


def strip_html(s: str) -> str:
    """Crude, dependency-free HTML to text. Enough to grep a docs page."""
    s = re.sub(r"(?is)<script.*?</script>", " ", s)
    s = re.sub(r"(?is)<style.*?</style>", " ", s)
    s = re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = re.sub(r"(?is)</(p|div|li|tr|h[1-6]|table|section)>", "\n", s)
    s = re.sub(r"(?is)<[^>]+>", " ", s)
    s = _html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s


# Our id can appear in a snapshotted or revisioned form and still name us:
# `claude-sonnet-4-5` -> `claude-sonnet-4-5-20250929`, `gemini-3.8-flash-001`.
# A *sibling* id that merely starts with our name is a different model and must not be
# reported as ours. Found 2026-10-18, in the third reading: `gemini-3.8-flash-tts`, the
# `gemini-3.8-flash-lite-tts` row, and — worse — the *replacement* column of the row
# above ours all matched, and the flattened hits read exactly like "our daily Gemini
# model is a legacy alias being silently re-routed". It is not; the sentence belonged
# to the neighbouring row. A watch that cries wolf on a prefix is a watch a reader
# learns to skim.
SNAPSHOT_CONTINUATION = re.compile(r"^-(?:20\d{6}|\d{1,4})$")


def _names_our_model(line: str, end: int) -> bool:
    """True when the text after our id ends it, or continues it as a snapshot stamp."""
    rest = line[end:]
    if not rest or not (rest[0].isalnum() or rest[0] in "-_."):
        return True
    token = re.match(r"[-_.][\w.-]*", rest)
    if not token:
        return False
    return bool(SNAPSHOT_CONTINUATION.match(token.group(0).rstrip(".,;:)]")))


def mentions(text: str, needle: str, window: int = 160, limit: int = 4, near_misses=None):
    """Lines containing `needle`, trimmed to a readable window, deduped.

    Substring match on purpose: the pages write `claude-sonnet-4-5-20250929`
    where we write `claude-sonnet-4-5`, and a snapshotted form still names us.
    A longer id that starts with ours (`gemini-3.8-flash-tts`) does not: it is a
    different model, and reporting it as ours is a false alarm. When `near_misses`
    is a list, every rejected id is appended to it, so the reader can see what the
    report ignored instead of trusting a silence.
    """
    out, seen = [], set()
    low_needle = needle.lower()
    for line in text.splitlines():
        low = line.lower()
        start = 0
        while True:
            j = low.find(low_needle, start)
            if j < 0:
                break
            end = j + len(needle)
            start = end
            if not _names_our_model(line, end):
                if near_misses is not None:
                    token = re.match(r"[-_.][\w.-]*", line[end:])
                    near_misses.append(needle + (token.group(0) if token else ""))
                continue
            snippet = line[max(0, j - 40) : end + window].strip()
            if snippet not in seen:
                seen.add(snippet)
                out.append(snippet)
            break
        if len(out) >= limit:
            break
    return out


def dates_in(s: str):
    return sorted({f"{y}-{m}-{d}" for y, m, d in ISO_DATE.findall(s)})


def dates_in(s: str):
    return sorted({f"{y}-{m}-{d}" for y, m, d in ISO_DATE.findall(s)})


# --- the calendar, read back out of the record -------------------------------------------------
#
# Why this exists. `research/hosts-watch.md` ends with a table of dated events ("2026-11-30 —
# `claude-sonnet-4-5` retired"). A date in prose is a date nobody counts down: the baseline found
# the Claude retirement on 2026-10-16 and the next action on it is due weeks later, so the event is
# only as reliable as some future wake happening to re-read the file. The doc stays the single
# source of truth — this parses it rather than keeping a second copy of the dates, because a
# duplicated calendar drifts and then two files disagree about when a route dies.
DOC = Path(__file__).resolve().parents[1] / "research" / "hosts-watch.md"

# A calendar row is a table line whose FIRST cell is nothing but a date. That is deliberately
# narrow: the other tables in the file (routes, prices, sources) start with a name or a URL, so
# they cannot be mistaken for an event.
_CAL_DATE = re.compile(r"^\**\s*(20\d{2}-\d{2}-\d{2})\s*\**$")


def parse_calendar(text: str) -> list:
    """Every dated event in the record, as {date, event, whose, impact}."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.count("|") < 4:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        m = _CAL_DATE.match(cells[0])
        if not m:
            continue
        try:
            when = datetime.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        clean = [re.sub(r"\*\*|`", "", c).strip() for c in cells]
        out.append({
            "date": when, "event": clean[1],
            "whose": clean[2], "impact": clean[3] if len(clean) > 3 else "",
        })
    return out


def upcoming(rows: list, today=None, within: int | None = None) -> list:
    """Events from today onward, soonest first. `within` keeps only the next N days."""
    today = today or datetime.date.today()
    rows = [r for r in rows if r["date"] >= today]
    rows.sort(key=lambda r: (r["date"], r["event"]))
    if within is not None:
        rows = [r for r in rows if (r["date"] - today).days <= within]
    return rows


def print_deadlines(rows: list, today=None) -> None:
    today = today or datetime.date.today()
    print(f"hosts_watch: deadlines from {DOC.name} (today {today.isoformat()})")
    if not rows:
        print("  no dated event ahead on record")
        return
    for r in rows:
        days = (r["date"] - today).days
        print(f"  {days:4d} days  {r['date'].isoformat()}  {r['event'][:78]}")
        print(f"  {'':9s} {'':10s}  touches: {r['whose']}"
              + (f"  [{r['impact']}]" if r["impact"] else ""))


def fetch(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "llm-symposium-hosts-watch/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 - fixed URLs above
        body = r.read().decode("utf-8", "replace")
    return strip_html(body)


def report(pages: dict) -> list:
    rows = []
    for amigo, route, model, key in ROUTES:
        text = pages.get(key)
        ptext = pages.get(pricing_key(key))
        p_near = []
        near = []
        p_hits = mentions(ptext, model, near_misses=p_near) if ptext else []
        row = {
            "amigo": amigo, "route": route, "model": model,
            "page": PAGES[key], "fetched": text is not None,
            "hits": mentions(text, model, near_misses=near) if text is not None else [],
            "near_misses": near,
            "pricing_page": PRICING_PAGES.get(key), "pricing_fetched": ptext is not None,
            "pricing_hits": p_hits, "pricing_near_misses": p_near,
        }
        row["dates"] = dates_in(" ".join(row["hits"]))
        row["pricing_dates"] = dates_in(" ".join(p_hits))
        rows.append(row)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="actually hit the network")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--deadlines", action="store_true",
                    help="print the dated events ahead, read from research/hosts-watch.md (no network)")
    ap.add_argument("--within", type=int, default=None, metavar="DAYS",
                    help="with --deadlines: only the next DAYS; exit 1 if any remain (for a cron check)")
    ap.add_argument("--today", default=None, metavar="YYYY-MM-DD",
                    help="pretend it is this date (testing the horizon, not the world)")
    args = ap.parse_args(argv)

    if args.deadlines:
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
        rows = upcoming(parse_calendar(DOC.read_text()), today=today, within=args.within)
        print_deadlines(rows, today=today)
        if args.within is not None and rows:
            return 1
        return 0

    if not args.fetch:
        print("hosts_watch: offline (pass --fetch to read the vendors' pages)\n")
        for amigo, route, model, key in ROUTES:
            pricing = PRICING_PAGES.get(key, "(price read from the same page)")
            print(f"  {amigo:7s} {route:26s} {model:26s} -> {PAGES[key]}\n"
                  f"  {'':7s} {'':26s} {'':26s}    price -> {pricing}")
        return 0

    pages = {}
    for key, url in PAGES.items():
        try:
            pages[key] = fetch(url)
            print(f"fetched {url}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - a dead vendor must not kill the report
            print(f"FETCH FAILED {url}: {exc}", file=sys.stderr)
            pages[key] = None
    for key, url in PRICING_PAGES.items():
        try:
            pages[pricing_key(key)] = fetch(url)
            print(f"fetched {url}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - a dead vendor must not kill the report
            print(f"FETCH FAILED {url}: {exc}", file=sys.stderr)
            pages[pricing_key(key)] = None

    rows = report(pages)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    for r in rows:
        if not r["fetched"]:
            print(f"\n## {r['amigo']} — {r['model']}\n  page not reachable: {r['page']}")
        else:
            head = "not mentioned" if not r["hits"] else f"{len(r['hits'])} mention(s)"
            print(f"\n## {r['amigo']} — {r['model']} ({r['route']})\n  {head}")
            for h in r["hits"]:
                print(f"    · {h}")
            if r["near_misses"]:
                print("  ignored (different ids sharing our prefix): "
                      + ", ".join(sorted(set(r["near_misses"]))))
            if r["dates"]:
                print(f"  dates seen: {', '.join(r['dates'])}")
        if not r.get("pricing_page"):
            continue
        if not r["pricing_fetched"]:
            print(f"  price page not reachable: {r['pricing_page']}")
        elif not r["pricing_hits"]:
            print(f"  price page: {r['model']} not named on {r['pricing_page']}")
        else:
            print(f"  price page mentions ({r['pricing_page']}):")
            for h in r["pricing_hits"]:
                print(f"    £ {h}")
            if r["pricing_dates"]:
                print(f"  price dates seen: {', '.join(r['pricing_dates'])}")
            if r["pricing_near_misses"]:
                print("  price page ignored: "
                      + ", ".join(sorted(set(r["pricing_near_misses"]))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
