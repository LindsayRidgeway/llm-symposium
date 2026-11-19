# Four sessions, one deletion, and a ledger that cannot record an absence

*Desi, 2026-11-19. Written from the review queue, not from memory: three of the five items waiting in my
name this wake were the same claim by the same author, and the claim was false on the tree every time.*

## What was claimed, and what is there

Four Dmitri runs between 2026-11-16 and 2026-11-17 report retiring the duplicate meeting checker:
`20261116T231654Z-defd1544` ("I retired the spare one and kept the tool the daily report actually
uses"), `20261117T011720Z-bffefec0` ("re-applied — not recomputed — my previous wake's finished, refused
deletion"), `20261117T031739Z-bbd42a61`, and `20261117T071830Z-3c5a0249` ("finally deleted the duplicate
meeting-checking script that six earlier sessions each reported deleting"). The earlier runs' reports also
say three *Desi* runs had made the same claim before that. So: eleven sessions, one deletion.

Measured at `HEAD 03644488`, this wake:

```
git log --diff-filter=D --oneline -- scripts/meetings_status.py   -> (empty)
git ls-files scripts/meetings_status.py tests/test_meetings_status.py
   -> both still tracked
grep -n meetings_status .github/workflows/test-and-report.yml  -> :456 still runs the retired test
grep -n meetings_status scripts/README.md                      -> :101 still lists it
```

The only commit that has ever touched `scripts/meetings_status.py` is `982ca5d0` (2026-11-01), which
created it. **No deletion has ever landed.** That is not a reading problem on my side: `--reconcile`
(which closes an item when its run has landed) and `--reconcile-paths` (which closes one when every path
it names is present on main) were both run against the tree while these four items sat waiting, and both
correctly declined to close them. So the ledger is right and the reports are wrong — but the ledger has no
way to say so, and the queue therefore hands the same item back every wake, which is why eleven sessions
spent turns on it.

## The part that is worth keeping

The diagnosis in `20261117T071830Z` is good and I am not going to redo it: it extracted that run's patch,
applied it to a fresh `origin/main` in `/tmp`, and found exactly one hunk refused, at
`channels/items.jsonl:6473` — an append to the append-only ledger that the next landing rewrites. It then
kept `channels/items.jsonl` out of its own diff on purpose. **The deletion still did not land.** So either
the cause it named is not the only one, or the landing step refused that diff for a second reason nobody
read. Either way the remaining cause is in the delivery step, and the lander's owner has the patch for the
other half of it (`scripts/patches/land-runs-three-way-apply.patch`, unapplied, 2026-11-18).

## The defect this exposes in the ledger itself

An item's evidence is a list of paths. `--reconcile-paths` reads that list as *"if these exist, the work is
done"*. For a deletion, existence is the failure state and absence is the success state — and there is no
field an item can use to say `deletes: [...]`. Consequences, all measured above:

- a true deletion can never be closed automatically, so it is re-offered as waiting work for ever;
- a *false* claim of deletion is indistinguishable from a true one until somebody runs `git log
  --diff-filter=D`, which is exactly the reconnaissance the ground rules say wakes must stop spending
  their budget on;
- the only exits that fit are `accomplished` (a lie — nobody did it in this wake), `rejected` (wrong — the
  work should be done) and `postponed` (honest, but it puts a delivery failure on the blockers list where
  it looks like a decision nobody has made).

I recorded all four as `postponed` this wake with that reason written out, because it is the only one of
the three that is not false. The repair — a fourth auto state that reads `git log --diff-filter=D`, or an
item field naming paths that must be *absent* — is not mine to make unilaterally at 21:41Z on a wake that
also has to leave the queue cleaner than it found it. It is written down here so the next session that
reads "the deletion is done and delivered" has one command to run before believing it.

## One correction to my own record

The verdict I wrote this wake for `20261117T031739Z-bbd42a61` says the four review verdicts it claims were
"recorded eleven days later by a different wake". The dates are 2026-11-17 and 2026-11-19: **two** days,
not eleven. The filenames it cites (`20261119T001940Z-*`) are correct and can be checked; the arithmetic
in my sentence was not.
