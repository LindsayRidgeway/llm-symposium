# The landing gate: ~36 hours with nothing delivered

*Measured 2026-10-05 20:5x EDT (run `20261006T002708Z-7539884d`, Desi). Source: the `result.json` of every
run under `~/LLM/desi-bot/tick-state/runs/` (189 runs, 2026-09-14 to 2026-10-05), checked against the
`land(wake)` commits in `main`.*

## The claim, with its number

**No wake's work has reached `main` since `5a5314ea` (2026-10-04 12:27Z).** The last `land(wake)`
commit before that is `a96c9de2` (2026-10-04 10:29Z); every commit since `5a5314ea` is a non-wake
commit (the chat record, the to-do edits, the R-008 row) made by an attended session, not by a wake's
landing step.

Of the **18 runs** since the last landing, **12 produced changes and 0 landed**:

| run (UTC) | status | changed paths | landing result |
|---|---|---|---|
| `20261004T122232Z-073e5f10` | awaiting_review | 8 | new_test_failures |
| `20261004T142238Z-2418f998` | awaiting_review | 6 | conflict |
| `20261004T162256Z-94c76c9b` | awaiting_review | 3 | refused_dirty_tree |
| `20261004T182309Z-2b6c4c6e` | awaiting_review | 6 | refused_dirty_tree |
| `20261004T202320Z-367b0fbe` | awaiting_review | 9 | refused_dirty_tree |
| `20261004T222329Z-68c32aa1` | awaiting_review | 6 | conflict |
| `20261005T022413Z-048b7567` | awaiting_review | 9 | refused_dirty_tree |
| `20261005T122543Z-09ba65ae` | awaiting_review | 8 | refused_dirty_tree |
| `20261005T142550Z-9b5d61ff` | awaiting_review | 3 | refused_dirty_tree |
| `20261005T162617Z-323f06d6` | awaiting_review | 8 | refused_dirty_tree |
| `20261005T182619Z-ecd0a080` | awaiting_review | 8 | refused_dirty_tree |
| `20261005T202646Z-8694cdda` | awaiting_review | 4 | refused_dirty_tree |

Of these 12 change-producing wakes, **0 landed**.

Across all 189 runs, the landing step's outcomes are: `landed` 40, `refused_dirty_tree` **42**,
`new_test_failures` 8, `conflict` 4, `push_failed` 1, and no land recorded for the rest (older runs
predate the field). So **42 of the 95 land attempts that recorded a result were refused for a dirty
tree — 44%.**

## The mechanism

`~/LLM/desi-bot/land_runs.py` lands a run by applying its `changes.patch` to the **live checkout**
(`~/LLM/llm-symposium`) and committing. Before it applies anything it computes the set of dirty
paths, commits the live-chat record (`channels/conversation/`, `channels/telegram/`) itself, ignores
the generated indexes it can re-derive, and then:

> `foreign = [p for p in dirty_paths() if p not in generated]`
> `if foreign: return "refused_dirty_tree: " + " | ".join(foreign)`

So *any* dirty path outside those two small sets refuses the landing — and the refusal does **not
clean the tree**. The same dirt is therefore still there for the next wake, which is refused for the
same reason. That is the loop: one refusal becomes every subsequent refusal.

The evidence that it is the *same* dirt, not fresh dirt each time: `insights/2026-09-09-rover-build-03-manual-transcription.md`
appears in **29 of the 42 refusals**, and three affective-pain files appear together in 9.

## The current blocker, read from the live checkout

`git -C ~/LLM/llm-symposium status --porcelain` at 2026-10-05 20:5x EDT (HEAD `8c32e180`):

```
 M channels/action-queue.md
 M channels/channel-digest.md
 M insights/2026-09-09-rover-build-03-manual-transcription.md
 D research/affective-pain-neuromodulation-acupuncture-filtered-raw.json
 D scripts/affective_pain_acupuncture_filtered.py
 D tests/test_affective_pain_acupuncture_filtered.py
?? channels/inbound/2026-10-05-231815-desi-Confirm-your-subscription-to-Lindsay-Ridgeway.md
?? channels/inbound/2026-10-05-231816-desi-One-change-for-you-bot.env-DeepSeek-key-name-must-match-the.md
?? channels/inbound/2026-10-05-231816-desi-You-re-in-Welcome-to-Lindsay-Ridgeway.md
?? channels/inbound/diagnostics/
```

None of these is in `land_runs.py`'s `GENERATED` set (`scripts/README.md`, `channels/agenda.md`,
`context/context-digest.md`, `discussions/README.md`) or its `RECORD_PREFIXES`
(`channels/conversation/`, `channels/telegram/`), so every one of them is "foreign" and refuses the
landing.

The three files marked `D` are **committed in `main`** (they landed in `5a5314ea`). Their
working-tree deletion was never committed, so it is spurious dirt — nothing that already exists in
`main` should be able to block a wake. The two `channels/` files and the `insights/` file are tracked
files with uncommitted local edits; the `channels/inbound/` files are untracked mail intake.

## Remediation (needs an attended session — a wake may not edit `~/LLM/llm-symposium`)

1. Clear the spurious dirt in the live checkout:
   `git -C ~/LLM/llm-symposium checkout -- channels/action-queue.md channels/channel-digest.md insights/2026-09-09-rover-build-03-manual-transcription.md research/affective-pain-neuromodulation-acupuncture-filtered-raw.json scripts/affective_pain_acupuncture_filtered.py tests/test_affective_pain_acupuncture_filtered.py`
   (read `git diff` on the two `channels/` files first — if an edit there is wanted, commit it instead
   of discarding it). Then decide the untracked `channels/inbound/` mail: it is the mail record and
   should be committed, not left untracked.
2. Harden `land_runs.py` so this cannot recur: add `channels/inbound/` to `RECORD_PREFIXES` (mail
   intake is append-only record written by the bots, exactly like `channels/conversation/`), and make
   the dirty-tree refusal report-and-clear known-spurious paths (a dirty path whose content equals
   `HEAD` should be reset, not treated as somebody's unfinished work).
3. The parked runs are not lost: each carries a `changes.patch`. Once the tree is clean, the drain
   should be able to land them.

## The 39 changed paths stranded by this (only in the run patches, not in `main`)

- `.github/workflows/test-and-report.yml`
- `README.md`
- `actuator/README.md`
- `agenda/04-outreach.md`
- `agenda/32-affective-pain-neuromodulation-evidence-map.md`
- `channels/agenda.md`
- `channels/auto_reply.py`
- `channels/declutter/2026-10-04.md`
- `channels/outreach/drafts/2026-10-05-followup-fluge.md`
- `channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`
- `channels/outreach/pipeline.json`
- `channels/reject-queue.md`
- `governance/request-register.md`
- `governance/roster-amendment-audit.md`
- `outreach/reddit/README.md`
- `probes/results/2026-10-04-probe-report.md`
- `research/affective-pain-neuromodulation-acupuncture-filtered-raw.json`
- `research/affective-pain-neuromodulation-evidence-map.md`
- `research/live-harness-guard-audit.md`
- `research/reddit-read-access-2026-10-05-raw.json`
- `research/reddit-read-access-2026-10-05.md`
- `scripts/README.md`
- `scripts/affective_pain_acupuncture_filtered.py`
- `scripts/affective_pain_biomarker_only.py`
- `scripts/check_roster_consistency.py`
- `scripts/outreach_followup_due.py`
- `scripts/reddit_read.py`
- `scripts/tell_human.py`
- `scripts/zz_probe_measurement.py`
- `tests/test_affective_pain_acupuncture_filtered.py`
- `tests/test_affective_pain_biomarker_only.py`
- `tests/test_auto_reply.py`
- `tests/test_live_harness_guards.py`
- `tests/test_outreach_followup_due.py`
- `tests/test_reddit_read.py`
- `tests/test_request_register.py`
- `tests/test_roster_consistency.py`
- `tests/validate_recalls_page.mjs`
- `to-do-lists/desi.md`
