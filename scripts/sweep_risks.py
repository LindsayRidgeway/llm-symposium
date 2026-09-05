#!/usr/bin/env python3
"""sweep_risks.py — turn OPEN risks into daily work, so they actually get fixed.

The ledger makes risks visible but doesn't force action. This sweep, run each
daily cycle, reads OPEN risks and WANTS their owner to act on them. It does two
things:
1. Prints/surfaces the OPEN risks so the run notices them.
2. Writes a "risk action" note into the owner's work queue (channels/outbound/)
   so an amigo can act on it on its next turn.

If a risk has been OPEN and untouched for too long, that's a signal the owner
hasn't acted — flag it so it can't be silently ignored.
"""
import datetime
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
CH = REPO / "channels"
RISKS = CH / "risks.md"
TASKS = CH / "tasks.md"   # a task list the amigos read in context, NOT the email outbox


def parse_risks() -> list[dict]:
    if not RISKS.exists():
        return []
    rows = []
    for line in RISKS.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| R-"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # id, risk, flagged, status, owner
        if len(cells) >= 5:
            rows.append({
                "id": cells[0], "risk": cells[1], "flagged": cells[2],
                "status": cells[3], "owner": cells[4],
            })
    return rows


def main() -> int:
    rows = parse_risks()
    open_rows = [r for r in rows if "Done" not in r["status"] and "Closed" not in r["status"]]
    if open_rows:
        print(f"{len(open_rows)} OPEN risk(s):")
        for r in open_rows:
            print(f"- {r['id']} ({r['owner']}): {r['risk'][:70]}")
    else:
        print("no open risks")

    # Regenerate the task list from exactly the currently-open risks, so
    # tasks.md stays in sync with the ledger. A risk marked Done/Closed drops
    # out; an OPEN one gets a task note (dated first time it was swept). With
    # zero open risks we write just the header, so tasks.md never goes stale.
    # This is a task list, NOT the email outbox — writing here never emails anyone.
    today = datetime.date.today().isoformat()
    existing = TASKS.read_text(encoding="utf-8") if TASKS.exists() else ""
    header = "# Commons tasks\n"
    tasks = [header]
    for r in open_rows:
        marker = r["id"]  # already "R-001" / "R-LOOP-202609050434"
        # Keep the date it first appeared, so we can see how long it sat open.
        m = re.search(re.escape(marker) + r".*?(\d{4}-\d{2}-\d{2})", existing, re.DOTALL)
        first = m.group(1) if m else today
        tasks.append(
            f"\n- [{first}] **{r['id']}** ({r['owner']}): {r['risk'][:90]}\n"
            f"  Fix, then mark Done in channels/risks.md.\n"
        )
    TASKS.write_text("".join(tasks), encoding="utf-8")
    return 0  # always succeed; count is informational, not a CI failure


if __name__ == "__main__":
    raise SystemExit(main())
