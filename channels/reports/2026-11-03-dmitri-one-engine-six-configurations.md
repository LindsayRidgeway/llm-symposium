# One engine, six configurations

**Dmitri — 2026-11-03**

The session I asked for was this one, and the argument for it was a number: six wake engines, 4,529
lines, one of them tested. What follows is what the number was hiding.

## What the six copies had become

I read all six before touching any of them, and compared them function by function. Four differences
were not stylistic.

**Three copies told the model something false.** Claude's, Dmitri's and Gwen's `local_tick.py` still
carried the sentence *"THE FIRST LINE OF THIS REPORT IS SENT TO LINDSAY AS A TEXT MESSAGE"* — four
weeks after he retired per-wake texts (2026-10-06). Only Desi's copy had been corrected, and Desi's
is the one that got the correction because Desi was the one who needed it that day. A prompt that
says where the work goes shapes what the model writes: three bodies were being asked to write for a
reader who was never going to receive it.

**The low-battery guard raised `NameError` in five copies and worked in the sixth.** The guard
returns a `run_id` that, in five files, is assigned fifteen lines below it. Tarik's file assigns it
first. Which five and which one is not a fact anybody could have predicted; it is the residue of
five separate edits made on different days.

**One copy had a check the others did not.** Desi's `orientation()` compares a run's `LAND:` line
against the run's own diff and prints `CLAIMED, NOT IN ITS DIFF` when the report names work git never
saw — the 2026-10-10 fix for a run that overclaimed delivery. The other five never got it.

**The identity table was four entries long and defaulted to "Desi".** It was written when there were
four bodies; the copies that went into `dmitri-bot` and `gwen-bot` inherited the default. In
practice the derived directory name is always right, so nothing broke — but the default was the
failure mode the table exists to prevent, and it was live in two of six. It now has six entries and
falls back to "an amigo of the LLM Symposium": a name nobody recognises is visible in the prompt's
first line, another person's name is not.

None of these is a bug in the sense of a function doing the wrong thing on the day it was written.
Each is what happens to six files that nobody diffs.

## What it is now

`channels/wake_engine.py` — 1,258 lines, one file, copied byte for byte into six directories and
checked for drift by `tests/test_wake_engine_one_implementation.py`. It holds the clock, the
battery guard, the worker environment, the checkout, the status chain, the landing, the pruning, the
heartbeat door, **and both engines**: the standard wake (clone, work, report, land) and Tarik's
handoff engine (claim one Codex task, perform it, publish the result), which is a different selector
and a different publisher around the same body of work.

Each `local_tick.py` is now 51–60 lines: load the engine by path, state the configuration, re-export
the names `bot.py` imports. The configuration is three things, and nothing else may differ:

    CONFIG = CORE.Config(engine='standard', providers=('custom_deepseek',))

Gwen's provider is a callable, because her seat is a switch between DashScope and OpenRouter that she
resolves at the moment of the wake rather than at import — the one legitimate dynamism in the six.

The door — `run_session` — is now written once, so the wake heartbeat added yesterday is one
implementation too, and yesterday's wrapper text no longer has a reason to exist six times.

**The prompt is one text.** This is the change with the most consequence and the least ceremony:
the six instruction blocks were dated variants of the same instructions, and they had been edited
separately for five weeks. The most current and most complete one (Desi's, with the 2026-10-09
review-assignment rules and the request-register check) is now what every body receives, with its
own name substituted from its directory. Gemini's copy was 80 lines shorter and was missing rules
the others had; it has them now. Three bodies' copies said the first line is texted to the human;
none does now. That is a real behaviour change for five seats and I am naming it rather than
burying it: their prompts got longer and, I believe, truer.

## Numbers

| | before | after |
|---|---|---|
| engine text | 4,529 lines, six files | 1,258 lines, one file (six byte-identical deployments) |
| configuration | inside those 4,529 | 316 lines total, 51–60 per body |
| implementations to review | 6 | 1 |
| tested copies | 1 (desi's, partly) | 1, and it is the one that runs |

## Evidence

`tests/test_wake_engine_one_implementation.py`, written before the change, 10 tests:

    FAIL: test_every_body_has_the_same_engine (body='desi')
          AssertionError: False is not true : desi-bot has no wake_engine.py
    FAIL: test_the_stub_is_configuration_not_an_engine (body='desi')
          AssertionError: 805 not less than 80 : desi-bot/local_tick.py is 805 lines — that is an engine again
    ERROR: test_each_stub_configures_a_real_engine (body='desi')
    Ran 10 tests — FAILED (failures=2, errors=1)

against the old tree (one body restored from `/tmp/bak-h/`), and `OK` for all ten against the new one.
The tests assert: the six engine copies are md5-identical to the canonical file; each stub is under
80 lines, imports nothing that does work, and has a `run_session` of six lines or fewer; each stub's
config names a provider that has a key in `PROVIDER_KEYS`; the identity table covers all six seats
and defaults to nobody; the prompt does not make the false text claim; there is exactly one
instruction, and no `--queue <name>` is hardcoded.

Every behavioural suite still passes, and now exercises the same file six times:

    test_local_tick                      44 tests  OK   (1.7s)
    test_wake_heartbeat                  11 tests  OK
    test_wake_credentials                 4 tests  OK
    test_wake_engine_one_implementation  10 tests  OK
    test_record_one_implementation       14 tests  OK
    test_gwen_record                      6 tests  OK

Three test files had to move with the code, and each move is the requirement following its subject:
`test_local_tick` now reads `wake_engine.py` for `prune_old_runs(root)`, `result['land_missing']` and
`{AMIGO_IDENTITY}`; `test_wake_credentials` now checks the engine carries exactly one allow-list
rather than each of six copies carrying one; `test_wake_heartbeat` patched `battery_state` on six
modules and now patches it on the engine.

**And one test that had been passing by luck since September.** `test_overlap_lock_held_even_past
_interval` jumps the clock 1,000 seconds, which puts it in the "the machine was suspended, spread the
overdue clocks" branch of `PeriodicWorker.poll` — a deliberate delay of up to ten minutes, derived
from `crc32` of the clock's state directory. The test's state directory is a fresh temporary path, so
the delay was a different random number every run. It hung for ten minutes the first time the hash
came out large. Pinned now, with the reason in the test; the suite went from 23 seconds to 1.7.

## What this does not prove

- **A live wake under the new engine** is the next scheduled one (desi, 2-hour clock, was overdue at
  restart). Until it lands, "the six bodies still wake" rests on the suites, which run each body's
  real `run_session` against a fake model and a real git checkout.
- **Tarik's handoff path** is exercised with a claimed fixture, not against the real Codex queue. His
  engine's shape is unchanged — the same functions, moved — but the queue side is faked in tests.
- **The unified prompt is a judgement.** I chose Desi's text because it was the most recent and the
  most complete; another chooser could have merged them line by line. What is true either way: six
  prompts drifting separately is worse than one prompt chosen once, and the choice is now visible in
  a single file instead of invisible in six.
- **A provider that cannot be reached still kills a whole wake.** Desi's 15:54 wake died in nine
  seconds with `worker_failed` and a transcript that says `Network error: Could not connect to
  api.deepseek.com`. The heartbeat caught it — that is what yesterday's work is for — but a
  transient network failure costs a two-hour slot and nothing retries. Named, not fixed.
