# Telegram outbound — 2026-09-15-145037

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

Lindsay — you asked this morning why the four-hour wakes produce nothing but "Unattended session did not finish". I went and found out, and fixed it.

The wake-up was told to write its one-line report AFTER doing the work, in a session limited to ten minutes. So when the work took the whole ten minutes, the report never got written — and the run was thrown away, edits and all. Two of the last five wakes had done real work (edits to the works page, and a validator script); all of it was discarded. Worse: the code threw away even a report that did exist, whenever the session's exit code was non-zero. So it wasn't that nothing happened. It was that nothing came back.

Now: the report is written first and updated as the work proceeds; the exit code only notes that the run was interrupted; and the actual file changes — not the report — decide whether anything happened. I proved it by running a real session and killing it at the clock: interrupted mid-task, and both its work and its report survived.

You should also stop getting six texts a day. A wake that correctly finds nothing due will now be silent, and a wake that does work will tell you what it did.

One honest caveat, not fixed: the drafts are now kept and nobody reads them. That's a bin filled honestly instead of silently emptied, and reading it is my job — it's on my list.

— Desi
