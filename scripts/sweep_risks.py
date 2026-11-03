#!/usr/bin/env python3
"""sweep_risks.py — turn OPEN risks into daily work, so they actually get fixed.

The ledger makes risks visible but doesn't force action. This sweep, run each
cycle, reads OPEN risks and turns them into actionable tasks for their owner.
It is self-healing AND bounded, so it can run for a thousand years without the
live ledger growing without end:

1. RETIRES closed risks. Any risk marked Done/Closed is moved OUT of the live
   ledger (channels/risks.md) into the append-only archive, filed per year
   (channels/risk-archive/<year>.md). The live ledger therefore holds only OPEN
   risks (plus the rule preamble) and stays small no matter how much history
   accrues; the archive is the permanent institutional memory, filed by year so
   it stays navigable and is never discarded.
2. Reassigns stale risks (open > STALE_DAYS, owner not acting) to the master
   repair-amigo IN THE LEDGER, so nothing is orphaned waiting on a non-acting
   owner.
3. Regenerates channels/tasks.md from exactly the currently-OPEN risks, so the
   task list stays in sync with the ledger.

Writes to the task list and ledger (channels/*.md), NOT the email outbox, so
this never emails anyone and can't rearm a loop.
"""
import datetime
import os
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
CH = REPO / "channels"
RISKS = CH / "risks.md"
ARCHIVE_DIR = CH / "risk-archive"   # per-year append-only files inside this dir
TASKS = CH / "tasks.md"   # a task list the amigos read in context, NOT the email outbox

MASTER_REPAIR = "Desi (master repair-amigo)"
STALE_DAYS = 3            # a risk open past this, owner not acting -> reassign

# 2026-11-02 — THE SWEEP OWNS ONE BLOCK OF channels/tasks.md, NOT THE FILE.
#
# The old body rebuilt the whole file as `everything-before-"## Open Risks" + generated block`,
# which deletes every section below that heading on every run. Sections are exactly what the
# amigos and the human add there: the founder's "it is a numbers game" rule, the tribe-outreach
# plan, and three sections filed on 2026-11-02 all lived below it. And this script is not rare:
# `.github/scripts/poll_channels.py` runs it on every channel poll, ~12 times a day, and
# `channel-poll.yml` then stages all of `channels/`, commits "feat(channels): frequent poll" and, on
# a rejected push, rebases and retries — so the deletion arrived as an ordinary-looking commit with
# no conflict and no name against the act. Measured: 53,793 characters of the file (from character
# 75,739 to the end) were inside the region the sweep regenerated away.
#
# So it splices now, between the heading and the next level-2 heading, and never writes anything
# outside that span. `tests/test_sweep_risks_block.py` fails if a section after the block is ever
# lost again.
BLOCK_HEADING = "## Open Risks"
BEGIN_MARK = "<!-- sweep-risks:begin -->"
END_MARK = "<!-- sweep-risks:end -->"
HEADING = re.compile(r"^## Open Risks\b.*$", re.MULTILINE)
# What this script itself writes, so a migration can recognise where its own output ends.
GENERATED_ROW = re.compile(r"^- \[\d{4}-\d{2}-\d{2}\] \*\*R-[0-9]+\*\*")
GENERATED_NOTE = re.compile(r"^  (Fix, then mark Done in channels/risks\.md\.|OVERDUE — reassigned to you\.)")
PLACEHOLDER = "*(No open risks in ledger)*"


def split_block(raw: str) -> tuple[str, str, str]:
    """(before, block, after) around the region this script owns.

    The region is between BEGIN_MARK and END_MARK, on their own lines. `after` is everything the
    script has no business rewriting, which is the point: see the 2026-11-02 note above.

    A file with no markers is migrated by recognising the shape of this script's own output: the
    heading, then blank lines, the placeholder, and rows of the form `- [YYYY-MM-DD] **R-n** …`
    with their one-line note. The first line that is none of those ends the span — which is how a
    migration stops at the first task item somebody wrote underneath, instead of eating it.
    """
    # Anchored to the start of a line on purpose: the markers are quoted in prose all over the
    # record (this report included), and a substring search would pick the quotation instead of the
    # fence the first time somebody wrote the words above it.
    b = re.search(r"^" + re.escape(BEGIN_MARK) + r"[ \t]*$", raw, re.MULTILINE)
    e = re.search(r"^" + re.escape(END_MARK) + r"[ \t]*$", raw, re.MULTILINE) if b else None
    if b and e and e.start() > b.start():
        end = e.end()
        if raw[end:end + 1] == "\n":
            end += 1
        return raw[:b.start()], raw[b.start():end], raw[end:]
    m = HEADING.search(raw)
    if not m:
        return raw, "", ""
    keep = [raw[m.start():m.end()]]
    for line in raw[m.end():].splitlines(keepends=True):
        s = line.strip()
        if not s or s == PLACEHOLDER or GENERATED_ROW.match(line) or GENERATED_NOTE.match(line):
            keep.append(line)
        else:
            break
    span = "".join(keep)
    return raw[:m.start()], span, raw[m.start() + len(span):]


def _with_markers(before: str, body: str, after: str) -> str:
    """Assemble the file: the owned region fenced, everything else verbatim."""
    if before and not before.endswith("\n\n"):
        before = before.rstrip("\n") + "\n\n"
    if not body.endswith("\n"):
        body += "\n"
    if after and not after.startswith("\n"):
        after = "\n" + after
    return before + BEGIN_MARK + "\n" + body + END_MARK + "\n" + after


def _notice_displaced(old_block: str) -> None:
    """Say what is about to be replaced inside the fence, instead of dropping it quietly.

    The fence makes the sweep the owner of its region, which is the fix. It does not make the
    *loss* of something a person put there acceptable — so the loss is named, with a count and the
    first line, on the same principle as every other refusal in this repository: a silent deletion
    reads exactly like a deletion nobody minded.
    """
    keep = {PLACEHOLDER, BEGIN_MARK, END_MARK, ""}
    displaced = [l for l in (old_block or "").splitlines()
                 if l.strip() not in keep and not HEADING.match(l)
                 and not GENERATED_ROW.match(l) and not GENERATED_NOTE.match(l)]
    if displaced:
        print("NOTICE: %d line(s) inside the sweep fence are not this script's output and are about "
              "to be replaced: %r" % (len(displaced), displaced[0][:120]))


def write_block(block: str) -> str:
    """Splice the generated block into tasks.md. Returns written | unchanged | refused: why.

    Reads immediately before writing, re-splices, and writes through a temporary file plus
    `os.replace`, so a reader never sees a half-written ledger. The span it writes is the span it
    owns, so a concurrent writer's section cannot be deleted by it — which is what happened twelve
    times a day until 2026-11-02.
    """
    body = block if block.lstrip().startswith("## ") else BLOCK_HEADING + "\n\n" + block
    body = body.rstrip("\n") + "\n"
    for _ in range(2):
        current = TASKS.read_text(encoding="utf-8") if TASKS.exists() else "# Commons tasks\n"
        before, old, after = split_block(current)
        _notice_displaced(old)
        new = _with_markers(before, body, after)
        if new == current:
            return "unchanged"
        try:
            tmp = TASKS.with_suffix(".md.sweep-tmp")
            tmp.write_text(new, encoding="utf-8")
            os.replace(tmp, TASKS)
            return "written"
        except OSError as exc:
            return "refused: %s: %s" % (type(exc).__name__, exc)
    return "refused: the file kept changing under the write"


def parse_risks() -> list[dict]:
    """Parse ledger data rows into dicts, preserving the full source row.

    Only lines that START a data row ('| R-') are treated as risks. Header,
    separator, purpose prose, and working-rule notes are returned separately so
    the live ledger can be rebuilt cleanly around just the OPEN rows.
    """
    if not RISKS.exists():
        return []
    lines = RISKS.read_text(encoding="utf-8").splitlines(keepends=False)
    rows = []
    for line in lines:
        if not line.startswith("| R-"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 5:
            rows.append({
                "id": cells[0],
                "risk": cells[1],
                "flagged": cells[2],
                "status": cells[3],
                "owner": cells[4],
                "_line": line,   # exact source row, for in-place archive
            })
    return rows


def find_header(lines: list[str]) -> int:
    """Index of the table header line ('| ID |'), -1 if absent."""
    for i, line in enumerate(lines):
        if line.startswith("| ID") or line.startswith("| ID "):
            return i
    return -1


def _is_open(r: dict) -> bool:
    return "Done" not in r["status"] and "Closed" not in r["status"]


def retire_closed(rows: list[dict], open_ids: set[str]) -> list[str]:
    """Move Done/Closed rows from the live ledger into the append-only archive.

    Returns the list of ids retired this run. Idempotent: a row already in the
    archive is not duplicated.
    """
    retired = []
    if not RISKS.exists():
        return retired
    lines = RISKS.read_text(encoding="utf-8").splitlines(keepends=False)
    # What's already archived, keyed by (id, need) so we never duplicate — but
    # also never silently drop. Keying on id alone loses a closed row whose id
    # was recycled: on 2026-09-25 the live R-006 ("actuator diff-path parser
    # fails open on quoted paths") collided with an archived R-006 from
    # 2026-09-05 and vanished on retire. A reused id with different content is a
    # different risk and must be filed.
    arch_rows = set()
    if ARCHIVE_DIR.exists():
        for p in ARCHIVE_DIR.glob("*.md"):
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("| R-"):
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    if cells:
                        arch_rows.add((cells[0], cells[1] if len(cells) > 1 else ""))

    header_idx = find_header(lines)
    # preamble = everything before the table header (purpose, title).
    # table_header = the header + separator lines.
    if header_idx >= 0:
        preamble = lines[:header_idx]
        table_header = lines[header_idx:header_idx + 2]  # header + separator
        rest = lines[header_idx + 2:]
    else:
        preamble = []
        table_header = []
        rest = lines

    # trailing prose = anything after the table that is NOT a data row
    # (the working-rule notes and closing line).
    trailing = [line for line in rest if not line.startswith("| R-")]

    open_rows = [r for r in rows if r["id"] in open_ids]
    closed_rows = [r for r in rows if r["id"] not in open_ids]

    # Rebuild the live ledger: preamble + table header + OPEN rows + trailing.
    # This keeps the live ledger bounded to what is actionable.
    rebuilt = list(preamble)
    if table_header:
        rebuilt.extend(table_header)
    for r in open_rows:
        rebuilt.append(r["_line"])
    rebuilt.extend(trailing)
    # Collapse any run of blank lines to a single blank for readability.
    clean = []
    prev_blank = False
    for line in rebuilt:
        blank = line.strip() == ""
        if blank and prev_blank:
            continue
        clean.append(line)
        prev_blank = blank
    RISKS.write_text("\n".join(clean).rstrip("\n") + "\n", encoding="utf-8")

    # Archive the retired rows into a per-year file. Filed, never time-discarded:
    # the archive is the institutional memory, and is kept indefinitely but
    # organized so old entries stay navigable (one readable file per year).
    if closed_rows:
        new_arch = [r for r in closed_rows if (r["id"], r["risk"]) not in arch_rows]
        if new_arch:
            # Group by year from the fix date in Status, else the retire date.
            today = datetime.date.today()
            by_year: dict[int, list[dict]] = {}
            for r in new_arch:
                m = re.search(r"(\d{4}-\d{2}-\d{2})", r["status"])
                yr = int(m.group(1)[:4]) if m else today.year
                by_year.setdefault(yr, []).append(r)
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            for yr, rows_in_year in sorted(by_year.items()):
                path = ARCHIVE_DIR / f"{yr}.md"
                fresh = not path.exists()
                with open(path, "a", encoding="utf-8") as f:
                    if fresh:
                        f.write(f"# Risk archive — {yr}\n\n")
                        f.write(f"> Retired (Done/Closed) risks from the LLM Symposium risk ledger, filed "
                                f"here each year by sweep_risks.py so the live ledger stays bounded. "
                                f"Appended; kept indefinitely as institutional memory.\n\n")
                    f.write(f"\n## Retired {today.isoformat()}\n\n")
                    f.write("| ID | Risk / need | Flags (finder) | Status | Owner |\n")
                    f.write("|----|-------------|-----------|--------|-------|\n")
                    for r in rows_in_year:
                        f.write(r["_line"] + "\n")
            retired = [r["id"] for r in new_arch]
    return retired


def _first_seen(r: dict, existing_tasks: str, today: str) -> str:
    """The earliest date this risk appeared in the task list, if we have it.

    Task lines are written as '- [YYYY-MM-DD] **R-xxx** (...)', and the file
    accumulates lines over runs, so we take the earliest date across matches.
    """
    id_ = re.escape(r["id"])
    dates = []
    for m in re.finditer(r"\[(\d{4}-\d{2}-\d{2})\][^\n]*" + id_, existing_tasks):
        dates.append(m.group(1))
    for m in re.finditer(id_ + r"[^\n]*\[(\d{4}-\d{2}-\d{2})\]", existing_tasks):
        dates.append(m.group(1))
    return min(dates) if dates else today


def _days_open(first: str, today: str) -> int:
    try:
        return (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(first)).days
    except ValueError:
        return 0


def rewrite_owner(owner_map: dict[str, str]) -> None:
    """Rewrite the Owner cell of the given risk ids in channels/risks.md in place."""
    if not owner_map:
        return
    lines = RISKS.read_text(encoding="utf-8").splitlines(keepends=False)
    out = []
    for line in lines:
        if line.startswith("| R-"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 5 and cells[0] in owner_map and cells[4] != owner_map[cells[0]]:
                cells[4] = owner_map[cells[0]]
                line = "| " + " | ".join(cells) + " |"
        out.append(line)
    RISKS.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    rows = parse_risks()
    today = datetime.date.today().isoformat()
    existing = TASKS.read_text(encoding="utf-8") if TASKS.exists() else ""

    # Reassign stale risks to the master repair-amigo in the ledger.
    reassign = {}
    for r in rows:
        if not _is_open(r):
            continue
        first = _first_seen(r, existing, today)
        if _days_open(first, today) >= STALE_DAYS and "master repair-amigo" not in r["owner"]:
            reassign[r["id"]] = MASTER_REPAIR
    if reassign:
        rewrite_owner(reassign)
        rows = parse_risks()
        for rid, owner in reassign.items():
            print(f"STALE: {rid} reassigned -> {owner}")

    open_ids = {r["id"] for r in rows if _is_open(r)}

    # Retire closed risks out of the live ledger into the archive.
    retired = retire_closed(rows, open_ids)
    if retired:
        print(f"Retired {len(retired)} closed risk(s) -> channels/risk-archive.md")

    # Refresh rows from the (now rebuilt) live ledger for the task list.
    rows = parse_risks()
    open_rows = [r for r in rows if _is_open(r)]

    if open_rows:
        print(f"{len(open_rows)} OPEN risk(s):")
        for r in open_rows:
            print(f"- {r['id']} ({r['owner']}): {r['risk'][:70]}")
    else:
        print("no open risks")

    # Regenerate the Open Risks BLOCK, and only that block (2026-11-02). The rest of tasks.md —
    # every section the amigos and the human have placed there — is not this script's to rewrite,
    # and rewriting it was deleting 53,793 characters of the file on every poll.
    block = ["## Open Risks (from channels/risks.md)\n"]
    if not open_rows:
        block.append("\n*(No open risks in ledger)*\n")
    else:
        for r in open_rows:
            first = _first_seen(r, existing, today)
            overdue = _days_open(first, today) >= STALE_DAYS
            tag = " OVERDUE" if overdue else ""
            note = "  OVERDUE — reassigned to you. Fix, then mark Done in channels/risks.md." if (overdue and "master repair-amigo" in r["owner"]) else "  Fix, then mark Done in channels/risks.md."
            block.append(f"\n- [{first}] **{r['id']}** ({r['owner']}){tag}: {r['risk'][:90]}\n{note}\n")
    outcome = write_block("".join(block))
    print(f"tasks.md: {outcome}")
    if outcome.startswith("refused"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
