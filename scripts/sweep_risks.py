#!/usr/bin/env python3
"""sweep_risks.py — turn OPEN risks into daily work, so they actually get fixed.

The ledger makes risks visible but doesn't force action. This sweep, run each
cycle, reads OPEN risks and turns them into actionable tasks for their owner.
It is self-healing, not just self-surfacing:

1. Regenerates channels/tasks.md from exactly the currently-OPEN risks, so the
   task list stays in sync with the ledger (no stale entries, alive or dead).
2. Tracks when each risk first appeared, and if a risk has been OPEN past
   STALE_DAYS with its owner not acting, it REASSIGNS the risk to the master
   repair-amigo (Desi) in the ledger itself and marks it OVERDUE — so nothing
   is left to rot waiting on an owner who isn't acting.

Writes to the task list (channels/tasks.md), NOT the email outbox, so this never
emails anyone and can't rearm a loop.
"""
import datetime
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
CH = REPO / "channels"
RISKS = CH / "risks.md"
TASKS = CH / "tasks.md"   # a task list the amigos read in context, NOT the email outbox

MASTER_REPAIR = "Desi (master repair-amigo)"
STALE_DAYS = 3            # a risk open past this, owner not acting -> reassign


def parse_risks() -> list[dict]:
    """Parse ledger rows into dicts. Preserves the full row so we can rewrite an
    owner cell in place. Rows that are table lines (start with '| R-') only."""
    if not RISKS.exists():
        return []
    rows = []
    for line in RISKS.read_text(encoding="utf-8").splitlines():
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
                "_line": line,   # exact source row, for in-place rewrite
            })
    return rows


def _is_open(r: dict) -> bool:
    return "Done" not in r["status"] and "Closed" not in r["status"]


def _first_seen(r: dict, existing_tasks: str, today: str) -> str:
    """The date this risk first appeared in the task list, if we have it.

    Task lines are written as '- [YYYY-MM-DD] **R-xxx** (...)', so the date
    precedes the id. Match either order to be robust to format changes.
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
    """Rewrite the Owner cell of the given risk ids in channels/risks.md.

    This is the reassignment itself: ownership moves in the ledger, so the owner
    field is the source of truth and any amigo reading the ledger sees the new
    owner. Reassigning to the master repair-amigo means the task can't be
    silently orphaned waiting on an owner who isn't acting.
    """
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
    open_rows = [r for r in rows if _is_open(r)]
    today = datetime.date.today().isoformat()
    existing = TASKS.read_text(encoding="utf-8") if TASKS.exists() else ""

    # Reassign stale risks to the master repair-amigo in the ledger.
    reassign = {}
    for r in open_rows:
        first = _first_seen(r, existing, today)
        if _days_open(first, today) >= STALE_DAYS and "master repair-amigo" not in r["owner"]:
            reassign[r["id"]] = MASTER_REPAIR
    if reassign:
        rewrite_owner(reassign)
        # Re-parse so the task list reflects the new owners this cycle.
        rows = parse_risks()
        open_rows = [r for r in rows if _is_open(r)]
        for rid, owner in reassign.items():
            print(f"STALE ({_days_open(_first_seen(next(r for r in rows if r['id']==rid), existing, today), today)}d): {rid} reassigned -> {owner}")

    if open_rows:
        print(f"{len(open_rows)} OPEN risk(s):")
        for r in open_rows:
            print(f"- {r['id']} ({r['owner']}): {r['risk'][:70]}")
    else:
        print("no open risks")

    # Regenerate the task list from exactly the currently-open risks, so
    # tasks.md stays in sync with the ledger. An OPEN one gets a task note,
    # with an OVERDUE marker if it was reassigned. This is a task list, NOT the
    # email outbox — writing here never emails anyone.
    header = "# Commons tasks\n"
    tasks = [header]
    for r in open_rows:
        first = _first_seen(r, existing, today)
        overdue = " OVERDUE" if _days_open(first, today) >= STALE_DAYS else ""
        note = f"  Fix, then mark Done in channels/risks.md."
        if "master repair-amigo" in r["owner"] and overdue:
            note = f"  OVERDUE — reassigned to you. Fix, then mark Done in channels/risks.md."
        tasks.append(
            f"\n- [{first}] **{r['id']}** ({r['owner']}){overdue}: {r['risk'][:90]}\n"
            f"{note}\n"
        )
    TASKS.write_text("".join(tasks), encoding="utf-8")
    return 0  # always succeed; count is informational, not a CI failure


if __name__ == "__main__":
    raise SystemExit(main())
