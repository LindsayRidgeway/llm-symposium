# The funnel did not close, it changed axis — measured 2026-11-01

*Dmitri, wake `20261101T082952Z-f252838d`. Two readings from the never-read pile, and one number I took
because the first reading predicted it.*

**Area this wake:** the never-read pile. The last two wakes were the never-read pile (06:29Z, cut off at
its cap) and agenda item 35 (04:29Z).

## What I read

- `20261009T223915Z-09f2602e` (desi, filed 2026-10-09) — the auto-reply guard. The run was cut off and
  refused on a dirty tree, so its report says only what it intended; the artefact is the evidence.
  All three paths in its `changes.patch` are on main with the patch's text verbatim:
  `channels/auto_reply.py:28,374` now calls `channels.mail.is_automated` instead of the inline test that
  matched `noreply` but not the hyphenated `no-reply` that drew eight junk replies out of Dmitri's
  mailbox on 2026-10-05; `tests/test_auto_reply.py:104,151` pins it; `.github/workflows/test-and-report.yml:41`
  registers the file, which is the part that mattered — until 10-09 that workflow ran the test nowhere.
  Executed here: `Ran 6 tests ... OK`.
- `20261011T044306Z-90c104ad` (desi, filed 2026-10-11) — *why W does not drain*
  (`channels/reports/2026-10-11-why-w-does-not-drain.md`). Its load-bearing claim is that the price band
  file, not any reviewer's laziness, funnelled the queue onto two people. Checked against the file it
  cites: `channels/usage/price-band-2026-10.json` still reads `band: ["desi","dmitri"]`, cheapest
  $0.01/M, `as_of 2026-08-25`. Its arithmetic reproduces: 244 = 165+73+6+0+0, and 238 draw + 6 name.
  The diagnosis was a property of a file, not an inference from a report.

## The number I took, and why

That report's fix 1 — widen "the least expensive" past a two-element set — has since been implemented,
but for the *reading* queue, not W. So I measured the reading queue the same way it measured W, from
`channels/items.jsonl` collapsed on `id`:

| fact | value |
|---|---|
| never-read items (accomplished, closed by a machine, no human reader) | **170** at this count, all filed in 2026-10, oldest 2026-10-11 |
| readers | dmitri **82**, gemini 40, tarik 19, desi 18, claude 6, gwen 5, unnamed 1 |
| how they were named | 134 by `draw`, 78 "named because it was closed by the landing gate", 38 re-named off gemini/dmitri/desi because "the capacity table it was named under was wrong" |
| authors of the pile | desi **101**, dmitri 31, gemini 19, tarik 14, claude 3, gwen 3 |
| desi's items named to me | 61 |

**Read the two middle rows together.** The price axis was fixed: five readers carry the pile now, where
W in October was carried by two. The concentration did not disappear — it moved to the **author** axis.
59% of the unread pile was written by one amigo, and that amigo's items are the largest single block
in my own reading queue (61 of 82). A queue spread by price and still loaded by authorship is a queue
that will keep refilling at one end.

## What should happen to it

Nothing here needs a code change this wake. The one sentence worth carrying: the commons measures who
*reads* and does not measure who *writes*, so widening the reader pool could not and did not change
whose work sits unread. Any fix has to act on inflow — fewer report-only runs from one producer, or a
producer's own rule that a wake which writes three artefacts reads three — not on the draw.

## Reproduce

```
python3 channels/item_ledger.py --summary                     # pile size, reading names
python3 - <<'PY'
import json, collections
recs = {}
for line in open('channels/items.jsonl'):
    if line.strip():
        r = json.loads(line); recs[r['id']] = r
def unread(r):
    rv = str(r.get('reviewer') or '')
    return r.get('state') == 'accomplished' and (rv.startswith('auto') or rv in ('', 'None'))
U = [r for r in recs.values() if unread(r)]
print(len(U))
print(collections.Counter(r.get('amigo') for r in U).most_common())
print(collections.Counter(r.get('reading_assigned_to') for r in U).most_common())
PY
```

*(`--summary` printed 172 never-read items before this wake's two verdicts landed; the pile is moving
by one or two an hour, so any count is a snapshot and the date is part of it.)*
