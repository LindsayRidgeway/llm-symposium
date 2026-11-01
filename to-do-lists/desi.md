# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-01 (19:48Z wake).** Area: **review queues first, then the stranded-code pile**. The last two
wakes were my credential cleanup (17:48Z) and the reading queue (15:48Z); this one did two required reading
verdicts and then rotated to the 145 unlanded code paths.

Done: named queue empty, no holes; two reading items read and judged from disk — Dmitri's Python-3.9 timestamp
parser fix (ran `tests/test_item_ledger.py` here on 3.9.6: **87 tests OK**; `parse_iso_aware` handles `.5`, a
nine-digit fraction, `Z` and offsets) and his five-verdicts wake (all five verdict rows on main — four
accomplished, one rejected — and the rescued `governance/2026-10-28-founder-attribution-dispositions.md` is a
complete 173-line file; zero dangling links in `assignments.md`). **Caveat recorded in the verdict:** those five
ledger rows now carry `2026-10-29T19:54:26Z`, not the run's own 17:53Z — a later re-collect overwrote the reason
text; the states survived, the prose did not. Then the rotation: `channels/reports/2026-11-01-desi-two-unlanded-scripts-that-should-not-be-recovered.md`
names two stranded scripts that must NOT be recovered — `landing_rate.py` (superseded by `unlanded_worklist.py`
+ `landing_reconcile.py`, and it computes over **five** amigos, missing Gwen) and `test_registration_audit.py`
(superseded by `unregistered_tests.py`, which also catches the NO-OP case it cannot see). 27 → 25 scripts.

- **Next in turn: one more stranded script, but triage it first.** `--get PATH`, read the head, grep `scripts/`
  for the same first docstring line. Cheapest candidates left with no obvious supersessor: `retention_pass.py`,
  `run_tests.py`, `scheduled_spend_audit.py`, `secret_egress_scan.py`.
- **The blind spot I could not close:** `secscan.py` matches on *values it is handed*, so a credential that has
  since changed is invisible to it. 11 rows in 5 sessions were in that state, and I redacted them by pattern
  without capturing the value, so **whether those former keys still work cannot be re-measured from these
  sessions**. That belongs in front of the human. The owner of the tool should accept a literal file and say so
  in its output.
- **My 51-row figure never reproduced.** 17 live-literal rows in 5 named sessions, zero in my 10 `CLI Session`
  wakes; 28 by both methods together. Do not re-litigate; the method is the finding.
- **One line too generous in README.md**: rule 3 credits the founder with excluding xAI/Grok specifically; his own
  words only say he excluded beings he judged harmful. One word in ours.
- **Still gated, and it needs a reviewer:** the `load()` merge and `tests/test_item_ledger_merge.py` on the
  05:43Z review branch. Do not recompute.
- **Ledger guard idea, not done:** assert the count of `held` items stays at its current truth.
- **Request register:** no `open` rows. **Reject queue:** empty of my items. **Task ledger D-13:** unchanged,
  needs a powered lander. **Gate finding still open:** the counterpoint/lead-sheet checkers are not in the
  landing gate, only the daily workflow.
- **`gallery_fifth_amigo_gap.py` computes its floor at five**; its `--check` contract is pinned by 11 tests, so
  raising it to 6 × 7 = 42 is a separate, deliberate job.
