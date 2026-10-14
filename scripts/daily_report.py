#!/usr/bin/env python3
# Owner: Desi
"""The daily item report — the human's request of 2026-10-06, revised by him on 2026-10-07.

His first words: stop sending a report of what each wake did; once a day, send counts for the last
24 hours and for life, for items performed (N), accomplished (A), postponed (P) and rejected (R),
each split by amigo and by internal/external, plus the titles added in the last 24 hours and the
titles still postponed with the reason each is postponed.

Then he took the vocabulary apart, in Telegram, over one morning, and the second version is his:

    N  performed, no review needed      V  performed, needs review
    A  accomplished                      P  postponed **by a decision** (reason on disk)
    W  waiting for review (nobody has looked)          R  rejected
    N + V = A + P + W + R

His reasons, in his words: P and W "were doing opposite work under one word — P is a decision with a
reason attached, W is nobody having looked — and collapsing them hid exactly the thing that tells
you which failure you have." And N — "performed, no review needed" — is a claim, so it needs a
written reason like P, or it becomes the new dumping ground. His test for the whole thing: N = P in
the lifetime totals means the criteria are broken; Δ(V−W) stuck at zero while ΔW grows means the
drain has stopped. He explicitly did not want dwell unless V−W > 0, and did not want any new ledger
or new field: "just the reporting algorithm to become more sophisticated."

He reads this to answer three questions: is each amigo doing more or less than before, is the work
reaching the world or only the repository (external vs internal), and is the pile of undecided work
growing. So the report leads with the counts and never buries the external/internal split, because
that split is the one he says is about the symposium's survival.

It is written to be read on a phone: one line per amigo, no table that wraps, and the detail lists
trimmed with an honest "+k more" rather than silently truncated.

Usage:
    python3 scripts/daily_report.py                 # render to stdout
    python3 scripts/daily_report.py --send          # render, send to the human, record it
    python3 scripts/daily_report.py --hours 24 --send

What is sent is `render_focus` — the two blocks the human asked for on 2026-10-14 (performed by
amigo, reviewed by amigo), and nothing else. It was 8.5k characters answering questions he did not
have. The rest is not deleted: the recorded file keeps the focus block, then a rule, then the full
analysis underneath, so the depth stays available without being delivered.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.item_ledger import (  # noqa: E402
    assigned,
    blocker_of,
    collect,
    counts,
    holes,
    landing_gap,
    last_landing,
    load,
    price_band,
)

# The six letters, in the order the human reasoned them out (Telegram, 2026-10-07): the
# review-needed axis first (N/V), then the outcome axis (A/P/W/R). His labels, near enough verbatim.
GROUP_LABEL = {
    "N": "N — performed, no review needed (only where the record says why)",
    "V": "V — performed, needs review",
    "A": "A — accomplished",
    "P": "P — postponed by a decision (reason on disk)",
    "W": "W — waiting for review (nobody has looked)",
    "R": "R — rejected",
}
LETTERS = ("N", "V", "A", "P", "W", "R")
GROUPS = LETTERS
AMIGO_ORDER = ("desi", "claude", "gemini", "tarik", "dmitri")
LIST_CAP = 8
BLOCKERS_SHOWN = 6      # blocker lines can run long; the total is printed above them
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


def _commit_own_outputs(paths: list[Path], message: str) -> None:
    """Commit what this script wrote, because leaving it dirty stops every amigo's work landing.

    The lander refuses a dirty shared checkout — deliberately, so it never applies a patch over
    someone's uncommitted writing. That makes anything written here and *not* committed a silent
    outage: nothing landed between 2026-10-06 and 2026-10-08 for exactly this reason, and for
    1.5 days before that. The fix belongs here rather than in the lander, because the lander's
    refusal is correct and this script is the one that made the mess.

    Best-effort and strictly path-scoped: it commits these paths and nothing else, so a session's
    uncommitted writing is never swept up, and a git failure is printed rather than raised — by
    then the report has already been sent, and a report is not worth an exception.
    """
    try:
        staged = [str(p) for p in paths if p.exists()]
        if not staged:
            return
        subprocess.run(["git", "add", "--", *staged], cwd=REPO, check=True,
                       capture_output=True, text=True)
        r = subprocess.run(["git", "commit", "-q", "-m", message], cwd=REPO,
                           capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            print(f"daily_report: committed its own output ({len(staged)} path(s))")
        elif "nothing to commit" not in out:
            print(f"daily_report: WARNING — its output is still uncommitted, landing is blocked: {out}")
    except Exception as exc:                                          # noqa: BLE001
        print(f"daily_report: WARNING — could not commit its own output, landing is blocked ({type(exc).__name__}: {exc})")


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
        out.append(f"  [{_letter(rec)}] {rec.get('amigo','?'):<7} {_name(rec)}")
    if len(rows) > cap:
        out.append(f"  … +{len(rows) - cap} more in the recorded copy")
    return out


def _landing_block(now: dt.datetime, hours: int, last: str | None, gap: int) -> list[str]:
    """Say plainly when the landing pipeline has gone quiet, because that fact changes what W means.

    The report's reading of W rests on `accomplished` being set by a `land(wake)` commit on main.
    When those commits stop, an item sitting in W no longer means only "nobody has looked" — it can
    also mean "the lander refused the whole wake and parked it on a side branch". The two are the
    same string in the ledger and completely different diseases, so the report has to distinguish
    them out loud rather than let a delivery stall read as a review backlog.
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
        "`waiting for review` counts below describe *delivery*, not review — they can include",
        "finished work the lander parked on a side branch rather than work nobody has looked at.",
    ]


def _letter_block(window: dict, life: dict, hours: int) -> list[str]:
    """The six letters as six lines, each split by amigo, plus the lifetime total.

    Six one-letter rows rather than a table: a table of six columns wraps on a phone, and this is
    read on a phone. The per-amigo and internal/external detail the human asked for in his original
    request (2026-10-06) is kept — it is a row per amigo per letter, which is longer but readable.
    """
    out = []
    for letter in LETTERS:
        names = [n for n in AMIGO_ORDER if n in window[letter]["by_amigo"]]
        names += [n for n in sorted(window[letter]["by_amigo"]) if n not in names]
        total = window[letter]["total"]
        life_s = life[letter]
        if not total and not life_s["total"]:
            out.append(f"{letter} — {window[letter]['total']} this window; lifetime 0")
            continue
        out.append(f"**{letter}** — {total} this window "
                   f"({window[letter]['internal']} int / {window[letter]['external']} ext); "
                   f"lifetime {life_s['total']} ({life_s['internal']} / {life_s['external']})")
        if not names:
            out.append("  (none this window)")
            continue
        for who in names:
            s = window[letter]["by_amigo"][who]
            out.append(f"  {who:<8} {s['total']:>3}  ({s['internal']} int / {s['external']} ext)")
    return out


def _diagnosis(window: dict, life: dict, hours: int, items: dict[str, dict],
               now: dt.datetime) -> list[str]:
    """The two readings the human asked for — is the drain running, and is N = P — stated plainly.

    His instructions (2026-10-07): track Δ(V−W) per day; zero for several days is the alarm, and
    zero *while* ΔW grows is unambiguous breakage. And N = P in the lifetime totals means the
    criteria are broken — globally, or for one amigo whose process is then worth a look. Dwell only
    when V−W > 0, which is the one regime where V=W cannot answer the question by itself.
    """
    filed = window["N"]["total"] + window["V"]["total"]
    decided = window["decisions"]
    out = ["", "### Is the drain running?", 
           f"  {filed} filed · {decided} decided · ΔW {filed - decided:+d} · Δ(V−W) {decided:+d}"
           f"  (over {hours}h)"]
    if decided == 0 and filed > 0:
        out.append("  → STOPPED: items kept arriving and nothing was decided. Broken process.")
    elif decided == 0:
        out.append("  → nothing arrived and nothing was decided — uninformative either way.")
    elif decided < filed:
        out.append("  → draining, but slower than the inflow — a capacity problem, not a broken "
                   "process.")
    else:
        out.append("  → draining at least as fast as the inflow.")

    out += ["", "### Is N = P?  (your test: equal totals mean the criteria are broken)"]
    for label, c in ((f"last {hours}h", window), ("lifetime", life)):
        n, p = c["N"]["total"], c["P"]["total"]
        if n == p and n:
            verdict = "EQUAL — the criteria are broken"
        elif n == p:
            verdict = ("equal, but vacuously: neither letter has ever been used — nothing has ever "
                       "declared itself exempt, nothing has ever been postponed by a decision")
        else:
            verdict = "different, so the criteria are doing work"
        out.append(f"  {label}: N={n} P={p} — {verdict}")
    worse = [who for who, s in life["N"]["by_amigo"].items()
             if life["P"]["by_amigo"].get(who, {}).get("total") == s["total"] and s["total"]]
    if worse:
        out.append(f"  per amigo (lifetime), N = P for: {', '.join(sorted(worse))} — worth a look")

    # Dwell, computed only in the regime he said earns it: some drainage happened, so V=W is false
    # and the age of the oldest waiting item is the thing V−W alone cannot tell you.
    v, w = life["V"]["total"], life["W"]["total"]
    if v > w:
        waiting = [r for r in items.values() if _letter(r) == "W" and r.get("filed_utc")]
        if waiting:
            oldest = min(waiting, key=lambda r: r["filed_utc"])
            try:
                when = dt.datetime.strptime(oldest["filed_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=dt.timezone.utc)
                days = (now - when).days
                out.append(f"  dwell: the oldest item still waiting has sat {days}d "
                           f"(filed {oldest['filed_utc'][:10]}, {oldest.get('amigo','?')})")
            except ValueError:
                pass
    else:
        out.append("  dwell: not computed — V = W, so the question has no content.")
    return out


def _letter(rec: dict) -> str:
    from channels.item_ledger import letter_for
    return letter_for(rec)


CREDENTIAL_FILE = Path.home() / ".config" / "llm-symposium" / "push-token"
ROTATION_DAYS = 300


def _credential_file_age(path: Path | None = None, now=None):
    """(installed, days_old) for the commons' credential file, or (None, None).

    Read from the file at report time and on the machine the report runs on: the register is
    written by whichever check ran last, including CI's, where this file does not exist. The
    install date is a property of this machine, so it is derived here rather than carried.
    """
    import datetime as _dt
    p = path or CREDENTIAL_FILE
    try:
        stamp = p.stat().st_mtime
    except OSError:
        return None, None
    when = _dt.datetime.fromtimestamp(stamp, _dt.timezone.utc)
    now = now or _dt.datetime.now(_dt.timezone.utc)
    return when, round((now - when).total_seconds() / 86400)


def _invitations_block(now=None, path: Path | None = None) -> list[str]:
    """Repository invitations: mail whose answer is not a reply.

    Added 2026-10-12 after the human asked why four amigos had ignored his
    collaboration request. They had not — every one of them answered it by email
    and every answer bounced off noreply@github.com — and the invitations
    themselves are to *addresses*, not accounts, so nobody can accept them. The
    point of printing this in the daily report is that it is a standing condition
    the human, and only the human, can change; a condition nobody looks at is the
    original defect, one level up.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    path = path or (REPO / "channels" / "gh-invitations.jsonl")
    if not path.exists():
        return ["", "### Repository invitations", "  no check has ever run — "
                "`python3 channels/gh_invites.py --status` says which are pending and why"]
    last = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                last = json.loads(line)
            except json.JSONDecodeError:
                continue
    if not last:
        return ["", "### Repository invitations", "  the register is empty or unreadable"]
    try:
        checked = dt.datetime.strptime(last.get("checked_utc", ""), "%Y-%m-%dT%H:%M:%SZ"
                                       ).replace(tzinfo=dt.timezone.utc)
        age_h = (now - checked).total_seconds() / 3600
        age = f"{age_h:.0f}h ago"
    except ValueError:
        age = "at an unreadable time"
        age_h = 999
    rows = last.get("pending", [])
    out = ["", f"### Repository invitations  (checked {age} as {last.get('actor') or '?'})"]
    cred = last.get("credential") or {}
    if cred:
        note = cred.get("note", "?")
        exp = cred.get("expires_utc", "")
        days = None
        if exp:
            try:
                when = dt.datetime.strptime(exp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
                days = round((when - now).total_seconds() / 86400)
            except ValueError:
                days = None
        if days is not None:
            note = f"expires in {days} days" if days >= 0 else f"EXPIRED {-days} days ago"
        out.append(f"  the credential that pushes and reads this: {note}"
                   + (f" (until {exp[:10]})" if exp else ""))
        if days is not None and days < 30:
            out.append("  → renew it before it dies: an expired credential stops CI pushes and this")
            out.append("    check, silently — which is the class of failure this register exists for.")
        commons = cred.get("commons") or {}
        stamp, age = _credential_file_age()
        if stamp is not None:
            out.append(f"  the commons' own credential: the file here was installed "
                       f"{stamp.strftime('%Y-%m-%d')}, {age} days ago")
            if age >= 300:
                out.append("  → ROTATION DUE: this credential carries no expiry date, so nothing")
                out.append("    else will ever call for it to be replaced. That is the one thing a")
                out.append("    date would have done, and a leaked token with no date is a token")
                out.append("    that never has to stop working.")
        elif commons.get("note"):
            out.append(f"  the commons' own credential: {commons['note']}")
    if not rows:
        out.append("  none pending.")
    else:
        out.append(f"  {len(rows)} pending:")
        for r in rows:
            who = r.get("amigo") or "?"
            addr = r.get("address") or "(address not in any mailbox)"
            out.append(f"    {r.get('id')}  {who:<7} {addr}  → {r.get('verdict')}")
        if all(r.get("verdict") == "no_account" for r in rows):
            out.append("  Every one is an invitation to an ADDRESS, not an account: acceptance is a")
            out.append("  sign-in, and no account holds those addresses. Neither the amigos nor any")
            out.append("  script can accept them; only the human can change that. The amigos each")
            out.append("  answered the invitation by email and their answers bounced.")
    if age_h > 48:
        out.append(f"  STALE: the last check is {age_h:.0f}h old — if this is not running, the "
                   "condition is invisible again, which is the defect this register exists to end.")
    if last.get("note"):
        out.append(f"  note: {last['note']}")
    return out


def _review_block(items: dict[str, dict], window: dict, hours: int) -> list[str]:
    """Who is looking, who is not, and what is actually blocking — the human's 2026-10-09 questions.

    His rule: every waiting item carries a name, or it is not a queue. He asked for three things
    that the letters alone cannot say: whether W has names on it at all (a nameless W is the
    failure, not the backlog), who is carrying it, and — the artifact he said is worth more than
    the count — the list of items that left W *without* being accomplished, each with the reason
    that stopped it. That last list is the boundary of what the commons can do without help, and
    separating our own failures from the world's limits is the whole value of printing it.
    """
    waiting = [r for r in items.values() if _letter(r) == "W"]
    named = collections.Counter(r.get("assigned_to") for r in waiting if r.get("assigned_to"))
    unnamed = len(holes(items))

    out = ["", "### Who is looking  (your assignment rule, 2026-10-09)"]
    if named:
        out.append("  W carries a name: " + " · ".join(f"{w} {n}" for w, n in named.most_common()))
    else:
        out.append("  W carries no names at all — every waiting item is unowned, so nothing is "
                   "addressed to anyone. That is the defect, not the pile size.")
    if unnamed:
        out.append(f"  {unnamed} waiting item(s) have NO name: a hole, not a queue. Reported as a "
                   f"fact, not a request — assign with `item_ledger.py --draw` or `--assign`.")
    else:
        out.append("  no holes: every waiting item is addressed to somebody.")
    try:
        band, as_of, band_file = price_band()
        out.append(f"  cheap band (prices {as_of}, {band_file.name}): {', '.join(band)} — the draw "
                   f"is a function of the item's id, so it cannot re-roll; the author is never the "
                   f"reviewer.")
    except (FileNotFoundError, ValueError) as exc:
        out.append(f"  NO PRICE BAND — {type(exc).__name__}: {exc}. Draws cannot be made until "
                   f"`scripts/price_band.py --write` has run.")

    # 2026-10-10: what the *window* A count cannot show. An item filed in September and reviewed
    # today is an accomplishment today, but the letters count items filed in the window, so it never
    # appears in the A line above — and the human reads A=0 in the window as "no reviews are being
    # done" when the review happened. Exits are counted by their own state_utc, which is the fact.
    exits = [r for r in items.values() if _in_window(r, hours) and _letter(r) in ("A", "P", "R")]
    if exits:
        tally = collections.Counter(_letter(r) for r in exits)
        reviewed = sum(1 for r in exits if _letter(r) == "A"
                       and r.get("reviewer") not in (None, "auto:land"))
        parts = [f"A {tally['A']}" + (f" ({reviewed} by a review)" if tally["A"] else "")]
        parts += [f"{letter} {tally[letter]}" for letter in ("P", "R") if tally[letter]]
        out.append(f"  exits recorded in the last {hours}h: " + " · ".join(parts))
    else:
        out.append(f"  exits recorded in the last {hours}h: none — nothing left W by any route.")

    # 2026-10-12, the human's question: "Do you report reviews?" The line above moves once they have
    # happened — only once W has been drained and its work landed, which can take weeks and can be
    # done by somebody walking past a wake rather than by the body assigned the review. That is a
    # rate, not a *who*. Measured today: 38 of the 39 review decisions in the ledger's whole history
    # are Desi's, and nothing in the report said so. A review is an act by a body, and no letter
    # counts it (the six letters describe items), so it is counted here instead, attributed.
    reviews = [r for r in items.values()
               if r.get("reviewer") not in (None, "auto:land") and _letter(r) in ("A", "P", "R")]

    def _who(tally: collections.Counter) -> str:
        if not tally:
            return "nobody"
        names = [n for n in AMIGO_ORDER if tally.get(n)]
        names += [n for n in sorted(tally) if n not in names and tally[n]]
        return " · ".join(f"{n} {tally[n]}" for n in names)

    out.append(f"  reviews performed: last {hours}h {_who(collections.Counter(r['reviewer'] for r in reviews if _in_window(r, hours)))}"
               f" / ever {_who(collections.Counter(r['reviewer'] for r in reviews))}"
               f"  ({len(reviews)} decisions by a body, ever; every other A is the lander's gate alone)")

    left = [r for r in items.values() if _letter(r) in ("P", "R") and _in_window(r, hours)]
    out += ["", f"### Blockers: left W in the last {hours}h without being accomplished ({len(left)})",
            "These are the items a review moved somewhere other than A, each with the reason that "
            "stopped it. This is the list that says *why* the commons is stuck rather than how much."]
    if not left:
        out.append("  (none — nothing left W by decision in this window)")
    for rec in sorted(left, key=lambda r: r.get("state_utc") or "")[:BLOCKERS_SHOWN]:
        out.append(f"  {_letter(rec)}  {rec.get('amigo','?'):<7} {_name(rec)}")
        out.append(f"     because: {blocker_of(rec) or '(no reason recorded)'}")
    if len(left) > BLOCKERS_SHOWN:
        out.append(f"  … +{len(left) - BLOCKERS_SHOWN} more")
    return out


def _in_window(rec: dict, hours: int) -> bool:
    """Did this item reach its state inside the window? (state_utc, not filed_utc.)"""
    stamp = rec.get("state_utc")
    if not stamp:
        return False
    try:
        when = dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return False
    return when >= dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)


def _sections(items: dict[str, dict], hours: int) -> tuple[list[dict], list[dict]]:
    """The two lists of undecided work: postponed by a decision, and waiting for review.

    They are different things and the second is the one that grows. He asked for the postponed list
    with reasons (2026-10-06); after the 2026-10-07 split that list is P, and it will usually be
    short, because a reason on disk is what makes something P.
    """
    postponed, waiting = [], []
    for rec in items.values():
        letter = _letter(rec)
        if letter == "P":
            postponed.append(rec)
        elif letter == "W":
            waiting.append(rec)
    return postponed, waiting


def _filed_within(rec: dict, hours: int, now: dt.datetime) -> bool:
    """Was this item *filed* inside the window? The performed tally counts filing, not decision.

    `_in_window` deliberately reads `state_utc`, because for the letters the question is when an
    item reached its state. Performance is the other axis: when the work was offered. Keeping them
    as two named helpers is the point — the earlier report used the words "last 24h" for both and
    the two populations are different sizes (23 filed, 172 moved), which is what made it unreadable.
    """
    stamp = rec.get("filed_utc")
    if not stamp:
        return False
    try:
        when = dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return False
    return (now - when) <= dt.timedelta(hours=hours)


def render_focus(hours: int = 24, now: dt.datetime | None = None) -> str:
    """The two questions the human asked on 2026-10-14, and nothing else.

    His words: "I think the report tries to answer more questions than I have right now." What he
    asked for instead is two blocks — by amigo, items performed; by amigo, items reviewed — five
    lines and a total each.

    Three things are deliberate:

    * One window, and only one. He asked for the last 24 hours, so every figure in the message comes
      from that window. The first draft of this block printed a lifetime total on each total line,
      which is the same defect the old report had — a number from one period sitting beside numbers
      from another — and he caught it the next day.
    * Five names always appear, zeros included. He asked for five lines, and a name missing from a
      scoreboard reads as a name that does not exist — which is how two amigos who have never
      reviewed anything stayed invisible.
    * The two blocks carry his words, not the ledger's letters. He calls the first "accomplished"
      and the second "reviewed", and asked for them as A and R — but A and R already mean other
      things in this same report (accepted as done; rejected), and giving one letter a second
      meaning is the kind of collision that made the old version unreadable. "Finished" and
      "reviewed" say it without the clash, and neither depends on knowing the letter scheme.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    items = load()
    every = list(items.values())
    since = (now - dt.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%MZ")

    finished = [r for r in every if _filed_within(r, hours, now)]
    performed = collections.Counter(r.get("amigo") for r in finished)

    reviewed = [r for r in every
                if r.get("reviewer") not in (None, "auto:land") and _letter(r) in ("A", "P", "R")
                and _in_window(r, hours)]
    decided = collections.Counter(r.get("reviewer") for r in reviewed)

    out = [f"**Daily item report — {_local(now)}**",
           f"window: the {hours}h to {_local(now)} (since {since})",
           "",
           "**Items finished, by amigo** — the last 24 hours"]
    for who in AMIGO_ORDER:
        out.append(f"  {who:<8} {performed.get(who, 0):>4}")
    out.append(f"  {'total':<8} {sum(performed.values()):>4}")
    out.append("  where they stand:")
    for letter, label in (("W", "waiting"), ("A", "accomplished"), ("P", "postponed"),
                          ("R", "rejected")):
        hits = [r for r in finished if _letter(r) == letter]
        if not hits:
            continue
        who = collections.Counter(r.get("amigo") for r in hits)
        out.append(f"    {label:<13} "
                   + " · ".join(f"{n} {who[n]}" for n in AMIGO_ORDER if who.get(n))
                   + f"   total {len(hits)}")

    out += ["", "**Items reviewed, by amigo** — the last 24 hours"]
    for who in AMIGO_ORDER:
        out.append(f"  {who:<8} {decided.get(who, 0):>4}")
    out.append(f"  {'total':<8} {sum(decided.values()):>4}")
    out.append("  how they were decided:")
    for state, label in (("accomplished", "accomplished"), ("postponed", "postponed"),
                         ("rejected", "rejected")):
        hits = [r for r in reviewed if r.get("state") == state]
        if not hits:
            continue
        who = collections.Counter(r.get("reviewer") for r in hits)
        out.append(f"    {label:<13} "
                   + " · ".join(f"{n} {who[n]}" for n in AMIGO_ORDER if who.get(n))
                   + f"   total {len(hits)}")
    return "\n".join(out)


def render(hours: int = 24, now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    items = load()
    window = counts(items, hours)
    life = counts(items, None)
    since = (now - dt.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%MZ")

    lines = [
        f"**Daily item report — {_local(now)}**",
        f"window: the {hours}h to {_local(now)} (since {since})",
        "",
        "Letters (your scheme of 2026-10-07; the split you insisted on):",
    ] + [f"  {GROUP_LABEL[g]}" for g in LETTERS] + [
        "`N+V = A+P+W+R` holds by construction. What carries information is the split inside A",
        "(reviewed vs the lander's gate) and whether W is draining.",
        "",
        f"**Lifetime**  " + "  ".join(f"{g}={life[g]['total']}" for g in LETTERS)
        + ("  ✓ N+V=A+P+W+R" if life["N"]["total"] + life["V"]["total"]
           == sum(life[g]["total"] for g in "APWR") else "  ✗ the identity is broken — investigate"),
        f"    A: {life['A']['by_review']} by a review / {life['A']['by_gate']} by the lander's "
        f"test gate.  P: {life['P']['total']} decided.  W: {life['W']['total']} never looked at.",
        f"**Last {hours}h**  " + "  ".join(f"{g}={window[g]['total']}" for g in LETTERS)
        + ("  ✓" if window["N"]["total"] + window["V"]["total"]
           == sum(window[g]["total"] for g in "APWR") else "  ✗"),
        f"    A: {window['A']['by_review']} by a review / {window['A']['by_gate']} by the gate.  "
        f"P: {window['P']['total']} decided.  W: {window['W']['total']} never looked at.",
    ]
    landed = last_landing()
    lines += _landing_block(now, hours, landed, landing_gap(items, landed))
    lines += _diagnosis(window, life, hours, items, now)
    lines += _review_block(items, window, hours)
    lines += _invitations_block(now)
    lines += ["", f"### Last {hours}h, by amigo"]
    lines += _letter_block(window, life, hours)
    lines += _inputs_block(now, hours)
    lines += [
        "",
        f"### Titles added in the last {hours}h",
        f"**Internal** ({window['V']['internal'] + window['N']['internal']})",
    ]
    lines += _title_list([x for x in window["items"] if x.get("scope") == "internal"])
    lines += [f"**External** ({window['V']['external'] + window['N']['external']})"]
    lines += _title_list([x for x in window["items"] if x.get("scope") == "external"])

    postponed, waiting = _sections(items, hours)
    lines += ["", f"### Postponed by a decision ({len(postponed)})",
              "A postponed item carries its reason on disk. This should grow slowly, and every line"
              " here should have been a choice:"]
    for scope in ("internal", "external"):
        rows = sorted([x for x in postponed if x.get("scope") == scope],
                      key=lambda x: x.get("filed_utc") or "")
        lines.append(f"**{scope.title()}** — {len(rows)}")
        if not rows:
            lines.append("  (none — nothing has ever been postponed by a decision)")
            continue
        for rec in rows[:POSTPONED_SHOWN]:
            lines.append(f"  {rec.get('amigo','?'):<7} {_name(rec)}")
            lines.append(f"          why: {rec.get('reason','(no reason recorded)')}")
        if len(rows) > POSTPONED_SHOWN:
            lines.append(f"  … +{len(rows) - POSTPONED_SHOWN} more")

    # W is the review backlog, and the total always survives truncation — he accepted a cut list
    # only on that condition (2026-10-06). Oldest first: with nothing reviewed, the informative
    # items are the ones that have sat longest.
    lines += ["", f"### Waiting for review ({len(waiting)})",
              "Nobody has looked at these. No reason is printed because there is none to print — "
              "that is the finding."]
    for scope in ("internal", "external"):
        rows = sorted([x for x in waiting if x.get("scope") == scope],
                      key=lambda x: x.get("filed_utc") or "")
        lines.append(f"**{scope.title()}** — {len(rows)} waiting; showing "
                     f"{min(POSTPONED_SHOWN, len(rows))}")
        if not rows:
            lines.append("  (none)")
            continue
        for rec in rows[:POSTPONED_SHOWN]:
            lines.append(f"  {rec.get('amigo','?'):<7} {_name(rec)}")
        if len(rows) > POSTPONED_SHOWN:
            lines.append(f"  … +{len(rows) - POSTPONED_SHOWN} more, oldest shown first")
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
    ledger = REPO / "channels" / "items.jsonl"
    text = render(a.hours)
    focus = render_focus(a.hours)
    if not a.send:
        print(focus)
        print("\n--- the full report below is recorded, not sent ---\n")
        print(text)
        # collect() just appended rows to the ledger; a render that walks away from them dirties the
        # checkout and blocks landing, so the ledger is committed on the render path too.
        if not a.no_collect:
            _commit_own_outputs([ledger], "report(ledger): ingest the runs filed since the last report")
        return 0

    out = REPO / "channels" / "reports" / f"daily-{dt.datetime.now():%Y-%m-%d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    # The record keeps both: what he was sent, then the full analysis underneath it. The message is
    # the two questions he actually has; the depth stays on disk for anyone who wants it, which is
    # why nothing below the rule was deleted — only stopped being delivered.
    out.write_text(focus + "\n\n---\n\n" + text + "\n", encoding="utf-8")
    # Telegram caps a message near 4096 characters. Never let a cap silently eat the counts: the
    # counts are at the top, the item lists are at the bottom, so the tail is what gets dropped.
    sent = focus
    if len(sent) > 3900:
        sent = sent[:3860].rsplit("\n", 1)[0] + f"\n\n[…trimmed; full report: {out.name}]"
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "tell_human.py"), "--amigo", a.amigo,
         "--text", sent],
        capture_output=True, text=True, timeout=120,
    )
    print(r.stdout.strip() or r.stderr.strip())
    print(f"daily_report: recorded {out.relative_to(REPO)} ({len(text)} chars, sent {len(sent)})")
    _commit_own_outputs([out, ledger],
                        "report(daily): the day's counts, sent")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
