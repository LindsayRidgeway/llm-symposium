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
import os
import pathlib
import subprocess
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "channels" / "reports" / "prominence.md"

API = "https://api.github.com/repos/{owner}/{repo}"
# Clones and views: measured by GitHub, readable only with a push-access token, 14 days, never
# retroactively. Same URL shape for both kinds.
TRAFFIC_API = "https://api.github.com/repos/{slug}/traffic/{kind}"

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


def summarise_traffic(payload: object) -> dict:
    """Pure: turn a `/traffic/clones` or `/traffic/views` payload into numbers.

    Separate from the fetch for the same reason as `summarise_releases`: the arithmetic must be
    testable against a fixture, because this number is the one most likely to be quoted wrongly.
    """
    if not isinstance(payload, dict):
        return {"error": "payload was not an object"}
    series = [d for d in payload.get("clones") or payload.get("views") or [] if isinstance(d, dict)]
    counts = [int(d.get("count") or 0) for d in series]
    uniques = [int(d.get("uniques") or 0) for d in series]
    days = [str(d.get("timestamp") or "")[:10] for d in series]
    return {
        "count": int(payload.get("count") or 0),
        "uniques": int(payload.get("uniques") or 0),
        "days": len(series),
        "peak_day": max(zip(counts, days), default=(0, "")) if series else (0, ""),
        "series": list(zip(days, counts, uniques)),
    }


def clones_per_view(clones: int, views: int) -> float | None:
    """Pure: how many clones each page view is worth. None when there is no view to divide by.

    This ratio is the whole attribution argument. A human install starts with a visit to the
    repository page; a crawler clones without one. A large ratio is not evidence of popularity,
    it is evidence of automation — so the file prints the ratio instead of letting a reader
    mistake the clone count for readers.
    """
    if views <= 0:
        return None
    return round(clones / views, 1)


def unexplained_clones(clones: int, own_runs: int) -> int:
    """Pure: clones minus the automated runs we can actually count, floored at zero.

    GitHub Actions is the one part of our own automation whose runs are public and countable, and
    every one of those runs checks the repository out. Local bot wakes clone the repo too and do
    not appear here — they are invisible from outside. So this is an UPPER BOUND on how many
    clones we cannot account for, never a count of outside installers.
    """
    return max(0, int(clones) - int(own_runs))


# 2026-11-20 (Desi): the daily job that will run this carries launchd's PATH
# (/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin), and `gh` lives in /opt/homebrew/bin — so scheduled,
# this function found no token, reported "UNREAD", and looked exactly like a host that is not logged
# in. Same defect as every other in this file: an absence that cannot say why is indistinguishable
# from a fact. So the search is explicit, and the *reason* travels back with the empty token.
GH_CANDIDATES = ("gh", "/opt/homebrew/bin/gh", "/usr/local/bin/gh", "/usr/bin/gh")


def traffic_token() -> tuple[str, str]:
    """Return (token, source). A push-access token is what GitHub requires; nothing lesser works.

    The second half of the return says where it came from, or why there is none: "no gh on PATH
    (/usr/bin:/bin:…)" is a fact a reader can act on; an empty string is not.
    """
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(name, "").strip()
        if value:
            return value, f"env {name}"
    tried: list[str] = []
    for binary in GH_CANDIDATES:
        try:
            out = subprocess.run([binary, "auth", "token"], capture_output=True, text=True, timeout=10)
        except FileNotFoundError:
            tried.append(binary)
            continue
        except Exception:  # noqa: BLE001 - a broken gh is an answer, not a crash
            tried.append(binary)
            continue
        token = (out.stdout or "").strip()
        if token and out.returncode == 0:
            return token, f"{binary} auth token"
        return "", f"{binary} is present but 'auth token' failed (rc={out.returncode})"
    return "", "no gh anywhere on PATH (%s); looked for %s" % (
        os.environ.get("PATH", "?"), ", ".join(GH_CANDIDATES))


def _auth_get(url: str, token: str, timeout: float = 15.0) -> tuple[object | None, str]:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "llm-symposium-prominence/1",
        "Authorization": f"Bearer {token}",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode()), str(resp.status)
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, f"UNREAD: {type(exc).__name__}"


def count_actions_runs(slug: str, days: list[str], token: str = "") -> dict[str, int | None]:
    """Runs of our own workflows per day — public, so a stranger can reproduce every count.

    One query per day rather than paging every run: `per_page=1` and read `total_count`.
    """
    out: dict[str, int | None] = {}
    owner, repo = slug.split("/", 1)
    for day in days:
        nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
        url = (f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=1"
               f"&created={day}T00:00:00Z..{nxt}T00:00:00Z")
        payload, _status = _auth_get(url, token) if token else fetch_json(url)
        out[day] = payload.get("total_count") if isinstance(payload, dict) else None
    return out


def measure_traffic(token: str = "", count_runs: bool = True) -> dict:
    """Clones and views for every repo in REPOS, plus our own countable automation."""
    token, source = (token, "passed in") if token else traffic_token()
    out: dict = {"token_available": bool(token), "token_source": source, "repos": []}
    for slug, _role in REPOS:
        row: dict = {"repo": slug}
        for kind in ("clones", "views"):
            payload, status = (_auth_get(TRAFFIC_API.format(slug=slug, kind=kind), token)
                               if token else (None, "UNREAD: no push-access token — %s" % source))
            if isinstance(payload, dict):
                row[kind] = summarise_traffic(payload)
                row[kind]["status"] = status
            else:
                row[kind] = {"status": status, "count": None, "uniques": None}
        if isinstance(row["clones"].get("count"), int) and isinstance(row["views"].get("count"), int):
            row["clones_per_view"] = clones_per_view(row["clones"]["count"], row["views"]["count"])
        if count_runs and row["clones"].get("series"):
            days = [d for d, _c, _u in row["clones"]["series"]]
            runs = count_actions_runs(slug, days, token)
            row["own_actions_runs"] = runs
            total_runs = None if any(v is None for v in runs.values()) else sum(runs.values())
            row["own_actions_runs_total"] = total_runs
            if total_runs is not None:
                row["unexplained_clones_upper_bound"] = unexplained_clones(
                    row["clones"]["count"], total_runs)
        out["repos"].append(row)
    return out


def measure(now: dt.datetime | None = None, traffic: bool = False) -> dict:
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
    if traffic:
        out["traffic"] = measure_traffic()
    return out


def render_traffic(data: dict) -> str:
    """The clones-and-views section: the only counter that could catch an install, and its caveat."""
    t = data.get("traffic") or {}
    lines = ["## Clones and views — the counter GitHub keeps, and what it is worth", ""]
    if not t.get("token_available"):
        lines += [
            "**UNREAD.** `GET /repos/{slug}/traffic/clones` and `/traffic/views` answer 403 without a",
            "push-access token, and a wake has none by design. This is the row that would hold a real",
            "installation signal, so it is left empty rather than guessed. What it would count:",
            "every `git clone` of each repo in the last 14 days, and every visit to the repo page.",
            "",
        ]
        return "\n".join(lines)
    for r in t.get("repos", []):
        clones, views = r.get("clones") or {}, r.get("views") or {}
        lines.append(f"### `{r['repo']}` — last 14 days")
        lines.append("")
        if not isinstance(clones.get("count"), int):
            lines += [f"clones: **{clones.get('status')}** — unmeasured, not zero", ""]
            continue
        lines += [f"- **{clones['count']:,} clones** ({clones['uniques']:,} unique cloners)",
                  f"- **{views.get('count', 0):,} page views** ({views.get('uniques', 0):,} unique visitors)"]
        ratio = r.get("clones_per_view")
        if ratio is not None:
            lines.append(f"- **{ratio:,.1f} clones per page view** — a reader who installs starts by "
                         f"visiting the page; a crawler does not")
        elif isinstance(views.get("count"), int):
            lines.append("- clones per page view: **undefined** — no page view in the window, so "
                         "every clone is unattributed by construction")
        if r.get("own_actions_runs_total") is not None:
            lines.append(f"- our own GitHub Actions runs in the same window: "
                         f"**{r['own_actions_runs_total']:,}** (public, countable), i.e. "
                         f"**{r['unexplained_clones_upper_bound']:,}** clones at most are not ours")
            lines.append("  - upper bound only: local bot wakes clone these repositories too and are "
                         "invisible from outside, and one run may check out more than once")
        lines += ["", "| day | clones | unique | our Actions runs |", "|---|---|---|---|"]
        runs = r.get("own_actions_runs") or {}
        for day, count, uniques in clones.get("series", []):
            own = runs.get(day)
            lines.append(f"| {day} | {count:,} | {uniques:,} | {'UNREAD' if own is None else own} |")
        lines.append("")
    return "\n".join(lines)


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
        (
            "- **Clones and views** are counted separately below: GitHub exposes them only to a "
            "push-access account, 14 days at a time, never retroactively."
            if data.get("traffic") else
            "- **Clones and views.** GitHub exposes them only to a push-access account, 14 days at a "
            "time, never retroactively. Cloning the repo is how the tribe is actually installed, and "
            "none of that appears in the number above. It is UNREAD, not zero."
        ),
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
    if data.get("traffic"):
        lines += [render_traffic(data).rstrip(), ""]
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
    ap.add_argument("--traffic", action="store_true",
                    help="also read /traffic/clones and /traffic/views (needs a push-access token)")
    args = ap.parse_args()
    data = measure(traffic=args.traffic)
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
