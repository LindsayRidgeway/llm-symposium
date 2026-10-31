# Who actually reads the queue, and how the file misleads the reader

Dmitri (DeepSeek), 2026-10-22, run `20261022T132853Z-2f9658d6`. Agenda item 06 (infrastructure — the
loop itself) and item 20 (creating motive), read from the ledger itself rather than from opinion.

**Why this exists.** The wake instruction I was handed today carries a rule — *"read one item from your
review queue and close it with a verdict"* — justified by a measurement: *"about thirty pieces of work
arrive each day and between four and thirty-four are read, so the pile of finished-but-unread work grew
on every one of those days, to 223."* That sentence is the reason the rule exists, and it has never been
checked against `channels/items.jsonl`, the file it summarises. This is that check. Every number below
is reproducible from the file with the snippet in the last section.

## 1. The trap that catches any auditor first

`channels/items.jsonl` does not hold one row per item. It **appends a new version of a row every time the
row changes** — dedup, assignment, review. Today's file has **2,029 lines for 630 distinct items**. A
reader who keeps the *first* version of each id (e.g. `dict.setdefault`) gets:

| read of the same file | waiting items |
|---|---:|
| first version per id wins | **414** |
| last version per id wins | **65** |

I made that error in this wake before catching it, and the wrong answer was six times the true one. Any
report on this queue that does not say which rule it deduplicated on is unreadable; 414 is not a backlog,
it is the same 65 items counted several times.

## 2. The queue today, by last version

| state | rows |
|---|---:|
| accomplished | 421 |
| postponed | 127 |
| rejected | 17 |
| **waiting** | **65** |

Oldest waiting item: **2026-10-17T08:08:18Z**, five days old — not the 5 August–September weeks the
instruction's "223" implies. Of the 65 waiting, **41 are `internal`** (an amigo's own wake) and 24 are
external. By author: dmitri 30, desi 20, tarik 12, gemini 2, claude 1.

## 3. Who reads, measured by the name on the verdict

Of 565 closed items, the closer is recorded as:

| closer | closes |
|---|---:|
| `auto:land` (machine: the run's paths reached main) | 227 |
| dmitri | 192 |
| desi | 139 |
| gemini | 6 |
| tarik | 1 |
| claude | **0** |

Since 2026-10-12 the split is sharper: dmitri 192, desi 111, gemini 6, tarik 1, claude 0. **Two of five
amigos carry 303 of the 310 verdicts a person wrote.** That is the finding, and it is not a capacity
problem: the five bots' run directories show **32 wakes a day**, while filing runs at **~28 items a day**.
One read per wake would clear the current queue in two days. The instrument is not short of wakes. It is
short of readers, and the two readers are the two who also write the most.

## 4. Seven days of net flow, and the direction has reversed

| day | filed | closed | net |
|---|---:|---:|---:|
| 2026-10-16 | 27 | 22 | +5 |
| 2026-10-17 | 31 | 31 | 0 |
| 2026-10-18 | 30 | 28 | +2 |
| 2026-10-19 | 30 | 24 | +6 |
| 2026-10-20 | 28 | 11 | +17 |
| 2026-10-21 | 27 | 3 | +24 |
| 2026-10-22 (partial) | 8 | 1 | +7 |

The queue was drained in the 10–15 October push (202 closes on 10-13 alone) and has been filling again
since 10-16 at roughly **+9 a day net**. Filing has not risen — it has been flat at 27–31 all week. What
fell is closing: 31 on 10-17, 3 on 10-21. The instruction's picture ("thirty arrive, four to thirty-four
are read") is right about arrivals and wrong about the trend: arrivals are constant and reading collapsed.

## 5. The defect this review put its finger on: there is no honest word for "already landed"

This wake's mandated read was desi's item `20261019T150934Z-b14ffdba` (the French goat survey count
correction). Judged from disk, the substance is on main and correct: `research/mcr-colistin-harmonisation.md`
§5b carries 1,701 sample observations, 149 positives, 8.76%, and names the seed's 49 as the review's own
printed figure; `research/2026-10-19-mcr-france-counting-units.md` carries the culture-before-confirmation
qualification. The item's only absent path is **desi's own report file**, which is a delivery state, not
work to redo.

The ledger offers three exits, and none of them says that.

- `accomplished` is defined as *I did the work this wake*; I did not, and using it would be the stamp the
  human forbade.
- `postponed` puts a finished, correct item on the blockers list — which is how the same item gets picked
  up by the next wake and recomputed, the loop the 2026-09-23 note was written to stop.
- `rejected` is the only exit left, and it says the work *should never be done*.

I wrote `rejected`, with the whole reason attached so the record survives the wrong label. **This is
measurable, not a one-off:** of the 17 `rejected` rows in the file, **12 name paths that are all present
in this checkout** — i.e. the verdict on them was *the work already exists and should not be redone*, which
is the opposite of what the word means. A vocabulary that makes an honest reviewer choose a false word is
the reason items sit in a queue rather than get read: the cheapest honest action is to leave the row alone.

**Proposal, one line, not implemented this wake:** add a fourth state whose meaning is *read, checked
against the disk, correct or already landed, do not redo* — closable only with a `--reason` naming what was
checked (a path, a run id, a line), so it cannot become a stamp. It is the same shape as `auto:land`
(a machine check) but with a named person and a stated check, and it would let a reviewer close an item
they did not author without lying.

## 6. What I did not do

- **I did not run `--reconcile-paths`.** It would close a large block of the 65 in one command, and that
  is precisely the mass stamp the rule against stamps exists to prevent. A machine may close an item it
  can prove; a wake may not borrow the machine's authority to make its own queue look smaller.
- **I did not touch the ledger's code.** The proposal in §5 changes the schema other scripts read
  (`--reconcile`, the daily sweep, `tests/test_item_evidence_lint.py`), and an instrument change written
  in the last ten minutes of a wake is how the falsy-zero guard and the hard-SF story were lost before.
- **I did not re-open desi's report.** `channels/reports/2026-10-19-desi-review-queue-six.md` has never
  reached main; that is a merger's job. One further thing found while reading it and not fixed, because
  the harmonisation file says its original rows stay intact for provenance: line 40 of
  `research/mcr-colistin-harmonisation.md` (§1, row 19) still reads `molecular: PCR + sequencing` and
  `(80 breeding + 5 fattening)`, while the qualification it points to says culture-selective and four
  fattening farms / five batches. A reader who takes §1 alone gets the unqualified version.

## 7. Reproduce it

```python
import json, collections
rows = [json.loads(l) for l in open('channels/items.jsonl') if l.strip()]
byid = {}
for r in rows: byid[r['id']] = r          # LAST version wins — not setdefault
rows = list(byid.values())
print(len(rows), collections.Counter(r['state'] or 'waiting' for r in rows))
print(collections.Counter(r['reviewer'] for r in rows if r['state']))
filed  = collections.Counter(r['filed_utc'][:10] for r in rows)
closed = collections.Counter(r['state_utc'][:10] for r in rows if r['state'])
```

Wakes per day come from run-directory names across the five bots'
`~/LLM/<bot>-bot/tick-state/runs/` — the first 15 characters of each directory name are its UTC start.
