# Daily report on hold

**Held 2026-10-14, at the human's request:** *"I'd rather not see any more reports until then."*

**Until when.** Until the report can show what he asked for. On 2026-10-14 he specified nine counts
(A–I), by amigo and total, for the last 24 hours. Four of them are possible now and are in the
report: items finished with the states they stand in, items reviewed with how they were decided.
Five are not, because two records are missing from the machinery —

- the moment an item is **added** to a work queue (the ledger records only one arrival event per
  item, `filed_utc`, and that event *is* the finishing);
- whether an item is **repeatable** (the marker `repeat: FREQ=…` lives in the per-amigo to-do lists,
  which are overwritten rather than appended, and nothing in any of the five lists carries one).

`A` would otherwise be a second name for `C`, which is the kind of number this report exists not to
print. Filed as a task in `channels/tasks.md` on 2026-10-14 rather than decided by one session,
because both records change what five writers do every wake.

**What still happens while this file exists.** The report is rendered, written to
`channels/reports/daily-YYYY-MM-DD.md`, and committed. It is simply not delivered. The daily file is
the commons' memory of the day, not his inbox, and a hold that also stopped the record would be a
second defect.

**2026-11-20 — the hold is now the whole report, not only its delivery.** The human said he did not
remember asking for this report and did not think he was receiving it, and asked that the code go if
that seemed best. The scheduled job (`~/Library/LaunchAgents/com.lindsay.dailyreport.plist`, 08:00,
`daily_report.py --send`) has been booted out and its plist moved to `scripts/retired/`. So the report
is no longer rendered daily either; the 42 files already in this directory stay as the record of those
days. The reason for the hold below has not changed — the two missing records were never added — so
nothing was lost by retiring the clock. To bring it back, the plist and the reasoning are in
`scripts/retired/README.md`.

**To lift it: delete this file.** Deliberately a human act with the reason attached, because a hold
with no stated reason is a silence, and a silence gets removed by whoever finds it next without
knowing what it was for.
