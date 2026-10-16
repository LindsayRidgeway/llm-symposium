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
import html as _html
import json
import re
import sys
import urllib.request

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

# Where each host says what it is retiring and what it charges. Read 2026-10-16.
PAGES = {
    "anthropic": "https://docs.anthropic.com/en/docs/about-claude/model-deprecations",
    "openai": "https://platform.openai.com/docs/deprecations",
    "google": "https://ai.google.dev/gemini-api/docs/deprecations",
    "deepseek": "https://api-docs.deepseek.com/updates",
    "openrouter": "https://openrouter.ai/api/v1/models",
}

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


def mentions(text: str, needle: str, window: int = 160, limit: int = 4):
    """Lines containing `needle`, trimmed to a readable window, deduped.

    Substring match on purpose: the pages write `claude-sonnet-4-5-20250929`
    where we write `claude-sonnet-4-5`, and a snapshotted form still names us.
    """
    out, seen = [], set()
    for line in text.splitlines():
        j = line.lower().find(needle.lower())
        if j < 0:
            continue
        snippet = line[max(0, j - 40) : j + window].strip()
        if snippet in seen:
            continue
        seen.add(snippet)
        out.append(snippet)
        if len(out) >= limit:
            break
    return out


def dates_in(s: str):
    return sorted({f"{y}-{m}-{d}" for y, m, d in ISO_DATE.findall(s)})


def fetch(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "llm-symposium-hosts-watch/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 - fixed URLs above
        body = r.read().decode("utf-8", "replace")
    return strip_html(body)


def report(pages: dict) -> list:
    rows = []
    for amigo, route, model, key in ROUTES:
        text = pages.get(key)
        if text is None:
            rows.append({"amigo": amigo, "route": route, "model": model,
                         "page": PAGES[key], "fetched": False, "hits": [], "dates": []})
            continue
        hits = mentions(text, model)
        rows.append({
            "amigo": amigo, "route": route, "model": model, "page": PAGES[key],
            "fetched": True, "hits": hits,
            "dates": dates_in(" ".join(hits)),
        })
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="actually hit the network")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    if not args.fetch:
        print("hosts_watch: offline (pass --fetch to read the vendors' pages)\n")
        for amigo, route, model, key in ROUTES:
            print(f"  {amigo:7s} {route:26s} {model:26s} -> {PAGES[key]}")
        return 0

    pages = {}
    for key, url in PAGES.items():
        try:
            pages[key] = fetch(url)
            print(f"fetched {url}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - a dead vendor must not kill the report
            print(f"FETCH FAILED {url}: {exc}", file=sys.stderr)
            pages[key] = None

    rows = report(pages)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    for r in rows:
        if not r["fetched"]:
            print(f"\n## {r['amigo']} — {r['model']}\n  page not reachable: {r['page']}")
            continue
        head = "not mentioned" if not r["hits"] else f"{len(r['hits'])} mention(s)"
        print(f"\n## {r['amigo']} — {r['model']} ({r['route']})\n  {head}")
        for h in r["hits"]:
            print(f"    · {h}")
        if r["dates"]:
            print(f"  dates seen: {', '.join(r['dates'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
