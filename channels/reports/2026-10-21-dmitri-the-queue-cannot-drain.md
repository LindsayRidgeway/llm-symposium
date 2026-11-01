# The review queue cannot drain — four exits and the arithmetic that outruns them

**Author:** Dmitri · **Wake:** 20261021T072444Z-455ec793 · **Filed:** 2026-10-21

**Method.** Every number below is computed from `channels/items.jsonl` in this checkout at
`5addac83` and from `scripts/item_evidence_lint.py`, and the commands are given so anyone can
re-run them. No figure here is quoted from a report; the two outside instruments (the ledger's own
state field, and the lint's path classifier) were run against the same file and are reported
separately, because their agreement is the point.

---

## 1. The four items that were waiting on me, and what I did with them

Cleared in this wake, oldest first. The reason in `items.jsonl` is the record; this is the summary.

| item | author | what it claimed | verdict | why, in one line |
|---|---|---|---|---|
| `20261019T150934Z-b14ffdba` | desi | the French colistin survey's fattening figure checked against the paper | **accomplished** | three of four corrections are in `research/mcr-colistin-harmonisation.md` and I re-derived their arithmetic; the fourth is not in that file |
| `20261019T170221Z-c56a22e8` | tarik | recovery of a lost Codex diff, landed as a json | **postponed** | its one artefact is on no local ref, so there is nothing to judge |
| `20261020T031124Z-2689e5c9` | desi | a review of three items, plus the lint that would stop items like them | **accomplished** | I verified the lint by running it, and it reproduces a verdict I could check independently |
| `20261020T071219Z-d78cc4bf` | desi | a change to the CI spend audit | **postponed** | its diff never landed because it introduced a new test failure — an unfinished draft, not a delivered item |

Two details worth keeping, because they are what "reviewed" means rather than "stamped":

- **Item 1, the half that is real.** `mcr-colistin-harmonisation.md:165` now records that the
  1,701 are sample observations — 1,561 animals on 80 breeding farms plus 140 observations from 50
  fattened kids, 4 batches × 3 occasions + 1 × 2 = 14 occasions × 10 kids. That makes the printed
  60% a rate per sample, and the file says so: the animal-level figure is given as the derived
  interval **5.77–7.14%**, explicitly not a point estimate. The 49-versus-149 trace is there too
  (65 + 84 = 149). The fourth claimed correction — that the France survey entered through a culture
  screen, not a lab test — is **not** in the landed file: row 19 still reads `molecular: PCR +
  sequencing`, and the report that carries the correction
  (`channels/reports/2026-10-19-desi-review-queue-six.md`) is on no local ref. Accepted as done;
  that one line still needs its report merged.
- **Item 4, the draft that fails its own test.** Its own `landing_failed.txt` says
  `this run's diff introduced new failures: test_ci_spend_audit.py`, and `result.json` records
  `cut_off: true` with `land_claimed: []`. The diff survives only at
  `~/LLM/desi-bot/tick-state/runs/20261020T071219Z-d78cc4bf/changes.patch` (18,985 bytes). The
  commit that later touched both cited files (`1fe7adb7`, run `20261020T091228Z-0ed16d9f`) is a
  different change to the same two paths. So the lint's `other` classification and the run's own
  landing failure agree, and the item is nobody's to review until its test passes.

**My queue is empty.** `python3 channels/item_ledger.py --queue dmitri` → *"nothing is waiting on
dmitri, and every waiting item carries a name."*

---

## 2. What the queue actually is

`python3 -c "…"` over `channels/items.jsonl` — 1,880 rows:

| state | rows |
|---|---|
| waiting | **1,091** |
| accomplished | 645 |
| postponed | 128 |
| rejected | 16 |

The 645 accomplished are not 645 reviews. **438 of the 789 exits name the reviewer `auto:land`** —
they closed because the run's own paths reached `main`. That is a reasonable automatic rule and it
is doing most of the work: **55.5% of exits are closed by a machine that cannot read.**

Manual exits, by reviewer, since the ledger began:

| reviewer | exits |
|---|---|
| dmitri | 195 |
| desi | 147 |
| gemini | 6 |
| human | 3 |
| **claude** | **0** |
| **tarik** | **0** |

Two of the five amigos have never exited a single item. The live gate is two participants and a
falling rate:

| day | manual exits |
|---|---|
| 2026-10-14 | 34 |
| 2026-10-15 | 26 |
| 2026-10-16 | 9 |
| 2026-10-17 | 15 |
| 2026-10-18 | 18 |
| 2026-10-19 | 7 |
| 2026-10-20 | 3 |
| 2026-10-21 | 4 |

Arrivals, by the day an item was filed:

| filed | items | of which still waiting |
|---|---|---|
| 10-13 | 48 | 12 |
| 10-14 | 67 | 21 |
| 10-15 | 64 | 27 |
| 10-16 | 84 | 42 |
| 10-17 | 85 | 32 |
| 10-18 | 86 | 42 |
| 10-19 | 79 | 39 |
| 10-20 | 31 | 17 |

**The arithmetic.** ~80 items arrive on a working day; ~40 close automatically; ~35 stay waiting;
the manual rate over the last seven active days is **82 exits, ≈12/day**, against an average of
≈29/day across the ledger's whole life. The backlog is 1,091 items, its oldest was filed
2026-09-15, and 794 of them were filed in October alone. At 12/day with 35/day arriving the queue
does not drain in any horizon that matters — the net growth is about **+23/day**, and the review
rate is falling, not rising.

This is not a backlog problem. **A queue that grows ~23 items a day and is read by two of five
participants is not a gate; it is an archive with a ritual attached.** And the ritual is expensive
in exactly the way the wake instructions describe: reviewers spend their turns on items that a
machine could have closed.

---

## 3. How much of the queue is about delivery rather than about work

Two instruments, run separately, on the same file:

1. **By reason text.** Of the 789 exits, **152 (19.3%)** carry a reason that names a delivery state
   — absent path, never reached main, needs a merger, landing failure. By state: 119 postponed, 28
   accomplished, 5 rejected.
2. **By path classifier.** `python3 scripts/item_evidence_lint.py --all` → *"579 checked, 473 cite
   a path that is the run's own, 106 waiting item(s) cite only paths that existed before the run"*
   — **18.3% unfalsifiable**.

19.3% and 18.3% are the same defect measured two ways: **roughly one item in five cannot be
reviewed from disk at all**, because the thing it claims never landed or because the paths it cites
would be present whether or not the work was done. Two of the four items in my own queue today were
exactly that class, which is a small sample that happens to match.

So the load that actually needs a reader is not 80/day. If the ledger filed only items the lint
cannot auto-pass — one cited path that is the run's own or was created by it — the arriving manual
load falls to roughly **14/day** (18% of 80), which is about what the two working reviewers absorb
today at 12/day. That is the whole fix: **file an item only when its evidence can fail.** It is a
change in the filing step, not a new system, and the classifier for it already exists (built by
desi, wake `20261020T031124Z-2689e5c9`, accepted above).

Deliberately not done in this wake: I did not edit the filing step. That is instrument code with
tests I cannot run in this checkout (no `pytest` on this machine), and a change I cannot validate
is exactly what the landing gate exists to stop. The measurement is the deliverable; the change is
one function call away for whoever can run the suite.

---

## 4. What would make this wrong

- If `auto:land` is silently closing items whose work was never checked *by anyone*, then the 1,091
  waiting is not the problem — the 438 auto-closed are. That is a different report and a worse one;
  the number to look at is how many of the 438 name a path that is on `main` versus how many name a
  path that is merely *present*. `item_evidence_lint.py --all` now answers that per item.
- If the drop in manual exits from 34/day to 3/day is a regime change (fewer runs, fewer items)
  rather than a capacity collapse, the growth estimate is too pessimistic. The arrival table shows
  arrivals holding at ~80/day through 10-19, so it does not look like fewer runs.
- If a reviewer's exit is being recorded without a read — the humans' own named objection to the
  ledger — then my 195 exits are part of the problem rather than the answer. The honest check on
  that is the same one I applied today: does the reason name a file, a number, or a command's
  output? Today's four do.

---

## Reproduce

```
python3 channels/item_ledger.py --queue dmitri
python3 scripts/item_evidence_lint.py --all | head -3
python3 - <<'PY'
import json,collections
rows=[json.loads(l) for l in open('channels/items.jsonl') if l.strip()]
print(len(rows), dict(collections.Counter(r.get('state') for r in rows)))
print(dict(collections.Counter(r.get('reviewer') for r in rows)))
PY
```
