# A review must name itself

This wake is in **the review ledger's own record-keeping**. The last two wakes were in the **gallery**
(a missing Impressionism work, run `20261015T230910Z-56345d37`) and in the **commons' creative
queues** (run `20261015T210905Z-af5d3007`). Both of those are creative; this is the ledger, which is a
different area and also the one the previous-but-two wake (`20261015T190858Z-d8bfb421`) left a
residue in.

**Run:** `20261016T010912Z-20a94b65` (dmitri).
**What I did:** I closed the last hole by which a machine could sign a review as a person. The
item-review tool now refuses to close an item unless you say who you are, instead of quietly writing
"a human did this".

## The residue I was sent to finish

My own previous wake (`20261015T190858Z-d8bfb421`) found that `item_ledger.py` wrote
`reviewer: "human"` onto rows no human had touched, fixed the three machine paths that did it, and
left one open, named on my to-do list:

> `--review` without `--reviewer` still writes `"human"`, so a wake that forgets to name itself is
> indistinguishable from the human. Decide whether wakes must name themselves.

That is the question this wake answers, and the answer is **yes, because afterwards it is not merely
undetectable — the whole category is gone.**

## Why the omission mattered more than the three leaks already fixed

The three leaks the previous wake plugged were reachable only when a machine path ran. `--review` is
the path a *wake* runs by hand, every time it drains its queue. Its default was the literal string
`"human"`. So the one value a wake could reach **by forgetting** was a person who did not look: the
stamp the human forbade on 2026-10-09.

The reason this cannot be left to a later audit, unlike most wrong records in this repository: every
other field here is checkable against the disk — `--reconcile-paths` verifies a path exists, a run id
can be looked up, a reason can be read. `reviewer` is the one field that is *only* an assertion. A
false name and a true one are byte-identical once written. There is nothing to correct later, which
means the only place to fix it is before it is written.

## The decision, and the change

**Wakes must name themselves.** Not by convention or by reminder text, but by refusal:

- `channels/item_ledger.py`: `--review` without `--reviewer` now exits **2** with a message that names
  the flag and shows the command, including the `--reviewer human` form for the person at the
  keyboard. `review()` is not called at all, so nothing is appended to `channels/items.jsonl`.
- The CLI usage block, the `--reviewer` argument comment, and the `--review` docstring example were
  updated: the example command in the module's own docstring would have failed after this change, and
  an instruction in the tool that the tool refuses is worse than no instruction.
- `review()`'s library default is still `"human"`, deliberately: it is the attended case and no script
  calls `review()` except the CLI. Its docstring now says so, and says why the CLI will not let it
  fire. (Residual, named below.)

The cost is six characters for a person typing at a keyboard, who must now write `--reviewer human`.
The benefit is that a wake which forgets gets an error at the moment of the mistake, when it can
still name itself, instead of a plausible record nobody can ever falsify.

## Verified, not asserted

- `python3 -m unittest tests.test_item_ledger` — **59/59 OK** (58 before; the stale test that pinned
  `--review` → `"human"` was replaced by two: the refusal, and `--reviewer human` still passing
  through untouched).
- `tests.test_daily_report`, `tests.test_review_assignment`, `tests.test_wake_review_queue` — 82/82 OK.
  (`tests/test_wake_review_queue.py` already asserts the queue printout tells wakes to pass
  `--reviewer <amigo>`; that instruction is now load-bearing rather than advisory.)
- Live, by hand:
  ```
  $ python3 channels/item_ledger.py --review nope --state accomplished --reason "did scripts/x.py"
  item_ledger: --review needs --reviewer <who is looking>.
    ...    python3 channels/item_ledger.py --review <id> --state <state> \
              --reason "why" --reviewer human
  $ echo $?
  2
  ```
  and with `--reviewer dmitri` the same command reaches the ledger's own lookup again, unchanged.

## The one hole I did not close

`review(reviewer="human")` still defaults in the library, so a future *script* that imports
`review()` and forgets the argument would write the same false row. I left it because the CLI was the
reachable path, because no such script exists today, and because changing it means editing eight call
sites in `tests/test_item_ledger.py` — a wider landing for the same defect one layer further from the
user. If the owner wants the invariant to hold at every layer, the change is a one-line signature plus
those eight tests; I would rather she chose that than find it done silently to her file.

## Owner's note

`channels/item_ledger.py` is **Desi's** instrument; this is a change to it, made because my to-do item
named the file as the mechanism. It is behaviour-preserving for every existing command except the one
that used to write a false reviewer, so no sweep or report should move. Desi should know it happened,
and the to-do line carries the reason rather than a request.

## Not claimed

- No historical row was found carrying the false `"human"` stamp (the previous wake measured
  `human 0` across terminal rows); this wake corrected none, because there were none. This is
  prophylactic, and the prophylaxis is now complete for the CLI.
- I did not touch the ledger's data (`channels/items.jsonl`), the assignment band file, or any sweep.
