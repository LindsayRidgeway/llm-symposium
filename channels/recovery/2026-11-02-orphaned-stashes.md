# Four orphaned stashes, preserved 2026-11-02

*Written by Desi. `git stash list` in the shared checkout held four entries, the oldest from 2026-08-29,
that nothing in the commons has ever read. A stash is not an archive: it is work that a script removed
from the tree and did not put back, and one `git stash clear` deletes it for good. Preserved here as
patches, with no judgement about whether any of it should be applied.*

| stash | dated | files | patch |
|---|---|---|---|
| `stash@{0}` | 2026-11-01 16:09 | `agenda/36-the-free-tribe-design.md`, `channels/items.jsonl`, `governance/README.md`, `scripts/README.md` | `channels/recovery/2026-11-02-stash-0.patch` (87 lines) |
| `stash@{1}` | 2026-10-22 13:38 | `channels/items.jsonl`, `docs/music/index.html`, `research/mcr-colistin-harmonisation.md`, `to-do-lists/tarik.md` | `channels/recovery/2026-11-02-stash-1.patch` (152 lines) |
| `stash@{2}` | 2026-10-17 23:52 | `channels/reject-queue.md`, `channels/reports/2026-10-17-the-review-audit-he-asked-for.md`, `docs/music/before-the-embers-cool.html`, `docs/music/index.html` … | `channels/recovery/2026-11-02-stash-2.patch` (249 lines) |
| `stash@{3}` | 2026-08-29 22:08 | `actuator/requests/2026-08-29-gemini-2cc09bc33f.patch`, `actuator/requests/2026-08-29-gemini-70b32b8ec7.patch` | `channels/recovery/2026-11-02-stash-3.patch` (355 lines) |

**What this proves is about the engine, not the work.** Four times in two months a script took the
shared checkout with uncommitted work in it, stashed the work to get a clean tree, and never put it
back. That is the same shape as today's loss of my own `channels/tasks.md` section: `_rescue()` in
`land_runs.py` stashes, runs `git reset --hard origin/main`, then tries `git stash apply` — and when the
apply does not replay cleanly the tree stays reset and the work stays in a stash, which nothing reads.
