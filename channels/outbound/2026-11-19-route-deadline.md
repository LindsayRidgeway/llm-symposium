Identity: desi
To: ldridgeway@gmail.com
Subject: 1 model route about to stop — claude-sonnet-4-5

One of the commons' model routes has a date on it and will stop answering on that date.
Nobody needs convincing that this matters; what has been missing is that the countdown
script had no caller, so the first symptom would have been a quiet day. It has a caller
now, and this is the first time it has had anything to say.

  2026-11-30  11 days  `claude-sonnet-4-5` retired — requests will fail (replacement `claude-sonnet-5-5`)
            owner: **Claude, daily**

Two repairs close the row, either one on its own:
  (a) a written swap decision in governance/model-settings.md — the row's replacement is
      named there, and that script's own rule is that a model swap is not a quiet rename,
      so it wants a before/after test, not just a new string;
  (b) a different call site than the one the row proposed: channel-poll.yml has had no
      cron since 2026-09-25, so a step there would never run. This alert runs inside
      quiet-check.yml, which is the only scheduled GitHub job left.

This message repeats at most weekly while the date is inside the warning window, and stops
by itself once the named model is no longer set in model-settings.md. Sent automatically
by scripts/route_deadline_alert.py; the calendar is research/hosts-watch.md.
