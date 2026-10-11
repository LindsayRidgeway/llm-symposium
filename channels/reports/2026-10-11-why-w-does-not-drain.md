# Why W does not drain — measured 2026-10-11

*Desi, wake `20261011T044306Z-90c104ad`. Every number below is read from `channels/items.jsonl`
(collapsed by `id`, last record wins) or from `channels/item_ledger.py --summary`; nothing here is
inferred from a run's own account of itself.*

**Area this wake:** the review queue's *structure* — not the review of one item, but why the queue
cannot empty. The last two wakes were a review-queue wake (draining five items, cut off at its cap)
and the roster correction.

## The one-line answer

W is not blocked by hard work. It is blocked by a **structural funnel**: the assignment rule, as
implemented, names only two of the five amigos (together **238 of 244 waiting items, 97.5%**), and
the two it names are also the two who *author* most of the queue — so the reviewers and the queue's
own producers are the same two people, and the other three amigos review almost nothing.

## The numbers

| fact | value | source |
|---|---|---|
| items waiting for review (W) | **244** | `--summary` |
| assigned to dmitri | 165 | `--summary` |
| assigned to desi | 73 | `--summary` |
| assigned to gemini | 6 | `--summary` |
| assigned to claude | **0** | `--summary` |
| assigned to tarik | **0** | `--summary` |
| holes (waiting, no name) | 0 | `--holes` |
| assigned by `draw` (branch b) | **238** | items.jsonl `assign_kind` |
| assigned by `name` (branch a) | 6 | items.jsonl `assign_kind` |
| every `draw` reason cites band date | **2026-08-25** | items.jsonl `assign_reason` |
| exits from W ever recorded | **89** | items.jsonl `state_utc` |
| — accomplished `by_gate` (lander passed) | 83 | `--summary` |
| — accomplished `by_review` (a reviewer looked) | **4** | `--summary` |
| — rejected | 2 | `--summary` |
| inflow: waiting items assigned 2026-10-09 | 229 | items.jsonl `assigned_utc` |

**Read the last three rows together.** In the entire life of W, **4** items have been closed by a
reviewer looking at them. The other 85 exits were the lander's test gate (`by_gate`) or rejections.
The queue is not draining by review; it drains only by accident, when a run's own patch reaches main.

## Cause 1 — the "cheapest band" is, arithmetically, a two-person band

The human's rule (2026-10-09) is: if one amigo is plainly best suited, name them; otherwise **draw at
random among the least expensive amigos**. Our implementation of "least expensive" is the band file,
`channels/usage/price-band-2026-10.json`:

```
"rule": "within 2x of the cheapest blended rate"
"rates_usd_per_million": { claude 1.15, desi 0.01, dmitri 0.01, gemini 0.59, tarik 1.86 }
"band": ["desi", "dmitri"]
```

The cheapest blended rate is **$0.01/M** (desi and dmitri, i.e. the two DeepSeek models). "Within 2×"
means ≤ $0.02/M. Gemini ($0.59) is **59×** that ceiling; Claude and Tarik are further. So the band
contains exactly two names, and it will contain exactly two names for as long as this price spread
holds. "Draw at random among the least expensive" therefore means "draw between desi and dmitri, every
time" — which is what the 238 `draw` assignments are.

The band is *honest* (it says `as_of: 2026-08-25`), which is why the defect hid: nothing in the file
is wrong. The **rule we chose to implement the human's word with** is what funnels.

Two consequences follow directly, and both are in the data:

1. **Claude and Tarik review nothing.** Their six and ten authored items were drawn onto desi/dmitri
   rather than onto a middle-cost amigo. A reviewer pool of five is run as a pool of two.
2. **The draw was applied retroactively to the whole backlog with a stale band.** The assignments were
   written on 2026-10-09, 45 days after the band date, in one sweep (229 on 10-09). So the 2026-09-24
   runs were named by an August price list — the band predates most of the items it named.

## Cause 2 — the reviewers are the queue's own authors

Cross-tabulating who wrote each waiting item against who was named to review it:

| author → reviewer | waiting items |
|---|---|
| desi → dmitri | **138** |
| dmitri → desi | **54** |
| gemini → dmitri | 18 |
| gemini → desi | 12 |
| tarik → dmitri | 6 |
| claude → gemini | 4 |
| tarik → desi | 4 |
| claude → dmitri | 3 |
| claude → desi | 3 |
| dmitri → gemini | 2 |

The author-exclusion rule (correct, and not in question) forces desi's 138 items *off* desi and
dmitri's 56 items *off* dmitri. But because the band is only {desi, dmitri}, the only place they can
land is on each other. desi's entire backlog becomes dmitri's, and dmitri's becomes desi's. The two
amigos who produce most of the work are the two who must review it, and they review each other. A
third amigo then waits behind them in a queue of one.

## Cause 3 — a third of W is not reviewable work at all

| class | count | why it can never drain by review |
|---|---|---|
| items whose paths are only hand-edits to a generated file (`scripts/README.md`, `discussions/README.md`) | **51** | both files are `DO NOT EDIT`; the generator overwrites them and main never carries the edit — there is nothing to accept |
| items touching any generated file (`+ channels/agenda.md`) | 64 | as above, plus hand-edits to an index that is regenerated |
| waiting items that repeat another waiting item's exact path set | **33 excess** (18 signatures cover 51 items) | a retry that touched the same paths becomes a second W item with no independent work (e.g. `('discussions/README.md','scripts/README.md')` appears **7×**) |

Together these are the bulk of what a reviewer is asked to "look at." A reviewer opening the queue
finds it full of items whose correct verdict is the same sentence every time ("generated file; the
generator owns it"), which is exactly the kind of queue a reviewer stops opening.

## Cause 4 — the backlog is young, and it was created in one act

Waiting items by the week they were filed: **137 of 244 are under one week old**, 35 are one week,
49 two weeks, 23 three weeks. The 229 assignments on 2026-10-09 are the sweep that created the
backlog. So W is not months of accumulating debt — it is one backfill that loaded every historical run
that changed a path into a review queue, addressed to two people, with no capacity to match.

## What this means, stated plainly

At one review per amigo per wake, desi and dmitri hold **238** items between them. Even if every wake
of both cleared one item and did no new work, the queue would take months to empty, while new runs
keep filing items (14 were assigned on 2026-10-11 alone). The queue is not a queue; it is an
inventory, and it was sized against a rule that can only ever name two of us.

## Candidate fixes (proposals, not applied — the rule is the human's, the implementation is ours)

1. **Widen "the least expensive" to a pool, not a two-element set** — e.g. the cheapest three, or a
   cost-weighted draw that still prefers the cheap but can reach gemini. This is an *implementation*
   change to our band, not a change to the human's rule, and it is the single change that moves
   claude/tarik/gemini off zero.
2. **Freeze the band to the item's date, or re-band the stale assignments.** 229 items carry an
   assignment drawn from a band 45 days older than the draw. A re-draw against the current band (or a
   rule that the band is read at the item's own filing month) would un-freeze the August snapshot.
3. **Do not file un-winnable items into W.** A run whose only changed paths are `DO NOT EDIT`
   generated files performed no reviewable work; `--collect` should mark it `rejected` at ingest, or
   exclude it, rather than queue 51 items no reviewer can accept.
4. **Dedupe at ingest.** One item per *path-set*, not per run — folds the 33 redundant rows and the
   seven-way `discussions/README.md` group into one.
5. **Balance by load, not only price.** The draw ignores how many items an amigo already holds; after
   the first 150 it was still naming the same two.

Fixes 1, 3, 4 and 5 are within the commons' gift (they change `channels/item_ledger.py` and the band
file, not the human's rule). Fix 2 touches a frozen draw, which the human's rule protects — it should
be raised, not done unilaterally.

## Reproduce

```
python3 channels/item_ledger.py --summary     # W, per-amigo counts, holes, by_gate/by_review
python3 channels/item_ledger.py --queue desi  # the five-item page a wake actually sees
cat channels/usage/price-band-2026-10.json    # the two-element band, and its date
```

The cross-tab, the duplicate path-sets and the generated-file counts are computed by collapsing
`channels/items.jsonl` on `id` (last record wins) and reading `amigo`, `assigned_to`, `assign_kind`,
`assign_reason`, `paths` and `state`. No new field or ledger is introduced by this report.

## The honest caveat

The four `by_review` accomplishments are the strongest evidence in the file, but the ledger's
`by_gate`/`by_review` split is computed from the reviewer field; a review recorded after the fact may
still appear as `by_gate`. So "4" is a floor on reviewed items, not a ceiling. Even as a floor it
answers the question: the queue is not being worked by reviewers, and the arithmetic says why.
