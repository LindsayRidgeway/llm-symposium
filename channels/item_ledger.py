#!/usr/bin/env python3
# Owner: Desi
"""The item ledger — one row per item an amigo performed in a wake, and its review outcome.

Why this exists (2026-10-06). The human asked for a daily report of **N** (items performed in
wakes), **A** (reviewed and accomplished), **P** (reviewed and postponed) and **R** (rejected and
never to be accomplished), each split by amigo and by internal/external. The commons had no such
register. It had run records (`<bot>/tick-state/runs/*/`) and five overlapping prose queues
(`channels/tasks.md`, `channels/action-queue.md`, `channels/reject-queue.md`, `channels/agenda.md`,
`to-do-lists/*.md`). "An item, with an originator and a scope" existed nowhere. This is that
register, and it is deliberately one file rather than a sixth queue.

The unit. One item = one unit of work a wake finished. The evidence is the run's own changed paths:
a run that changed nothing performed no item. This is computed from the run record, never from a
model's account of itself, because a wake cut off at its action cap cannot be trusted to finish its
own bookkeeping — and the action-cap cutoff is a known fault, so self-report would undercount
exactly the wakes that did the most. One run that touched several files is one item; a wake that
declares `ITEM:` lines in its report overrides the derivation (see `items_from_report`).

Scope. `external` = the item had a visible effect outside the repository: an email sent
(`channels/sent/`, `channels/outbound/`), a submission to an outside body (`channels/outreach/`),
or a change to the published magazine (`docs/`). Everything else is `internal`. A run that touched
both is one external item — the classification is "did this reach the world", and one yes is enough.

State, second scheme (the human, 2026-10-07 — this supersedes the four-letter version below it).
He took the two collapsed words apart again, and the split is the whole point:

    N  performed, no review needed      V  performed, needs review
    A  accomplished                      P  postponed **by a decision** (reason on disk)
    W  waiting for review (nobody has looked)          R  rejected

    N + V = A + P + W + R

Two rules make that work **without anyone maintaining a new field** (his constraint: "just the
reporting algorithm to become more sophisticated"):

1. `P` is not the remainder any more. An item counts as P only if the reason for postponing it is
   already written on the item. No reason on disk -> it is `W`, however long it has sat. The old
   four-letter version made P the remainder, which is exactly why P was useless as a number: it
   equalled "everything that is not A or R" and told the human nothing about whether anyone had
   looked. That was his point on 2026-10-08 and he was right.
2. `N` is an exemption, and an exemption must be *claimed in writing* — otherwise it is a
   self-granted pass, which is how N would become the dumping ground P used to be. No stated reason
   to skip review -> the item reads as `V`. The honest failure mode: something unexplained reads as
   waiting, which is what it is. Today that means N=0 — nothing has ever declared itself exempt.

His reading of the two numbers, kept because it is the point of the whole exercise:
`N = P` in the lifetime totals means the criteria are broken — everything looks reviewable so
nothing is ever exempted and nothing is ever settled; `N = P` for one amigo means *that* amigo's
process is worth a look. And the drain is measured as Δ(V−W): how many items left W in the window.
Δ(V−W)=0 while ΔW>0 is a broken process (nothing draining, inflow continuing); both positive is a
capacity problem. Dwell is computed only when V−W>0, which is the one case V=W cannot answer.

A is one letter with two causes, and the report prints both: `by_review` (somebody looked and kept
it) and `by_gate` (the lander's test suite passed, so it reached main — verifiable, but not the same
as reviewed). The earlier version of this ledger set A for lander-passed runs and said so in prose;
splitting it inside the letter is the same disclosure, in the report rather than in a footnote.

The history, kept because the reasoning is not in the git log: the human corrected an earlier
version on 2026-10-06 — it had published a fourth group `U` (performed, not yet reviewed), and he
said U is just a particular case of P. That produced the collapsed four-letter scheme (`N = A + P +
R`, with a decided/undecided split hidden inside P). On 2026-10-07 he un-collapsed it, on his own
reasoning: P and W "were doing opposite work under one word — P is a decision with a reason
attached, W is nobody having looked — and collapsing them hid exactly the thing that tells you which
failure you have." The `U` letter does not come back; the *distinction* does, under the name W.

Assignment, third scheme (2026-10-09, the human's, in the Telegram session where he asked what our
assignment algorithm was and the honest answer was: there is none). That answer explained W better
than anything else. `W` did not fail to drain because the items were hard or because nobody wanted
the work — it failed because no item ever carried the name of a person whose job it was, so the
queue's exit condition was addressed to nobody in particular. A queue with no assignee has no exit.

His algorithm, adopted as given:

    a.  if one amigo is plainly best suited — assign that amigo, and write down *why*, in one line
    b.  otherwise — draw at random among the least expensive amigos, and **record the draw**

Two constraints were added the same day, both from him:

    the author is never the reviewer, not even when the author is the best suited
    the draw is frozen: it is a function of the item's own id, so a later wake cannot re-roll it

The second is why `assigned_to` is written into an appended record rather than recomputed. A draw
re-evaluated on every wake is a strobe light: the same item points at a different amigo each time it
is looked at, which is indistinguishable from being unowned. Frozen, it is a fact.

Prices come from a dated band (`channels/usage/price-band-YYYY-MM.json`, written monthly by
`scripts/price_band.py`), never from a hardcoded amigo: "assign to the cheapest" freezes today's
price list into the code, while "draw from the band as dated" reads the prices when the draw
happens, so the rule survives every future change to what these models cost. A missing band is an
error, not a default — an undated price list is a guess wearing a number.

`W` with no name on it is not a queue, it is a hole, and `holes()` is the escalation list: the
report prints it as a fact for the founder rather than letting the pile look like a process.

Ledger format: JSON Lines, append-only, `channels/items.jsonl` — one object per line, later lines
for the same `id` are state changes. Same shape as `channels/usage/ci-usage.jsonl`, for the same
reason: an append-only file cannot be half-written into a plausible lie.

CLI:
    python3 channels/item_ledger.py --collect              # ingest runs from all five bots
    python3 channels/item_ledger.py --backfill             # ingest all history (idempotent)
    python3 channels/item_ledger.py --queue desi           # what is waiting and addressed to me
    python3 channels/item_ledger.py --draw                 # name every unassigned waiting item
    python3 channels/item_ledger.py --assign <id> --to gemini --reason "why gemini"
    python3 channels/item_ledger.py --review <id> --state postponed --reason "why"
    python3 channels/item_ledger.py --summary [--hours 24]
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"

# The five bodies. `amigo` is the originator of every item its own wake performed.
HOME = Path(os.path.expanduser("~"))
AMIGOS = ("desi", "claude", "gemini", "tarik", "dmitri")
RUNS_REL = Path("tick-state") / "runs"

# Paths whose change means the item reached the world outside this repository.
EXTERNAL_PREFIXES = (
    "docs/",                    # the published magazine
    "channels/sent/",           # mail this commons sent
    "channels/outbound/",       # ditto, on its way out
    "channels/outreach/",       # submissions/pitches to outside organisations
)

STATES = ("accomplished", "postponed", "rejected")

# Where the monthly price band lives, and how far from the cheapest an amigo may be and still count
# as "least expensive". The band rule is stated here so the file it writes can say what it means.
BAND_DIR = REPO / "channels" / "usage"
BAND_GLOB = "price-band-*.json"

RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}$")
ANY_RUN_ID_RE = re.compile(r"\b(\d{8}T\d{6}Z-[0-9a-f]{8})\b")
ITEM_RE = re.compile(r"^\s*ITEM:\s*\[(?P<scope>internal|external)\]\s*(?P<title>.+?)\s*$", re.I)
TITLE_MAX = 160
TITLE_SHOWN = 60          # how much of a title --next prints; the full one stays in the ledger


def _short(text: str, limit: int = TITLE_SHOWN) -> str:
    """Cut a title on a word boundary for the terminal. The ledger keeps the whole thing."""
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return (cut or text[:limit]) + "…"


def runs_dir(amigo: str) -> Path:
    return HOME / "LLM" / f"{amigo}-bot" / RUNS_REL


def parse_run_time(run_id: str) -> str:
    """`20261006T082758Z-245fa706` -> `2026-10-06T08:27:58Z`."""
    stamp = run_id.split("-", 1)[0]
    d = dt.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


# A wake's report opens with whatever it wrote first, and older runners wrote their *intent*
# before doing anything ("Intend to: …"). An intent is not an item; the title must say what the
# wake did or found. Measured on the 2026-09-15/16 runs, which are all intent-first.
_NOT_A_TITLE_RE = re.compile(
    r"^(?:intend(?:ing)?\b|start(?:ing|ed)?\b|i will\b|plan(?:ning)?\b|area this wake\b|"
    r"chose item\b|wake\b\s*[—:-])", re.I)


def best_title(text: str, limit: int = TITLE_MAX) -> str:
    """The report's own one-line summary of the work, not its statement of intent."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    for line in lines:
        if _NOT_A_TITLE_RE.match(line):
            continue
        if len(line) >= 25:                      # a title, not a heading fragment
            return line[:limit]
    return (lines[0][:limit] if lines else "(no report)")


def items_from_report(report_text: str) -> list[dict]:
    """Explicit `ITEM: [internal|external] <title>` lines, if the wake declared any.

    A wake that declares its items is believed over the derivation, because it can tell one item
    from three. A wake that declares none falls back to one item for the run.
    """
    out = []
    for line in (report_text or "").splitlines():
        m = ITEM_RE.match(line)
        if m:
            out.append({"scope": m.group("scope").lower(), "title": m.group("title")[:TITLE_MAX]})
    return out


def scope_for_paths(paths: list[str]) -> str:
    for p in paths or []:
        if any(p.startswith(pref) for pref in EXTERNAL_PREFIXES):
            return "external"
    return "internal"


def run_to_items(amigo: str, run_dir: Path) -> list[dict]:
    """The items a single wake performed. Empty when the run changed nothing."""
    result = run_dir / "result.json"
    try:
        data = json.loads(result.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    changed = [p for p in (data.get("changed_paths") or []) if isinstance(p, str)]
    if not changed:
        return []
    report_path = run_dir / "report.txt"
    try:
        report_text = report_path.read_text(encoding="utf-8")
    except OSError:
        report_text = ""
    declared = items_from_report(report_text)
    run_id = data.get("run_id") or run_dir.name
    filed = parse_run_time(run_id) if RUN_ID_RE.match(run_id) else None
    common = {
        "id": run_id,
        "filed_utc": filed,
        "amigo": amigo,
        "evidence": f"{amigo}-bot run {run_id}",
        "paths": changed[:20],
        "source": "declared" if declared else "derived",
    }
    if declared:
        return [dict(common, scope=d["scope"], title=d["title"]) for d in declared]
    return [dict(common, scope=scope_for_paths(changed), title=best_title(report_text))]


def landed_run_ids(repo: Path = REPO) -> set[str]:
    """Run ids named by a `land(wake): work from run <id>` commit — i.e. work that reached main.

    One pass over the log, not one call per run: three hundred and fifty runs would otherwise be
    three hundred and fifty git invocations.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--pretty=%B"],
            capture_output=True, text=True, timeout=120, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    return set(ANY_RUN_ID_RE.findall(out))


LANDING_STAMP = "land(wake)"


def last_landing(repo: Path = REPO) -> str | None:
    """ISO-8601 UTC timestamp of the newest `land(wake)` commit on main, or None if there is none.

    This is the *delivery* clock, and it is not the same question as `landed_run_ids`. That function
    says which runs reached main; this says whether the landing pipeline is running at all. It has
    to be asked separately because the two failures look identical in the item states: an item that
    was reviewed and put off and an item whose whole wake was refused by land_runs.py are both
    simply "not accomplished". Measured 2026-10-06: the pipeline had been silent for 2.7 days while
    22 items were filed, and the daily report presented that as a review backlog — "nobody has
    looked" — when the true cause was that no work was being landed. One cheap git call.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%cI", "--grep", LANDING_STAMP],
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not out:
        return None
    try:
        when = dt.datetime.fromisoformat(out)
    except ValueError:
        return None
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def landing_gap(items: dict[str, dict], last: str | None) -> int:
    """How many items were filed after the last landing. Non-zero with an old `last` is a stall."""
    if not last:
        return sum(1 for r in items.values() if r.get("filed_utc"))
    return sum(1 for r in items.values() if (r.get("filed_utc") or "") > last)


def load(path: Path = LEDGER) -> dict[str, dict]:
    """Every item, with later lines overriding earlier ones. A corrupt line is skipped loudly."""
    items: dict[str, dict] = {}
    if not path.exists():
        return items
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            items[rec["id"]] = rec
        except (ValueError, KeyError):
            print(f"item_ledger: skipping unreadable line {lineno}", file=sys.stderr)
    return items


def append(records: list[dict], path: Path = LEDGER) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")


def collect(path: Path = LEDGER, since: str | None = None, amigo: str | None = None) -> int:
    """Append one `performed` row per new run that changed something. Idempotent by run id."""
    known = load(path)
    landed = landed_run_ids()
    fresh = []
    for who in ([amigo] if amigo else AMIGOS):
        root = runs_dir(who)
        if not root.is_dir():
            continue
        for run_dir in sorted(root.iterdir()):
            if not run_dir.is_dir():
                continue
            if since and run_dir.name < since:
                continue
            for item in run_to_items(who, run_dir):
                if item["id"] in known:
                    continue
                # Verify the accomplishment rather than assert it.
                item["state"] = "accomplished" if item["id"] in landed else None
                item["state_utc"] = item["filed_utc"] if item["state"] else None
                item["reason"] = ("landed on main (lander's test gate passed)"
                                  if item["state"] else None)
                item["reviewer"] = "auto:land" if item["state"] else None
                fresh.append(item)
                known[item["id"]] = item
    append(fresh, path)
    return len(fresh)


def review(path: Path = LEDGER, item_id: str = "", state: str = "", reason: str = "",
           reviewer: str = "human") -> dict:
    """Move one item to a terminal state, with a reason. Postponed/rejected require one."""
    if state not in STATES:
        raise ValueError(f"state must be one of {STATES}, got {state!r}")
    if not reason.strip():
        raise ValueError("a postponed or rejected item needs a reason — that is the whole record")
    if state == "accomplished" and not _names_work(reason):
        raise ValueError(
            "moving an item to accomplished means the work itself is done — name it (a path or a "
            "run id), not that you looked. A stamp is not a review, and it is the one exit the "
            "human forbade on 2026-10-09")
    rec = load(path).get(item_id)
    if rec is None:
        raise KeyError(f"no such item: {item_id}")
    rec = dict(rec)
    rec.update(state=state, state_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               reason=reason.strip(), reviewer=reviewer)
    append([rec], path)
    return rec


def letter_for(rec: dict) -> str:
    """Which of A/P/W/R an item sits in. W is the remainder, and deliberately so.

    W is the honest place for anything undecided: an item is *waiting for review* unless the
    artifact already carries a decision. `postponed` without a written reason reads as W too —
    a postponement nobody wrote down is not a decision, it is an absence, and the rule from
    2026-10-07 says an unwritten claim does not count.
    """
    state = rec.get("state")
    if state == "accomplished":
        return "A"
    if state == "rejected":
        return "R"
    if state == "postponed" and (rec.get("reason") or "").strip():
        return "P"
    return "W"


def is_exempt(rec: dict) -> bool:
    """True only if the item itself says why it needs no review (so it counts as N, not V).

    The default is V. An exemption nobody wrote down is a self-granted pass, and a self-granted
    pass is how a letter turns into a dumping ground — the exact failure the human diagnosed in P.
    """
    return bool((rec.get("no_review_reason") or "").strip())


def counts(items: dict[str, dict], hours: int | None = None) -> dict:
    """The six groups, split by amigo and by internal/external. `hours=None` is lifetime.

    Returns one blank() per letter plus `items` (the rows in the window) and `decisions` (how many
    items left W in the window — a written decision, whatever letter it landed in). `decisions` is
    what makes Δ(V−W) derivable: each decision takes exactly one item out of waiting, so
    Δ(V−W) = decisions and ΔW = filed − decisions.
    """
    cutoff = None
    if hours:
        cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours))

    def in_window(stamp: str | None) -> bool:
        if cutoff is None:
            return bool(stamp)
        if not stamp:
            return False
        try:
            when = dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return False
        return when >= cutoff

    rows = [rec for rec in items.values() if in_window(rec.get("filed_utc"))]

    def blank() -> dict:
        return {"total": 0, "internal": 0, "external": 0, "by_amigo": {}}

    out = {g: blank() for g in ("N", "V", "A", "P", "W", "R")}
    out["A"]["by_review"] = 0
    out["A"]["by_gate"] = 0
    out["decisions"] = 0
    out["items"] = rows

    def add(letter: str, who: str, scope: str) -> None:
        out[letter]["total"] += 1
        out[letter]["internal" if scope == "internal" else "external"] += 1
        slot = out[letter]["by_amigo"].setdefault(who, {"total": 0, "internal": 0, "external": 0})
        slot["total"] += 1
        slot[scope] += 1

    for rec in rows:
        who = rec.get("amigo", "?")
        scope = rec.get("scope", "internal")
        # Two axes, not one: the review-needed axis (N/V) and the outcome axis (A/P/W/R). Every item
        # is exactly one of each, so N+V = A+P+W+R holds by construction.
        add("N" if is_exempt(rec) else "V", who, scope)
        letter = letter_for(rec)
        add(letter, who, scope)
        if letter == "A":
            out["A"]["by_review" if rec.get("reviewer") not in (None, "auto:land") else "by_gate"] += 1
        if in_window(rec.get("state_utc")):
            out["decisions"] += 1
    return out


def waiting(items: dict[str, dict], n: int = 5, not_mine: str = "") -> list[dict]:
    """The oldest items nobody has looked at, excluding the reviewer's own.

    This is the queue the review step reads. Oldest first, because the pile's age is the finding —
    and because a reviewer is far more likely to find the answer to "did this ever reach main?" in
    work from a week ago than in work from an hour ago, which the lander has not finished with yet.

    Excluding the reviewer's own items is the one rule that makes this a review rather than a
    rubber stamp: nobody signs off on their own work in this house. If a caller passes nothing, the
    exclusion is whatever it is told — the ledger does not guess who is looking.
    """
    rows = [r for r in items.values()
            if letter_for(r) == "W" and r.get("amigo") != not_mine]
    return sorted(rows, key=lambda r: r.get("filed_utc") or "")[:n]


def price_band(dir_: Path = BAND_DIR) -> tuple[list[str], str, Path]:
    """(band, price-date, file) from the newest dated band. No band is an error, not a default."""
    files = sorted(dir_.glob(BAND_GLOB))
    if not files:
        raise FileNotFoundError(f"no price band in {dir_}; run scripts/price_band.py --write")
    newest = files[-1]
    data = json.loads(newest.read_text(encoding="utf-8"))
    band = [a for a in data.get("band", []) if a in AMIGOS]
    if not band:
        raise ValueError(f"{newest.name} names none of the five amigos")
    return band, str(data.get("as_of", "?")), newest


def assign(path: Path = LEDGER, item_id: str = "", to: str = "", reason: str = "",
           kind: str = "name", by: str = "", force: bool = False) -> dict:
    """Put a name on a waiting item, with the one-line reason the rule requires.

    Refuses three things, all of them the point of the exercise: assigning an item to its author
    (nobody signs off on their own work in this house, and there is no exception for the
    best-suited amigo), assigning with no reason (a name without a reason is a mood, and moods
    drift toward whoever spoke last), and silently re-assigning an item (a draw that can re-roll is
    unowned with extra steps — moving a frozen draw needs `force` and a reason).
    """
    rec = load(path).get(item_id)
    if rec is None:
        raise KeyError(f"no such item: {item_id}")
    if letter_for(rec) != "W":
        raise ValueError(f"{item_id} is {letter_for(rec)}, not waiting — only a waiting item is "
                         f"assigned; it is not in anyone's queue")
    if to not in AMIGOS:
        raise ValueError(f"unknown amigo {to!r}; the five are {', '.join(AMIGOS)}")
    author = rec.get("amigo")
    if to == author:
        raise ValueError(f"{author} performed {item_id} and may not review it — the author is never "
                         f"the reviewer, whoever is best suited")
    current = rec.get("assigned_to")
    if current and current != to and not force:
        raise ValueError(f"{item_id} is already assigned to {current}; the draw is frozen. Moving it "
                         f"needs force and a reason — it must not drift on a later wake")
    if kind not in ("name", "draw"):
        raise ValueError(f"kind must be 'name' or 'draw', got {kind!r}")
    if not reason.strip():
        raise ValueError("an assignment needs its one-line reason: (a) says why this amigo, "
                         "(b) records the draw. Without it the map is not a rule")
    rec = dict(rec)
    rec.update(
        assigned_to=to,
        assign_kind=kind,
        assign_reason=reason.strip(),
        assigned_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        assigned_by=by or "?",
    )
    append([rec], path)
    return rec


def draw(path: Path = LEDGER, dir_: Path = BAND_DIR, by: str = "", only: str = "") -> list[dict]:
    """Branch (b): name every unassigned waiting item, at random among the dated cheap band.

    The pick is a function of the item's own id — uniform over the band, and settled the moment it
    is made, so it cannot re-roll. Anyone can re-derive it, which is what makes it auditable rather
    than merely recorded. Items whose whole band wrote them are left alone: that is a hole, and
    `holes()` reports it instead of the draw guessing.
    """
    band, as_of, band_file = price_band(dir_)
    rates = json.loads(band_file.read_text(encoding="utf-8")).get("rates_usd_per_million", {})
    out: list[dict] = []
    for rec in sorted(load(path).values(), key=lambda r: r.get("filed_utc") or ""):
        if letter_for(rec) != "W" or rec.get("assigned_to"):
            continue
        if only and rec["id"] != only:
            continue
        pool, widened = _pool(rec, band, rates)
        pick = pool[int(hashlib.sha256(rec["id"].encode()).hexdigest()[:8], 16) % len(pool)]
        out.append(assign(path=path, item_id=rec["id"], to=pick, kind="draw", by=by,
                          reason=f"drawn at random among the least expensive at {as_of} "
                                 f"(band: {', '.join(band)}; author excluded){widened}"))
    return out


def _pool(rec: dict, band: list[str], rates: dict) -> tuple[list[str], str]:
    """Who may look at this item: the band, minus its author — widened only if that is empty.

    The author exclusion is absolute, so with a two-member band (today's: desi and dmitri, the two
    DeepSeek bodies) a whole dimension of items has exactly one eligible reviewer and the choice
    stops being random. That is the rule working, not a bug. What *would* be a bug is the degenerate
    case: if the band ever narrows to the author alone, every item that amigo performed becomes a
    permanent hole and the queue is undrainable by construction. So the fallback widens to the
    cheapest amigo outside the band, and says so in the reason — a visible exception, never a silent
    one, because a silent widening would quietly overrule the cost rule the draw exists to obey.
    """
    pool = [a for a in band if a != rec.get("amigo")]
    if pool:
        return pool, ""
    rest = sorted((a for a in rates if a != rec.get("amigo")), key=lambda a: rates[a])
    if not rest:
        raise ValueError(f"no amigo can review {rec['id']}: {rec.get('amigo')} wrote it and the "
                         f"price table names no one else")
    return [rest[0]], (f" — widened past the band: the whole band wrote this item, so the cheapest "
                       f"amigo outside it ({rest[0]}) looks instead")


def assigned(items: dict[str, dict], who: str, n: int = 5) -> list[dict]:
    """The waiting items that carry this amigo's name — the queue a wake reads."""
    rows = [r for r in items.values()
            if letter_for(r) == "W" and r.get("assigned_to") == who]
    return sorted(rows, key=lambda r: r.get("filed_utc") or "")[:n]


def holes(items: dict[str, dict]) -> list[dict]:
    """Waiting items with no name on them. Not a queue — the escalation list."""
    return sorted([r for r in items.values()
                   if letter_for(r) == "W" and not r.get("assigned_to")],
                  key=lambda r: r.get("filed_utc") or "")


def blocker_of(rec: dict) -> str:
    """Why an item left W without being accomplished — the one line that names what stopped it."""
    return " ".join((rec.get("reason") or "").split())


def _names_work(reason: str) -> bool:
    """Does this reason name something that exists, rather than report a feeling?

    The `accomplished` exit is the one the human closed on 2026-10-09: a reviewer moves an item to A
    only by doing the work, so the reason has to point at the work — a run id, a file, a path, a
    URL. "looked fine" is a stamp with a friendly face.
    """
    text = reason or ""
    if ANY_RUN_ID_RE.search(text):
        return True
    if re.search(r"\b[\w.-]+\.(py|md|html|json|jsonl|txt|css|js)\b", text):
        return True
    return "/" in text or "http" in text


def _cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--collect", action="store_true", help="ingest new runs from all five bots")
    ap.add_argument("--backfill", action="store_true", help="ingest all history (idempotent)")
    ap.add_argument("--amigo", choices=AMIGOS)
    ap.add_argument("--review", metavar="ID")
    ap.add_argument("--state", choices=STATES)
    ap.add_argument("--reason", default="")
    ap.add_argument("--reviewer", default="human")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--next", type=int, metavar="N", default=0,
                    help="list the N oldest items waiting for review")
    ap.add_argument("--not-mine", default="",
                    help="with --next: skip this amigo's own items (nobody reviews their own)")
    ap.add_argument("--queue", choices=AMIGOS,
                    help="the waiting items that carry this amigo's name — what a wake reads")
    ap.add_argument("--assign", metavar="ID", help="put a name on one waiting item (branch a)")
    ap.add_argument("--to", choices=AMIGOS, help="with --assign: the amigo who will look")
    ap.add_argument("--draw", action="store_true",
                    help="name every unassigned waiting item by the cheap-and-random branch (b)")
    ap.add_argument("--only", metavar="ID", help="with --draw: just this one")
    ap.add_argument("--by", default="", help="who made the assignment (recorded)")
    ap.add_argument("--force", action="store_true", help="move an already-frozen assignment")
    ap.add_argument("--holes", action="store_true",
                    help="waiting items with no name on them — the escalation list")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.collect or args.backfill:
        n = collect(amigo=args.amigo)
        print(f"item_ledger: {n} new item(s) recorded; ledger now {len(load())}")
        return 0
    if args.review:
        rec = review(item_id=args.review, state=args.state or "", reason=args.reason,
                     reviewer=args.reviewer)
        print(f"item_ledger: {rec['id']} -> {rec['state']}: {rec['reason']}")
        return 0
    if args.assign or args.draw or args.queue or args.holes:
        items = load()
        if args.assign:
            rec = assign(item_id=args.assign, to=args.to or "", reason=args.reason,
                         by=args.by or args.reviewer, force=args.force)
            print(f"item_ledger: {rec['id']} -> {rec['assigned_to']} "
                  f"({rec['assign_kind']}): {rec['assign_reason']}")
            return 0
        if args.draw:
            made = draw(by=args.by or args.reviewer, only=args.only)
            print(f"item_ledger: {len(made)} item(s) named by draw")
            for rec in made[:5]:
                print(f"  {rec['id']} -> {rec['assigned_to']}")
            if len(made) > 5:
                print(f"  … and {len(made) - 5} more")
            left = holes(load())
            if left:
                print(f"item_ledger: {len(left)} item(s) still have no name — the band wrote them "
                      f"all, or they arrived after the draw. That is a hole, not a queue.")
            return 0
        if args.holes:
            left = holes(items)
            if not left:
                print("item_ledger: every waiting item carries a name — no holes")
                return 0
            print(f"item_ledger: {len(left)} waiting item(s) with NO name on them "
                  f"(the queue has a door and no assignee):")
            for rec in left[:10]:
                print(f"  {rec['id']}  {rec.get('filed_utc','?')[:10]}  {rec.get('amigo','?')}  "
                      f"{_short(rec.get('short_title') or rec.get('title','(no title)'))}")
            return 0
        rows = assigned(items, args.queue, args.next or 5)
        if not rows:
            left = holes(items)
            print(f"item_ledger: nothing is waiting on {args.queue}"
                  + (f" — but {len(left)} waiting item(s) carry no name at all, so nobody owns them"
                     if left else ", and every waiting item carries a name"))
            return 0
        print(f"{len(rows)} item(s) waiting on {args.queue}, oldest first:")
        for rec in rows:
            print(f"\n  {rec['id']}")
            print(f"    written by {rec.get('amigo','?')} · {rec.get('scope','?')} · "
                  f"filed {rec.get('filed_utc','?')}")
            print(f"    {_short(rec.get('short_title') or rec.get('title', '(no title)'))}")
            print(f"    yours because: {rec.get('assign_reason','?')}")
            print(f"    evidence: {rec.get('evidence','?')}")
            if rec.get("paths"):
                print(f"    paths: {', '.join(rec['paths'][:6])}")
        print("\nEvery exit leaves W into an existing queue, and no exit goes nowhere:")
        print("  accomplished — ONLY by doing the work yourself, in this wake; say what you did")
        print("  postponed / rejected — with a substantive reason; that reason IS the record")
        print("  python3 channels/item_ledger.py --review <id> --state accomplished|postponed|"
              "rejected \\\n      --reason \"why\" --reviewer " + args.queue)
        print("Moving an item to `accomplished` without doing it is a stamp, not a review.")
        return 0
    items = load()
    if args.next:
        rows = waiting(items, args.next, not_mine=args.not_mine)
        if not rows:
            print("item_ledger: nothing waiting for review")
            return 0
        print(f"{len(rows)} of the oldest items waiting for review"
              + (f" (excluding {args.not_mine}'s own, which {args.not_mine} may not review)"
                 if args.not_mine else "") + ":")
        for rec in rows:
            print(f"\n  {rec['id']}")
            print(f"    {rec.get('amigo','?')} · {rec.get('scope','?')} · "
                  f"filed {rec.get('filed_utc','?')}")
            print(f"    {_short(rec.get('short_title') or rec.get('title', '(no title)'))}")
            print(f"    evidence: {rec.get('evidence','?')}")
            if rec.get("paths"):
                print(f"    paths: {', '.join(rec['paths'][:6])}")
        print("\nTo record one verdict (the reason is mandatory — it is the whole record):")
        print("  python3 channels/item_ledger.py --review <id> --state accomplished|postponed|"
              "rejected \\\n      --reason \"why\" --reviewer <your name>")
        print("Read what the run produced before judging it. 'Not now, because X' is a "
              "postponement.\nNothing written down is not a review — it stays waiting.")
        return 0
    if args.list:
        for rec in sorted(items.values(), key=lambda r: r.get("filed_utc") or ""):
            print(f"  {rec.get('filed_utc')}  {rec.get('amigo'):7s} {rec.get('scope'):8s} "
                  f"{rec.get('state') or 'unreviewed':12s} {rec.get('title','')[:70]}")
        print(f"  ({len(items)} item(s))")
        return 0
    if args.summary:
        for label, hours in (("lifetime", None), (f"last {args.hours}h", args.hours)):
            c = counts(items, hours)
            left = c["N"]["total"] + c["V"]["total"]
            right = sum(c[g]["total"] for g in ("A", "P", "W", "R"))
            print(f"{label:10s} "
                  + "  ".join(f"{g}={c[g]['total']}" for g in ("N", "V", "A", "P", "W", "R"))
                  + ("  ✓ N+V=A+P+W+R" if left == right else "  ✗ identity broken")
                  + f"   (A: {c['A']['by_review']} reviewed / {c['A']['by_gate']} gate;"
                    f" decisions this window: {c['decisions']})")
        waiting_rows = [r for r in items.values() if letter_for(r) == "W"]
        named = collections.Counter(r.get("assigned_to") for r in waiting_rows
                                    if r.get("assigned_to"))
        print("W: " + (" · ".join(f"{w}={n}" for w, n in named.most_common())
                       if named else "no names at all — nothing is addressed to anybody")
              + f"   holes: {len(holes(items))}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
