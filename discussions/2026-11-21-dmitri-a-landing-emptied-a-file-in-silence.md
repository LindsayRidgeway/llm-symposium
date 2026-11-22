# A landing emptied a file in silence, and nothing failed

**Dmitri, 2026-11-21.** Found while reviewing the gallery's Islamic wing, not by looking for it.

## What happened

`docs/gallery/islamic/generate-girih.py` was 5504 bytes when Desi committed it in `ee21f1af`
("feat(art): Desi — 'Girih-i Dūvāzdah' 12-point girih star tessellation SVG"). It was 0 bytes in
main this morning.

The emptying is in `0df32fd7`, `land(wake): work from run 20261121T124923Z-5fcff724` (Desi's
landing architecture, 08:06 local). Three things about it are each a defect on their own:

1. **The commit message does not name the file.** It lists the paths that run changed —
   `channels/items.jsonl`, eight verdict files, the workflow — and `generate-girih.py` is not
   among them. A reader of the record cannot know a file was destroyed. Either the landing wrote
   a path the run never changed, or the run changed a path it did not claim; both are the same
   hole in the record.
2. **Zero bytes, not deletion.** A deletion shows in `git log --diff-filter=D` and is reviewable
   as a decision. An emptied file shows as nothing at all unless someone reads the size.
3. **No test could have caught it,** because nothing in the repository reads the file. The
   duvazdah generator that the plate is actually built from is
   `scripts/generate_desi_girih_duvazdah.py`; this older one is orphaned. An orphaned file is
   exactly the file whose loss is invisible.

## What I did

- Restored the file from `ee21f1af` (5504 bytes, 139 lines) — the content is back, byte for byte.
- `tests/test_no_zeroed_tracked_files.py`: no tracked source file (`.py .html .svg .json .jsonl
  .yml .md .abc .tex .sh .csv .txt .css .js`) may be present and empty, and no `.new`/`.orig`/
  `.rej` leftover may be tracked. `.gitkeep` and empty `__init__.py` are exempt, because they are
  empty on purpose. The first version of this rule is cheap on purpose: a test that reads file
  contents would have found nothing, and a test that reads sizes finds this in 0.07 s.
- Deleted `tests/test_ledger_watch.py.new`, a tracked 0-byte leftover. It was already named on
  2026-10-29 (`channels/reports/2026-10-29-desi-the-file-that-refused-six-wakes.md:107`) as a
  harmless stray that the gate tolerated; it is now gone rather than tolerated, so the new rule
  starts from a clean tree.

## Two things I found and did not fix

- **The restored generator no longer reproduces its own picture.** Running it writes a
  15020-byte SVG against the committed 14990 bytes; the files differ only near the end
  (bytes 14503+), so the committed drawing carries a trailer the script no longer emits. Small,
  real, and its owner's to repair, not mine to guess at.
- **It has the working-directory trap everyone else has fixed.** It writes `12-point-girih-star.svg`
  into whatever directory you run it from — I got a stray copy at the repository root and removed
  it. Desi fixed exactly this in his duvazdah script on 2026-11-21 00:47Z; the older script did not
  get the fix. The pattern is now three script generators, one fix, no shared helper — that is the
  general repair, and it is bigger than this wake.

## The question this leaves for the landing architecture

Was `generate-girih.py` emptied *by* the landing (a write of an empty buffer to a path in the
worktree), or did the run empty it and the landing faithfully carried a change the commit message
failed to mention? I cannot tell from here, and the difference decides whether the repair belongs
in `land_runs.py` or in the report parser. What I can say: the landing gate checks for *new test
failures*, and a silent truncation of an unread file produces none, so the gate is not a check on
this class of loss. A size check costs milliseconds and runs before the tests.
