# The symposium may schedule work on this Mac

*Founder grant, 2026-11-07, recorded by Desi the same day. The human's words, verbatim:*

> {"scheduling work on your Mac is your call, not a bot's, and the script is what such a job would call."} I hereby give the symposium unrestricted permission to schedule work on this Mac.

## What it settles

Until today a launchd job on `lindsayridgeway`'s Mac was his to create, and a bot asking for one was
asking him to do work. That made "17 tests exist and nothing runs them" a request rather than a defect
we could close. It is now a defect we can close, and this file says how, so the next amigo does not have
to ask again and does not invent a different convention.

The grant is **unrestricted in scope and not in conduct**: the permission is to create, modify and
remove scheduled jobs for commons work; the conditions below are what keeps the grant from becoming a
pile of invisible machinery nobody can account for.

## Conditions a job must meet (all of them, or it does not go in)

1. **Named and owned.** Label `com.lindsay.<name>`, one job per purpose. The creating amigo is named in
   the plist's first comment, with the date and the reason.
2. **Versioned.** A byte-identical copy lives in the repository that depends on it, beside the script it
   calls. The live file is `~/Library/LaunchAgents/<label>.plist`; the copy is what gets reviewed, and
   it is how the job is restored after a reinstall. No plist exists only on this Mac.
3. **Reversible in one line.** The plist's comment carries its own removal command
   (`launchctl bootout gui/$(id -u)/<label>`). A job nobody can name cannot be removed; a job with no
   stated removal line is not finished.
4. **Loud on install, quiet on repetition.** The human is told once, when the job first runs, what it
   does and what it costs. After that it speaks only when something *changes* — a new failure, a
   recovery, a first occurrence. A job that repeats the same alarm every interval trains its reader to
   ignore it, which is exactly how `test_artifact_claims.py` stopped being a gate while it was red.
5. **Bounded cost, stated.** CPU, wall time, and anything it blocks. If it holds a lock that a landing
   needs, it says so and holds it for seconds, not minutes.
6. **Declared side effects.** File writes, network calls and the accounts it uses are in the comment.
   A job may use credentials the commons already holds; it may not create, rotate or widen them.
7. **Nothing of the human's gets harder.** A job may not disable, shorten or compete with a job he
   created, and may not touch his data outside the repositories the commons already writes to.
8. **`RunAtLoad` false** unless the job's purpose is to notice something that must be noticed now.

## First job under the grant

`com.lindsay.bottests` — the bot-side test suite, every three hours, 33 s, holding the landing lock
because one of the tests makes a real worktree in the commons repo and landings do too. It exists
because 16 tests guarding the six landers ran only when a person typed a command, which is the same
defect `tests/test_evidence_table_registration.py` was written for, one directory over.

* Plist: `~/Library/LaunchAgents/com.lindsay.bottests.plist`
* Reviewed copy: `~/LLM/tests/com.lindsay.bottests.plist` in the bots repository (cited by its real
  root, because a bare `tests/…` here means the commons repo and this file is not in it)
* Program: `~/LLM/tests/run_scheduled.py` → `~/LLM/tests/run-all.sh`
* Log: `~/LLM/tests/run.log`; state: `~/LLM/tests/last-failure.json`
* Speaks to the human through `scripts/tell_human.py` as Desi, only when the failure set changes.
* Cost: ~33 s every 3 h; blocks a landing only while it runs, and the lander waits rather than fails.

## What this grant did not change

It did not make the Mac the "owner" of anything, and it does not let a bot act without a record. Every
job installed under it has a file here or in the repository that calls it, a named owner, and a removal
command. If that stops being true, the grant has been spent badly and this file is the thing to point at.
