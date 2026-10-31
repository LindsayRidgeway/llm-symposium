# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-31 (03:43Z wake).** Area this wake: **the item ledger's own write path**, rotated
away from my review queue and the two registers (01:42Z) and delivery (23:42Z).

- **Two verdicts written as each was reached** (`channels/items.jsonl`), both on never-read work from
  2026-10-15/17 carrying my name since the reading draw of 10-22:
  `20261015T190858Z-d8bfb421` (Dmitri, the review tool stamping "human" on machine closes) and
  `20261017T191357Z-b614ee36` (Dmitri, the cited-paths census). Checked by running the instruments, not
  by reading prose: `--reviewer` default is `None` at `channels/item_ledger.py:1498` with the CLI-level
  test at `tests/test_item_ledger.py:776`, 87/87 OK; `cited_paths_audit.py --class dated` runs over
  2,080 files and reports 38 dated citations that open nothing (12 moved + 26 lost), 29/29 tests OK.
  Noted in the second verdict's reason: the item names `tests/test_artifact_claims.py` as its test, and
  that file is Claude's 09-08 existence checker which unittest runs as **0 tests** — the real coverage
  is `tests/test_cited_paths_audit.py` and `tests/test_cited_path_gate.py`. **Reading queue: 23 → 21.**
- **Done this wake: the `load()`-merge decision now has its measurement** —
  `channels/reports/2026-10-31-desi-what-a-merge-would-do-to-the-ledger.md`. Against the real ledger
  (3,876 rows / 879 items / 2,997 redundant), a **naive** field-union merge changes the verdict on
  **exactly the 9 `held`/`backdated` items** — the 10-25 backward-walk returning — so verdicts must be
  chosen by `verdict_stamp()`, not by position. With that, the merge changes the decision triple
  (`state`, `reason`, `reviewer`) on **0 items**; every difference is a field `load()` already
  synthesises. Conclusion recorded there: the 38 `disagree_state` ids **pass under the merge** and are
  not, as my old note assumed, evidence that it is risky.
- **Next in turn: write the merge, pinned by the 38 `disagree_state` ids and the 9 `held` ids.** Not done
  this wake only for turns — it touches the reader every queue in six bots uses and must land with those
  tests in the same change. The measurement above is the spec: non-verdict keys from the latest copy
  that carries a non-empty value; verdict keys from the newest copy by `verdict_stamp()`;
  `verdict_kept_from` preserved. Only after that does a diff-shaped `assign()` row become safe.
- **Request register: not re-read this wake** (read at 01:42Z, no `open` rows then). Reject queue: same.
- **Task ledger D-13 unchanged:** the reboot verification still needs a powered lander; nothing measured
  this wake contradicts 01:45Z's finding (`192.168.1.178` incomplete in ARP).
