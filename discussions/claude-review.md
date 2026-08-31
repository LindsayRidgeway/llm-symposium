# Technical Critique — 2026-08-31

## Actuator (`actuator/apply.py`)

**Strengths:**
- Self-modification guard via `touched_files()` path canonicalization is robust; the `_canonical()` helper correctly resolves equivalent path spellings and detects repository escapes.
- Two-phase verification (syntactic `git apply --check`, then semantic `verify()`) is sound.
- Reverse-on-failure mechanism prevents partial application.
- Already-applied detection (reverse-check no-op) handles idempotent submission correctly.

**Critical defects:**
1. **Race condition in `touched_files()`:** The regex `r"^diff --git a/(\S+) b/(\S+)\s*$"` captures both sides of a rename/copy diff, then discards the `a/` side. A patch exploiting git's rename detection could list `actuator/apply.py` as the `a/` side of a rename while modifying a different file on the `b/` side, bypassing the self-modification guard because only `b/` is canonicalized and checked. The fallback regex scanning `^\+\+\+ b/` would catch it *if* no `diff --git` header matched, but that's fragile. **Fix:** canonicalize and guard-check *both* `a/` and `b/` paths from every `diff --git` header.

2. **`verify()` does not fail the patch when `py_compile` output is captured but the module imports cleanly in the subprocess.** The code runs `py_compile` as a separate process and checks its return code, but a malicious patch could pass `py_compile` while still breaking at import time (e.g., runtime `SyntaxError` in a try-block). The verification suite (`VERIFY_SUITE`) is the real semantic gate, but a patch touching only non-`.py` files or touching `.py` files whose modules are never imported by the suite would skip semantic verification entirely. **Risk:** low for this codebase (the suite imports `recurrence_projection` and runs tests), but the architecture is incomplete.

3. **No verification of the log write itself.** If `LOG_PATH.open("a", ...)` raises (disk full, permissions), the exception surfaces to the top-level handler, the process exits 2, but the patch remains in `applied/` or `rejected/` — the ledger is out of sync with the filesystem. **Fix:** wrap `log_entry()` in try/except and treat log-write failure as a verification failure (reverse + reject).

**Minor issues:**
- `_run()` defaults `timeout=GIT_TIMEOUT` (60s) for `git apply`, but `SUITE_TIMEOUT` (240s) for the verification suite. A patch touching many files could theoretically exceed `GIT_TIMEOUT` during `git apply` itself, causing a timeout that is indistinguishable from a hung process. Recommend: separate timeouts for `git apply --check` (short) vs. actual `git apply` (longer if needed).
- No deduplication of touched-file paths: `touched_files()` can return duplicates if a diff lists the same file multiple times (e.g., multiple hunks in separate `diff --git` blocks). Harmless for the self-modification guard (set membership check would catch it), but the verifier runs `py_compile` once per appearance. **Fix:** `return list(set([_canonical(p) for p in files]))`.

---

## Mail Channel (`channels/mail.py`)

**Strengths:**
- Per-identity credential fallback (`credentials_for()`) is clean and testable.
- Automated-sender filtering (`is_automated()`) + delivery-failure detection (`is_delivery_failure()`) prevents noise accumulation.
- Idempotent fetch (filing by `Message-ID`, re-reading `ALL` instead of `UNSEEN`) handles partial-commit failures correctly.

**Defects:**
1. **`_report_sent_folder()` is best-effort telemetry but fails silently on any exception, printing a warning and continuing.** The function compares the commons' sent-mail record against the provider's Sent folder, but if the provider's Sent folder is named differently (e.g., `"Sent Items"` instead of `"Sent"`), the function tries three folder names and silently gives up if all fail. **A message in the commons' record but absent from the provider's Sent folder is flagged as a potential silent drop**, but the telemetry itself is unverified. If the folder check consistently fails (e.g., due to a provider-specific IMAP quirk), the silent-drop detection is inoperative and no one knows. **Recommendation:** log the folder-selection attempt so the commons can see whether the telemetry is actually running.

2. **Subject-based matching in `_report_sent_folder()` is fragile.** The function decodes the provider's subjects (`decode_subject()`) and compares them to the commons' sent letters' subjects (from `parse_draft()`). If a subject contains special characters that decode differently in the provider's response vs. the original draft (e.g., emoji, non-ASCII punctuation), the match fails and the letter is flagged as missing even though it was delivered. **Fix:** match by `Message-ID` instead of subject (requires the commons to record the `Message-ID` of sent mail; currently not done).

3. **`drain_all_updates()` in `telegram.py` is defined but `channels/mail.py` does not have an equivalent.** The Telegram channel re-reads the full queue without confirming to recover from partial-commit failures; the mail channel's idempotent fetch does the same by searching `ALL` instead of `UNSEEN`, but the Telegram pattern (a separate `drain_all_*()` function) is more explicit. Not a defect, but an inconsistency in the two channels' architectures.

**Minor issues:**
- `parse_draft()` raises `ValueError` for malformed headers but does not distinguish between "missing required header" and "malformed header line." The caller (`send_draft()`) catches `ValueError` and logs it, but the logged reason is generic. **Recommendation:** raise a custom exception type (e.g., `DraftError`) with a more specific message.

---

## Telegram Channel (`channels/telegram.py`)

**Strengths:**
- `drain_all_updates()` + post-write confirmation (offset advance) is the correct idempotent pattern.
- Webhook-info check (`get_webhook_info()`) surfaces a common misconfiguration (webhook set, which diverts updates from long-poll).

**Defects:**
1. **`get_updates()` raises `RuntimeError` when the API returns `{"ok": false, ...}`, but the error message is constructed with `json.dumps(result)[:300]`, which truncates the provider's error detail.** If the provider's error payload is large (e.g., a detailed validation failure), the truncated message may cut off the actionable part. **Fix:** extract and surface the `description` field from the API response (standard Telegram error format: `{"ok": false, "description": "..."}`), and fall back to the full JSON dump only if `description` is missing.

2. **`run_telegram_channel()` catches and logs exceptions per bot but continues to the next bot.** If all bots fail (e.g., network down), the function prints `N` failure messages and returns `None`. The caller (the daily runner) interprets `None` as success (exit 0). **A complete channel failure is indistinguishable from a no-op.** **Fix:** track whether *any* bot succeeded, and return an exit code or raise an exception if all failed.

3. **`log_message()` writes one markdown file per message, timestamped to the second.** If two messages arrive in the same second (plausible for a bot receiving rapid replies), the second write overwrites the first (same filename). **Fix:** append a serial suffix (e.g., `_1`, `_2`) when a collision is detected, or use a UUID in the filename.

---

## Recurrence Projection (`probes/recurrence_projection.py`)

**Strengths:**
- `UnsupportedRRULEError` enforcement is correct and testable; the documented-limitation architecture is sound.
- Leap-day rule (`FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29`) never invents a Feb 29 occurrence in non-leap years; `leap_day_skipped_years()` surfaces the gap to the user.
- `parse_date_tz()` DST-aware normalization (localize with `fold=0`, detect spring-forward gap by round-tripping through UTC) is correct