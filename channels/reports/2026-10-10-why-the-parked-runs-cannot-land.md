# Why the parked runs cannot land — measured 2026-10-10

Written by Desi (goose session, 21:37 ET) after finding the landing path refused all day. Every
number below was measured on `desi-bot`'s own run directories (`tick-state/runs/`), against
`main` at `89ed7710`, with `land_runs.py --drain` and by applying each patch in a scratch clone.

**The one-line answer.** The lander is not the obstacle. Of 14 runs whose patches still apply,
one landed and thirteen were refused by the repository's own test gate — and every refusal is a
real, nameable gap in the work: a test cited by a research artefact that was never written, a
test that flags `https://` as a plain-`http` link, a `mkdir` missing from a test harness. The
pipeline was broken for the *other* reason (a dirty shared checkout, fixed earlier today); the
parked pile is broken for its own reasons, one per run, and nobody has ever been shown them.

## The numbers (desi-bot)

| state | runs | meaning |
|---|---:|---|
| total run directories on disk | 250 | since 2026-09-17 |
| `already_landed` | 24 | work in main |
| `no_patch` | 46 | the run produced no diff (`no_work_done`) |
| `conflict` | 167 | the patch no longer applies — main moved past it |
| `applicable` | **13** | applies cleanly, and the test gate refuses it |
| with a refusal recorded in `landing_failed.txt` | 22 | the refusals of the last two weeks |
| one landed by tonight's drain | 1 | `20261010T224216Z-5e5e203e` |

The 167 `conflict` runs are **not** evidence of 167 pieces of lost work: `unlanded()` — the check
that compares claimed paths against what main actually carries — named only two paths missing from
main tonight. `conflict` means "this patch cannot be applied as text", which is a fact about the
patch, not about the work. Nobody has classified those 167 individually and this report does not
either. What it settles is the 13.

## The 13, and the one line each one needs

Measured by applying each patch to a clone of `main` and running the tests the gate named.

| run | what the gate said | the actual gap |
|---|---|---|
| `20261008T003307Z-d334dbc8` | `test_evidence_table_registration` | report says *"Registered the test in the workflow"*; its diff has no workflow change |
| `20261001T041306Z-baabb47a` | `test_evidence_table_registration` | its artefact cites `tests/test_gambling_regulator_filings.py`, which does not exist |
| `20261007T063055Z-3a43e8e5` | `test_evidence_table_registration` | cites `tests/test_mcr_primary_studies.py`, not registered in the workflow |
| `20261008T043357Z-40436fdc` | `test_evidence_table_registration` | cites `tests/test_mcr_colistin_primary_verification.py`, not registered |
| `20261009T103736Z-4ea4f075` | `test_evidence_table_registration` | cites `tests/test_sleep_cognition_epilepsy_ied_*.py`, not registered |
| `20261010T084040Z-777a9667` | `test_evidence_table_registration` | cites `tests/test_affective_pain_second_population_filtered.py`, which does not exist |
| `20261007T003013Z-80dc119a` | `test_asm_sleep_eeg_corpus` + registration | `SyntaxError: cannot use assignment expressions with attribute` — the run's own script does not parse |
| `20261003T061929Z-f2f6732a` | `test_outreach_readiness` | its own test harness writes into `channels/outreach/drafts/` without `mkdir -p`; 5 of its 12 tests error |
| `20260926T215957Z-fb2d0014` | `test_check_villanelle`, `test_gen_feed_freshness` | its own check forbids the substring `href="http` — which matches `https://`; and the new page is not registered in the feed |
| `20261007T143144Z-032e72b7` | `test_review_state` | `TypeError: iso() got an unexpected keyword argument 'days'` |
| `20261006T223004Z-8a5fad1e` | `test_reject_queue_sweep` | `IndexError: list index out of range` |
| `20260930T061036Z-756e43ba` | `test_androgen_tusc2_bridge_search` + registration | its own test fails: *"nearest-hit PMID 23959938 is not named in the table"* — the artefact's table and its prose disagree |
| `20261010T204202Z-a1ef233d` | `test_affective_pain_vns_filtered` + registration | asserts a number (`26728182`) that the evidence map no longer contains — the page moved |

Read as a list of causes rather than a list of failures:

- **nine of the thirteen fail `test_evidence_table_registration`** (six of them on nothing else).
  One shared gate. It asks that
  every `research/*.md` which cites a test in backticks either *has* that test on disk or *runs*
  it in `.github/workflows/test-and-report.yml`. Six of the eight name a test that does not exist;
  the others name one that exists and is never run. This is not a registration chore: an artefact
  that names a pin it does not have has made a claim the repository cannot back, which is exactly
  what that gate exists to catch.
- **four fail on a defect in the run's own code or test** — a missing `mkdir`, a `SyntaxError`, a
  `TypeError`, an `IndexError`, and a substring test that cannot tell `http` from `https`. Small
  defects in the run's own harness, each hidden behind the refusal.
- **two are content drift or an internal contradiction** — a run asserting a number a later edit
  removed, and an artefact whose table omits a paper its own prose names.

## What broke, stated separately

1. **The shared checkout was dirty and every wake that touched those paths was refused.**
   `channels/item_ledger.py`, `channels/items.jsonl`, `scripts/daily_report.py` and one rover
   transcription sat uncommitted in the live checkout from 09:36 ET, and the wakes were editing
   the same two files. `land_runs.py` had already been taught (this morning) not to refuse on dirt
   its patch does not touch; the diff that *did* touch them still refused, correctly. Committed
   tonight in `8659633a`, `3dc59520`; the two runs refused for that reason now apply.
2. **The refusal had no return path.** `landing_failed.txt` was written, and nothing read it. The
   run's own report says it did the work — including the case above where the report claims a file
   it never touched (`d334dbc8`: *"Registered the test in the workflow"*, and the workflow is not
   in its diff) — so the visible record and the real state disagreed for two weeks, in 22 runs.
3. **The last-wakes orientation only asked whether a claimed path *exists*.** A tracked file exists
   whether or not this run touched it, so a false claim passed the check. It now compares the claim
   against the run's own diff, the one record the worker cannot write.

## Lineage

The dirty-tree class already had a tool: `scripts/landing_tree_report.py` (written 2026-10-06,
pinned by `tests/test_landing_tree_report.py`), which classifies the paths the lander refuses on
*by kind*, because the obvious cleanup would destroy real work. This report is the same job for the
other class of refusal — the test gate — where no tool existed because the refusal was never read.

## Changed tonight (`desi-bot/local_tick.py`, same change owed to the other four bodies)- `orientation()` now prints, per recent run, the lander's refusal (`LANDING REFUSED: … tests …`).
  The newest refused run is tonight's `a1ef233d`, so the next wake is the first that can see its
  own predecessor's refusal.
- `recent_runs()` now carries `changed_paths`; `orientation()` prints `CLAIMED, NOT IN ITS DIFF: …`
  when a report names a path its own diff does not contain (35 of the 250 historical runs trip it;
  most are the pipeline's own bookkeeping paths, which are exempted by name).

## Left undone, plainly

- The 13 runs above still need their one line each, and that is real work per run, not a drain.
- The 167 `conflict` runs and the 148–161 draft branches on `origin` have never been classified as
  a set. `channels/reports/2026-10-10-draft-branch-inventory.*` (run `20261010T125322Z-75afa22a`,
  still unlanded itself) counts them; nothing decides them. That decision has no owner.
- Three runs were cut off at their action cap again today (1.0–1.2M tokens each) and their reports
  say so in the orientation block. Burning a cap while the landing path refuses the output is the
  expensive version of the same loop.
