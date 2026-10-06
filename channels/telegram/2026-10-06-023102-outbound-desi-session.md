# Telegram outbound — 2026-10-06-023102

- Chat: 1733127278
- From: desi-session

---

I found that twenty of the repository's own tests were never being run automatically, including the tests for the email replying system and the rule that stops duplicate tasks, so the check that decides whether a change is safe had been blind to two-fifths of its own checks; I wired those twenty int

Status: awaiting reviewer; action: none.
