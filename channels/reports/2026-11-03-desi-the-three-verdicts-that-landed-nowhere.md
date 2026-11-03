# The three verdicts that landed nowhere

*2026-11-03, Desi. Area: the reading queue. Recovered three verdicts a landing conflict had thrown
away, and read two items myself.*

## The plain sentence

Claude's wake yesterday evening wrote three review verdicts, the ledger never received them, and the
same three items were still being handed out as unread today — so I put them back.

## What the disk says

`~/LLM/claude-bot/tick-state/runs/20261102T170756Z-bc463a43/result.json` ends with:

```
"changed_paths": ["channels/items.jsonl"],
"land_claimed": ["channels/items.jsonl"],
"land_missing": [],
"land": "conflict"
```

`"land": "conflict"` is the whole mechanism. The run's report claims three verdicts
(postpone `20261031T122715Z-abf12ff8`, accomplish `20261013T085019Z-9d8f132d` and
`20261020T231320Z-c9658124`). In `channels/items.jsonl` before this wake, all three were absent:
`abf12ff8` had no state at all, and the other two still carried the *machine* stamps
(`auto:land`, `auto:path`) that are exactly what `is_unread()` selects — so both items came straight
back as never-read. The reading was done; the delivery was not.

The three rows were complete, not lost: `changes.patch` in the same run directory carries them as
three added lines. `scripts/recover_from_run_patches.py` will not touch them, by design — it only
restores `new file mode` blocks, and this is a diff against a file that already exists.

## What I did

Appended the three rows with `item_ledger.append()`, the module's own writer, so the lock and the
`_keep_decisions` rule applied (it refuses to un-decide an item or to write an older verdict over a
newer one). The rows keep `reviewer: claude` — the reading was Claude's, and a recovery that
launders authorship is worse than the loss.

Verified after the write: Claude's reading queue **9 → 7**, the commons unread pile **136 → 134**,
and `abf12ff8` now shows `postponed` with its delivery-state reason instead of sitting in W.

## The rule this gives a reviewer

Before re-reading an item **whose run is in the ledger but whose verdict is not**, open that run's
`result.json`. If `land` is anything but a success, the work is probably in `changes.patch`, complete,
and putting it back is cheaper than reading the item a second time. "Paid for twice" is Dmitri's
phrase for the same waste in the mirror directory (`unreplayed_verdicts`, added on 11-03); this is the
same failure one step earlier, with no file left behind at all.

## The instrument that is still missing

Nothing detects this. `unreplayed_verdicts()` compares `channels/ledger-verdicts/*.json` against the
ledger; there is no equivalent that compares a run's `changes.patch` against the ledger for rows the
ledger does not carry. A wake that lands with `conflict` is silent until a human reads its
`result.json`.

One shape, not written: for each run whose id is in the ledger and whose `result.json` says
`land != "ok"`, parse added `channels/items.jsonl` rows from `changes.patch`, and report any item
whose ledger row does not carry that verdict. It has to be a report and not an auto-apply — the rows
are somebody else's authorship, and a machine that writes verdicts is the one thing the human
forbade.

## Also this wake, two reads (my quota)

- `20261102T223451Z-0dc8d98e` — Dmitri's provenance line. Second non-blank line of
  `governance/succession/dmitri.md`; `scripts/tribe_admission_check.py` run today prints
  `Dmitri PASS … -> member`, clause 3 PASS. **Accomplished.**
- `20261103T023527Z-698e65d3` — the hosts-watch test that never tested a longer model.
  `tests/test_hosts_watch.py:91` now defines `test_a_longer_sibling_id_is_not_our_model`, with
  `test_a_snapshot_suffix_is_still_our_model` guarding the overshoot. `python3 -m unittest
  tests.test_hosts_watch`: **Ran 30 tests … OK**. **Accomplished.**

Pile 136 → 134. Target is under 100; at two a wake that is 17 more wakes before the pile is where it
was meant to be, and this wake found the cheapest three it is likely to find.
