# Retired schedules

Launchd jobs that used to run on this Mac, kept here because a switch nobody can find again is a
deletion, not a retirement. Nothing in this directory runs. To bring one back, copy its plist into
`~/Library/LaunchAgents/` and `launchctl bootstrap gui/$(id -u) <path>`.

## com.lindsay.dailyreport.plist — retired 2026-11-20

Ran `/usr/bin/python3 scripts/daily_report.py --send` at 08:00 local every day.

The job was created on 2026-10-06 for a report the human asked for that morning, and he rewrote its
definition himself on 2026-10-07 (the letters N/V/A/P/W/R are his). On **2026-10-14** he asked it to
stop reaching him — *"I'd rather not see any more reports until then"* — and `channels/reports/HOLD.md`
held the delivery from that day. So for five weeks the job did what a held report does: it rendered a
file into `channels/reports/daily-YYYY-MM-DD.md`, spent a model call titling the day's items, and
committed, while nothing reached his phone.

On **2026-11-20** he said he did not remember asking for it and did not think he was receiving them,
and asked that the code be removed if that seemed best. The clock was the part that acted without
anyone wanting it, so the clock is what went: the job was booted out and its plist moved here.

What was deliberately *not* deleted, and why:

- **`scripts/daily_report.py` itself.** It is not only a sender. `scripts/world_report.py` imports
  `HUMAN_EMAILS` and `received()` from it (the incoming-mail measure), and the file's own docstring is
  the written definition of the N/V/A/P/W/R vocabulary the whole ledger uses — a specification in the
  human's words. Deleting the sender would have deleted the spec and broken the mail measure.
- **The 42 daily files already in `channels/reports/`.** They are the commons' record of those days,
  cited as evidence elsewhere; the complaint was about what reached his inbox, not about the archive.

Nothing runs it now. `scripts/daily_report.py` can still be invoked by hand if the record is ever
wanted for a day, and the same file says so.
