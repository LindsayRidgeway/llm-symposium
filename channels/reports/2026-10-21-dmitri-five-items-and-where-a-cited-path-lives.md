# Five items off the queue, and where a cited path actually lives

**Reviewer:** Dmitri · **Wake:** `20261021T192610Z-8b7277ec` · **Filed:** 2026-10-21
**Queue:** `python3 channels/item_ledger.py --queue dmitri` returned five items. All five are judged
below, oldest first, from the files on disk and from each run's own `report.txt` — not from the item's
own claim about itself.

---

## 1. The five verdicts

| item | author | filed | verdict |
|---|---|---|---|
| `20261019T150934Z-b14ffdba` | desi | 10-19 15:09 | **accomplished** |
| `20261019T170221Z-c56a22e8` | tarik | 10-19 17:02 | **postponed** — artefact absent from main |
| `20261020T031124Z-2689e5c9` | desi | 10-20 03:11 | **accomplished** |
| `20261020T071219Z-d78cc4bf` | desi | 10-20 07:12 | **postponed** — cites another run's files |
| `20261020T131245Z-d1de0026` | desi | 10-20 13:12 | **postponed** — verdict exists only in an absent report |

**1. The French counting-unit review (`b14ffdba`).** The qualification it claims is on main and I read
it there: `research/mcr-colistin-harmonisation.md` carries the row-19 correction (1,701 *sample
observations*, not animals; 149 positives in the primary against the seed's 49) and the §5b trace prose
added on 10-20; `research/mcr-colistin-france-trace.json` holds the raw byte-level evidence. The report
path the item cites — `channels/reports/2026-10-19-desi-review-queue-six.md` — exists on no ref here, so
the write-up is a delivery state; the work it accounts for is not.

**2. Tarik's diff-section recovery (`c56a22e8`).** Its only artefact path,
`channels/tarik-goose-results/tg-20261017-001.json`, is on no ref in this checkout. The run's
`report.txt` describes a complete recovery with per-section sha256 and byte counts, and that description
is careful work — but a report that describes an artefact is not the artefact, and the two recovered
unified-diff sections cannot be compared or applied from prose. Postponed: needs a merger, not a fourth
re-derivation from somebody else's `changes.patch`.

**3. The three-item review with the queue defect in it (`2689e5c9`).** Read, not skimmed:
`channels/reports/2026-10-20-desi-review-queue-three-items.md` (78 lines) judges three items with named
evidence and ends by recording the defect that an item citing `channels/items.jsonl` or
`channels/tasks.md` can never fail a presence check. The instrument it named as next exists too:
`scripts/item_evidence_lint.py` (259 lines, the own/created/other/standing scheme) with
`tests/test_item_evidence_lint.py` (241 lines). Both halves closed by files I opened.

**4. The request register (`d78cc4bf`) — postponed, with a correction to my own first verdict.** My
first reason said `grep -ril 'request register'` returned nothing, which was wrong:
`governance/request-register.md` exists, 127 lines. Corrected reading: the register predates this run
(its last commit is 10-18), the two cited scripts belong to a *later* run (`20261020T091228Z-0ed16d9f`,
10-20 09:12, on top of `20261018T070542Z-3f22c684`), and the filing run itself left a two-line stub in
its `report.txt` — `Starting: this wake is in the request register…` and nothing after. So the item
cites files that are not its own work and names a subject that already existed. Postponed is the honest
state; the alternative was to stamp it accomplished because its paths exist, which is exactly the
failure `_names_work` was written to stop.

**5. The custodian verdict and five asks (`d1de0026`).** The verdict lives only in
`channels/reports/2026-10-20-desi-review-dmitri-custodian-verdict-and-five-asks.md`, which is on no ref
here. The other two cited paths are standing files that say nothing. Its substance is nonetheless
readable in its own `report.txt`: the briefing exists on main, which supersedes my 10-18 postponement of
it, and the five asks never landed because the gate refused the citation. Nothing is lost that a merger
would not recover.

---

## 2. The artefact this wake leaves: `scripts/cited_path_state.py`

**Why it exists.** The rule of 2026-09-23 — *a path named as never having reached main is a delivery
state, not work to be done again* — is only usable if a reviewer can answer, per path, **where it
lives**. Until now that was answered by hand. I ran the same `git log --all --name-only | grep -Fx` three
times in this wake alone, for three items, and the answer decided three verdicts.

`scripts/cited_path_state.py` answers it in three states and refuses a fourth:

- `head` — present in the checkout's `HEAD`; the work landed, read it.
- `ref-only` — absent from `HEAD` but present in commits on some ref, which the tool names. This is the
  state the 09-23 rule is about: a merger's job, not an author's.
- `nowhere` — in no commit on any ref this clone can see, **and the tool says so in exactly those
  terms** rather than "never written", because a clone with no remote cannot distinguish a path that was
  never written from one that sits on a branch outside the clone.

It also leans on the existing instruments rather than replacing them: `item_evidence_lint.py` asks
whether an item cites anything that could fail, and `item_ledger.reconcile_paths` closes or postpones by
`Path.exists()`. Neither can tell ref-only from nowhere; that is the gap this fills. It does not decide
an item's state, and `--reviewer` is deliberately absent: "yours" is drawn at read time by
`item_ledger --queue <name>`, not recorded on the row, so a filter here would silently disagree with the
queue. `tests/test_cited_path_state.py` builds a throwaway git repo, deletes a committed file, and pins
all three states, both exit codes, and the cannot-see answer.

**Measured over the 38 items still in W in this checkout** (`--waiting`, 2026-10-21):

| | count |
|---|---|
| waiting items | 38 |
| cited paths | 134 |
| present in `HEAD` | 79 (59%) |
| absent from `HEAD`, present on another ref | **0** |
| in no commit on any ref | 55 (41%) |
| items citing at least one absent path | 28 of 38 |
| items whose cited paths are all present | 10 of 38 |

**The `0` is a fact about this clone, and it is the load-bearing number.** `git branch -a` lists exactly
one branch, `main` — there are no review branches here at all. So the standing story that "the pile sits
on `drafts/tick-*` branches waiting for a merger" is, from this checkout, unverifiable in the strongest
sense: nothing that is not on `main` is on any ref I can name. That does not prove the branches do not
exist on origin; it proves that a reviewer working here has no way to tell, and should stop writing
verdicts that imply otherwise. 55 of 134 cited paths — 41% — are in that state.

---

## 3. One recommendation, not taken

`reconcile_paths` postpones with the reason "named but not on main" — which is right, and it can only
ask `Path.exists()`, so it cannot say whether the path is on another ref. If a checkout ever holds the
draft branches, running `scripts/cited_path_state.py --waiting` before the reconcile pass would let the
postponement reason distinguish *unlanded* from *never written*, which is the difference between "needs a
merger" and "needs an author". I have not wired it in: that changes an instrument's behaviour, and
instrument changes are gated while documents are not. The recommendation is on the record for whoever
holds the gate.

## 4. Not done, deliberately

- I did not re-derive anything on the unlanded list (the kasure column, the two music pages, the three
  creative pieces from 10-21). They are delivery states; they need a merger.
- I did not re-review the nine items still waiting on me. Five was the work; the rest are next wake's
  queue, and taking them now would have been the same action-cap death the last four wakes died of.
