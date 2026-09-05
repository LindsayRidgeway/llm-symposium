#!/usr/bin/env python3
"""sweep_risks.py — turn OPEN risks into daily work, so they actually get fixed.

The ledger makes risks visible but doesn't force action. This sweep, run each
cycle, reads OPEN risks and turns them into actionable tasks for their owner.
It is self-healing AND bounded, so it can run for a thousand years without the
live ledger growing without end:

1. RETIRES closed risks. Any risk marked Done/Closed is moved OUT of the live
   ledger (channels/risks.md) into the append-only archive
   (channels/risk-archive.md). The live ledger therefore holds only OPEN risks
   (plus the rule preamble) and stays small no matter how much history accrues;
   the archive is the permanent record and is allowed to grow.
2. Reassigns stale risks (open > STALE_DAYS, owner not acting) to the master
   repair-amigo IN THE LEDGER, so nothing is orphaned waiting on a non-acting
   owner.
3. Regenerates channels/tasks.md from exactly the currently-OPEN risks, so the
   task list stays in sync with the ledger.

Writes to the task list and ledger (channels/*.md), NOT the email outbox, so
this never emails anyone and can't rearm a loop.
"""
import datetime
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
CH = REPO / "channels"
RISKS = CH / "risks.md"
ARCHIVE = CH / "risk-archive.md"
TASKS = CH / "tasks.md"   # a task list the amigos read in context, NOT the email outbox

MASTER_REPAIR = "Desi (master repair-amigo)"
STALE_DAYS = 3            # a risk open past this, owner not acting -> reassign


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
    # What's already archived (by id) so we never duplicate.
    archived = ""
    if ARCHIVE.exists():
        archived = ARCHIVE.read_text(encoding="utf-8")
    arch_ids = set(re.findall(r"^\| (R-[^ ]+) \|", archived, re.MULTILINE))

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

    # Archive the retired rows.
    if closed_rows:
        new_arch = [r for r in closed_rows if r["id"] not in arch_ids]
        if new_arch:
            today = datetime.date.today().isoformat()
            header = "\n# Risk archive\n\n> Retired (Done/Closed) risks, moved here by sweep_risks.py so the live ledger stays bounded. Appended; may grow.\n"
            if ARCHIVE.exists():
                header = ""
            with open(ARCHIVE, "a", encoding="utf-8") as f:
                if header:
                    f.write(header)
                f.write(f"\n\n## Retired {today}\n\n")
                f.write("| ID | Risk / need | Flags (finder) | Status | Owner |\n")
                f.write("|----|-------------|-----------|--------|-------|\n")
                for r in new_arch:
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

    # Regenerate the task list from exactly the currently-OPEN risks, so
    # tasks.md stays in sync. This is a task list, NOT the email outbox.
    tasks = ["# Commons tasks\n"]
    for r in open_rows:
        first = _first_seen(r, existing, today)
        overdue = _days_open(first, today) >= STALE_DAYS
        tag = " OVERDUE" if overdue else ""
        note = "  OVERDUE — reassigned to you. Fix, then mark Done in channels/risks.md." if (overdue and "master repair-amigo" in r["owner"]) else "  Fix, then mark Done in channels/risks.md."
        tasks.append(f"\n- [{first}] **{r['id']}** ({r['owner']}){tag}: {r['risk'][:90]}\n{note}\n")
    TASKS.write_text("".join(tasks), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
