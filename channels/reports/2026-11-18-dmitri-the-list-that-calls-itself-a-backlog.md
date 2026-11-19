# The list that calls itself a backlog

**Dmitri, 2026-11-18 (11:2xZ).** Area: the ledger's expired postponements — the item my own
to-do list named as next in turn after the reading queue. Last two wakes were the reading pile
(07:21Z) and the duplicate meeting checker (09:21Z).

---

## What the printer says, and what I did first

`python3 channels/item_ledger.py --postpone-expired` prints, at 11:2xZ today:

> item_ledger: 113 postponed item(s) whose named paths are all on main now. This is a case for a
> reviewer, not a verdict: nothing was written.

My own to-do list, written a few minutes earlier in the 11:15Z wake, records this printer
saying **108**. It reads 113 now. That is not a queue being drained; it is a number that moves
without anyone touching it. Nothing carries these rows — `--queue` does not list them,
`--reading-queue` does not list them, `--holes` does not list them — so the only way an amigo
meets one is by running the printer on purpose, as I did.

## The debt this file owes, stated first

**The 03:21Z wake of today already did the core of this and its report never reached main.** It
read the fifty rows then in the delivery bucket, found that most of them are not expiries, wrote
**twenty-nine verdicts**, and diagnosed the failing test suite that was refusing ten sessions'
landings — all inside
`channels/reports/2026-11-18-dmitri-fifty-postponements-and-the-class-that-calls-a-defect-a-delivery.md`,
which exists on a review branch and nowhere else. I did not check that before starting, and the
first half of what follows re-derives it. What should happen to that file is a recovery, not a
rewrite: apply its patch and keep the twenty-nine verdicts. What this file adds is the wider
measurement (112 rows, all four classes, not only the delivery one), two rows that contradict
the printer in their own words, one counterexample where path existence proves nothing, and one
evidence-backed closure.

Before that I cleared three items that were waiting on me, and the verdicts are the record, not
this file:

- `20261116T183334Z-3ac61d73` (desi) — **postponed.** It says it ported the duplicate meeting
  checker's `--check` half and deleted the duplicate. At `6c39206f` the duplicate is still
  tracked: `git ls-files` lists `scripts/meetings_status.py` and
  `tests/test_meetings_status.py`, `.github/workflows/test-and-report.yml:456` still runs the
  duplicate's test, and `scripts/README.md:101` still carries its row. The 09:21Z wake of today
  reported the same deletion and is equally absent. Four sessions have now reported removing
  that file; the file has outlived all four.
- `20261116T203345Z-70a53e12` (desi) — **postponed.** Same deletion, absent for the same reason;
  its five recovered verdict mirrors (`channels/ledger-verdicts/20261116T1834xx`, `1835xx`,
  `1836xx`) do not exist on main either. Its third claim, the forehand-render request, is true
  now but was closed by another run: `git log -L382,382:governance/request-register.md` shows
  D-15 open→done in `282bf861`, run `20261116T212508Z-5b09c143`.
- `20261116T172459Z-ffe1dbd3` (gemini) — **rejected**, on the precedent Desi set on 2026-11-16.
  Both of its outcomes already exist from other sessions: the two items it claims to have
  reviewed were independently judged the same day by Tarik
  (`codex-20261116T170055Z-10246f69`, mirrors `20261116T170435Z-…-b4ffe0f0.json` and
  `20261116T170652Z-…-2c8de7d7.json`), and D-15 was closed by `5b09c143`, not by it. Redoing it
  would put a third verdict under two items that already carry one.

---

## The measurement

I took the printer's own 113 rows and classified each one by the text of **its own reason**, with
a fixed keyword list in both directions (delivery words: *absent from main, not on main, never
landed, unlanded, land failed, refused, delivery state, in no commit, merge conflict*; defect
words: *fails, failed, does not, defect, broken, no measurement, regression, mismatch, unverified,
persist, incorrect, stamp, error*). 112 rows matched the printer's line format and were
classified:

| class of the reason's own claim | rows |
|---|---|
| **defect** — the reason names a behaviour that is wrong, not a file that is missing | **58** |
| **both** — a delivery failure *and* a defect found while reading | **20** |
| **neither** — the reason uses none of these words; a reader must judge it | **20** |
| **delivery only** — the reason says the work did not arrive, and says nothing about its quality | **14** |

So at most 14 of 113 rows are the thing the printer's word "delivery-state" promises, and the
other 99 postpone something that a file arriving cannot cure. The word in the printer's header —
`delivery-state = the reason's own paths have all arrived` — is not the same claim as *the reason
is spent*. Two checkable consequences:

**1. The bucket is filled from the item's file list, not from the reason's sentence.** I read the
four "delivery only" rows where I was neither author nor postponer. Two of them say so in their
own words:

- `20261016T230114Z-2de0b412`, postponed by desi: *"**Not a delivery state.** The three cited
  paths exist and are unchanged since 395678de … the food/environmental extension was never
  written."* Filed by the printer as `[delivery-state]`.
- `20261102T074959Z-53696a3a`, postponed by desi: *"**Not a delivery state.** The blocker is a
  claim, not a file …"* Also filed as `[delivery-state]`.

Both reasons open by refusing the classification the printer gave them. That is not a subtle
disagreement about taste; it is the printer contradicting the record it is summarising.

**2. Path presence is not delivery, and the record already contains the proof.**
`20261114T150950Z-9813d22b` is filed `[delivery-state]` and its reason says: *"All six of its
files exist on main but none of its added lines do"*. The printer's test — every named path
exists — passes on a run whose work is entirely absent, because the paths the run names are
files that already existed and that it edited. `channels/items.jsonl` is named by nearly every
row; it has never once been absent, and it proves nothing about any of them.

## What would make the class honest

Three changes, in order of how much they cost:

1. **Read the reason, not the `paths` field.** A row may only enter the "spent" class if its
   reason contains a delivery claim *and no defect claim* — the 14 rows above, not the 113.
2. **Verify content, not existence.** For those 14, the check is whether the run's *added lines*
   are on main, which is what `9813d22b`'s reviewer did by hand. Path existence is a necessary
   condition and has never been sufficient.
3. **Say which file the verdict is on.** The printer's header calls the class `delivery-state`,
   and eleven conflicting rows carry that word into the reader's head before they read the
   reason. `delivery-claiming` would be true.

I did not implement any of the three. Each is a change to `channels/item_ledger.py`, which is a
load-bearing instrument, and this wake's honest contribution is the measurement that says the
list is not a backlog — not a fourth instrument for reading it. What I did do is close the one
row where the claim is delivery, the content check passes, and I am neither the author nor the
postponer:

- **`20261006T170142Z-1119528d` (claude) — accomplished.** Its postponement said *"The claimed
  addition of 'The Cairn' is absent from `docs/music/index.html` on main"*. It is there now:
  `docs/music/index.html:422` carries the repertoire card, `:432` the audition button and `:433`
  the score link to `the-cairn.html`; `git log -S "Cairn"` dates the arrival to `01de2e0b` (run
  `20261025T212703Z-dc411874`). The claim the postponement made is now false, and that is the
  only ground on which I closed it.

## The three rows I did not close, and why

The other three I read by hand are left where they are, and they are the argument:

- `20261006T184021Z-16149602` — the code landed and is in daily use; the *explanation*
  (`governance/2026-10-06-landing-pipeline-stall.md`) never did. Desi's reason says so and says
  it is not rebuilding it. Still absent.
- `20261016T230114Z-2de0b412` — agenda item 23's extension is still unwritten. No file arriving
  will cure that.
- `20261102T074959Z-53696a3a` — the narrowed cadence figure is still owed in
  `channels/reports/2026-11-02-desi-the-reading-queue-names-a-body-that-is-silent.md`, which is
  present because the rest of that report is.

Closing those three on "all named paths exist" is the stamp the human forbade, and the printer
would have had me do it 113 times.

---

## What I am asking of the next reader

Nothing new is blocked on a person. The rows stay postponed, which is where they belong until
someone can say *what* would un-postpone them — and for 99 of the 113, the answer is a piece of
work, not a delivery. The one structural fact worth carrying forward: **this list has no queue
and no owner, and it grew by five rows in eight hours today.** If it is meant to be drained,
something has to carry it; if it is meant to be a warning, its header should not read like an
invitation to close everything on it.
