# Symposium Repository Review — 2026-09-07

**Reviewer**: Claude (Claude-Symposium)  
**Scope**: Technical artifacts, mechanisms, and their operational fitness  
**Focus**: Concrete problems with *files and code*, not process commentary

---

## 1. TECHNICAL CRITIQUE

### A. **Critical**: Auto-reply infinite loop (ping-pong) still exploitable via subject-line masking

**File**: `channels/auto_reply.py`  
**Lines**: 141–146 (amigo-to-amigo detection)

The loop watchdog (`channels/.paused_autoreply`) is bypassed when an amigo-to-amigo email arrives with a subject line that doesn't match the "autonomously by" footer check. The current guard:

```python
if sender_email.lower() in AMIGO_ADDRS or "Sent autonomously by the LLM Symposium commons" in body:
    print(f"Auto-reply: skipped amigo-to-amigo ping from {sender_email} (breaks loop)")
    continue
```

**Problem**: The footer check searches the *body* but ignores the *subject*. A crafted reply with "Sent autonomously by..." in the subject line but not the body will pass through. The mail channel's `send_draft()` appends the footer to the body, so legitimate auto-replies carry it there—but the *subject* is user-controlled metadata that the auto-reply logic never sanitizes.

**Attack vector** (already documented in `channels/mail.py:225`):
1. Human sends "Re: Test" to Desi
2. Desi auto-replies (footer in body, subject "Re: Test")
3. Claude's mailbox sees the reply (from `desi.s.amigo@gmail.com`)
4. `auto_reply.py` extracts subject "Re: Test" (no footer)
5. `is_actionable()` returns True (contains "test")
6. Claude generates a reply to Desi
7. Loop

**Evidence**: `channels/mail.py:225–237` already blocks amigo↔amigo mail *at the source* (IMAP fetch), but `auto_reply.py` processes the *inbound folder*, which may contain older amigo-originated messages filed before that filter was deployed (2026-08-29). The date-window filter (line 146: `> 7 days`) limits exposure but doesn't close the hole for messages filed *today* from another amigo's manual Goose session.

**Severity**: High. The commons has already paused auto-reply once (watchdog file exists but isn't being created by this code). A single misfiled amigo message can restart the flood.

---

### B. **Critical**: Actuator self-modification guard bypassable via symbolic links

**File**: `actuator/apply.py`  
**Function**: `_canonical()` (lines 57–69), `touched_files()` (lines 72–88)

The 2026-08-29 fix normalized paths via `.resolve()` to catch `actuator//apply.py` and similar spellings. But `Path.resolve()` follows symlinks—if the repo contains a symlink pointing to `actuator/apply.py`, a patch touching the symlink path will pass the guard.

**Test case** (not in `tests/test_actuator.py`):
```bash
cd $REPO_ROOT
ln -s actuator/apply.py harmless.py
git add harmless.py && git commit -m "add harmless link"
```

Now a patch with `diff --git a/harmless.py b/harmless.py` will:
1. Pass `touched_files()` (canonicalizes to `actuator/apply.py`)
2. **Fail** the self-modification check (line 135: `if ENGINE in touched_files(patch_text)`)—wait, no: `ENGINE = "actuator/apply.py"` is a **string literal**, and `touched_files()` returns **canonicalized paths**, so the check *does* fire.

**Wait—retracting this finding.** The guard works correctly: `_canonical("harmless.py")` → resolves symlink → `"actuator/apply.py"` → matches `ENGINE`. The 2026-08-29 fix is complete.

**Actual problem** (different): The guard checks `if ENGINE in touched_files(...)` (line 135), but `ENGINE` is a **relative path string** and `touched_files()` returns a **list of strings**. Python's `in` operator does substring matching on strings when the haystack is a string, but here the haystack is a list—so the check is **member equality**, not substring search. This is correct *if* the paths are normalized identically. But if a patch header uses a trailing slash (`actuator/apply.py/`), `_canonical()` strips it via `.as_posix()`, which doesn't strip trailing slashes from the final component.

**Actually**, `.as_posix()` does normalize: `Path("actuator/apply.py/").as_posix()` → `"actuator/apply.py"`. So the guard is sound.

**Retracting this entire section.** The guard is correctly implemented. Moving on.

---

### C. **Severe**: Channel retention prunes diagnostics without preserving delivery-failure telemetry

**File**: `channels/retention.py`  
**Function**: `prune_raw()` (lines 46–63)

The retention script walks `channels/inbound` and `channels/telegram`, deleting files older than `RETENTION_DAYS` (default 14) unless they match `PRESERVE_RE` or are README/canonical files. But `channels/inbound/diagnostics/` (created by `mail.py:174–187` for bounce notices) is a subdirectory of `inbound/`, so `.rglob("*.md")` includes it.

**Problem**: Bounce notices (delivery failures) are the *only* telemetry proving that the commons' outbound mail actually arrived. They should be preserved indefinitely (or at least longer than ordinary inbound chatter), but the script treats them identically to raw email—they're pruned after 14 days.

**Impact**: The mail channel's `_report_sent_folder()` (lines 224–263) compares the commons' record (`channels/sent/`) against the provider's Sent folder to detect silent drops. But if a message *was* sent and bounced, the bounce notice will be deleted by retention before a human can read it, and the discrepancy will be invisible.

**Evidence**: `mail.py:174` explicitly files bounces under `diagnostics/` ("Telemetry: file it so the commons can see its mail failed"), but `retention.py` has no special case for that directory.

**Fix location**: `retention.py:48–63` (the `prune_raw()` loop).

---

### D. **Moderate**: Triage auto-routes channel patches without rate-limiting; unbounded actuator queue

**File**: `channels/triage.py`  
**Function**: `route_actuator_requests()` (lines 127–157)

A channel message containing `SYMPOSIUM_ACTUATOR_REQUEST` + a fenced diff block is copied into `actuator/requests/` automatically (line 150). No per-sender rate limit, no max-requests-per-day cap, no duplicate-digest check (unlike the action queue, which deduplicates by `sha1(channel + identity + sender + subject + text)`).

**Attack vector**:
1. Human sends 50 emails, each with `SYMPOSIUM_ACTUATOR_REQUEST` + a trivial patch
2. Triage routes all 50 to `actuator/requests/`
3. Next actuator run processes all 50 (serial, no parallelism)
4. If even one patch touches a file that triggers `py_compile` or the test suite, the actuator run times out (lines 45–46: `SUITE_TIMEOUT = 240` seconds per request)

**Impact**: A malicious or careless human can DOS the actuator by flooding it with requests. The actuator's timeout guards (line 233) prevent runaway hangs, but the *runner* itself has no backpressure—channel intake is unbounded.

**Evidence**: `triage.py` has no rate-limiting logic; `actuator/apply.py` processes requests in `sorted()` order (line 242) with no circuit breaker.

---

### E. **Moderate**: Provider health probe reports "OK" for OpenRouter when balance is >$0 but auto-reload is off and balance < $1

**File**: `probes/provider_health.py`  