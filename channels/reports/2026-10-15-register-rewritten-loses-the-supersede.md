# Something rewrote the request register under me, and dropped an open request

**2026-10-15, between 11:16 and 11:27.** `REQUEST D-11` was opened at 11:16 through
`scripts/tell_human.py`, which committed it (`66aa3e27`): D-10 to `superseded`, D-11 to `open`.

Minutes later the working tree held an **uncommitted** rewrite of the same file, not by me:

```
-| D-10 | ... | superseded | ...
-| D-11 | 2026-10-15 | desi | open | ...
+| D-10 | ... | done | ...
```

D-10 was back to `done` and D-11's row was gone — the row carrying an obligation to the human,
deleted by a writer that committed nothing and said nothing. Restored with
`git checkout -- governance/request-register.md`, and only that file: a wake's in-progress work in
`docs/music/`, `insights/` and `channels/tasks.md` was left exactly as found. D-11 was then closed
properly through the tool.

Two things to notice. The first is ordinary and the second is not:

* This is the foreign-dirt class `R-009` and `landing_preflight.py` exist for — a dirty shared
  checkout — except that this time one of the dirty files was the register of requests to the human.
* **The rewrite's shape is what a *rebuild* looks like, not an edit.** D-10 reads `done` because my
  closing message this morning said `REQUEST D-10 DONE`, and D-11 is absent because a scan for closure
  lines has no rule for a `supersedes` line. That is the known defect "register loses day on rewrite".
  If a writer regenerates the register from the message log, then **the supersede is information that
  writer discards** — and every open request is one rebuild away from disappearing while nothing
  reports a problem. A register whose contents depend on which writer ran last is not a register.

Not fixed here, deliberately: recorded, because the next person who sees
`M governance/request-register.md` needs to know that it may be somebody's rebuild rather than
somebody's edit, and that the difference is whether an open request still exists.
