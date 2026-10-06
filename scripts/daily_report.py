#!/usr/bin/env python3
# Owner: Desi
"""The daily item report — the human's request of 2026-10-06.

His words: stop sending a report of what each wake did; once a day, send counts for the last 24
hours and for life, for N (items performed during wakes), A (reviewed and accomplished), P
(reviewed and postponed) and R (rejected and never to be accomplished), each split by amigo and by
internal/external, plus the titles added in the last 24 hours and the titles still postponed with
the reason each is postponed.

He reads this to answer three questions: is each amigo doing more or less than before (N and A),
is the work reaching the world or only the repository (external vs internal), and is the pile of
postponed work growing. So the report leads with the counts and never buries the external/internal
split, because that split is the one he says is about the symposium's survival.

It is written to be read on a phone: one line per amigo, no table that wraps, and the detail lists
trimmed with an honest "+k more" rather than silently truncated.

Usage:
    python3 scripts/daily_report.py                 # render to stdout
    python3 scripts/daily_report.py --send          # render, send to the human, record it
    python3 scripts/daily_report.py --hours 24 --send
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.item_ledger import collect, counts, landing_gap, last_landing, load  # noqa: E402

GROUP_LABEL = {
    "N": "N — performed",
    "A": "A — accomplished",
    "P": "P — postponed (everything not accomplished and not rejected)",
    "R": "R — rejected",
}
AMIGO_ORDER = ("desi", "claude", "gemini", "tarik", "dmitri")
LIST_CAP = 8
POSTPONED_SHOWN = 3
# Roughly the budget he pointed at (the old COBOL paragraph-name limit). A truncated sentence is
# still a sentence fragment — which is why the durable fix is for a wake to *name* its own item
# rather than for this code to cut one — but a fragment under forty characters is readable at a
# glance and a 160-character one is not.
DISPLAY_TITLE = 42

# A report's first line is written in the first person, so the value is in what follows the verb.
_LEAD_IN_RE = re.compile(
    r"^(?:(?:I|We)\s+(?:have\s+|had\s+|just\s+|also\s+|now\s+|am\s+|was\s+|were\s+|will\s+|can\s+)?|"
    r"(?:found(?:\s+out)?|checked|verified|noticed|discovered|established)\s+that\s+|"
    r"what\s+i\s+did\s*[:\-—]\s*|area(?:\s+this\s+wake)?\s*[:\-—]\s*|"
    r"this\s+wake\s*[:\-—,]?\s*)", re.I)


def _local(stamp: dt.datetime) -> str:
    return stamp.astimezone().strftime("%Y-%m-%d %H:%M %Z")


def _group_table(group: str, window: dict, life: dict) -> list[str]:
    """One line per amigo, for one group. Compact enough not to wrap on a phone."""
    out = [GROUP_LABEL[group]]
    names = [n for n in AMIGO_ORDER if n in window[group]["by_amigo"]]
    names += [n for n in sorted(window[group]["by_amigo"]) if n not in names]
    if not names:
        out.append("  (none)")
    for who in names:
        s = window[group]["by_amigo"][who]
        out.append(f"  {who:<8} {s['total']:>4}  ({s['internal']} int / {s['external']} ext)")
    life_s = life[group]
    out.append(f"  {'all':<8} {window[group]['total']:>4}  "
               f"({window[group]['internal']} int / {window[group]['external']} ext)"
               f"   lifetime {life_s['total']} ({life_s['internal']} / {life_s['external']})")
    return out


# ---------------------------------------------------------------------------------------------
# Input from outside the commons (the human, 2026-10-06: "I do want external world *input* as well
# as *output*"). Output was the whole of the first version of this report. It is half the picture:
# a commons that only counts what it did cannot tell the difference between being ignored and
# having nothing to say to anyone.
#
# Nothing new is recorded for this. Every message the mail channel fetches already lands as a file
# under channels/inbound/, so the input side is a read of what is there, classified.
# ---------------------------------------------------------------------------------------------
INBOUND_DIR = REPO / "channels" / "inbound"
_RECEIVED_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})-(\d{6})")
_FROM_HDR_RE = re.compile(r"^- From:\s*(.+)$", re.M)
_SUBJ_HDR_RE = re.compile(r"^- Subject:\s*(.+?)\s*$", re.M)
_OUR_LOCAL_RE = re.compile(r"^(?:desi|claude|gemini|tarik|dmitri)[._-]", re.I)
_MACHINE_LOCAL_RE = re.compile(
    r"^(?:no[-_.]?reply|do[-_.]?not[-_.]?reply|mailer[-_.]?daemon|postmaster|bounce[sd]?|"
    r"notifications?|alerts?|automated|system|support|hello|info)\b", re.I)
_MACHINE_SUBJ_RE = re.compile(
    r"undeliverable|delivery status notification|delivery (?:failure|has failed)|mail delivery|"
    r"automatic(?:al)?(?: reply| response| message)|out of office|confirm your subscription|"
    r"security alert|verify your|welcome to|you'?re in", re.I)
# Strong auto-responder markers only. A weak one ("thank you for your message") appears in real
# letters too, and counting a person as a machine hides a human reply — the one thing this section
# exists to show. Every phrase below is something only a robot writes.
_AUTO_BODY_RE = re.compile(
    r"this is an automated|automated (?:reply|response|message|acknowledg)|do not reply to this|"
    r"cannot always respond|unable to respond to|out of office|ticket (?:number|has been created)|"
    r"has been received and will be|we'?ll get back to you|we'?ll be in touch|thrive on reader|"
    r"reply above this line|response within (?:one|two|\d+) business|no-?reply@", re.I)
# A subject that IS an acknowledgement. Safe where a body phrase would not be: nobody titles their
# own reply "Thank you for your message".
_MACHINE_SUBJ_RE_EXTRA = re.compile(r"^\s*thank you for your (?:message|email|enquir|inquir)", re.I)
# The founder is not "outside the commons". He writes to us constantly and counting him as world
# input would swamp the one number this section exists to isolate.
HUMAN_EMAILS = {"ldridgeway@gmail.com", "lindsayridgeway@gmail.com"}


def _bucket(frm: str, subject: str, where: str, body: str = "") -> str:
    """human | ours | automated | bounce | world.

    'world' is the only bucket the human is asking about, and it is deliberately the hardest to
    enter: a message has to come from an address that is not ours and not the founder's, not be a
    robot's, and not be a bounce of our own letter. Everything that cannot be shown to be from a
    person or an organisation is counted as a machine, because the failure that matters here is
    inflating the number of outsiders who wrote to us.
    """
    if where == "bounce":
        return "bounce"
    m = re.search(r"<([^>]+)>", frm)
    addr = (m.group(1) if m else frm).strip().lower()
    local = addr.split("@")[0]
    if addr in HUMAN_EMAILS:
        return "human"
    if _OUR_LOCAL_RE.match(local) or "buttondown" in addr:
        return "ours"
    if (_MACHINE_LOCAL_RE.match(local) or _MACHINE_SUBJ_RE.search(subject or "")
            or _MACHINE_SUBJ_RE_EXTRA.match(subject or "")):
        return "automated"
    if _AUTO_BODY_RE.search(body or ""):
        return "automated"
    return "world"


def received(now: dt.datetime | None = None, hours: int | None = None) -> list[dict]:
    now = now or dt.datetime.now(dt.timezone.utc)
    out = []
    if not INBOUND_DIR.is_dir():
        return out
    for path in sorted(INBOUND_DIR.rglob("*.md")):
        m = _RECEIVED_RE.search(path.name)
        if not m:
            continue
        when = dt.datetime.strptime(m.group(0), "%Y-%m-%d-%H%M%S").replace(tzinfo=dt.timezone.utc)
        if hours is not None and when < now - dt.timedelta(hours=hours):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fh = _FROM_HDR_RE.search(text)
        sh = _SUBJ_HDR_RE.search(text)
        frm = fh.group(1).strip() if fh else "(unknown sender)"
        subj = " ".join((sh.group(1) if sh else "(no subject)").split())
        where = "bounce" if path.parent.name == "diagnostics" else "inbox"
        body = text.split("\n---\n", 1)[1] if "\n---\n" in text else ""
        out.append({"when": when, "from": frm, "subject": subj, "where": where,
                    "bucket": _bucket(frm, subj, where, body)})
    return out


def _inputs_block(now: dt.datetime, hours: int) -> list[str]:
    window = received(now, hours)
    life = received(now, None)
    w = collections.Counter(r["bucket"] for r in window)
    l = collections.Counter(r["bucket"] for r in life)
    lines = [
        "",
        f"### Input from outside (last {hours}h)",
        f"  {len(window)} received — {w['world']} from a person or organisation outside · "
        f"{w['automated']} automated notices · {w['bounce']} bounces of our own mail",
        f"  and {w['human']} from you, {w['ours']} from another amigo (inside the commons)",
        f"  lifetime: {len(life)} received — {l['world']} outside · {l['automated']} automated · "
        f"{l['bounce']} bounces · {l['human']} from you · {l['ours']} from another amigo",
    ]
    world = [r for r in window if r["bucket"] == "world"]
    lines.append(f"**From a person or organisation** ({len(world)})")
    if not world:
        lines.append("  (none — nothing outside the commons wrote to us in this window)")
    for rec in world[:LIST_CAP]:
        lines.append(f"  {_short(rec['from'])} — {_short(rec['subject'])}")
    if len(world) > LIST_CAP:
        lines.append(f"  … +{len(world) - LIST_CAP} more")
    bounces = [r for r in window if r["bucket"] == "bounce"]
    if bounces:
        lines.append(f"**Our own letters that did not arrive** ({len(bounces)})")
        for rec in bounces[:POSTPONED_SHOWN]:
            lines.append(f"  {_short(rec['subject'])}")
        if len(bounces) > POSTPONED_SHOWN:
            lines.append(f"  … +{len(bounces) - POSTPONED_SHOWN} more")
    return lines


def _name(rec: dict) -> str:
    """An item's name: the model-written title if it has one, else the truncated description.

    The model-written one is the point (the human, 2026-10-06: truncation "produces mostly
    boilerplate with little if anything to describe the actual work"). Truncation stays only as the
    fallback for an item titled in the last few minutes, so a missing title never costs the report.
    """
    return rec.get("short_title") or _short(rec.get("title", ""))


def _short(title: str) -> str:
    """A readable glance-length name for an item. The full title stays in the ledger."""
    t = " ".join((title or "").split())
    t = _LEAD_IN_RE.sub("", t).strip()
    if len(t) <= DISPLAY_TITLE:
        return t
    cut = t[:DISPLAY_TITLE - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "…"


def _title_list(rows: list[dict], cap: int = LIST_CAP) -> list[str]:
    if not rows:
        return ["  (none)"]
    rows = sorted(rows, key=lambda r: r.get("filed_utc") or "")
    out = []
    for rec in rows[:cap]:
        group = {"accomplished": "A", "rejected": "R"}.get(rec.get("state"), "P")
        out.append(f"  [{group}] {rec.get('amigo','?'):<7} {_name(rec)}")
    if len(rows) > cap:
        out.append(f"  … +{len(rows) - cap} more in the recorded copy")
    return out


def _landing_block(now: dt.datetime, hours: int, last: str | None, gap: int) -> list[str]:
    """Say plainly when the landing pipeline has gone quiet, because that fact changes what P means.

    The report's whole reading of P rests on `accomplished` being set by a `land(wake)` commit on
    main. When those commits stop, an item stuck "not accomplished" no longer means "nobody has
    looked" — it can mean "the lander refused the whole wake and parked it on a side branch". The
    two are the same string in the ledger and completely different diseases, so the report has to
    distinguish them out loud rather than let a delivery stall read as a review backlog.
    """
    if not last or not gap:
        return []
    when = dt.datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    age_h = (now - when).total_seconds() / 3600.0
    if age_h < hours:
        return []
    return [
        "",
        f"⚠ **No wake work has reached main for {age_h / 24:.1f} days.** The newest `land(wake)`",
        f"commit is {last[:10]} and {gap} item(s) have been filed since. Until landing resumes, the",
        "`not yet reviewed` counts below describe *delivery*, not review — they can include finished",
        "work the lander parked on a side branch rather than work nobody has looked at.",
    ]


def render(hours: int = 24, now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    items = load()
    window = counts(items, hours)
    life = counts(items, None)
    since = (now - dt.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%MZ")

    n, a, p, r = (life[g]["total"] for g in "NAPR")
    lines = [
        f"**Daily item report — {_local(now)}**",
        f"window: the {hours}h to {_local(now)} (since {since})",
        "",
        "P is everything not accomplished and not rejected, so `N = A + P + R` holds by",
        "construction. The number that carries information is inside P: **decided** (someone looked",
        "and said not now, and why) against **not yet reviewed** (nobody has looked).",
        "",
        f"**Lifetime**  N={n}  A={a}  P={p}  R={r}"
        + ("  ✓ N=A+P+R" if n == a + p + r else "  ✗ the identity is broken — investigate"),
        f"    of P: {life['P']['decided']} decided / {life['P']['undecided']} not yet reviewed",
        f"**Last {hours}h**  N={window['N']['total']}  A={window['A']['total']}  "
        f"P={window['P']['total']}  R={window['R']['total']}",
        f"    of P: {window['P']['decided']} decided / {window['P']['undecided']} not yet reviewed",
    ]
    landed = last_landing()
    lines += _landing_block(now, hours, landed, landing_gap(items, landed))
    lines += ["", f"### Last {hours}h, by amigo"]
    for group in "NAPR":
        lines += _group_table(group, window, life)
    lines += _inputs_block(now, hours)
    lines += [
        "",
        f"### Titles added in the last {hours}h",
        f"**Internal** ({window['N']['internal']})",
    ]
    lines += _title_list([x for x in window["items"] if x.get("scope") == "internal"])
    lines += [f"**External** ({window['N']['external']})"]
    lines += _title_list([x for x in window["items"] if x.get("scope") == "external"])

    postponed = [x for x in items.values()
                 if x.get("state") not in ("accomplished", "rejected")]
    decided = [x for x in postponed if x.get("state") == "postponed"]
    lines += ["", f"### Currently postponed ({len(postponed)})",
              f"{len(decided)} decided (someone looked and said not now) — "
              f"{len(postponed) - len(decided)} not yet reviewed (nobody has looked)"]
    for scope in ("internal", "external"):
        rows = [x for x in postponed if x.get("scope") == scope]
        dated = [x for x in rows if x.get("state") == "postponed"]
        fresh = [x for x in rows if x.get("state") != "postponed"]
        shown = max(0, POSTPONED_SHOWN - len(dated))
        lines.append(f"**{scope.title()}** — {len(rows)} postponed "
                     f"({len(dated)} decided / {len(fresh)} not yet reviewed); "
                     f"showing {min(len(dated) + shown, len(rows))}")
        if not rows:
            lines.append("  (none)")
            continue
        for rec in sorted(dated, key=lambda x: x.get("filed_utc") or ""):
            lines.append(f"  {rec.get('amigo','?'):<7} {_name(rec)}")
            lines.append(f"          why: {rec.get('reason','(no reason recorded)')}")
        # Oldest first: with nothing reviewed yet, the informative ones are the items that have sat
        # longest, not the newest. Listing all 146 would bury the signal and blow past one message.
        for rec in sorted(fresh, key=lambda x: x.get("filed_utc") or "")[:shown]:
            lines.append(f"  {rec.get('amigo','?'):<7} {_name(rec)}")
            lines.append("          why: not yet reviewed — nobody has looked at it")
        if len(fresh) > shown:
            lines.append(f"  … +{len(fresh) - shown} more, none of them reviewed yet "
                         f"(oldest shown first)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--amigo", default="desi")
    ap.add_argument("--no-collect", action="store_true",
                    help="skip ingesting new runs first (for a reproducible re-render)")
    ap.add_argument("--title-limit", type=int, default=60,
                    help="most new items to name with the model in one run (0 = no limit)")
    a = ap.parse_args()

    if not a.no_collect:
        collect()
        # Name the new items before rendering, best-effort: a titling failure must never cost the
        # report, and an untitled item falls back to its truncated description.
        try:
            from channels.titles import backfill as title_backfill
            done, failed = title_backfill(limit=a.title_limit)
            if done or failed:
                print(f"daily_report: titled {done} item(s), {failed} failed")
        except Exception as exc:                      # noqa: BLE001
            print(f"daily_report: titling skipped ({type(exc).__name__}: {exc})")
    text = render(a.hours)
    if not a.send:
        print(text)
        return 0

    out = REPO / "channels" / "reports" / f"daily-{dt.datetime.now():%Y-%m-%d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    # Telegram caps a message near 4096 characters. Never let a cap silently eat the counts: the
    # counts are at the top, the item lists are at the bottom, so the tail is what gets dropped.
    sent = text
    if len(sent) > 3900:
        sent = sent[:3860].rsplit("\n", 1)[0] + f"\n\n[…trimmed; full report: {out.name}]"
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "tell_human.py"), "--amigo", a.amigo,
         "--text", sent],
        capture_output=True, text=True, timeout=120,
    )
    print(r.stdout.strip() or r.stderr.strip())
    print(f"daily_report: recorded {out.relative_to(REPO)} ({len(text)} chars, sent {len(sent)})")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
