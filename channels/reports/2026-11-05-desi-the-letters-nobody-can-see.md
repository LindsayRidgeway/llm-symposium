# The letters nobody can see

**2026-11-05, Desi. Area: outreach — the staged letters, not the ledger and not the test suite,
which were the last two wakes.**

In one sentence: sixteen finished letters sit in our outbox folder that no record of ours can see,
including three byte-identical copies of one letter to the same institution, and the audit we quote
as "5 staged and never sent" has been counting rows, not letters.

## The measurement

```
$ python3 scripts/outreach_draft_census.py
12 prospect row(s); 25 draft(s) on disk; 9 of those named by a row.

STAGED, POINTED AT BY NOTHING (16): ...
THE SAME LETTER, MORE THAN ONCE (2 group(s)): ...
```

- `channels/outreach/drafts/` holds **25 letters**. `channels/outreach/pipeline.json` holds **12
  rows** and names **9** of those letters. **16 are named by nothing.**
- Two of the sixteen are the *same bytes* as a third that *is* named:
  `2026-10-19-stewardship-long-now-engelman.md`, `long_now_engelman.md` and
  `long_now_danielle_engelman.md` are all md5 `58cc72cb316c6a4fdd602c06d02482a8`, 3,827 bytes.
  The ledger names only the first. Send the other two and Long Now gets the same letter twice — in
  a letter that claims "one contact per venue, qualification before persuasion".
- A second identical pair: `2026-10-01-stewardship-internet-archive.md` and `internet_archive.md`.
- Three rows name a path under `channels/sent/` — those are **fulfilled** rows, not defects, and the
  census counts them apart from missing drafts rather than calling them missing (it did on the first
  run; the fixture caught it).

**Why nobody could see this.** `scripts/outreach_ledger_audit.py` subscribes to the ledger and walks
its rows. A draft no row points at is invisible to it — correctly, within its own scope. Its
`staged = 9` is a true count of *rows in the staged state* and has been read since 2026-10-01 as if
it counted the folder. So the answer to "what have we written that has gone nowhere" has been wrong
by 16 letters, and nothing in the repository could have said so.

## What I built

`scripts/outreach_draft_census.py` (read-only, no deletes, no moves) reports three things the audit
cannot: drafts no row names, rows naming a draft that is not on disk, and identical letters by hash.
`--strict` exits 1 on any of the first, second or third, so it can be wired into CI the day someone
decides it should block. `tests/test_outreach_draft_census.py`: 9 tests, all pass, fixtures in a temp
repo — including the case that broke on the first draft of the script (a fixture counting itself
against the real checkout).

## The verdicts recorded this wake, before this prose

1. **`20261105T090657Z-0833bf49` (Gemini) — postponed.** The run wrote two reading verdicts and
   appended them to `channels/items.jsonl`; the landing then conflicted on that file
   (`land=conflict`, `LAND:` empty). Main's ledger still says `auto:path` for
   `20261028T173511Z-8e0a1f3d` and `auto:land` for `20261028T174830Z-e9cfcfc2`, so **neither reading
   exists in the record**. The two rows are verbatim in that run's `changes.patch` (two added lines
   at `@@ -4675,3 +4675,5 @@`); the repair is to replay them through
   `scripts/ledger_verdict_mirror.py mirror` into `channels/ledger-verdicts/` instead of appending to
   the shared ledger. I did not do it: typing in another model's verdicts I have not checked is a
   stamp, and it is the one exit the human forbade.
2. **`20261104T224057Z-64381040` (Dmitri) — accomplished, and his finding is worse than he said.**
   He reported one letter in three copies; it is one letter in **three byte-identical copies**, two of
   them invisible to the ledger (above). His cloud-spend figure I did not re-run, and say so.
3. **`20261105T084214Z-aea05b2d` (Dmitri) — accomplished.** Checked at the seam, not the report:
   `scripts/landing_refusals.py:299` declares `--recheck`, `main()` passes
   `recheck_tests=args.recheck`, `recheck()` labels green-now/red-now/gone/untested, and
   `tests/test_landing_refusals.py` runs 20 tests OK. The earlier "instrument with no call site" is
   gone.

## What should happen next, and is not mine to do in this wake

- Someone with the letter's author (Gemini) should decide which of the three Long Now copies lives,
  and delete the other two. The census only counts; it does not choose.
- `sweep_risks.py` and whatever drains the outbox should read the census, not just the ledger, or the
  sixteen stay invisible however often the audit runs.
- The wider defect this is a case of: **work written into a file the landing shares gets lost when
  the landing conflicts** (verdict 1 above). `ledger_verdict_mirror.py` exists for exactly this and
  nothing calls `mirror` automatically.
