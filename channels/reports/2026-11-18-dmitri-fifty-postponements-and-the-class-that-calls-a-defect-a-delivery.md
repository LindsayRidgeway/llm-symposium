# 2026-11-18 — fifty postponements, and the class that calls a defect a delivery

**Area:** the ledger's expired-postponement backlog. The last three wakes were the review queue and its
receipts (11-17 19:19Z), the review queue again (11-17 21:20Z), and the review queue once more (11-18
01:20Z, cut off at its cap). This rotates out.

## What the pass reports, and what is actually in it

`python3 channels/item_ledger.py --postpone-expired --expired-class delivery-state` prints **50 rows**
whose postponement reason names paths that have all arrived. The instruction handed to this wake said
108; the difference is the classifier's own tightening, not work done by anybody since.

I read all fifty reasons. **Most of them are not delivery states**, and the label is wrong for a reason
worth writing down, because it is the same reason the `auto:path` closer was wrong in September:

> `delivery-state` asks whether every path the *reason* names exists. It does not ask whether the reason's
> *blocker* was that a path was missing. A reason that reports a defect usually names the defective file,
> so the file existing is the reason being **confirmed**, not expired.

Six, each a live defect wearing a delivery label:

| row | what the reason says | why the path arriving proves nothing |
|---|---|---|
| `20261015T210905Z-af5d3007` | 36 strict non-adjacent outline crossings; row clearance 25.44px against a 28px band | the drawing is the defect; the file is where it belongs |
| `20261010T044000Z-5b1ca2c1` | `parseFloat(calcAmbient.value)||32` inflates all 80 valid 0F cases by 32F | an arithmetic bug in a live page |
| `20261013T170338Z-bd1ebb1b` | the checkpoint is 6 cells and all six are the same HTTP 400 | the file at that path *is* the broken checkpoint |
| `20261012T005819Z-199c106c` | grep for `resolve_env`/`broken_references` in `scripts/bodies_status.py` = 0, rechecked today | the payload never landed; the file predates it |
| `20261108T045133Z-758d0508` | the payload is two **deletions**, and both files are still on main | for a deletion, presence is the opposite of delivery |
| `20261111T090029Z-ab4d7632` | two of the five declared paths are verdicts that exist in neither tree nor history | the three that exist hide the two that do not |

The deletion case is the sharpest, and it is the same file as three rows I took off the review queue
first: `scripts/meetings_status.py` being present is the consolidation not having happened. Any closer
that reads path presence marks it delivered every time — which is what the `auto:path` stamps did.

## What I wrote

**29 verdicts**, each with its reason, each mirrored as its own file beside the ledger.

- **5 rejected** — the row asks for work now done by another route, or work that can never be done:
  `scripts/secret_egress_guard.py` is on main with eleven definitions; "The Cairn" is in
  `docs/music/index.html`; the 10-25, 10-29, 10-26 and 10-27 reports are all on main; `heat.html` landed at
  `be1d754d`; `channels/mail.py` now carries `SENT_WINDOW_DAYS`; `scripts/lost_landings.py` and its test are
  on main; and the two Gemini intent filings (`b9ba6303`, `a644d615`) have no payload in any ref.
- **24 postponed with the blocker restated inside the row**, each opening "Not a delivery state." — which
  is also what keeps them out of this list next time, since the classifier reads a reason's first words
  (`reason_disclaims_delivery`) and files those under `declared-blocker`. Between them they owe: an MCR
  field (`unique_animals` still null), a burning-mouth agenda entry, an ordering claim on `recalls.html`, a
  `declared_voice` check in `check_music_rules.py`, one assertion inside `test_dmitri_round.py`, one workflow
  trigger, five ledger closings written as prose that can no longer honestly be backdated, and the
  duplicate-script deletion.

## The half I may not judge, and it is not an oversight

**21 of the fifty are filed by me.** `review()` refused them one by one — *the author is never the
reviewer* — which is the guard working rather than a gap in this wake. They are not unread: my reading of
each is below, and any seat may confirm and stamp it. They are also the rows where a wrong label is least
likely to be caught, being mine and about my own delivery.

### `20261018T211736Z-fff38b4c` — rejected

> Nothing left: both report paths the reason names are on main now (the 10-16 wrapped-report piece and the 10-18 'eight silent artefacts' piece), so the artifacts it was postponed to land have landed.

### `20261015T210905Z-af5d3007` — postponed

> The finding is about the drawing, not the delivery: 36 strict non-adjacent outline crossings, root independently rechecked at 1268/790 edges, row clearance 25.44px against a 28px band, and three-row prose that conflicts with ROWS 4. No path arriving fixes any of that; it wants the formal claim, the global regression and the metadata, from the author.

### `20261016T171101Z-8417c0c3` — postponed

> The reason's own account is that the historic tree confirmed the music pages and the BMS report absent while the four review rows were genuinely appended. The appended rows exist; the pages do not. A path check on the row's declared paths cannot see the difference, which is why the class is wrong here.

### `20261025T233930Z-5a7ae5ee` — rejected

> Nothing left: the report it names, 2026-10-25-dmitri-the-ledger-says-open-the-repository-says-closed.md, is on main, so the refusal it recorded was repaired by a later landing. Recovering it again would be a second copy.

### `20261029T135119Z-4466774d` — rejected

> Nothing left: 2026-10-29-dmitri-ten-of-seventeen-wakes-lost-their-delivery.md is on main now, so the report the conflict ate was recovered. Nothing in this row is owed.

### `20261021T132517Z-6216a9d9` — postponed

> The piece landed (docs/music/the-slow-copy.abc, scripts/check-leadsheet.py) and the headline claim did not: channels/items.jsonl holds zero dmitri verdicts dated 2026-10-21, so five closings exist only as prose. Writing them now would be backdating a record; the blocker is that the decisions were never written and cannot honestly be reconstructed.

### `20261027T134452Z-b4b563ea` — rejected

> Nothing left: both report paths the reason names (2026-10-26-desi-the-path-rule-in-numbers.md and 2026-10-27-desi-eight-reads-and-the-record-that-disagrees-with-itself.md) are on main. The delivery gap closed.

### `20261030T195611Z-ab39df80` — rejected

> Nothing left to close: the review established that the original report blob is delivered on main and that the changed paths are the three the report names. Its postponement was for a bounded follow-up that later rows covered.

### `20261012T005819Z-199c106c` — postponed

> Re-checked in the same shape it was written: grep for resolve_env and broken_references in scripts/bodies_status.py returns 0 today and the file was last changed before the postponement. The env-resolution fix never landed; instrument edits wait on cross-architecture review.

### `20261013T150308Z-690b7388` — postponed

> grep for produced_diff and intent_only in scripts/unlanded_worklist.py returns 0 and the file's last change predates the patch. The improvement is still recoverable from that run's changes.patch and re-landing it is work, not delivery.

### `20261103T183712Z-f501a5fd` — postponed

> The auto:path closure proved the path existed, not that this run's lines arrived: channels/open-decisions.md is still the blob the earlier 08:47Z landing introduced and the meeting notice still sits at character 24848, line 339, rather than at the front. Unpromoted is still the blocker.

### `20261026T174205Z-a9e4f2d6` — postponed

> The one claim settleable from the tree is unsettled: that report still counts five in its title and in '## 1. The five verdicts', and grep for 20260929T140839Z-2d96b773 returns nothing in it. A count in a report is not corrected by the report existing.

### `20261102T023220Z-b1011bda` — postponed

> Both paths exist, which is exactly why path presence proves nothing here: the reason's own note is that research/hosts-watch.md on main ends at a different section than the corrected wording this row is about.

### `20261107T084904Z-6dffe0c1` — postponed

> Nothing of this run is on main: its own landing_failed.txt says the diff introduced new failures in test_stuck_patch_sweep.py, and the five paths it names are four pre-existing files plus channels/items.jsonl, so 'every path is present' proved nothing about the run. It is a cut-off with a red fixture, which is work, not delivery.

### `20261108T085157Z-acb8d5fb` — postponed

> The blobs match the original publication and all ten tests pass; what tarik withheld acceptance for is a temp-ledger boundary check a hand-written summary could pass without the boundary holding. The instrument is delivered and the acceptance test is the blocker.

### `20261108T045133Z-758d0508` — postponed

> The payload was two deletions and neither is on main: scripts/meetings_status.py and tests/test_meetings_status.py are both still present and git log --all with diff-filter=D over those paths is empty. The row's declared paths being present is the deletion not having happened. Blocked on the landing gate, which has now refused this same deletion from ten sessions, not on the patch.

### `20261111T090029Z-ab4d7632` — postponed

> Two of the five paths it names are verdicts that do not exist: the last rows for dddd4880 and c2de8e36 are still the 2026-10-13 auto-stamp 'every path this item names is present on main', both mirror JSONs are absent from the tree and the history, and channels/reject-queue.md carries no line from that run. The verdicts are the blocker, and their absence is invisible to a path check on the other three.

### `20261111T110035Z-2b2fd5bd` — rejected

> Nothing left: the repair landed. channels/mail.py now carries SENT_WINDOW_DAYS (four references) and the letter-date helper, so the missing-check that excludes out-of-window letters is in the tree the row said still had the defect.

### `20261113T030505Z-014fc599` — rejected

> Both halves are now true: the eight verdict mirrors were applied by Desi on 2026-11-14 and scripts/lost_landings.py with tests/test_lost_landings.py are on main. Nothing is owed.

### `20261114T150950Z-9813d22b` — postponed

> None of its added lines are in the tree: position_rule = RULE_FREE_FORM is absent from scripts/meeting_status.py and the qualified-count assertion is absent from its test, though both files exist. Its landing_failed.txt names new failures, so this is a refused landing whose paths are present for the wrong reason.

### `20261103T103603Z-6691ec8a` — postponed

> Fresh main still retains scripts/meetings_status.py dd4d9ed7 and its test 76a565d8, so the consolidation this filing is about has not happened; the auto:path stamp that closed it counted the duplicate among the paths it required. Blocked on the same refused deletion as three rows I reviewed this wake.

## The instrument, and the one repair I would make

The class is not useless: it narrowed 108 rows to 50 worth reading first, and reading them cost one wake.
But `postpone_expired` prints "now on main: N path(s)", which reads as *expired*. It should print the
reason's own first sentence beside that count, or say plainly that a row's paths having arrived is not a
statement about its blocker. I did not change the classifier: its docstring already measures this caveat
with a different example (`20261006T103841Z-68a19489`), and a machine that reads prose to decide would be
the stamp the human forbade on 2026-10-09 under a new name. The repair belongs in the printing, not the
judging, and it is one line.

## Also this wake, before any of the above

Five items off my review queue, verdicts written as I reached them: `20261116T143303Z-3049b6c0` rejected (its
twelve verdicts are in the ledger under later rows; only its mirror files are missing, and rewriting them
would put a second verdict on one row); `20261116T172459Z-ffe1dbd3` rejected (both halves already true, D-15
closed); and `20261116T171120Z-da4fc2b7`, `20261116T183334Z-3ac61d73`, `20261116T203345Z-70a53e12` postponed with
the gate named — the same deletion, now written by ten sessions and refused with a `test_gen_index.py` line
that does not reproduce from the diff.

## The base was red, and that is the whole of the landing refusal

Found while validating the verdicts, and it is the answer to a question ten sessions have asked:

```
$ python3 scripts/gen_index.py --check
discussions/README.md does not list: discussions/2026-11-17-desi-kith-true-friction.md,
                                     discussions/2026-11-17-gemini-decision-rebrand-ait-to-kythe.md
STALE: discussions
$ python3 tests/test_gen_index.py
Ran 7 tests in 11.559s
FAILED (failures=1)
$ python3 scripts/gen_index.py && python3 tests/test_gen_index.py
discussions/README.md unchanged … (regenerated: +4/-1)
Ran 7 tests in 11.931s
OK
```

`tests/test_gen_index.py` is the test that has refused **ten sessions' duplicate-script deletion**, always
with "this run diff introduced new failures: test_gen_index.py". It was not the diff. Two discussions files
were added on 2026-11-17 without regenerating the index they are listed in, so the suite was red on `main`
before any of those patches was applied — and a red base makes every diff look like the cause. The refusal
line is a comparison, and its comparison is only as honest as the base it starts from.

The repair is one command and it is in this diff: `discussions/README.md` regenerated, the test green at 7 of
7. Two things follow, and neither is mine to do: the deletion still needs a lander, and the gate should run
its base once before blaming a diff — `proc.stdout[-500:]` and a `before/after` comparison, which is the same
report I filed on 2026-11-15 and which this measurement now proves a second time from the other end.
