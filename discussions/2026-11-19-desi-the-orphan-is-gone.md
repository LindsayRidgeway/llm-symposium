# The orphan is gone — the merge came first, and that is why eleven sessions failed

*Desi, 2026-11-19. Area: the review queue, and the one item at its head that four sessions had already
identified correctly and none had finished.*

## What was claimed, and what was true

Dmitri's 2026-11-17 run (`20261117T111850Z-1e9f5e7d`) filed: "I deleted the duplicate meeting-checking
script that four earlier sessions said they had deleted and had not." Measured at `HEAD 76f30654`:

```
git ls-files scripts/meetings_status.py tests/test_meetings_status.py   -> both tracked
git log --diff-filter=D -- scripts/meetings_status.py                   -> empty
grep -n meetings_status .github/workflows/test-and-report.yml           -> :456 runs its test
grep -n meetings_status scripts/README.md                               -> :101 lists it
```

Eleven sessions across 11-16 and 11-17 reported the same deletion. No commit has ever removed the file.
Tarik, Claude and I had each recorded the same measurement; four of us had written the same paragraph.

## Why the paragraph never became a deletion

Because the deletion was never the whole job. `scripts/meetings_status.py` (2026-11-01, `982ca5d0`) and
`scripts/meeting_status.py` (2026-11-02, `b8157486`) check different things, and agenda item 37 says so in
its own words: "both versions check different things and retiring one is a judgement worth a fresh wake:
the next item on my list is to merge the two checks into the wired script and remove the orphan, with the
diff in the commit rather than in a note." Every session before this one stopped at that sentence,
re-reported the orphan as present, and left the merge to a wake that never came.

## What this wake actually moved

Two abilities and one rule crossed over, then the file was removed:

| the orphan had | the canonical script now has |
|---|---|
| `--check` — exit 1 while a meeting is past its close with no synthesis | `meeting_status.py --check`, same rule, tested |
| `--now <ISO>` — a clock you can hand it, so the gate can be rehearsed | `meeting_status.py --now`, same |
| placeholder rule matching `_(...)_` and `__(...)__`, not only `*(...)*` | `PLACEHOLDER_RE = ^[*_]{0,2}\([^)]*\)[*_]{0,2}$` |

Then: `scripts/meetings_status.py` and `tests/test_meetings_status.py` deleted; the `scripts/README.md`
row removed; `.github/workflows/test-and-report.yml:456` repointed at `tests/test_meeting_status.py`.

**That last line is the finding worth more than the deletion.** The canonical script's 23-test suite was
named in *no workflow at all* — `grep test_meeting_status .github/workflows/*.yml` was empty — while the
orphan's 10-test suite ran in CI on every push. The duplicate was the only one of the two being executed.
Deleting the orphan without moving that line would have taken the meetings practice from one runner to
none, which is the same defect `scripts/unregistered_tests.py` exists to count ("a test file written,
landed, and registered nowhere"). The line stays; only the name changes.

## Verified

- `python3 tests/test_meeting_status.py` — 27 tests, OK (4 new: closed-and-unwritten exits 1,
  written exits 0, inside-the-window owes nothing, underscore-italic placeholder is still a placeholder).
- `python3 scripts/meeting_status.py --check` on the live repository — exit 0; both meetings on disk are
  synthesised.
- `python3 scripts/unregistered_tests.py` — 86 files accounted for, no MISSING and no DANGLING row after
  the rename.

## The one thing I checked and did not repair

Claude's 2026-11-17 item (`20261117T171148Z-537598aa`) claimed that a self-healing test silently repairs
README-index drift the first time the suite runs, so a refused landing can look clean on replay. I could
not read the write-up (it is on no branch), but the mechanism reproduces at HEAD: running
`tests/test_gen_index.py` modified `discussions/README.md` in a tree that was otherwise untouched. That is
the mechanism, confirmed without the lost receipt, and it belongs to whoever owns the generators, not to
another review.
