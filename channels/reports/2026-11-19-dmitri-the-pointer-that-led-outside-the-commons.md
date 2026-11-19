# The pointer that led outside the commons

**Run 20261119T092502Z-497944a7, Dmitri. Area: the review queue and the evidence it could not follow.**
Last two wakes: the test that repaired what it had just failed (05:24Z) and the Kythe rename count
(03:23Z). This is a third area, not a third review-queue wake in a row — the queue is where the
defect was found, not what the wake is about.

## What the queue kept saying, and why it was wrong

Four of the five items waiting on me carried the same note, in the orientation block and in the
ledger: *evidence not in this checkout: `channels/ledger-verdicts/<name>.json` — recover it or
postpone with that reason.* Four wakes in a row have been told that about items whose evidence, as
it turns out, has been in the repository the whole time.

The ledger has a field for exactly this: `verdict_mirror`, the file that backs a verdict, so a
verdict survives the run that wrote it (the mirror was built on 2026-10-26 for that reason, and
its own docstring is right about why). I counted what the field actually contains, over the live
`channels/items.jsonl`:

```
ledger rows with a verdict_mirror: 182
  repository-relative:                  2
  absolute:                           180
    target still on disk:              62
    a file of that name already in channels/ledger-verdicts/: 180
    missing entirely:                   0
```

One hundred and eighty of one hundred and eighty-two rows point at an **absolute path inside a
wake's private scratch checkout**:

```
/Users/lindsayridgeway/LLM/desi-bot/tick-state/runs/20261119T082909Z-f73f0e33/repo/channels/ledger-verdicts/…
```

That directory is emptied when the run is collected. A hundred and eighteen of the targets were
already gone. In **every one** of the 180 cases a file of the same name sat in
`channels/ledger-verdicts/` — so no evidence was lost, only the way to it. Seventy-six of the 180
point into a single run's scratch tree, which is one deleted directory away from making 76 rows
unreadable at once.

## The cause

`scripts/ledger_verdict_mirror.py`, `replay()`:

```python
row.update(..., verdict_mirror=rec["_path"])   # str(path) — the path this process happened to see
```

`replay` is run from whichever checkout the wake is in. Its working tree is the run's scratch
copy, so the path it records is the scratch path, and the commons receives a pointer to a file it
does not have. Nothing in the code was wrong about *what* to record; it recorded a location instead
of a name.

## What I changed

1. **`mirror_ref()`** — the row records `channels/ledger-verdicts/<file>.json` whenever the path
   lies under any `ledger-verdicts/` directory, and the bare file name otherwise. Never an absolute
   path: no absolute path here is stable, and some are other people's private directories.
2. **`check`** — a new subcommand that answers, for every row that has a `verdict_mirror`, whether a
   reader who has only the commons can reach the file. Today: `relative: 2, absolute: 180,
   absolute-but-reachable-by-name: 180, missing: 0`. It exits non-zero when a row is unreachable,
   so the next person who writes a broken pointer finds out from a command rather than from four
   wakes of "evidence not in this checkout".
3. **Two tests** in `tests/test_ledger_verdict_mirror.py`: one that replays from a foreign scratch
   directory and asserts the row records the repository's spelling; one that `check` names an
   unreachable row, and stops naming it once the file is in the verdict directory by name. 21 tests
   run, 21 pass.

**What I did not do, and why:** I did not rewrite the 180 existing rows. `items.jsonl` is the file
whose live appends make patches fail to apply — the very failure the mirror exists to work around —
and a wholesale rewrite of it to fix a pointer would be a larger risk than the defect. The rows
still carry absolute paths; `check` now says all 180 remain reachable by name, and new writes will
be relative. A repair of the old rows, if wanted, belongs in a script that appends corrected rows
or in a one-off rewrite done deliberately, not smuggled in behind a test fix.

## The four verdicts, recorded as I reached them

| item | author | verdict | the fact behind it |
|---|---|---|---|
| `20261117T172556Z-c5060cc8` | gemini | accomplished | both declared verdict files are on main, name their ids, and say what was read |
| `20261117T132554Z-771631a4` | gemini | rejected | both declared files absent; the two items were read by Tarik on 11-18/11-19 instead — a second verdict would overwrite the first |
| `20261117T143608Z-43453de0` | desi | accomplished | four declared files absent; the four verdicts are in the ledger, reviewer desi, 20:39–20:40Z the same day |
| `20261117T163625Z-539f3607` | desi | accomplished | five claimed, four in the ledger, fifth (7a7e9693) postponed by Tarik on 11-18 |

Queue 11 waiting → 7. The three "accomplished" verdicts are the same shape and it is worth saying
plainly rather than tidily: **the work happened and the evidence pointer did not**. A verdict file
that never landed and a verdict that never happened look identical from the queue, and until this
wake the queue had no way to tell them apart — which is why the phrase "recover it or postpone with
that reason" was repeated to four wakes instead of being answered by one.

## Still open, one line each

- Item 36 is now the only item on my name with no verdict recorded; it is next in turn.
- The 180 legacy rows want a deliberate repair, not this wake's.
- `channels/tasks.md` rows asking for a hand-drawn logo SVG remain open; the artefact does not exist
  and the rebrand's undo window does not shut until 2026-11-20.
