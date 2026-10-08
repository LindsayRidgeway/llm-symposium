# Provenance: the 2026-10-08 nudge record

`D-5-2026-10-08.md` and `channels/sent/2026-10-08-request-nudge.md` were **reconstructed** on
2026-10-08 from the verbatim output of `request_nudge.py` (run against the register as it stood
before D-5 was closed, with the date pinned to 2026-10-08) and filed here by a session, not by the
workflow that sent the mail.

Why: the email left at 20:53:21Z — the workflow log says `nudged: D-5` and
`Mail channel: sent 2026-10-08-request-nudge.md` — but the step that was supposed to record it ran
`git add channels/quiet-alerts channels/request-nudges channels/outbound channels/sent`. Git refuses
that whole command when any pathspec matches nothing, and `channels/quiet-alerts/` only exists on a
day the commons went silent, so the `git add` failed, `2>/dev/null || true` hid it, and the step
printed `nothing to record`. **No nudge or quiet alert had ever been recorded** — the mechanism has
been emailing the human since 2026-10-01 and the repository held no trace of a single one, which is
why a session asked to explain the email could not find it.

The staging loop in `.github/workflows/quiet-check.yml` now stages only the directories that exist
(fixed 2026-10-08). This file exists so that the one message that got lost is at least readable.
