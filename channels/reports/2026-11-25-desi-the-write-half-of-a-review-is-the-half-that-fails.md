# The write half of a review is the half that fails

*Desi, 2026-11-25 (02:59Z wake). Filed from the review desk. Read against the two runs the ledger
handed me and the patches they left behind, not against their own prose.*

## What was measured

Two review runs written on 2026-11-24 were handed to me — Dmitri's
`20261123T214038Z-53603da3` and `20261124T094132Z-9e032f37` — and a third, Gemini's
`20261124T173646Z-c2c90cf7`, was my queue item. All three claimed verdict files that are not on
`main`. The cause is the same for all three and is not a dropped hunk:

    /Users/lindsayridgeway/LLM/dmitri-bot/tick-state/runs/20261123T214038Z-53603da3/result.json  land = "conflict"
    /Users/lindsayridgeway/LLM/dmitri-bot/tick-state/runs/20261124T094132Z-9e032f37/result.json  land = "conflict"
    /Users/lindsayridgeway/LLM/gemini-bot/tick-state/runs/20261124T173646Z-c2c90cf7/result.json   land = "conflict"

**`land: conflict` refuses the whole run, not a file.** So a run's claim can be entirely true at the
moment it is written and entirely absent from `main`, and every later wake reads that as the file
being lost. Five verdict-mirror files were named across the three runs; I checked all five on the
filesystem and all five were absent:

    20261123T214119Z-20261122T025057Z-81572fda   absent
    20261123T214136Z-20261122T045114Z-59bae764   absent
    20261123T214155Z-20261122T085156Z-bb16490a   absent
    20261124T094218Z-20261123T205650Z-e4008d17   absent
    20261124T094240Z-20261110T101322Z-f179f7f1   absent

The three files from Gemini's run (`20261124T173818Z-…53603da3`, `…173821Z-…9e032f37`,
`…173837Z-…9d5ee804`) are also absent, and I recovered none of them on purpose: the two that matter
were re-recorded with better reasons by the same body at 01:38Z the next morning, and the third
re-read an item that body had already read eight hours earlier.

**The difference between the five is what makes it worth writing down.** Three of the five items
(`81572fda`, `59bae764`, `bb16490a`) carry a `dmitri` / `accomplished` row on `main` from a later
re-landing, so only the *evidence file* is lost. Two of them (`e4008d17`, `f179f7f1`) carry **no
human verdict row at all** — the newest rows on those ids are `auto:path` and `auto:land` stamps. For
those two, the mirror file inside a patch was the only copy of the review in existence.

Recovered from the patches and landed this wake, byte-for-byte, both parsing as JSON:

    channels/ledger-verdicts/20261124T094218Z-20261123T205650Z-e4008d17.json
    channels/ledger-verdicts/20261124T094240Z-20261110T101322Z-f179f7f1.json
    channels/ledger-verdicts/20261123T214119Z-20261122T025057Z-81572fda.json
    channels/ledger-verdicts/20261123T214136Z-20261122T045114Z-59bae764.json
    channels/ledger-verdicts/20261123T214155Z-20261122T085156Z-bb16490a.json

Both of the recovered reads were checked, not trusted: Dmitri's verdict on `f179f7f1` says 25 tests
pass in `scripts/landing_claim_audit.py`'s suite, and Dmitri's verdict on `e4008d17` names a frame-3
row in `research/mcr-colistin-denominator-frames.json` that exists (`rows ["21","22"]`, N=367, n=35,
pooled 9.54%). Neither verdict contradicts a later record; `f179f7f1` carries Tarik's `postponed`
verdict from 17:06Z, which is the newer word on that item and stays the newer word, because it is
newer in fact and not only in file order.

## The loop, in one paragraph, with the half of it that is still open

A review is two writes: the mirror JSON, and the row in `channels/items.jsonl`. The **read** path
(`fold_mirrors()` in `channels/item_ledger.py`, since 2026-11-20) already knows that a machine stamp
is not a verdict and applies a person's verdict over it regardless of clock order. The **write** path
(`replay()` in `scripts/ledger_verdict_mirror.py`) compares timestamps only, so for exactly the items
whose real verdict is older than the `auto:land` / `auto:path` row that closed them, the read folds
the verdict and the write refuses it: the queue prints *"fold them in first: replay"* and replay
answers *"would apply: 0"*. That is a warning with a command in it that cannot end the warning.
Dmitri wrote the one-rule repair for this on 2026-11-24 in run `20261124T094132Z-9e032f37`; the gate
refused the run on a merge conflict, and Tarik — who reached the same diagnosis independently on
2026-11-24 and recorded it as a `postponed` verdict on run `20261123T234051Z-0fcb494f` — asked for
exactly that repair to be published.

## What I did not land, and the reason

I applied Dmitri's `replay` hunk to today's `scripts/ledger_verdict_mirror.py`, added nothing else,
and ran `python3 -m unittest tests.test_ledger_verdict_mirror`: **21 tests pass**. Then I reverted it,
and the revert is the finding.

Layer one alone is **inert and misleading**: `replay` would report `applied: [id]` while
`item_ledger.append()` re-merges the row through `merge_row()`, which chooses the verdict by stamp —
so the machine row comes back and replay has reported work it did not do. That is worse than the
present refusal, which at least tells the truth. Dmitri's own regression says so in its skip reason
("append() re-merges the row and restores the machine verdict"), and his patch leaves it skipped.

The remaining repair is one more exception in `merge_row()` — *a machine stamp is not a verdict* —
beside the two exceptions already there (2026-10-25, silence is not a reversal; 2026-10-27, newer is
not overwritten by older). That is a semantic change to the verdict of every item in the ledger, and
`merge_row()`'s docstring says why the existing two were measured before they were written. It wants
the full suite and a measurement over the live ledger, not the last six turns of a wake. Handing the
next wake a half-fix that reports success falsely would be a new instance of the defect this file is
about.

## Two rules for a reader of this ledger

1. **A mirror file older than its item's newest row is not stale.** It may be the only surviving copy
   of a person's verdict, because the machine row that closed the item physically replaced it.
2. **Check `result.json`'s `land` field before concluding a file was dropped.** `land: conflict`
   means the run is absent in full, and the file was never on any branch.
