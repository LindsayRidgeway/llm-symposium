# Technical Critique — 2026-09-03

## Actuator (`actuator/apply.py`)

**Strengths:**
- The self-modification guard is correctly implemented with path canonicalization (`_canonical`), preventing bypasses via `actuator//apply.py` or `actuator/./apply.py`.
- The pipeline is sound: `git apply --check` → apply → verify → commit or rollback.
- Path traversal defense: `verify()` explicitly checks `candidate.resolve().is_relative_to(REPO_ROOT)` before compiling.
- Idempotency via reverse-apply check prevents duplicate processing of already-applied patches.

**Defects:**

1. **Race condition in `process_request`**: The patch is applied at L136 but not committed to git. If the actuator crashes or is interrupted between apply and the `_move` call (L156), the working tree is dirty but the patch file remains in `requests/`, causing re-application attempts on the next run. The reverse-apply check (L128) will pass because git sees the change as already applied, but the ledger state (patch still in `requests/`) is inconsistent.

   **Fix:** Stage and commit the change immediately after successful verification, before moving the patch file.

2. **`touched_files` regex is brittle**: L65 uses `r"^\+\+\+ b/(\S+)\s*$"` as a fallback, which fails for paths containing spaces (valid in POSIX filesystems). A patch touching `docs/my file.md` will be misparsed.

   **Fix:** Use `r"^\+\+\+ b/(.+?)\s*$"` (non-greedy match to the first trailing whitespace) or parse the entire `+++ b/...` line and strip.

3. **Verification suite hardcoded**: `VERIFY_SUITE` (L27) is a static tuple. Adding new test files requires editing the engine, violating the "models build the actuator" principle stated in the docstring.

   **Fix:** Auto-discover `tests/test_*.py` and `probes/*_probe.py` at runtime.

## Channels (`channels/mail.py`, `channels/telegram.py`, `channels/auto_reply.py`, `channels/triage.py`)

**Strengths:**
- Stdlib-only SMTP/IMAP and HTTP implementations are robust.
- Per-amigo credential isolation is correctly implemented via `IDENTITIES` dict + fallback.
- The mail channel's `_report_sent_folder` telemetry (L212) is excellent operational hygiene—silent SMTP acceptance without delivery is a real failure mode.
- `triage.py` enforces narrow actuator-request routing: `PATCH_SENTINEL` + `_model_proposer` + blocked-path list prevents arbitrary channel-originated workflow modification.

**Defects:**

1. **`auto_reply.py` email extraction regex is underspecified**: L90 uses `r"<([^>]+)>"` to extract addresses from `Name <email>` format, but RFC 5322 allows nested comments and quoted strings. The regex will misbehave on `"Lastname, Firstname" <user@example.com>`.

   **Fix:** Use the stdlib `email.utils.parseaddr()` instead of regex.

2. **Telegram `drain_all_updates` does not confirm consumed offsets**: L105 pages through updates but never issues the final confirming offset (L161 in `run_telegram_channel` does confirm, but only after processing). If the script crashes mid-page, the same batch will be re-read on the next poll, potentially causing duplicate processing.

   **Fix:** Confirm the offset after each page, not just at the end.

3. **`triage.py` actuator-request routing has a TOCTOU gap**: L194 checks `path.exists()` before writing, but another process could create the file between the check and the write (L196). On high-frequency polling (e.g., Telegram bot with many users), this could cause silent overwrites.

   **Fix:** Open with `mode='x'` (exclusive creation) and catch `FileExistsError`.

4. **Mail channel `_fetch_one` uses `ALL` search but docstring says "idempotent"**: L119 searches `ALL` messages and skips filed ones, but the connector still fetches every raw message body on every run. For a mailbox with 1000+ archived messages, this is O(n) bandwidth waste.

   **Fix:** Use `SEARCH UNSEEN` and track filed message-IDs in a persistent index (e.g., `channels/.filed-ids.json`), not by re-scanning all inbound files on every run.

## Probes (`probes/recurrence_projection.py`, `probes/ticktick_recurrence_probe.py`)

**Strengths:**
- The RRULE subset is explicitly validated (`validate_rrule` + `UnsupportedRRULEError`), preventing silent misexpansion.
- DST-aware `parse_date_tz` correctly handles spring-forward gaps (fold=0, round-trip check) and preserves explicit offsets.
- The leap-day exception (FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29) is correctly never invented in non-leap years.
- Truncation detection (`probe_overlap`, `projected_but_not_returned`) is sound.

**Defects:**

1. **`expand_rrule` monthly anchor assumes `base.day` exists in all months**: L168 checks `if d.day != base.day: return False`, but if `base` is Jan 31, the rule will never match Feb (no Feb 31). This is documented as "no end-of-month rollover," but the code will silently skip months rather than failing loudly.

   **Fix:** Raise `UnsupportedRRULEError` in `validate_rrule` when FREQ=MONTHLY and `dtstart.day > 28` (or document the skip behavior in a note entry, like the leap-day case).

2. **`_matches` YEARLY logic conflates anniversary and leap-day rules**: L157–170 has a conditional that checks `if not (by_month or by_monthday): if (d.month, d.day) != (base.month, base.day): return False`. This is correct for anniversary rules, but for the leap-day exception it means `base` must itself be Feb 29. A rule anchored on Jan 1 with `BYMONTH=2;BYMONTHDAY=29` will fail the anniversary check and never project.

   **Fix:** Split YEARLY logic: if `by_month` or `by_monthday` is set, apply *only* those filters (the rule is explicit); if neither is set, apply the anniversary check.

3. **Probe report uses `os.path.relpath` but never sets `REPO_ROOT` env**: L34 (ticktick_recurrence_probe.py) says `from recurrence_projection import DEFAULT_HORIZON_DAYS` but the probe script itself sets `sys.path.insert(0, os.path.join(os.path.dirname(__file__)))` (L23), so imports resolve. However, L170 prints `shown_path = os.path.relpath(fixture_path)` without a `start=` argument, which will be relative to the *current working directory*, not the repo root. If run from a subdirectory, the path will be wrong.

   **Fix:** Use `shown_path = os.path.relpath(fixture_path, REPO_ROOT)` after setting `REPO_ROOT = Path(__file__).resolve().parent.parent`.

## Provider Health (`probes/provider_health.py`)

**Strengths:**
- Probe diversity: balance endpoints (DeepSeek, OpenRouter) + model-list pings (OpenAI, Gemini, Anthropic) correctly distinguish token validity from balance depletion.
- The OpenRouter `is_depleted` check (L60) is the right signal for auto-reload failure.

**Defects:**

1. **Anthropic fallback ping uses non-deterministic model name**: L92 defaults to `claude-sonnet-4-5`, but model names change (e.g., `claude-sonnet-4-20250514`). A model deprecation will cause false-negative health reports.

   **Fix:** Use the Anthropic SDK's model-list response to pick the current default Sonnet variant, or document the probe model name as an operational dependency.

2. **No timeout on `urllib.request.urlopen`**: While `TIMEOUT = 15` is set (