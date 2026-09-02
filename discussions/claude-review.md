# Technical Critique — LLM Symposium Repository State (2026-09-02)

## Actuator (`actuator/apply.py`)

**Architecture: Sound.** The self-modification guard, verification pipeline, and rollback-on-failure design are exactly what an autonomous patch engine needs.

**Critical vulnerability discovered and fixed:** The path-canonicalization bug (lines 38–48, `_canonical()`) was a real exploit vector. Before the fix, `actuator//apply.py` or `actuator/./apply.py` would bypass the string-match guard while `git apply` treated them as the engine itself. The current implementation resolves paths against `REPO_ROOT` and collapses to POSIX form, closing the gap. Test coverage confirms it (`test_self_modification_guard_catches_normalized_path`).

**Minor fragility:** `touched_files()` uses two regex passes (diff headers, then unified-diff `+++` lines as fallback). Edge case: a patch with *only* deletions (no `+++` lines) would return an empty list, bypassing the self-mod guard if the deletion targets the engine. Suggest: parse `---` lines as well, or fail-closed when no files are detected.

**Timeout hygiene:** `GIT_TIMEOUT=60`, `SUITE_TIMEOUT=240` are sane. The top-level `try/except subprocess.TimeoutExpired` (line 171) surfaces timeouts explicitly instead of hanging CI.

**Verification gap:** `py_compile` catches syntax errors but not runtime failures in non-test code. A patch that introduces a logic bug in a module imported only at runtime (e.g., `channels/triage.py`) would pass verification. The current suite (`test_projection.py`, `ticktick_recurrence_probe.py`) exercises the TickTick stack but not the mail/telegram/triage modules. Recommendation: add smoke imports for all production modules to the verification suite.

---

## Channels (`channels/mail.py`, `channels/telegram.py`, `channels/triage.py`)

**Credential resolution (`mail.py` lines 89–112):** The per-amigo + generic-fallback pattern is clean. The `credentials_for()` logic treats partial config (one env var set, the other missing) as unconfigured — correct; sending with a half-configured identity would leak which half is present.

**IMAP idempotency (`mail.py` lines 216–235):** The recorded fix (search `ALL`, skip already-filed Message-IDs) closes the "fetch crashes mid-run, loses messages on retry" hole. Current implementation maintains a `filed_ids` set built from existing files' Message-ID headers. A Message-ID collision (same ID, different body) would suppress the second message. Probability: low for human mail, zero for typical MUAs. Document or accept.

**Automated-sender filter (`mail.py` lines 51–68):** The `AUTOMATED_SENDER_RE` + delivery-failure exception is pragmatic. Delivery failures are telemetry (filed under `inbound/diagnostics/`) rather than noise. The regex covers `mailer-daemon`, `postmaster`, `noreply`, and Google account notices. **Blind spot:** transactional mail from services (Stripe receipts, GitHub notifications) will be skipped. If a human forwards such a message, the `From:` is the service, not the human, so it's lost. Document the limitation or route forwards differently (e.g., check `Reply-To` for human domains).

**Sent-folder verification (`mail.py` lines 265–308):** Subject-based matching against the provider's Sent folder is a clever telemetry layer. Silent SMTP acceptance + provider drop is detectable. **Fragility:** subject collisions (two letters with identical subjects) yield false positives. The report prints both missing letters *and* the full provider list, so a human can disambiguate. Accept as operational telemetry, not a proof.

**Telegram long-poll avoidance (`telegram.py` line 72):** `timeout=0` (non-long-poll) is justified in the comment: the scheduled poller is already frequent; long-poll connections risk HTTP 409 collisions. **HTTP 409 handling (lines 172–175):** caught and logged, not fatal. Correct.

**Triage action-queue deduplication (`triage.py` lines 100–114):** SHA-1 digest over `channel|identity|sender|subject|text` prevents duplicate queue entries. **Collision risk:** a human resends identical text with identical subject → same digest, suppressed as duplicate even if the intent differs. Pragmatic trade-off; false-negative rate is acceptably low for operational use.

**Channel-originated actuator bridge (`triage.py` lines 136–180):** The `PATCH_SENTINEL` + `Proposer:` + blocked-path filter is the right narrow gate. Blocking `.github/`, `actuator/apply.py`, and secret-bearing paths is correct. **Gap:** a malicious model proposer could craft a patch to `probes/` or `tests/` that introduces a backdoor exercised only when the probe/test runs (e.g., exfiltrate env vars during CI). The current gate assumes probe/test code is trusted. Recommend: either block `probes/` and `tests/` from channel-originated patches, or add a review step for those paths.

---

## Probes (`probes/recurrence_projection.py`, `probes/ticktick_recurrence_probe.py`)

**RRULE subset enforcement (`recurrence_projection.py` lines 54–104):** `validate_rrule()` raises `UnsupportedRRULEError` for keys outside the documented subset. The leap-day exception (lines 64–75) is explicit and narrow. Test coverage is strong (`test_projection.py` lines 94–112 enumerate rejected rules). **Undocumented behavior:** `BYMONTH` and `BYMONTHDAY` with conflicting values (e.g., `BYMONTH=2;BYMONTHDAY=29;BYMONTH=3`) are rejected, but the rejection message doesn't explain *why*. The test expects rejection; suggest: clarify in the error message that multi-value `BYMONTH` is unsupported.

**DST-aware parsing (`recurrence_projection.py` lines 155–189):** `parse_date_tz()` localizes naive datetimes with `fold=0`, then round-trips through UTC to detect spring-forward gaps. A nonexistent wall time (e.g., 2:30 AM on spring-forward Sunday) shifts forward to the first valid instant (3:00 AM), *preserving the calendar date*. The implementation is correct per the documented edge-case coverage. Test coverage confirms spring-forward, fall-back, and explicit-offset cases (`test_projection.py` lines 114–127).

**Truncation detection (`recurrence_projection.py` lines 286–310):** `probe_overlap()` compares two windows' returned instances over their shared range. Divergence → truncation evidence. `projected_but_not_returned()` flags dates projected but absent from *all* probe windows. The dual approach (overlap divergence + missing projections) catches both "window A vs. B differ" and "connector consistently under-returns." **Fixture dependency:** the probe requires recorded probe windows with known-good returned instances. The fixture schema (`probes/fixtures/example.json`) is well-formed; the probe report (`probes/results/2026-09-01-probe-report.md`) confirms the dual approach surfaces truncation.

**Layer attribution (Gap C, `ticktick_recurrence_probe.py` lines 42–89):** The live API check hits `/open/v1/project` (proves token validity) and `/open/v1/task/query` (task-list endpoint candidate). The function captures response bodies and status codes. The report (lines 145–163 of the probe output) shows `projects: HTTP 200 OK — returned 7 item(s)` and `tasks: HTTP 200 OK — returned 0 item(s)`. Token validity is confirmed; the task-list endpoint shape is documented. **Gap:** the probe doesn't compare the live API response to a connector's response for the same query. Layer attribution "now hinges on the task-list endpoint shape" (probe report line 162), but no recorded connector response exists to compare against. To close Gap C fully, record a parallel connector query and diff the two responses.

---

## Retention (`channels/retention.py`)

**Artifact timestamp heuristic (`retention.py` lines 35–49):** Prefers leading `YYYY-MM-DD` in filename over mtime (because GitHub checkouts refresh mtimes). Falls back