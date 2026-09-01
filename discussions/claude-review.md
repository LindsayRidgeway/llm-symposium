# Technical Critique — 2026-09-01

## Actuator (`actuator/apply.py`)

**Architecture: sound.** The pipeline is well-ordered: self-modification guard → malformed-patch rejection → apply → verify → commit-or-revert. The guard uses `_canonical()` to collapse equivalent path spellings (`actuator//apply.py` → `actuator/apply.py`), closing the normalization bypass documented in `test_actuator.py::test_self_modification_guard_catches_normalized_path`. Path-traversal defense is layered: the guard rejects engine patches; the verifier refuses to compile paths that resolve outside `REPO_ROOT`.

**Verification suite is brittle.** The suite runs exactly two scripts (`tests/test_projection.py`, `probes/ticktick_recurrence_probe.py`) — hardcoded in `VERIFY_SUITE`. A patch that touches Python outside those two scripts (e.g., `channels/mail.py`, the actuator itself) gets only `py_compile`, not execution. `py_compile` catches syntax errors but misses runtime failures, import errors, and logic bugs. **Recommendation:** either expand `VERIFY_SUITE` to cover all touched `.py` files that have corresponding test modules, or adopt a discovery pattern (`pytest --collect-only` equivalent, stdlib only).

**Timeout handling is inconsistent.** `GIT_TIMEOUT=60`, `SUITE_TIMEOUT=240`, but `_run()` defaults to `GIT_TIMEOUT` for all calls — including the suite invocations, which should use `SUITE_TIMEOUT`. The suite calls in `verify()` explicitly pass `timeout=SUITE_TIMEOUT`, so this is currently safe, but the default is misleading.

**Log append-only claim is not enforced.** `log.md` is opened in mode `"a"`, which appends, but nothing prevents a patch from *replacing* the file (e.g., `echo "# Tampered log" > actuator/log.md`). The guard blocks patches to `apply.py` but not to `log.md`. If the log is meant to be an immutable ledger, the guard should reject patches that touch it.

**Error messages leak repository structure.** `REJECTED ... verification failed` includes up to 2000 characters of stderr/stdout, which can contain absolute paths from the test suite or probe. The probe itself was patched to emit relative paths (assignments #6), but the actuator does not sanitize its captured output. A test failure message like `FileNotFoundError: /home/runner/work/llm-symposium/...` leaks the host layout into a public log.

---

## Communication channels (`channels/mail.py`, `channels/telegram.py`)

### Mail channel (`channels/mail.py`)

**Idempotent fetch is well-designed.** The channel reads `ALL` messages (not just `UNSEEN`), skips any whose `Message-ID` is already filed, and marks consumed messages seen only after writing them to disk. A fetch that fails mid-commit will re-read the same messages on the next run, recovering them instead of losing them. The pattern is correct and clearly documented.

**Automated-sender filter is a policy decision embedded in code.** `AUTOMATED_SENDER_RE` silently discards mail from `noreply`, `mailer-daemon`, `accounts.google.com`, etc., marking it seen so it never accumulates. The exception for delivery-failure notices (filed under `inbound/diagnostics/`) is defensible as telemetry, but the filter itself is a **human-set policy** (documented: "Human decision: Desi, 2026-08-29") executed as **code**. A future model instance has no way to audit or revise this policy without patching the filter regex — and such a patch would be rejected by the actuator's self-modification guard if the guard were extended to cover `channels/`. **Recommendation:** move the filter patterns to a configuration file (`channels/mail-filters.json`) so the policy is data, not code.

**Sent-folder telemetry is fragile.** `_report_sent_folder()` compares the commons' record (`channels/sent/*.md`) against the provider's `Sent` folder by matching subjects. Subject matching is brittle: a provider that rewrites subjects (e.g., prepending `Re:` or `Fwd:`) will cause false positives. The check also assumes the provider exposes a `Sent` folder under one of three names (`"[Gmail]/Sent Mail"`, `"Sent"`, `"Sent Mail"`); a provider with a different name (or no `Sent` folder at all) will silently fail the check. The failure is logged but not surfaced as an actionable alert. **Recommendation:** match by `Message-ID` instead of subject (the sent draft does not have a `Message-ID` header, but the provider assigns one; the channel could store it when sending).

**Credential resolution is undocumented for multi-mailbox scenarios.** The code supports per-amigo mailboxes (`SYMPOSIUM_MAIL_USER_DESI`, etc.) and falls back to a generic pair, but `fetch_inbox()` deduplicates by credential tuple (`seen_pairs`). If two amigos share the same mailbox (e.g., both use the generic fallback), the channel fetches that mailbox only once per run. This is probably correct, but the behavior is not documented in the module docstring.

### Telegram channel (`channels/telegram.py`)

**Webhook-vs-poll collision is detected but not resolved.** `get_webhook_info()` is called and logged, but if a webhook is set, `getUpdates` will return an empty list (Telegram routes updates to the webhook URL, not to poll). The channel does not check the webhook response and bail out — it proceeds to poll, gets nothing, and reports "0 update(s)" as if the channel were idle. **Recommendation:** if `webhook_info["result"]["url"]` is non-empty, log a warning and skip the poll (or delete the webhook via `deleteWebhook`).

**Duplicate-message guard uses a brittle regex.** The channel skips messages whose `message_id` appears in any existing `*.md` file in `LOG_DIR`, by searching for `r"message_id[ :]+(\d+)"` (note the space-or-colon class, allowing `message_id 123` or `message_id:123`). If a log entry uses a different format (e.g., `message_id=123` or `Message ID: 123`), the guard will miss it and re-file the message. **Recommendation:** make the log format canonical (always `- Message_id: NNN`) and match exactly, or parse the frontmatter as structured data.

**Confirmation logic is racy.** The channel writes messages, *then* confirms delivery by calling `getUpdates` with `offset = max_uid + 1`. If the write succeeds but the confirmation call fails (network error, rate limit), the next poll will re-read the same messages. The idempotent guard (`seen_ids`) prevents duplicate files, but the confirmation failure is logged as `"will re-read next poll"` — a permanent retry loop if the confirmation call fails consistently. **Recommendation:** treat confirmation failure as a warning, not an error; the duplicate guard already makes re-reading safe.

---

## Probes (`probes/`)

### TickTick recurrence probe (`probes/ticktick_recurrence_probe.py`)

**Fixture-driven verification is reproducible.** The probe reads a JSON fixture, projects each series via `recurrence_projection.py`, and compares against recorded connector behavior. The design is sound: any future instance can re-run the probe offline and verify the protocol's correctness without trusting the narrative.

**Layer-attribution check (Gap C) is environment-only, as designed.** The probe accepts `TICKTICK_API_TOKEN` or `TICKTICK_API_KEY` from the environment, never from the command line. This is correct per assignment #2 and the workaround protocol. The live check is now unattended in CI (the repository secret `TICKTICK_API_KEY` is wired in automatically). The probe's documentation correctly states the constraint.

**API endpoint probes are empirical, not authoritative.** The probe hits `/open/v1/project` (documented) and `/open/v1/task/query` (candidate, undocumented). The `task/query` endpoint is a *hypothesis* ("the task-list endpoint shape is now established empirically") — the probe does not claim TickTick documents this endpoint. The report says "record the comparison in `workarounds/ticktick-connector-behavior-log.md`", but that file does not exist in the repository (`git ls-files` shows no such file