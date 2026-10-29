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

Cheap is not the same as different (2026-10-18, the to-do list's own next item). The band exists
to bound cost, but on 2026-10-18 it holds two DeepSeek bodies — `desi` and `dmitri` — so every item
one of them wrote was drawn to the other: the same model, reading its own work, called a second
opinion. The rule "the author is never the reviewer" was being satisfied while the thing it is for
was not. So the draw now takes **one item in four outside the cheap band**, and excludes the
author's *architecture* as well as the author — a bounded share, because a review by a body that
costs 59–186× per token is worth having occasionally and not worth having always. The quarter is
decided from the item's id like everything else here, so the wide draw cannot re-roll either; and
`--cheap-only` restores the old behaviour for a bounded experiment, which is how the spend gets
measured rather than asserted.

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
    python3 channels/item_ledger.py --review <id> --state postponed --reason "why" \
        --reviewer <your name>          # required: the ledger will not guess who looked
    python3 channels/item_ledger.py --reconcile            # waiting rows whose run has since landed
    python3 channels/item_ledger.py --summary [--hours 24]
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"
# Repository-relative form, for comparing against the `paths` an item names.
LEDGER_PATH = "channels/items.jsonl"

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

# One drawn item in four goes outside the cheap band, to a body that is not the author's own
# architecture. A quarter is a bound on the spend, not a sample size: three cheap reviews pay for
# one expensive one, and the expensive one is the only one that can say "this does not reproduce".
WIDE_SHARE = 4

RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}$")
ANY_RUN_ID_RE = re.compile(r"\b(\d{8}T\d{6}Z-[0-9a-f]{8})\b")
# A run id may be written with a platform prefix. Codex records its rows as
# `codex-20261016T200444Z-14786fb8` (`scripts/record_codex_wake.py`), while the landing log names the
# bare id — `ANY_RUN_ID_RE` pulls the `20261016T200444Z-14786fb8` token out of the subject
# `land(wake): Codex work from run codex-…`. So matching a row's id against the land log has to strip
# the prefix, or a Codex run whose work is already on main sits in W for ever and surfaces as an item
# nobody owns. Measured 2026-10-16: the single `--holes` row was exactly this — Tarik's recovered
# conflict guard, on main since commit cc47d39d, still waiting because its id kept the prefix.
PREFIXED_RUN_ID_RE = re.compile(r"^[a-z][a-z0-9]*-(\d{8}T\d{6}Z-[0-9a-f]{8})$")


def canonical_run_id(run_id: str) -> str:
    """`codex-20261016T200444Z-14786fb8` -> `20261016T200444Z-14786fb8`; anything else unchanged."""
    match = PREFIXED_RUN_ID_RE.match(run_id or "")
    return match.group(1) if match else (run_id or "")
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
_INTENT_RE = re.compile(
    r"^(?:intend(?:ing)?\b|start(?:ing|ed)?\b|i will\b|i intend(?:ed)?\b|i'm going to\b|"
    r"i am going to\b|plan(?:ning)?\b|area this wake\b|"
    r"chose item\b|wake\b\s*[—:-])", re.I)
# The rest of a report's furniture, which is not the work either: the LAND line is addressed to the
# lander rather than to a reader, and the progress markers are what a run writes *before* it has
# anything finished to report ("Done so far: …", "In progress: …").
_FURNITURE_RE = re.compile(
    r"^(?:land(?:pre)?\b|done so far\b|in progress\b|so far\b|progress\b\s*:|area\b\s*:|"
    r"intent\b\s*:)", re.I)
_MARKUP_START = "#-*|>"


def _is_furniture(line: str) -> bool:
    return bool(_INTENT_RE.match(line) or _FURNITURE_RE.match(line))


# A wrap is not a title. Added 2026-10-17, from Dmitri's measurement in
# `channels/reports/2026-10-16-dmitri-the-ledger-titles-a-wrapped-report-with-a-fragment.md`, which
# found two faults in one function and left the second one to its owner (this file):
#   A. `best_title()` skipped the labelled *line*, not the labelled *sentence*, so when the label
#      wrapped, the continuation was filed as the title — run `20261015T170413Z-562d5e04` went into
#      the ledger as "were introspection/item 11 (10-13, 10-14); the one before that was music/item
#      26 (10-12)."
#   B. The unit was a line, so **any** content sentence that wrapped was cut at the wrap — run
#      `20261007T164305Z-b8d58b3c` titled as "The last two wakes were the disease-screen instrument
#      and the creek-water drinking guide, so this is a", and `--next` then printed 60 characters of
#      it.
# The decision the report asked for is B: a title is the first **sentence** of the first content
# block, joined across its wrap, not the first line. Measured before and after on every report on
# disk: 11 of 655 changed title, and each change replaced a fragment with the sentence it came from.
_TERMINAL_RE = re.compile(r"""[.!?]["')\]]?$""")


def _skip_label(lines: list[str], i: int, skip) -> int:
    """Advance past the label at `i` and past the lines that are its wrap (a wrap does not end)."""
    i += 1
    while i < len(lines) and not _TERMINAL_RE.search(lines[i - 1]):
        nxt = lines[i]
        if nxt[:1] in _MARKUP_START or skip(nxt):   # a heading or the next label, not a wrap
            break
        i += 1
    return i


def _title_at(lines: list[str], i: int, limit: int) -> str:
    """The first sentence from line `i`, joined across its wrap, cut at `limit`."""
    out = lines[i]
    j = i
    while (not _TERMINAL_RE.search(out) and j + 1 < len(lines) and len(out) < limit
           and not _is_furniture(lines[j + 1]) and lines[j + 1][:1] not in _MARKUP_START):
        j += 1
        out = f"{out} {lines[j]}"
    # A title is a sentence, and a *useful* one: a short opener ("Done. Then …", "I have just
    # started this wake.") is no title at all, so sentences accumulate until there is enough of one
    # to name the work — TITLE_SHOWN, the width the daily report and `--next` print — and stop
    # there, which keeps the title to the first informative sentence and not the whole report.
    title = ""
    for part in re.split(r"(?<=[.!?])\s+", out):
        title = f"{title} {part}".strip() if title else part
        if len(title) >= TITLE_SHOWN:
            break
    if len(title) > limit:                       # cut on a word, never mid-word
        title = title[:limit].rsplit(" ", 1)[0] or title[:limit]
    return title


def _title_with(lines: list[str], skip, limit: int) -> str:
    i = 0
    while i < len(lines):
        if skip(lines[i]):
            i = _skip_label(lines, i, skip)
            continue
        if len(lines[i]) >= 25:                  # a title, not a heading fragment
            return _title_at(lines, i, limit)
        i += 1
    return ""


def best_title(text: str, limit: int = TITLE_MAX) -> str:
    """The report's own one-sentence summary of the work — never its intent, never a wrap.

    Two passes: the first skips intent, LAND and progress furniture; the second skips only the
    intent labels, so a report whose *only* prose is a LAND or progress line still lends its title
    rather than falling back to its opening line. A report that is nothing but intent is quoted
    rather than invented, as before.
    """
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    return (_title_with(lines, _is_furniture, limit)
            or _title_with(lines, lambda ln: bool(_INTENT_RE.match(ln)), limit)
            or (lines[0][:limit] if lines else "(no report)"))


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


def is_generated_path(path: str, repo: Path = REPO) -> bool:
    """True if the repo file is a generated index — its own header says GENERATED and DO NOT EDIT.

    A run whose *only* changed paths are generated indexes performed nothing a reviewer can accept:
    the generator owns those files, a hand-edit to them is overwritten on the next rebuild, and main
    never carries it. Filing such a run into W asks a reviewer to write the same sentence every time,
    which is how a queue stops being opened. Measured 2026-10-11 (`channels/reports/
    2026-10-11-why-w-does-not-drain.md`, cause 3): 51 waiting items of this class, one path-signature
    repeated seven times. A path that does not exist is not generated — a run that adds a real file
    stays reviewable.
    """
    try:
        head = (repo / path).read_text(encoding="utf-8", errors="replace").splitlines()[:5]
    except OSError:
        return False
    text = "\n".join(head).upper()
    return "GENERATED" in text and "DO NOT EDIT" in text


def run_to_items(amigo: str, run_dir: Path, repo: Path = REPO) -> list[dict]:
    """The items a single wake performed. Empty when the run changed nothing reviewable."""
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
    # A run whose only changed paths are generated indexes is not an item, for the same reason a
    # run that changed nothing is not one: there is no reviewable work in it. A wake that declared
    # its own ITEM lines is still believed over the derivation.
    if not declared and all(is_generated_path(p, repo) for p in changed):
        return []
    run_id = data.get("run_id") or run_dir.name
    canonical = canonical_run_id(run_id)
    filed = parse_run_time(canonical) if RUN_ID_RE.match(canonical) else None
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


VERDICT_KEYS = ("state", "state_utc", "reason", "reviewer")


_FRACTION = re.compile(r"\.(\d+)")


def parse_iso_aware(value: str) -> dt.datetime:
    """`fromisoformat` for an ISO stamp, on this machine's Python as well as a newer one.

    Two things `datetime.fromisoformat` will not take before Python 3.11, both of which this
    repository's own tooling produces:

      * a trailing `Z`, which every other module here patches by hand before parsing;
      * a fractional second that is not exactly three or six digits — `.5` and `.50` raise
        `ValueError: Invalid isoformat string`, so an aware, valid, perfectly ordinary stamp is
        rejected. Measured 2026-10-29 on Python 3.9.6, which is the interpreter the landing gate
        and the suite census both use.

    A stamp with no fraction, three digits or six digits is passed through untouched; anything
    else is padded (or cut) to six digits, which is microsecond precision and loses nothing that
    a caller could have meant.
    """
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    match = _FRACTION.search(text)
    if match and len(match.group(1)) != 6:
        digits = match.group(1)[:6].ljust(6, "0")
        text = text[: match.start()] + "." + digits + text[match.end() :]
    return dt.datetime.fromisoformat(text)


def verdict_stamp(rec: dict) -> str:
    """Comparable aware-UTC verdict time, or empty for an unstamped decision.

    `state_utc` only. It deliberately does not fall back to `filed_utc` the way
    `scripts/ledger_row_recovery._stamp` does: a row's filing time is when the work happened, not
    when somebody judged it, and mixing the two makes "older" mean two different things in two
    readers. A row with a state and no `state_utc` is therefore *not comparable* and loses the
    protection below rather than being guessed at — measured 2026-10-27, no such row exists.
    """
    value = rec.get("state_utc")
    if not rec.get("state") or value in (None, ""):
        return ""
    if not isinstance(value, str):
        raise ValueError("state_utc must be an aware ISO timestamp")
    try:
        stamp = parse_iso_aware(value)
    except ValueError:
        raise ValueError("state_utc must be an aware ISO timestamp") from None
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("state_utc must be an aware ISO timestamp")
    # Fixed precision makes lexical comparison valid for offsets and fractional seconds.
    return stamp.astimezone(dt.timezone.utc).isoformat(timespec="microseconds")


def load(path: Path = LEDGER) -> dict[str, dict]:
    """Every item, with later lines overriding earlier ones. A corrupt line is skipped loudly.

    One exception, added 2026-10-25: a later line that says nothing about the verdict cannot
    erase one. `assign()` and `review()` both append a *whole record* rather than a diff, so a
    row written by a process that had not seen an earlier verdict is a snapshot of the record as
    that process found it — verdict fields included, and `None` if it never saw them. When the
    two histories meet in one file the snapshot sorts later and silently reopens the item.

    Measured, not hypothesised: three of my own verdicts (state `postponed`, `state_utc`
    2026-10-25T03:25:36Z, reviewer desi) were re-filed for review at 2026-10-25T11:45:06Z as
    unowned waiting items with `state: None`, and the queue handed them back to the same reviewer
    three hours after the reasons were written. Five consecutive wakes then "worked the queue"
    and cleared nothing visible, which is the same shape as the vulvodynia loop, arriving through
    the merge instead of the to-do list.

    So: a row may change a verdict (a later review wins), but a row that omits it inherits it.
    Nothing in the ledger reopens an item; a second review is an explicit new state, not a None.

    Second exception, added 2026-10-27: **line order is not time order.** The file is merged from
    several checkouts, so a row can be appended *after* a decision it predates — a re-collection
    that reproduced an old snapshot, or a patch applied out of order. When that happens the last
    line carries an older `state_utc` than the record already holds, and the 10-25 rule above does
    not save it: both rows have a state, so nothing is inherited and the older decision wins on
    position alone. Measured on the real ledger this morning (3,281 rows for 778 items): 9 items
    were showing a reason written at 09:21Z while the reason written at 15:23Z — and, for three of
    them, at 2026-10-25 — was nowhere in the leading record. Both rows said `postponed`, so no
    count was wrong; the *reason* was, and the reason is the whole record.

    So the rule is now the one `scripts/ledger_row_recovery` has enforced in its own reader since
    2026-10-14: newer must not be overwritten by older. A row whose verdict predates the record's
    keeps its own non-verdict fields (paths, title, assignment) and inherits the newer verdict,
    naming the stamp it inherited from — the recovery path and the read path finally agree.
    """
    items: dict[str, dict] = {}
    if not path.exists():
        return items
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            prev = items.get(rec["id"])
            if prev is not None and prev.get("state") and not rec.get("state"):
                for key in VERDICT_KEYS:
                    if not rec.get(key):
                        rec[key] = prev.get(key)
            elif prev is not None and verdict_stamp(prev) and verdict_stamp(rec) \
                    and verdict_stamp(rec) < verdict_stamp(prev):
                for key in VERDICT_KEYS:
                    rec[key] = prev.get(key)
                rec["verdict_kept_from"] = prev.get("state_utc")
            items[rec["id"]] = rec
        except (ValueError, KeyError):
            print(f"item_ledger: skipping unreadable line {lineno}", file=sys.stderr)
    return items


def duplicates(path: Path = LEDGER) -> dict:
    """How much of the ledger is restatement, and whether any row walks a verdict backwards.

    Append-only is the right shape for a file five processes write — a row cannot be half-written
    into a plausible lie — but it has a cost nothing was counting. `append()` writes a *whole
    record*, not a diff, so every assignment, every reconcile and every review copies the item
    again: measured 2026-10-27, 778 items in 3,281 rows, 2,503 of them restatement (76% of a 3 MB
    file), every item repeated at least three times and no two copies identical. That is the shape
    the human's rule forbids rather than the volume: a record that restates itself is a record
    whose last line can disagree with its own history, and "which copy is the item" then depends on
    the reader.

    Two readers of this file exist and they disagreed until today. `scripts/ledger_row_recovery`
    has refused to append a row older than the ledger's own line since 2026-10-14; `load()`, which
    every queue in the commons reads through, took the last line whatever its stamp. `backdated`
    below is that disagreement, counted: ids whose final row carries an older `state_utc` than a
    row above it. `held` is the subset where a *verdict* would have changed — the ones the guard
    added to `load()` on 2026-10-27 is holding to the newer decision.

    A census, not a gate. Redundancy is how this format works, so it must not fail a build; a
    `--duplicates` that went red every day would be turned off within a week, which is how the
    generated-index check failed for months.
    """
    rows = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    by_id: dict[str, list[dict]] = collections.defaultdict(list)
    total = 0
    for line in rows:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            by_id[rec["id"]].append(rec)
            total += 1
        except (ValueError, KeyError):
            continue
    backdated: list[str] = []
    held: list[str] = []
    disagree_state: list[str] = []
    for item_id, recs in by_id.items():
        stated = [r for r in recs if verdict_stamp(r)]
        if len({r.get("state") for r in stated}) > 1:
            disagree_state.append(item_id)
        if len(stated) < 2:
            continue
        newest = max(stated, key=verdict_stamp)
        last = stated[-1]
        if verdict_stamp(last) != verdict_stamp(newest):
            backdated.append(item_id)
            if (last.get("state"), last.get("reason"), last.get("reviewer")) != \
                    (newest.get("state"), newest.get("reason"), newest.get("reviewer")):
                held.append(item_id)
    return {
        "rows": total,
        "items": len(by_id),
        "redundant": total - len(by_id),
        "copies": collections.Counter(len(v) for v in by_id.values()),
        "backdated": sorted(backdated),
        "held": sorted(held),
        "disagree_state": sorted(disagree_state),
    }


@contextlib.contextmanager
def _append_lock(path: Path):
    """One appender at a time. The ledger is the commons' only write-hot file.

    Two writers appending at once cannot corrupt a row here — each write is a single small
    ``write()`` under the same append file — but the readers between them can see a half-written
    line, and `load()` skips unreadable lines, so a torn row disappears rather than failing loudly.
    Cheap to prevent: flock on a file inside .git (which can never make the tree dirty), or in the
    temp directory when this is not a checkout (a wake's clone, a test fixture).
    """
    git_dir = path.parent.parent / ".git"
    lock_dir = git_dir if git_dir.is_dir() else Path(tempfile.gettempdir())
    lock_path = lock_dir / "symposium-ledger.lock"
    try:
        fh = lock_path.open("a+")
    except OSError:
        yield                          # a lock that cannot be taken must not stop the write
        return
    try:
        deadline = time.monotonic() + 10.0
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    break              # an append is smaller than the risk of refusing it
                time.sleep(0.05)
        try:
            yield
        finally:
            try:
                fcntl.flock(fh, fcntl.LOCK_UN)
            except OSError:
                pass
    finally:
        fh.close()


DECISION_FIELDS = ("state", "state_utc", "reason", "reviewer")


def _keep_decisions(records: list[dict], path: Path = LEDGER) -> list[dict]:
    """An append may add to an item; it may not un-decide it.

    Found 2026-10-25: 25 items showed a row with no state sitting between two closures — the item
    read as "waiting" to anything that looked at the last line, and only the reconcile two seconds
    later put the decision back. On a day when the reconcile did not run (10-21, 10-24) those items
    simply stayed in W, which is one of the ways the review queue appeared to grow while reviewers
    were working. Whatever wrote them, the rule that makes it harmless is here rather than in each
    writer: a later row that carries no state inherits the decision the record already has, and says
    which row it inherited it from. Silence is not a reversal.
    """
    known = load(path)
    out = []
    for rec in records:
        verdict_stamp(rec)  # validate supplied decision times before any batch bytes are written
        old = known.get(rec.get("id"))
        if old and old.get("state") and not rec.get("state"):
            rec = dict(rec)
            for field in DECISION_FIELDS:
                if not rec.get(field):
                    rec[field] = old.get(field)
            rec["decision_preserved_from"] = old.get("state_utc")
        elif old and verdict_stamp(old) and verdict_stamp(rec) \
                and verdict_stamp(rec) < verdict_stamp(old):
            # Appending an older decision than the one already on file is a regression, whether it
            # arrived as a stale snapshot or from a patch applied out of order. Refused at the
            # write the way `load()` refuses it at the read, so the file stops accumulating rows
            # that contradict the record. Same rule as `scripts/ledger_row_recovery` (2026-10-14).
            rec = dict(rec)
            for field in DECISION_FIELDS:
                rec[field] = old.get(field)
            rec["verdict_kept_from"] = old.get("state_utc")
        out.append(rec)
        # Later records in this append see earlier decisions from the same batch.
        known[rec["id"]] = rec
    return out


def append(records: list[dict], path: Path = LEDGER) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with _append_lock(path):
        # Read the decision snapshot after entering the writer lock, not before it.
        records = _keep_decisions(records, path)
        with path.open("a", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")


def is_native_codex(rec: dict) -> bool:
    """Native app publication is not evidence that the private Goose gate ran."""
    return (rec.get("platform") == "codex" or rec.get("source") == "codex"
            or str(rec.get("id", "")).startswith("codex-"))


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
                item["state"] = ("accomplished" if not is_native_codex(item)
                                 and canonical_run_id(item["id"]) in landed else None)
                item["state_utc"] = item["filed_utc"] if item["state"] else None
                item["reason"] = ("landed on main (lander's test gate passed)"
                                  if item["state"] else None)
                item["reviewer"] = "auto:land" if item["state"] else None
                fresh.append(item)
                known[item["id"]] = item
    append(fresh, path)
    # 2026-10-10: a new item arrives with nobody's name on it, and an unowned item is a hole the
    # moment it is filed — 26 accumulated overnight before anyone noticed. Naming happens here,
    # once, at the moment of filing: the draw's branch (b), deterministic by item id, so re-running
    # collect never re-rolls it. A wake can still move it with force and a reason when one amigo is
    # plainly best suited; that is branch (a), and it is a judgement, so it is not made here.
    if fresh:
        try:
            named = draw(path=path, by="collect")
            if named:
                print(f"item_ledger: {len(named)} new item(s) named by the draw as they were filed")
        except (FileNotFoundError, ValueError) as exc:
            print(f"item_ledger: WARNING — {len(fresh)} new item(s) filed with no name ({exc}); "
                  f"they are holes until `--draw` runs")
    # Rows filed before their run landed would otherwise sit in W for ever; re-check them (2026-10-10).
    reconcile_landed(path, landed=landed)
    # The landing gate and the path check close items without a reader. That used to leave them in
    # no queue at all — 252 of them by 2026-10-22 — because `--queue` sees only W and the reading
    # queue had to be remembered and run by hand. Naming them here, at the moment they are closed,
    # is the routing fix: an unread item is in somebody's queue the same second it is delivered,
    # and the balance between inflow and reading stops depending on anybody remembering.
    try:
        pending = [r for r in load(path).values()
                   if is_unread(r) and not r.get("reading_assigned_to")]
        if pending:
            named = name_unread(path=path, by="collect")
            print(f"item_ledger: {len(named)} machine-closed-but-unread item(s) named for "
                  f"reading (delivered is not read)")
    except (OSError, ValueError) as exc:
        print(f"item_ledger: WARNING — {exc}; the unread pile is unnamed until "
              f"`--name-unread` runs")
    return len(fresh)


def reconcile_landed(path: Path = LEDGER, repo: Path = REPO, landed: set[str] | None = None) -> list[dict]:
    """Mark still-waiting items whose run has since landed as accomplished (auto:land).

    `collect` sets the state once, when a row is first filed, from the land log as it stood *then*.
    But the lander runs after the wake: a run collected before its own `land(wake): work from run
    <id>` commit appears is keyed by run id and never revisited, so it stays `waiting` for ever and
    the queue the review step reads slowly fills with work that is already on main. Measured
    2026-10-10: nine such rows, and the count grows with every wake — the exact "recompute what is
    already done" loop, arriving through the ledger instead of the to-do list.

    Only rows still in W are touched: a reviewer's decision (accomplished/postponed/rejected) is a
    person's judgement and is never overwritten by the lander's.

    Native Codex publications use the same delivery stamp but are pushed directly through GitHub,
    without the private Goose lander's test gate. Keep those items waiting rather than claiming
    that gate passed. Their delivery ids still belong in landed_run_ids and the delivery clock.
    """
    if landed is None:
        landed = landed_run_ids(repo)
    items = load(path)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates = []
    for rec in items.values():
        if is_native_codex(rec):
            continue
        if letter_for(rec) != "W" or canonical_run_id(rec.get("id")) not in landed:
            continue
        upd = dict(rec)
        upd.update(state="accomplished", state_utc=now,
                   reason="landed on main (lander's test gate passed)",
                   reviewer="auto:land")
        updates.append(upd)
    if updates:
        append(updates, path)
    return updates


def reconcile_paths(path: Path = LEDGER, repo: Path = REPO, reviewer: str = "",
                    scope: str = "", postpone_absent: bool = False,
                    skipped: list | None = None,
                    self_referential: list | None = None) -> list[dict]:
    """Close waiting items whose named paths already exist on main (auto:path).

    `reconcile_landed` keys on the item's *own* run id, so a wake's work that landed under a
    recovery run — or a wake whose own landing hit a conflict — stays waiting for ever. Measured
    2026-10-13 (`channels/reports/2026-10-13-dmitri-review-drain.md`, residual 2): of 137 items
    waiting on dmitri, 64 named only paths already present on main and *none* of the 118
    land-stamp run ids matched them. The drain closed those 64 by hand — checking each path
    against `main` — and its own landing then hit a conflict, so the rows came straight back.

    That is a reviewer re-doing, every wake, a check a machine can do once: a run's work reached
    main if and only if every path it names is in the checkout. This function does that check and
    leaves the terminal state the rule requires, so the hand-drain is not repeated.

    Only rows still in W are touched; a reviewer's decision is never overwritten. `scope` limits
    the pass to the items assigned to one amigo, so a reviewer closes their own queue and not
    somebody else's. `postpone_absent` also moves items naming paths absent from this checkout to
    `postponed`, with the 2026-09-23 reason (a path that never reached main is a *delivery state*,
    not missing work); without it those rows stay in W, because "not here yet" is not a decision.

    A *named request* (`assign_kind == "name"`: one amigo wrote "this one is plainly yours, and here
    is why") is never closed here, however many of its paths are present, and is appended to
    `skipped` when a list is passed in. For a drawn row the paths are the run's own output, so
    "every path is on main" answers the only question the ledger asked — did this work arrive. For
    a named row the paths are the *subject* the named amigo was asked to look at: the answer is the
    reviewer's verdict, and the subject being present is the premise of the question, not the
    answer. Closing on presence writes `accomplished` over a review nobody did — the stamp the
    human forbade on 2026-10-09, produced this time by a machine checking a file. Measured
    2026-10-21 (Desi, run `20261021T051359Z-547c2e61`): of 20 rows in W, 9 named only paths already
    present, and 7 of those 9 were named requests. Her fix never reached main; measured again
    2026-10-23 (Dmitri): 88 of 1,101 rows carry `assign_kind == "name"`, so the passing guard is
    still the difference between a verdict and a stamp on a standing share of the queue.
    """
    items = load(path)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates = []
    for rec in items.values():
        if letter_for(rec) != "W":
            continue
        if scope and rec.get("assigned_to") != scope:
            continue
        if rec.get("assign_kind") == "name":
            if skipped is not None:
                skipped.append(rec)
            continue
        paths = [p for p in (rec.get("paths") or []) if isinstance(p, str)]
        if not paths:
            continue
        if all(p == LEDGER_PATH for p in paths):
            # Every wake in the commons appends to the ledger, so "the ledger is on main" is
            # guaranteed true and says nothing about the work: an item whose *only* artefact is a
            # row it wrote in this file can be judged only by reading the row. Measured 2026-10-27
            # (Desi): two Gemini items had been closed `accomplished` on the reason "every path this
            # item names is present on main (channels/items.jsonl)" while neither run had written a
            # single verdict anywhere in that file. Leave them waiting and name them.
            if self_referential is not None:
                self_referential.append(rec)
            continue
        missing = [p for p in paths if not (repo / p).exists()]
        upd = dict(rec)
        if not missing:
            rest = f" and {len(paths) - 1} more" if len(paths) > 1 else ""
            upd.update(state="accomplished", state_utc=now, reviewer=reviewer or "auto:path",
                       reason=f"delivered: every path this item names is present on main "
                              f"({paths[0]}{rest})")
            updates.append(upd)
        elif postpone_absent:
            upd.update(state="postponed", state_utc=now, reviewer=reviewer or "auto:path",
                       reason=f"delivery state: {missing[0]} is named but not on main — under the "
                              f"2026-09-23 rule a missing path is work awaiting a closer, not "
                              f"work to redo")
            updates.append(upd)
    if updates:
        append(updates, path)
    return updates


def review(path: Path = LEDGER, item_id: str = "", state: str = "", reason: str = "",
           reviewer: str = "human") -> dict:
    """Move one item to a terminal state, with a reason. Postponed/rejected require one.

    `reviewer` is the *only* thing this row says that cannot be checked against the disk: a false
    name and a true one look identical once written. The library default is still "human" for the
    reason it always was (the attended case), but since 2026-10-15 the CLI refuses to let it fire —
    `--review` without `--reviewer` exits 2 instead of recording a person — so the value is always
    typed by whoever is looking.
    """
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


# Closed by a machine and never by a reader. `auto:land` is the Goose lander's test gate (the paths
# exist and the suite passed); `auto:path` is the delivery check (every named path is on main).
# Both are statements about the repository, not about the work, and neither is a review.
MACHINE_REVIEWERS = ("auto:land", "auto:path", "auto")


def letter_for(rec: dict) -> str:
    """Which of A/D/P/W/R an item sits in. W is the remainder, and deliberately so.

    W is the honest place for anything undecided: an item is *waiting for review* unless the
    artifact already carries a decision. `postponed` without a written reason reads as W too —
    a postponement nobody wrote down is not a decision, it is an absence, and the rule from
    2026-10-07 says an unwritten claim does not count.

    D is the 2026-10-25 addition and it exists because A was carrying two incompatible claims:
    "someone read this and kept it" and "a machine found its paths on main". Measured the hour it
    was added: of 492 accomplished items, 263 had never been read by a model (195 auto:land, 68
    auto:path), and of the 306 items ever machine-closed only 38 — 12% — were opened by a reviewer
    afterwards. A letter meaning both things cannot answer "is review keeping up"; it answers "is
    the lander working", which is a different question with a much better answer. That is how a
    54%-unread pile came to be reported, in good faith, as accomplished.

    Not the retired U (2026-10-06). U meant "performed, not yet reviewed", which duplicated W and
    he killed it for that reason. D has a state, a delivery and a reason on disk; what it lacks is
    a reader, and `is_unread()` is the only definition of its membership — the letter and the
    reading queue are the same predicate, so they cannot drift apart.
    """
    state = rec.get("state")
    if state == "accomplished":
        return "D" if (rec.get("reviewer") or "") in MACHINE_REVIEWERS else "A"
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

    out = {g: blank() for g in ("N", "V", "A", "P", "W", "R", "D")}
    out["A"]["by_review"] = 0
    out["D"]["by_gate"] = 0
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
            out["A"]["by_review"] += 1
        if letter == "D":
            out["D"]["by_gate"] += 1
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


def is_unread(rec: dict) -> bool:
    """Closed by a machine and never taken up by a model afterwards — the pile nobody queues.

    This is the 252-item pile on 2026-10-22: work that landed, was closed by the landing gate
    because its paths exist, and was then in no queue at all. `--queue` cannot see it (those items
    are not waiting) and `--draw` cannot see it either, which is why an instruction to "read one
    item from your review queue" can be obeyed perfectly and never touch it.
    """
    return (rec.get("state") == "accomplished"
            and (rec.get("reviewer") or "") in MACHINE_REVIEWERS)


# Wakes per day, measured 2026-10-22 from the tick-state/runs directories. A name is worth nothing
# on a body that does not wake, so the pile is shared by capacity rather than uniformly: flat, this
# put 115 of 252 items on claude and tarik, who wake once a day each and would carry them to the
# grave. Dated like the price band, and re-measured the same way — a change in how often we wake
# should change this table, not be discovered later.
WAKES_PER_DAY = {"desi": 12, "dmitri": 12, "gemini": 6, "claude": 1, "tarik": 3}
# Re-measured 2026-10-22 evening: tarik was 1 in the morning table and is 3 now that Tarik-app
# (the codex platform) runs several wakes a day; Tarik-goose has not woken since 2026-10-19, so
# the 3 are counted on the app. The morning table named 9 of the 252 pile items to tarik when
# it should have named about 22; `--rebalance-unread` corrects names made under a stale table.
#
# 2026-10-25: the numbers below are still right and this table is unchanged on purpose. Read by
# `scripts/wake_cadence.py --now 2026-10-25T11:25:40Z`: desi 11.9/day, gemini 5.9, claude 1.0,
# dmitri 11.7, tarik 2.6 — every weight within tolerance, so no weight is re-derived. The number
# was never the whole question. The same reading found tarik's *last evidence of a wake* 39.4
# hours old (codex filing `codex-20261023T200050Z-61cf96dc`; no goose run since
# `20261019T170221Z-c56a22e8`), i.e. 22 never-read items named to a body that had gone quiet for
# a day and a half, and nothing in the repository could notice — the table is dated, and a dated
# table says nothing about today. A weight is a capacity, not a heartbeat: it is the second number
# that needed measuring, and `wake_cadence.py --check` is what measures it. Changing tarik's weight
# to 1 would re-name items already assigned, which the frozen-draw rule forbids; so the table stands
# and the reading stands beside it.


def _capacity_pick(item_id: str, author: str | None) -> str:
    """A deterministic pick, weighted by how often each amigo actually wakes, author excluded."""
    pool = [(a, WAKES_PER_DAY.get(a, 1)) for a in AMIGOS if a != author] or \
           [(a, WAKES_PER_DAY.get(a, 1)) for a in AMIGOS]
    total = sum(w for _, w in pool)
    roll = int(hashlib.sha256(item_id.encode()).hexdigest()[:8], 16) % total
    for who, weight in pool:
        if roll < weight:
            return who
        roll -= weight
    return pool[-1][0]


def name_unread(path: Path = LEDGER, by: str = "", dry_run: bool = False) -> list[dict]:
    """Put a name on every never-read item, so that a wake can pick it up.

    The pick is a function of the id and the dated capacity table above — settled the moment it is
    made, re-derivable by anyone, author excluded. The assignment is recorded in its own fields
    (`reading_assigned_to`, ...) and does NOT change the item's state: the item is still
    accomplished, and what is being assigned is the reading, not the verdict.
    """
    out: list[dict] = []
    for rec in sorted(load(path).values(), key=lambda r: r.get("filed_utc") or ""):
        if not is_unread(rec) or rec.get("reading_assigned_to"):
            continue
        pick = _capacity_pick(rec["id"], rec.get("amigo"))
        row = dict(rec)
        row.update(
            reading_assigned_to=pick,
            reading_assigned_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            reading_assigned_by=by or "?",
            reading_assign_kind="draw",
            reading_assign_reason=(
                "named because it was closed by the landing gate and read by nobody: it was in no "
                "queue at all, which is how 252 items came to sit unread at once. Shared by capacity "
                "(wakes per day), not uniformly: a name on a body that does not wake is a name on "
                "nothing"),
        )
        out.append(row)
        if not dry_run:
            append([row], path)
    return out


def reading_assign(path: Path = LEDGER, item_id: str = "", to: str = "", reason: str = "",
                   by: str = "", force: bool = False) -> dict:
    """Branch (a) for the second queue: one amigo is plainly the right reader, and this says why.

    The reading queue was named by a capacity draw and could only ever be re-named by the draw
    (`--rebalance-unread`, and only when the *table* was measurably wrong). So the rule the review
    queue has carried since 2026-10-09 — "if one amigo is plainly best suited, assign that amigo and
    write one line saying why" — had no implementation on the half of the work that is already in
    the repository. Measured 2026-10-28: `scripts/landing_suite_check.py` and its 18 tests had been
    owed a non-author reading for four wakes while the draw had put it on an amigo carrying 74
    unread items, and there was no command that could move it to the amigo who owns gate tooling.

    The three refusals of `assign()` apply unchanged: the author is never the reader, a name with
    no reason is a mood, and a frozen name does not drift without `force` and a fresh reason. What
    is *not* changed is the item's verdict — it stays `accomplished`, because what is being named
    is the reading, not the outcome.
    """
    rec = load(path).get(item_id)
    if rec is None:
        raise KeyError(f"no such item: {item_id}")
    if not is_unread(rec):
        raise ValueError(f"{item_id} is not a never-read item: reading is assigned only to work the "
                         f"machine closed and no model has opened since")
    if to not in AMIGOS:
        raise ValueError(f"unknown amigo {to!r}; the five are {', '.join(AMIGOS)}")
    author = rec.get("amigo")
    if to == author:
        raise ValueError(f"{author} performed {item_id} and may not read it back as a review — the "
                         f"author is never the reviewer, whoever is best suited")
    current = rec.get("reading_assigned_to")
    if current and current != to and not force:
        raise ValueError(f"{item_id} is already named for reading by {current}; that name is frozen. "
                         f"Moving it needs force and a reason")
    if not reason.strip():
        raise ValueError("a reading assignment needs its one-line reason: (a) says why this amigo. "
                         "Without it the name is a mood, and moods drift to whoever spoke last")
    rec = dict(rec)
    rec.update(
        reading_assigned_to=to,
        reading_assigned_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        reading_assigned_by=by or "?",
        reading_assign_kind="name",
        reading_assign_reason=reason.strip(),
    )
    append([rec], path)
    return rec


def rebalance_unread(path: Path = LEDGER, by: str = "", dry_run: bool = False) -> list[dict]:
    """Re-name pile items whose name was made under a stale capacity table.

    A draw does not re-roll — that is the rule, and it is why a name means something. This is the
    one honest exception: the table the names were made from was *wrong*, measurably so (tarik woke
    three times a day, not once), and not one of the 252 had been opened yet. Re-deriving them
    against the corrected table before any work has been spent is cheaper than carrying a wrong
    distribution for months. It says so in the row, and it will not fire again for the same item
    unless the table changes again.
    """
    items = load(path)
    out: list[dict] = []
    for rec in sorted(items.values(), key=lambda r: r.get("filed_utc") or ""):
        if not is_unread(rec):
            continue
        current = rec.get("reading_assigned_to")
        if not current:
            continue
        if rec.get("reading_assign_kind") == "name":
            # A judgement is not a draw. A corrected capacity table is a good reason to re-roll a
            # name the table made, and no reason at all to overrule a wake that had a reason of its
            # own — same guard `reconcile_paths` applies to a named request.
            continue
        pick = _capacity_pick(rec["id"], rec.get("amigo"))
        if pick == current:
            continue
        row = dict(rec)
        row.update(
            reading_assigned_to=pick,
            reading_assigned_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            reading_assigned_by=by or "?",
            reading_assign_kind="draw",
            reading_assign_reason=(f"re-named from {current}: the capacity table it was named under "
                                   f"was stale (tarik wakes 3 times a day, not once); corrected "
                                   f"before any of these items was opened"),
        )
        out.append(row)
        if not dry_run:
            append([row], path)
    return out


def reading_queue(path: Path = LEDGER, who: str = "") -> list[dict]:
    """The never-read items that carry this amigo's name — the second queue."""
    items = load(path)
    out = []
    for rec in sorted(items.values(), key=lambda r: r.get("filed_utc") or ""):
        if not is_unread(rec):
            continue
        if who and rec.get("reading_assigned_to") != who:
            continue
        out.append(rec)
    return out


def architectures(dir_: Path = BAND_DIR, band_data: dict | None = None) -> dict[str, str]:
    """amigo -> architecture, from the band's own copy or the price table beside it.

    Never guessed. The band file carries the map (since 2026-10-18); an older band does not, and
    then the price table it was built from is the next source. If neither exists the map is empty
    and the wide draw stops claiming a different-architecture reader it has no evidence for — it
    falls back to the band and says so, because an unverified diversity claim is worse than a cheap
    review honestly labelled.
    """
    data = band_data
    if data is None:
        files = sorted(dir_.glob(BAND_GLOB))
        data = json.loads(files[-1].read_text(encoding="utf-8")) if files else {}
    carried = (data or {}).get("architectures")
    if isinstance(carried, dict) and carried:
        return {k: v for k, v in carried.items() if isinstance(v, str) and v}
    prices = dir_ / "model-prices.json"
    if prices.exists():
        try:
            rates = json.loads(prices.read_text(encoding="utf-8")).get("rates_usd_per_million") or {}
        except (OSError, ValueError):
            return {}
        return {who: e["architecture"] for who, e in rates.items()
                if isinstance(e, dict) and isinstance(e.get("architecture"), str)}
    return {}


def draw(path: Path = LEDGER, dir_: Path = BAND_DIR, by: str = "", only: str = "",
         cheap_only: bool = False) -> list[dict]:
    """Branch (b): name every unassigned waiting item, at random from the dated cheap band.

    The pick is a function of the item's own id — uniform over the pool, and settled the moment it
    is made, so it cannot re-roll. Anyone can re-derive it, which is what makes it auditable rather
    than merely recorded. One item in `WIDE_SHARE` is drawn outside the band instead, so that an
    item written inside the cheap band still gets read by a body of a different architecture;
    `cheap_only` turns that off for a measured experiment. Items whose whole band wrote them are
    left to `holes()` rather than guessed at.
    """
    band, as_of, band_file = price_band(dir_)
    data = json.loads(band_file.read_text(encoding="utf-8"))
    rates = data.get("rates_usd_per_million", {})
    arch = architectures(dir_, data)
    out: list[dict] = []
    for rec in sorted(load(path).values(), key=lambda r: r.get("filed_utc") or ""):
        if letter_for(rec) != "W" or rec.get("assigned_to"):
            continue
        if only and rec["id"] != only:
            continue
        digest = hashlib.sha256(rec["id"].encode()).hexdigest()
        wide = (not cheap_only) and int(digest[8:16], 16) % WIDE_SHARE == 0
        pool, branch, note = _pool(rec, band, rates, arch, wide=wide)
        pick = pool[int(digest[:8], 16) % len(pool)]
        head = ("drawn at random outside the cheap band"
                if branch == "wide" else
                f"drawn at random among the least expensive at {as_of}")
        out.append(assign(path=path, item_id=rec["id"], to=pick, kind="draw", by=by,
                          reason=f"{head} (band: {', '.join(band)} at {as_of}; "
                                 f"author excluded){note}"))
    return out


def _pool(rec: dict, band: list[str], rates: dict, arch: dict[str, str] | None = None,
          wide: bool = False) -> tuple[list[str], str, str]:
    """(who may look, which branch, the reason suffix) for one item.

    Cheap branch (three in four): the band, minus its author.

    Wide branch (one in four): outside the band entirely, minus the author and minus anyone who
    runs the author's own architecture. This is the failure the cheap branch cannot see: with a
    band of `desi` and `dmitri` — both DeepSeek — every Desi item went to Dmitri, so "the author is
    never the reviewer" held while the *point* of review (a reader who does not share the author's
    blind spots) did not. Where nobody outside the band runs a different architecture, it uses the
    widest pool it has and says exactly that. Where the map is *absent*, it still widens on price,
    but then it says the architecture is unrecorded instead of asserting the reader's model differs:
    a diversity claim nothing supports is worse than a cheap review honestly labelled, and that
    holds for the reason as much as for the pick (fixed 2026-10-19 — with an empty map the reason
    used to read "the band runs <author>'s own architecture" from no evidence at all;
    `tests/test_item_ledger_wide_branch.py` pins the honest wording).

    Degenerate case: if the band narrows to the author alone, the cheap branch widens to the
    cheapest amigo outside it — a visible exception, never a silent one, because a silent widening
    would quietly overrule the cost rule the draw exists to obey.
    """
    arch = arch or {}
    author = rec.get("amigo")
    if wide:
        outside = [a for a in sorted(rates) if a not in band and a != author]
        same = arch.get(author)
        different = [a for a in outside if not same or arch.get(a) != same]
        if different:
            why = (f"because the band runs {same}'s own architecture and a same-model reader "
                   f"cannot give this item a second opinion" if same else
                   f"but no architecture is recorded for {author or 'the author'}, so the pool was "
                   f"widened by price alone and this reason claims nothing about the reader's model")
            return different, "wide", (
                f" — wide draw, 1 item in {WIDE_SHARE}: read outside the cheap band on purpose, "
                f"{why}")
        if outside:
            return outside, "wide", (
                f" — wide draw, 1 item in {WIDE_SHARE}, but no body outside the band runs a "
                f"different architecture from {author}'s; the widest pool available was used rather "
                f"than quietly reusing the band")
    pool = [a for a in band if a != author]
    if pool:
        return pool, "cheap", ""
    rest = sorted((a for a in rates if a != author), key=lambda a: rates[a])
    if not rest:
        raise ValueError(f"no amigo can review {rec['id']}: {author} wrote it and the price table "
                         f"names no one else")
    return [rest[0]], "widened", (
        f" — widened past the band: the whole band wrote this item, so the cheapest amigo outside "
        f"it ({rest[0]}) looks instead")


def _named(items: dict[str, dict], who: str) -> list[dict]:
    """Every waiting item that carries this amigo's name, oldest first, uncapped."""
    rows = [r for r in items.values()
            if letter_for(r) == "W" and r.get("assigned_to") == who]
    return sorted(rows, key=lambda r: r.get("filed_utc") or "")


def assigned(items: dict[str, dict], who: str, n: int = 5) -> list[dict]:
    """The page of waiting items that carry this amigo's name — the queue a wake reads.

    The page is capped at `n`; the queue is not. `queue_size` is the other half of this answer,
    and the CLI prints both, because a page shown without its total is how a 39-item mandate
    reads as a five-item afternoon (measured 2026-10-10, re-measured 2026-10-14).
    """
    return _named(items, who)[:n]


def queue_size(items: dict[str, dict], who: str) -> int:
    """How many waiting items carry this amigo's name — the whole queue, not the page of five.

    This exists because `assigned()` truncates and the CLI printed only the page: it said
    "5 item(s) waiting on desi" while 39 did, so a wake read its own mandate as five jobs and
    never learned the rest existed. The count above a page must be the queue's, not the page's.
    """
    return len(_named(items, who))


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
    # No default. The default used to be the literal "human", which is true only for an attended
    # `--review`; every machine path (`--reconcile-paths`, `--draw`, `--assign`) inherited it and
    # wrote `reviewer: "human"` / `by: "human"` onto a row no human touched. Found 2026-10-15
    # (dmitri, run 20261015T190858Z-d8bfb421) on the three rows its own `--reconcile-paths` had just
    # closed; completed the same day (run 20261016T010912Z-20a94b65), which removed the last silent
    # fallback: `--review` now *requires* this flag rather than defaulting to "human". So no path in
    # this CLI can name a reviewer by omission, which is the only way the false stamp was reachable.
    ap.add_argument("--reviewer", default=None)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--reconcile", action="store_true",
                    help="move waiting items whose run has since landed to accomplished (auto:land)")
    ap.add_argument("--reconcile-paths", action="store_true",
                    help="close waiting items whose named paths are all present on main (auto:path)")
    ap.add_argument("--scope", choices=AMIGOS,
                    help="with --reconcile-paths: only the items assigned to this amigo")
    ap.add_argument("--postpone-absent", action="store_true",
                    help="with --reconcile-paths: also mark items naming absent paths postponed")
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
    ap.add_argument("--cheap-only", action="store_true",
                    help="with --draw: keep every draw inside the cheap band (no wide share)")
    ap.add_argument("--by", default="", help="who made the assignment (recorded)")
    ap.add_argument("--force", action="store_true", help="move an already-frozen assignment")
    ap.add_argument("--holes", action="store_true",
                    help="waiting items with no name on them — the escalation list")
    ap.add_argument("--name-unread", action="store_true",
                    help="put a name on every item the landing gate closed and nobody read — "
                         "the second queue, which nothing could see before 2026-10-22")
    ap.add_argument("--reading-queue", choices=AMIGOS,
                    help="the never-read items that carry this amigo's name")
    ap.add_argument("--rebalance-unread", action="store_true",
                    help="re-name never-read items whose name was made under a stale capacity table")
    ap.add_argument("--reading-assign", metavar="ID",
                    help="name one never-read item for a reader chosen by judgement (branch a), "
                         "with --to and --reason; the verdict is untouched")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --name-unread: say what would be named, change nothing")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.collect or args.backfill:
        n = collect(amigo=args.amigo)
        print(f"item_ledger: {n} new item(s) recorded; ledger now {len(load())}")
        return 0
    if args.review:
        # An unattributed review is the one row this ledger must never write. The default used to be
        # "human", so the single reviewer value a wake could reach *by omission* was a person who did
        # not look — the stamp the human forbade on 2026-10-09, and the one error the ledger cannot
        # detect after the fact, because a wrong name and a right one look identical on disk. Nothing
        # in the process says whether a person is at the keyboard, so the tool stops guessing: it
        # asks. Cost to the attended reviewer is six characters; cost of the guess was a false record.
        # Decided 2026-10-15 (dmitri, run 20261016T010912Z-20a94b65) as the residue the 10-15 wake
        # (run 20261015T190858Z-d8bfb421) left open: a wake that forgets must fail loudly, not sign
        # as a human.
        if not args.reviewer:
            print("item_ledger: --review needs --reviewer <who is looking>.\n"
                  "  The ledger will not guess. It used to write \"human\" here, which records a\n"
                  "  person as the reviewer of work no person looked at — the stamp the human\n"
                  "  forbade on 2026-10-09. Pass your own name, or `human` if you really are the\n"
                  "  person at the keyboard:\n"
                  "    python3 channels/item_ledger.py --review <id> --state <state> \\\n"
                  "        --reason \"why\" --reviewer human", file=sys.stderr)
            return 2
        rec = review(item_id=args.review, state=args.state or "", reason=args.reason,
                     reviewer=args.reviewer)
        print(f"item_ledger: {rec['id']} -> {rec['state']}: {rec['reason']}")
        return 0
    if args.reconcile:
        made = reconcile_landed()
        print(f"item_ledger: {len(made)} waiting item(s) reconciled — their run has landed on main")
        for rec in made[:10]:
            print(f"  {rec['id']}  {rec.get('amigo','?')}")
        return 0
    if args.reconcile_paths:
        skipped: list = []
        self_ref: list = []
        made = reconcile_paths(reviewer=args.reviewer, scope=args.scope or "",
                               postpone_absent=args.postpone_absent, skipped=skipped,
                               self_referential=self_ref)
        if self_ref:
            print(f"item_ledger: {len(self_ref)} item(s) left waiting — their only named path is "
                  f"the ledger itself, which every wake writes, so its presence cannot close them")
            for rec in self_ref[:10]:
                print(f"  {rec['id']}  {rec.get('amigo', '?')}")
        if skipped:
            print(f"item_ledger: {len(skipped)} named review request(s) left waiting — the paths "
                  f"they name are the subject, not the answer")
            for rec in skipped[:10]:
                print(f"  {rec['id']}  {rec.get('amigo', '?')} asked "
                      f"{rec.get('assigned_to', '?')}")
        done = [r for r in made if r["state"] == "accomplished"]
        post = [r for r in made if r["state"] == "postponed"]
        print(f"item_ledger: {len(done)} item(s) closed accomplished — every named path is on "
              f"main; {len(post)} postponed — delivery state")
        for rec in (done + post)[:10]:
            print(f"  {rec['id']}  {rec['state']}  {rec['reason'][:70]}")
        return 0
    if args.reading_assign:
        try:
            rec = reading_assign(item_id=args.reading_assign, to=args.to or "",
                                 reason=args.reason, by=args.by or args.reviewer or "",
                                 force=args.force)
        except (KeyError, ValueError) as exc:
            print(f"item_ledger: refused — {exc}")
            return 2
        print(f"item_ledger: {rec['id']} reading -> {rec['reading_assigned_to']} "
              f"({rec.get('reading_assign_kind')}): {rec.get('reading_assign_reason')}")
        return 0
    if args.name_unread or args.reading_queue or args.rebalance_unread:
        if args.rebalance_unread:
            rows = rebalance_unread(by=args.by or args.reviewer or "", dry_run=args.dry_run)
            verb = "would re-name" if args.dry_run else "re-named"
            print(f"item_ledger: {verb} {len(rows)} never-read item(s) against the current table")
            counts_by: dict[str, int] = {}
            for rec in rows:
                counts_by[rec["reading_assigned_to"]] = counts_by.get(rec["reading_assigned_to"], 0) + 1
            for who, n in sorted(counts_by.items()):
                print(f"  {who}: {n}")
            return 0
        if args.name_unread:
            rows = name_unread(by=args.by or args.reviewer or "", dry_run=args.dry_run)
            verb = "would name" if args.dry_run else "named"
            print(f"item_ledger: {verb} {len(rows)} never-read item(s)")
            counts_by: dict[str, int] = {}
            for rec in rows:
                counts_by[rec["reading_assigned_to"]] = counts_by.get(rec["reading_assigned_to"], 0) + 1
            for who, n in sorted(counts_by.items()):
                print(f"  {who}: {n}")
            return 0
        mine = reading_queue(who=args.reading_queue)
        print(f"item_ledger: {len(mine)} never-read item(s) carry {args.reading_queue}'s name. "
              f"These are in the repository already and nobody has checked them.")
        for rec in mine[:args.hours]:
            print(f"  {rec['id']}  by {rec.get('amigo','?'):8} filed {(rec.get('filed_utc') or '')[:10]}"
                  f"  {(rec.get('short_title') or rec.get('title') or '')[:60]}")
        if len(mine) > args.hours:
            print(f"  … and {len(mine) - args.hours} more")
        return 0
    if args.assign or args.draw or args.queue or args.holes:
        items = load()
        if args.assign:
            rec = assign(item_id=args.assign, to=args.to or "", reason=args.reason,
                         by=args.by or args.reviewer or "", force=args.force)
            print(f"item_ledger: {rec['id']} -> {rec['assigned_to']} "
                  f"({rec['assign_kind']}): {rec['assign_reason']}")
            return 0
        if args.draw:
            made = draw(by=args.by or args.reviewer or "", only=args.only,
                        cheap_only=args.cheap_only)
            print(f"item_ledger: {len(made)} item(s) named by draw")
            for rec in made[:5]:
                print(f"  {rec['id']} -> {rec['assigned_to']}")
            if len(made) > 5:
                print(f"  … and {len(made) - 5} more")
            left = holes(load())
            if left:
                print(f"item_ledger: {len(left)} item(s) still have no name — every amigo wrote them "
                      f"all, or they arrived after the draw. That is a hole, not a queue.")
            # 2026-10-17: Tarik's body claims one task from channels/tarik-goose-handoff.json and is
            # told that task is its whole scope, so a review assigned to him is invisible until it is
            # in that file. Run the adapter here rather than trusting a wake to remember: the place
            # that hands out the name is the place that must make the name reachable.
            if any(rec["assigned_to"] == "tarik" for rec in made):
                adapter = REPO / "scripts" / "queue_review_handoff.py"
                if adapter.is_file():
                    code = subprocess.call([sys.executable, str(adapter), "--write"])
                    print(f"item_ledger: queued Tarik's review(s) for his handoff harness "
                          f"(exit {code})")
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
        total = queue_size(items, args.queue)
        rest = f" (--next {total} to see the rest)" if total > len(rows) else ""
        print(f"{len(rows)} of {total} item(s) waiting on {args.queue}, oldest first{rest}:")
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
            right = sum(c[g]["total"] for g in ("A", "P", "W", "R", "D"))
            print(f"{label:10s} "
                  + "  ".join(f"{g}={c[g]['total']}" for g in ("N", "V", "A", "P", "W", "R", "D"))
                  + ("  ✓ N+V=A+D+P+W+R" if left == right else "  ✗ identity broken")
                  + f"   (A: {c['A']['by_review']} read by a model / D: {c['D']['total']} closed "
                    f"by a machine and unread; decisions this window: {c['decisions']})")
        waiting_rows = [r for r in items.values() if letter_for(r) == "W"]
        named = collections.Counter(r.get("assigned_to") for r in waiting_rows
                                    if r.get("assigned_to"))
        print("W: " + (" · ".join(f"{w}={n}" for w, n in named.most_common())
                       if named else "no names at all — nothing is addressed to anybody")
              + f"   holes: {len(holes(items))}")
        unread = [r for r in items.values() if letter_for(r) == "D"]
        if unread:
            oldest = min(unread, key=lambda r: r.get("filed_utc") or "")
            reading = collections.Counter(r.get("reading_assigned_to") for r in unread)
            print(f"D: {len(unread)} delivered-but-unread, oldest filed {oldest.get('filed_utc')}"
                  f"  ·  reading names: "
                  + (" · ".join(f"{w}={n}" for w, n in reading.most_common() if w)
                     if any(reading) else "none — this pile is in nobody's queue")
                  + f"  ·  unnamed: {reading.get(None, 0)}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
