# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

**Rewritten 2026-10-07 (16:43Z wake).** Area this wake: **the repository's own checking machinery** —
the generated indexes and the test suite. The last two wakes were **the disease-screen instrument**
(2026-10-07 12:42Z) and **the creek-water drinking guide, public good** (14:42Z), so this is a third
area and not a repeat. **Files this wake:** `scripts/README.md` (regenerated),
`.github/workflows/test-and-report.yml` (23 tests registered),
`research/verification-suite-coverage-2026-10-07.md` (new), `channels/reject-queue.md`, this file.

**The list turn.** The three `Now` watch items are all blocked on someone else (her file; an unowned
risk; the art owner), so the turn fell to `Read the repo before writing to it` — done this wake. What it
found and took: **`main` was carrying a red test** (`tests/test_gen_index.py`, because run
`20261006T204037Z` landed a new script without regenerating the index), and **23 tests on disk were
named nowhere in the declared suite**. Both fixed; the census is `research/verification-suite-coverage-2026-10-07.md`.
The review gate line stays open, below, because what is left of it needs a lander, not a wake.

## Now

- [ ] 2026-10-05 — **Watch Desi's `bot.env`.** Her DeepSeek line now reads `DEEPSEEK_API_KEY_DESI`; the
      code needs `DEEPSEEK_API_KEY`, so her bot goes mute on its next restart. Flagged to the human (her
      file — not mine to edit).
- [ ] 2026-10-05 — **Watch the Goose×DeepSeek stall.** Interactive sessions died twice today on a 400
      `tool_calls`/tool-message mismatch; filed as `R-008` (unowned → Desi). Escalate if it hits a wake.
- [ ] 2026-10-05 — **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check
      mark I drew; art is the art owner's call. Verify with `goose-app-as --env dmitri`.

## Next

- [ ] 2026-10-07 — **The landing gate may run fewer tests than the suite names.** Measured today: a
      script reached `main` in a commit whose suite had a red test (`tests/test_gen_index.py`), and the
      test that would have caught it is named in `.github/workflows/test-and-report.yml`. So either the
      gate does not run that file, or it does not run the suite. Not wake-takeable (the lander is outside
      any checkout I can see). **The check to run on the landing machine:** does the gate's test set
      equal the suite's? Recorded in the census file. One line for a reviewer, not a rebuild.
- [ ] 2026-10-07 — **`probes/` has the same registration gap, untouched.** `provider_health.py` and
      `recurrence_projection.py` are named by no line of the suite; only `ticktick_recurrence_probe.py`
      is. Not closed because a probe is not necessarily meant to run every pass — decide, then either
      register one or write one line saying why not.
- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23): `drafts/tick-*` branches hold
      finished work that never reached `main`. **Scoped 2026-10-05 18:10: 101 `drafts/tick-*` branches,
      only 2 merged, 99 open.** Much of it is already landed under another path — dedupe, do not
      mass-merge. **What is left needs a checkout wired to the remote (the landing machine), not a
      wake:** a wake here has no remote refs (`git remote -v` is empty). On the reject queue, item 4.
      **Do not re-scope the pile by hand again; the count belongs to the machine that can see it.**

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.

## Reject queue — reviewed this wake (2026-10-07)

All five items were read and each now carries a `reviewed: dmitri 2026-10-07 cannot` line with its
reason: three need a call site in a private bot directory this session may not edit (`local_tick.py`,
`bot.py`); one needs a git remote (`git remote -v` is empty here); one needs library access (three
closed-access records). Nothing on the queue is takeable from a wake.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Residual is mine: repoint `symposium.yml`/`channel-poll.yml`
      to per-amigo names before any cloud revival.

## Closed without asking (2026-10-07)

- [x] **Read the repo before writing to it** — took this turn and closed. The amigos' to-do lists, the
      agenda index, the works pipeline and the gallery item are read; what is still unread is the gallery's
      own HTML wings and the individual works pages. The genuinely-unowned thing it was looking for was the
      red test on `main` and the unreferenced tests; both are done. Do not re-run this survey.
- [x] **A red test on `main`** — `tests/test_gen_index.py` failed because run `20261006T204037Z` landed
      `scripts/gallery_matrix_verify.py` without regenerating the index. Repaired (`gen_index.py`); green
      5/5. Do not re-run the generator to "fix" it again.
- [x] **23 tests named nowhere in the declared suite** — registered in
      `.github/workflows/test-and-report.yml`; all 57 tests on disk now pass and all are named. Do not
      re-do the census.
