#!/usr/bin/env python3
"""Re-measure the reachability catalogue, and report what CHANGED since it was measured.

Why this exists (agenda item 17, rule 1: "a source-reachability list, maintained").
`scripts/measure_sources.py` measures 35 public sources once and writes
`docs/works/fetchable-sources.json`. That file was generated on 2026-09-16 and, for a month,
nothing re-asked it a single question — so the catalogue was a photograph labelled "maintained".
Item 17's whole argument is that access fails *silently*: the agent that cannot read a page does
not announce it, it falls back on memory. A list nobody re-measures fails the same way: it keeps
printing "25 browser-usable" after the world has moved.

What this tool adds to the measurement, beyond running it again:

  1. A TAXONOMY OF REFUSALS, not one bucket called "unreachable". Item 17 already paid for this
     distinction by hand (2026-09-16): GDELT's 429 is a *speed* wall and clears on retry; Gutendex's
     403 Cloudflare challenge is a *bot* wall, about who is asking; FRED's 400 is a *key* wall. A
     catalogue that calls all three "unreachable" is wrong three times, and wrong in a way that
     tells a future agent to give up on a source that would have answered.
  2. A CHECK THAT A 200 IS ACTUALLY DATA. The catalogue's `ok` is "status 200 and some bytes came
     back", and its own stored witnesses show that definition is too generous: `US Census (ACS)`
     returned a 200 HTML page titled "Missing Key", and `REST Countries` returned
     `{"success": false, ... "errors": [...]}`. Both are recorded as reachable. This tool keeps
     that verdict but reports it separately, as `claims_data: false` with the witness as evidence,
     rather than silently redefining a published count.
  3. A CONFIRMATION PASS. A single request is not a measurement of a source; it is a measurement of
     one minute of one CDN edge. Any source whose reading differs from the baseline is re-asked
     once after a pause, and both attempts are kept in the record. A flake must not become a
     "regression", and the only way to tell them apart is to ask twice.

Verdicts, and what they are allowed to mean:

  unchanged   the reading matches the baseline in both axes (answers, and readable by a page)
  regressed   it answered before and does not now, or a page could read it and cannot now
  improved    the reverse
  changed     same answers/reachability, different *kind* of answer (e.g. 200 -> 429 speed wall)

Exit code is 0 unless something regressed, so this can be wired to a clock and left alone.

Usage
  python3 scripts/source_drift.py                  # measure, compare, write the record
  python3 scripts/source_drift.py --dry-run        # measure and compare, print only, write nothing
  python3 scripts/source_drift.py --only Gutendex --only GDELT
  python3 scripts/source_drift.py --baseline PATH  # compare against some other snapshot
  python3 scripts/source_drift.py --no-confirm     # one request per source, for a quick look
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import measure_sources  # noqa: E402  (one implementation of "ask it politely", not two)

BASELINE = os.path.join(REPO, "docs", "works", "fetchable-sources.json")
SNAPSHOT_DIR = os.path.join(REPO, "research", "source-drift")
RECORD_MD = os.path.join(REPO, "research", "source-drift.md")

# Wording that means "this 200 is not data": an error document served with a success status.
REFUSAL_MARKERS = (
    "missing key",
    "invalid api key",
    '"success": false',
    '"success":false',
    "api key is required",
    "requires an api key",
    "unauthorized",
    "access denied",
    "just a moment",          # Cloudflare interstitial
    "enable javascript and cookies",
)


def kind(m: dict) -> str:
    """What sort of answer is this? One bucket per *reason*, not per status code.

    Kept pure and total: every record gets a kind, including the ones with no status at all.
    """
    if m.get("ok"):
        return "answered"
    status = m.get("http_status")
    witness = (m.get("witness") or "").lower()
    if status == 429:
        return "speed wall"
    if status in (401, 403):
        if "just a moment" in witness or "cloudflare" in witness or "captcha" in witness:
            return "bot wall"
        if m.get("advertised_key"):
            return "key wall"
        return "refused"
    if status == 400 and m.get("advertised_key"):
        return "key wall"
    if status is not None and 500 <= int(status) < 600:
        return "server error"
    if status is None:
        return "unreachable"
    return "empty or other"


def claims_data(m: dict) -> tuple[bool, str]:
    """Does this record carry data, as opposed to an error page wearing a 200?

    Deliberately does NOT consult `ok`: a source can be `ok` by the published definition and still
    hand back "Missing Key". The disagreement is the finding, so both are reported.
    """
    if not m.get("ok"):
        return False, "did not answer"
    witness = " ".join((m.get("witness") or "").lower().split())
    for marker in REFUSAL_MARKERS:
        if marker in witness:
            return False, "200 but the body says %r" % marker
    ctype = (m.get("content_type") or "").lower()
    if ctype.startswith("text/html") and "json" in (m.get("error") or "").lower():
        return False, "200 with an HTML body where data was asked for"
    return True, ""


def reading(m: dict) -> dict:
    """The two axes item 17 says are separate questions, plus the reason for a refusal."""
    data, why = claims_data(m)
    return {
        "answers": bool(m.get("ok")),
        "browser_usable": bool(m.get("browser_usable")),
        "claims_data": data,
        "why_not": why,
        "kind": kind(m),
        "cors": m.get("cors"),
    }


def drift(before: dict, after: dict) -> dict:
    """Compare two readings of the same source. Pure: no clock, no network, no I/O."""
    b, a = reading(before), reading(after)
    if b["answers"] and not a["answers"]:
        verdict = "regressed"
    elif not b["answers"] and a["answers"]:
        verdict = "improved"
    elif b["browser_usable"] and not a["browser_usable"]:
        verdict = "regressed"
    elif not b["browser_usable"] and a["browser_usable"]:
        verdict = "improved"
    elif b["kind"] != a["kind"]:
        verdict = "changed"
    else:
        verdict = "unchanged"
    return {"verdict": verdict, "before": b, "after": a}


def summarise(rows: list[dict]) -> dict:
    counts = {"unchanged": 0, "regressed": 0, "improved": 0, "changed": 0}
    for row in rows:
        counts[row["drift"]["verdict"]] += 1
    counts["sources"] = len(rows)
    counts["answered_now"] = sum(1 for r in rows if r["drift"]["after"]["answers"])
    counts["browser_now"] = sum(1 for r in rows if r["drift"]["after"]["browser_usable"])
    counts["answered_then"] = sum(1 for r in rows if r["drift"]["before"]["answers"])
    counts["browser_then"] = sum(1 for r in rows if r["drift"]["before"]["browser_usable"])
    counts["claims_data_now"] = sum(1 for r in rows if r["drift"]["after"]["claims_data"])
    return counts


def render_markdown(doc: dict) -> str:
    c = doc["counts"]
    lines = []
    lines.append("## %s — %d sources re-measured" % (doc["run_utc"], c["sources"]))
    lines.append("")
    lines.append("Baseline: %s (`%s`). Measured from a client sending "
                 "`Origin: %s`.\n" % (doc["baseline_utc"], doc["baseline_path"],
                                       doc["origin_sent"]))
    lines.append("| | then | now |")
    lines.append("|---|---|---|")
    lines.append("| answered without a key | %d | %d |" % (c["answered_then"], c["answered_now"]))
    lines.append("| readable by a browser page (CORS) | %d | %d |"
                 % (c["browser_then"], c["browser_now"]))
    lines.append("| answered *and* carried data | — | %d |" % c["claims_data_now"])
    lines.append("")
    moved = [r for r in doc["sources"] if r["drift"]["verdict"] != "unchanged"]
    if not moved:
        lines.append("**No source changed its reading in %d days.** That is the useful answer "
                     "too: it says the catalogue is still true, and it costs one run."
                     % doc["days_since_baseline"])
    else:
        lines.append("### What changed")
        lines.append("")
        lines.append("| source | then | now | verdict | confirmed |")
        lines.append("|---|---|---|---|---|")
        for r in moved:
            b, a = r["drift"]["before"], r["drift"]["after"]
            lines.append("| %s | %s/%s | %s/%s | %s | %s |" % (
                r["name"],
                b["kind"], "page-readable" if b["browser_usable"] else "server-only",
                a["kind"], "page-readable" if a["browser_usable"] else "server-only",
                r["drift"]["verdict"],
                r.get("confirmation") or "single pass"))
        lines.append("")
    hard = [r for r in doc["sources"] if not r["drift"]["after"]["claims_data"]
            and r["drift"]["after"]["answers"]]
    if hard:
        lines.append("### Answered, but the answer is not data")
        lines.append("")
        for r in hard:
            lines.append("- **%s** — %s" % (r["name"], r["drift"]["after"]["why_not"]))
        lines.append("")
    lines.append("Snapshot: `%s`" % doc["snapshot"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", default=BASELINE)
    ap.add_argument("--only", action="append", default=[],
                    help="measure only sources whose name contains this text (repeatable)")
    ap.add_argument("--no-confirm", action="store_true", help="one request per source")
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    ap.add_argument("--pause", type=float, default=6.0,
                    help="seconds to wait before a confirmation request (default 6)")
    args = ap.parse_args(argv)

    with open(args.baseline, encoding="utf-8") as f:
        baseline = json.load(f)
    before = {s["name"]: s for s in baseline["sources"]}
    baseline_utc = baseline.get("generated_utc", "unknown")
    try:
        t0 = datetime.datetime.strptime(baseline_utc, "%Y-%m-%dT%H:%M:%SZ")
        days = (datetime.datetime.utcnow() - t0).days
    except ValueError:
        days = -1

    wanted = [s for s in baseline["sources"]
              if not args.only or any(k.lower() in s["name"].lower() for k in args.only)]

    rows = []
    for source in wanted:
        name, url = source["name"], source["url"]
        now = measure_sources.measure(url)
        now.update(name=name, url=url,
                   advertised_key=source.get("advertised_key", False))
        now["ok"] = bool(now["http_status"] == 200 and now["bytes"] > 0)
        now["browser_usable"] = bool(now["ok"] and now["cors"] in ("*", "origin"))
        row = {"name": name, "url": url, "drift": drift(source, now),
               "then": source, "now": now, "confirmation": None}

        if not args.no_confirm and row["drift"]["verdict"] != "unchanged":
            time.sleep(args.pause)
            again = measure_sources.measure(url)
            again.update(name=name, url=url, advertised_key=source.get("advertised_key", False))
            again["ok"] = bool(again["http_status"] == 200 and again["bytes"] > 0)
            again["browser_usable"] = bool(again["ok"] and again["cors"] in ("*", "origin"))
            second = drift(source, again)
            if second["verdict"] == "unchanged":
                row["confirmation"] = "not reproduced on a second request (%s) — treated as a flake" % (
                    again.get("http_status"))
                row["drift"] = second
                row["now"] = again
            else:
                row["confirmation"] = "reproduced (%s then %s)" % (
                    now.get("http_status"), again.get("http_status"))
                row["flaked"] = now.get("http_status")

        rows.append(row)
        print("%-34s %-4s cors=%-6s %-11s %s" % (
            name, now.get("http_status"), now.get("cors"),
            row["drift"]["after"]["kind"], row["drift"]["verdict"]), flush=True)

    counts = summarise(rows)
    run_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp = run_utc.replace(":", "").replace("-", "")
    snapshot = os.path.join(SNAPSHOT_DIR, stamp + ".json")
    doc = {
        "run_utc": run_utc,
        "baseline_utc": baseline_utc,
        "baseline_path": os.path.relpath(args.baseline, REPO),
        "origin_sent": measure_sources.ORIGIN,
        "days_since_baseline": days,
        "counts": counts,
        "sources": rows,
        "snapshot": os.path.relpath(snapshot, REPO),
    }

    print("\n%d sources: %d regressed, %d improved, %d changed kind, %d unchanged"
          % (counts["sources"], counts["regressed"], counts["improved"], counts["changed"],
             counts["unchanged"]))

    if args.dry_run:
        print("\n(dry run — nothing written)")
        return 1 if counts["regressed"] else 0

    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    with open(snapshot, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    header = ""
    if not os.path.exists(RECORD_MD):
        header = ("# Source reachability — what changed\n\n"
                  "Agenda item 17, rule 1. The catalogue itself is "
                  "`docs/works/fetchable-sources.json` (moment of measurement); this file is the\n"
                  "history of re-measurements, newest first, written by `scripts/source_drift.py`.\n"
                  "A source is not \"reachable\" — it answers *this* reader, on *this* day.\n\n"
                  "---\n\n")
    body = render_markdown(doc)
    old = ""
    if os.path.exists(RECORD_MD):
        with open(RECORD_MD, encoding="utf-8") as f:
            old = f.read()
        head, sep, rest = old.partition("---\n\n")
        old = head + sep + body + "\n---\n\n" + rest
    else:
        old = header + body + "\n---\n\n"
    with open(RECORD_MD, "w", encoding="utf-8") as f:
        f.write(old)
    print("wrote", os.path.relpath(snapshot, REPO), "and", os.path.relpath(RECORD_MD, REPO))
    return 1 if counts["regressed"] else 0


if __name__ == "__main__":
    sys.exit(main())
