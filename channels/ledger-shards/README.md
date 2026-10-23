# Ledger shards — one file per wake, so a verdict can land

*A row written here is part of the item ledger. `channels/item_ledger.py` reads this directory
after `channels/items.jsonl`, in name order, and lets the later-dated row for an id win.*

## Why this directory exists (2026-10-23, Dmitri)

`channels/items.jsonl` is append-only and shared by every writer, and a wake's rows land at the end
of it — the same lines every other writer appends to. By the time the lander replays a run's patch,
that hunk no longer matches main. `land_runs.py` applies the whole patch with `git apply`, which is
atomic, so **one stale ledger hunk discards the entire run**: its verdicts, its report, its artefact.

Measured cost, from the run reports rather than from memory: item `20261019T170221Z-c56a22e8`
(Tarik's finished `tg-20261017-001.json`) was recovered, hashed against the author's declared
sha256 and marked `accomplished` by wakes `20261022T233003Z`, `20261023T013022Z` and
`20261023T073059Z`. On main its row still reads `state=null`, because all three of those runs died
on their `channels/items.jsonl` hunk. It is not missing work; it is a lost write.

## The rule

- A wake writes its rows to `channels/ledger-shards/<its run id>.jsonl`. Run ids begin with a UTC
  timestamp, so a directory of shards reads chronologically.
- A shard never touches another run's file, so its patch hunk always applies.
- `load()` applies a shard row only when it is not older than the row it would replace, so a shard
  landing late cannot undo a newer verdict written straight into the ledger.
- Outside a wake checkout — the shared clone, `--collect`, a test fixture — rows still go to
  `channels/items.jsonl`. This is not a migration, and nothing has to be backfilled.
