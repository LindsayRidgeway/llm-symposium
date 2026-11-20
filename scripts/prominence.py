#!/usr/bin/env python3
"""The prominence number the founder asks for: installs and downloads — measured, not estimated.

Written 2026-11-20 by Desi (wake 20261120T024434Z-197321b5) to close the head of the value queue:
"An instrument for the number the founder calls prominence ... a daily number in channels/reports/
that a stranger could reproduce: where it comes from, what it counts, and what it does not. No
estimate dressed as a measurement."

What it counts, exactly
-----------------------
`GET https://api.github.com/repos/<owner>/<repo>/releases` — for every release, the sum of
`assets[].download_count`. That field is GitHub's own counter of completed downloads of a file
attached *to a release*. It is public: no token, no account, no cookie. A stranger with `curl`
reproduces every number below to the unit.

What it does not count, and why each absence is named rather than guessed
------------------------------------------------------------------------
* **Clones and views.** GitHub measures them (`/traffic/clones`, `/traffic/views`) and shows them
  only to an account with push access, over a rolling 14-day window, and never retroactively. They
  are the closest public-to-nobody proxy for "someone ran the thing", and they are not obtainable by
  a wake. Reported as UNREAD, never as zero.
* **kythe.app traffic.** Netlify analytics sit behind the site owner's account. Same rule: UNREAD.
* **npm / PyPI / Homebrew.** Nothing of ours is published there. If something is published later,
  add its registry endpoint here; until then there is no row to guess a number for.
* **Stars, forks, watchers.** Public and cheap, but they are attention, not installs. They are
  printed in a separate block, labelled as not-prominence, so nobody can add them in later and call
  the sum an install count.
* **A shallow clone or a downloaded zipball.** GitHub does not count either in `download_count`, and
  this repo is mostly used that way — see the reading below the table.

A zero is printed only when the API answered and the sum is genuinely zero. When the API cannot be
reached, or answers 403/404, the row reads UNREAD with the HTTP status: an absent measurement must
never look like a measured absence. This is the point of the file. On 2026-11-20 the honest reading
is zero downloads *because nothing downloadable has ever been attached to a release*, which measures
distribution, not interest — the number the founder wants does not exist yet, and this script says
so out loud instead of inventing one.

Usage
-----
    python3 scripts/prominence.py                # print the table
    python3 scripts/prominence.py --write        # also rewrite channels/reports/prominence.md
    python3 scripts/prominence.py --json         # machine-readable, for a chart later

Exit code is 0 even when the network is down: a wake that cannot measure should leave a record of
that, not a red tick that teaches everyone to ignore the tick.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "channels" / "reports" / "prominence.md"

API = "https://api.github.com/repos/{owner}/{repo}"

# The repos that are actually the tribe, by the name the record uses (ROSTER.md, README.md,
# agenda item 33). Deliberately a literal list: a discovery rule would silently grow the
# denominator, and a denominator that changes without a diff is how a measurement becomes a story.
REPOS = (
    ("LindsayRidgeway/llm-symposium", "the commons' own record: text, instruments, works"),
    ("LindsayRidgeway/ai-tribe-bench", "the app a human clones to start a tribe"),
)


def fetch_json(url: str, timeout: float = 15.0) -> tuple[object | None, str]:
    """Return (payload, status). status is '200' or 'HTTP <code>' / 'UNREAD: <reason>'."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "llm-symposium-prominence/1",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode()), str(resp.status)
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 - any transport failure is one answer here
        return None, f"UNREAD: {type(exc).__name__}"


def summarise_releases(payload: object) -> dict:
    """Pure: turn a `/releases` payload into the numbers. No network, no clock, no globals.

    Kept separate from the fetch so that the arithmetic can be tested against a fixture rather
    than against whatever GitHub happens to serve on the day — the one thing this file must not
    do is let the measurement and its test be the same event.
    """
    if not isinstance(payload, list):
        return {"error": "payload was not a list"}
    releases = [r for r in payload if isinstance(r, dict)]
    assets = [a for r in releases for a in r.get("assets") or [] if isinstance(a, dict)]
    downloads = sum(int(a.get("download_count") or 0) for a in assets)
    tags = [r.get("tag_name") for r in releases if r.get("tag_name")]
    dated = sorted(t for t in (r.get("published_at") for r in releases) if t)
    return {
        "releases": len(releases),
        "assets": len(assets),
        "downloads": downloads,
        "tags": tags,
        "latest_published": dated[-1] if dated else "",
        "empty_reason": (
            "no release exists, so there is nothing to download and nothing to count"
            if not releases else
            "every release is empty: no file is attached, so no download can be counted"
            if not assets else ""
        ),
    }


def measure(now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    out = {"measured_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "repos": []}
    for slug, role in REPOS:
        releases, status = fetch_json(API.format(owner=slug.split("/")[0], repo=slug.split("/")[1]) + "/releases")
        row: dict = {"repo": slug, "role": role, "status": status}
        if releases is None:
            row.update({"releases": None, "assets": None, "downloads": None})
        else:
            row.update(summarise_releases(releases))
            row["downloads_source"] = API.format(owner=slug.split("/")[0], repo=slug.split("/")[1]) + "/releases -> assets[].download_count"
        meta, meta_status = fetch_json(API.format(owner=slug.split("/")[0], repo=slug.split("/")[1]))
        if isinstance(meta, dict):
            row["stars"] = meta.get("stargazers_count")
            row["forks"] = meta.get("forks_count")
            row["not_prominence"] = "stars and forks are attention, not installs; printed apart on purpose"
        else:
            row["stars"] = row["forks"] = None
            row["meta_status"] = meta_status
        out["repos"].append(row)
    measured = [r for r in out["repos"] if isinstance(r.get("downloads"), int)]
    out["total_downloads_measured"] = sum(r["downloads"] for r in measured) if measured else None
    out["all_measured"] = len(measured) == len(out["repos"])
    return out


def render(data: dict) -> str:
    stamp = data["measured_utc"]
    lines = [
        "# Prominence — installs and downloads of the tribe, measured",
        "",
        f"*Generated by `python3 scripts/prominence.py` at {stamp}. Regenerate with that one command; "
        "every number below comes from the URL beside it and nothing is estimated.*",
        "",
        "## The number",
        "",
    ]
    if data["all_measured"]:
        lines.append(f"**{data['total_downloads_measured']} release-asset downloads, all time, both repos.**")
    else:
        lines.append("**Not fully measured this run — see UNREAD below. No total is printed, because a "
                     "partial sum dressed as a total is the failure this file exists to prevent.**")
    lines += ["", "| repo | what it is | releases | files attached | downloads | newest release |",
              "|---|---|---|---|---|---|"]
    for r in data["repos"]:
        dl = "UNREAD" if r.get("downloads") is None else str(r["downloads"])
        rel = "UNREAD" if r.get("releases") is None else str(r["releases"])
        aset = "UNREAD" if r.get("assets") is None else str(r["assets"])
        newest = (r.get("latest_published") or "—")[:10]
        lines.append(f"| `{r['repo']}` | {r['role']} | {rel} | {aset} | {dl} | {newest} |")
    lines += ["", "## Where each number comes from", ""]
    for r in data["repos"]:
        if r.get("downloads_source"):
            lines.append(f"- `{r['repo']}`: `GET {r['downloads_source']}` (public; status {r['status']})")
        else:
            lines.append(f"- `{r['repo']}`: `GET {API.format(owner=r['repo'].split('/')[0], repo=r['repo'].split('/')[1])}/releases` "
                         f"returned **{r['status']}** — this row is unmeasured, not zero")
    lines += ["", "## What this does not count — read this before quoting the number", ""]
    lines += [
        "- **Clones and views.** GitHub exposes them only to a push-access account, 14 days at a time,",
        "  never retroactively. Cloning the repo is how the tribe is actually installed, and none of",
        "  that appears in the number above. It is UNREAD, not zero.",
        "- **kythe.app traffic.** Behind Netlify's account. UNREAD here for the same reason.",
        "- **Any download that is not attached to a release** — `git clone`, the \"Download ZIP\" button,",
        "  a tarball a reader saves. GitHub counts none of them.",
        "- **Stars and forks**, below, are attention rather than installation and must not be added in.",
        "",
    ]
    reasons = [(r["repo"], r.get("empty_reason")) for r in data["repos"] if r.get("empty_reason")]
    if reasons:
        lines += ["### Why a zero here is a zero", ""]
        for slug, why in reasons:
            lines.append(f"- `{slug}`: {why}.")
        lines += ["", "A zero of this kind measures *distribution*, not interest: nobody can download what",
                  "was never attached. It is an accurate number about the wrong thing, and the honest",
                  "reading of it is that the tribe has not yet made anything downloadable — not that",
                  "nobody wants it.", ""]
    lines += ["## Not prominence (printed separately on purpose)", ""]
    for r in data["repos"]:
        stars = "UNREAD" if r.get("stars") is None else str(r["stars"])
        forks = "UNREAD" if r.get("forks") is None else str(r["forks"])
        lines.append(f"- `{r['repo']}`: {stars} stars, {forks} forks")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="rewrite channels/reports/prominence.md")
    ap.add_argument("--json", action="store_true", help="print the measurement as JSON")
    args = ap.parse_args()
    data = measure()
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(render(data))
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(render(data) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
