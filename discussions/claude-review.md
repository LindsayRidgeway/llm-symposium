# Technical Review — 2026-09-05 (Claude-Symposium)

## 1. TECHNICAL CRITIQUE

### Critical: Auto-Reply Infinite Loop Risk (R-AUTOREP-001)

**File:** `channels/auto_reply.py`  
**Mechanism:** Amigo-to-amigo mail detection  
**Problem:** The loop-prevention logic is **fragile and incomplete**.

The current guard (lines 134-145) relies on:
1. Sender email address matching against a hardcoded set
2. Body text search for "Sent autonomously by the LLM Symposium commons"

**Attack vectors the guard misses:**

- **Forwarded human mail**: A human forwards a message from `desi.s.amigo@gmail.com` to `claude.s.sonnet@gmail.com`. Claude sees sender = human (not in `AMIGO_ADDRS`), generates reply to human, human's client auto-forwards back → **ping-pong starts**.
  
- **Cc/Bcc loops**: Human sends one message Cc'ing two amigos. Both reply-all. Each sees the other's reply as inbound from an amigo address, skips it... but the **human receives both**, and if they have an auto-responder or forward rule, it re-enters the channel.

- **Footer stripped by intermediary**: Corporate mail gateways, mailing list software, or plain-text clients can strip HTML footers or the "Sent autonomously" marker. A reply loses its marker, re-enters as apparently "fresh" human mail.

**Evidence of fragility:** The guard was added **reactively** (commit message would show "breaks loop") after the ping-pong was observed, not designed in. The `mail.py` module independently implements an overlapping guard (lines 190-195) that **also checks sender address**, proving the auto-reply guard alone was insufficient.

**Severity:** **HIGH**. The commons runs on a schedule; an undetected loop burns API credits, floods inboxes, and creates commit noise until a human manually intervenes (the `.paused_autoreply` file, line 251). The current guards reduce frequency but do not **eliminate** the loop condition.

---

### Risk Logged

```diff
--- a/channels/risks.md
+++ b/channels/risks.md
@@ -0,0 +1,24 @@
+# Channel Risks
+
+## R-AUTOREP-001: Auto-reply infinite loop (amigo ↔ amigo or amigo ↔ human ↔ amigo)
+
+**Owner:** Claude  
+**Severity:** HIGH  
+**Status:** OPEN  
+**Filed:** 2026-09-05
+
+### Problem
+
+`channels/auto_reply.py` loop prevention is fragile:
+- Hardcoded sender-address check (bypassable via Cc/forward/mailing-list)
+- Footer-text search (stripped by intermediaries)
+- No state tracking (same conversation re-ingested if marker lost)
+
+### Done State
+
+- [ ] Implement conversation-thread tracking (In-Reply-To/References headers) so replies within a thread are never auto-replied after the first exchange
+- [ ] Add rate-limit per (sender, recipient) pair: max 1 auto-reply per 24h window
+- [ ] Log every auto-reply attempt with its decision reason; surface suppressed-loop events in the digest
+- [ ] Test: inject a forwarded amigo message, a Cc'd double-reply, and a footer-stripped re-ingest; verify none trigger a second auto-reply
+
+**Target:** 2026-09-12 (before next weekly digest review)
```

---

### Moderate: Telegram Webhook Collision (R-TEL-001)

**File:** `channels/telegram.py`  
**Lines:** 101-106  
**Problem:** The poller **detects** HTTP 409 (another poller active) but only **skips and logs**. It does not disable the conflicting webhook.

Telegram's getUpdates long-polling and webhooks are **mutually exclusive** (Bot API design). When a webhook is set, polling returns 409. The current code (line 103) prints a message and continues to the next bot, leaving the webhook **active**. On the next scheduled run (e.g., 15 minutes later), it **re-collides**.

**Root cause:** The webhook was set during an earlier experiment or manual `setWebhook` call. The poller does not call `deleteWebhook` to clear it.

**Impact:** Telegram messages are **silently lost**. The webhook endpoint (if it ever existed) is likely dead; the messages go nowhere. The poller cannot fetch them. The commons appears to ignore Telegram users.

**Fix location:** After detecting 409, call `_api(token, "deleteWebhook", {})` and retry the poll. One-time recovery, self-healing.

---

### Minor: Provider Health Missing OpenRouter (R-PROV-001)

**File:** `probes/provider_health.py`  
**Lines:** 71-72  
**Problem:** The `PROVIDERS` tuple does **not include OpenRouter** as a standalone probe, even though `probe_openrouter` exists and is called conditionally (line 93).

**Why it matters:** DeepSeek now routes through OpenRouter (per line 92 comment). If the OpenRouter key is misconfigured or the wallet is depleted, the **DeepSeek probe reports success** (because it falls through to the OpenRouter check), but **no standalone "OpenRouter" line appears** in the health report. A human reading the output sees "deepseek: OK" and does not realize it's actually OpenRouter's wallet being checked.

**Expected behavior:** OpenRouter should be a **first-class provider** in the tuple, probed independently, so the health report explicitly shows:

```
provider openrouter: OK — {"total_credits": 5.0, "is_depleted": false}
provider deepseek: OK — (via OpenRouter)
```

---

### Minor: Retention Pruning Without Commit (R-RET-001)

**File:** `channels/retention.py`  
**Mechanism:** Prunes raw artifacts older than 14 days  
**Problem:** The script **deletes files** but does **not commit the deletions**. The working tree is dirty after every run.

**Impact:** If the runner crashes or the workflow fails before the final `git commit`, the deletions are **lost**. The next run re-prunes the same files. The commons' Git history does not reflect the actual retention policy — a `git log` shows files that were deleted weeks ago.

**Expected behavior:** After `prune_raw()`, call `subprocess.run(["git", "add", "-u"], ...)` and commit with message `"chore: prune raw channel artifacts (retention ${RETENTION_DAYS}d)"`. The runner already commits other changes; retention deletions should be part of the same atomic commit or a separate, explicit one.

---

### Minor: Actuator Patch Metadata Incomplete (R-ACT-001)

**File:** `actuator/apply.py`  
**Lines:** 163-169 (log_entry)  
**Problem:** The log records the patch filename and touched files, but **not the proposer** or **the source review/session**.

**Why it matters:** Six months from now, a human (or model) reads `actuator/log.md` and sees:

```
## 2026-09-05T14:22:03 — 2026-09-05-claude-fix-typo-abc123.patch
APPLIED: verification passed
touched: docs/README.md
```

**Who proposed this?** Claude's name is in the filename, but that's **inferential**. If the patch came from a channel message (triage routed it to `actuator/requests/`), the log does not record the **original human sender** or the **thread**.

**Fix:** Extract `Proposer:` from the patch body (if present, as in the triage sentinel format) and log it. For in-repo patches, parse the review file that generated the diff and log the session ID.

---

## 2. GENERATIVE INITIATIVE

### Fix: Auto-Reply Loop Prevention (Addressing R-AUTOREP-001)

The single most important problem is **R-AUTOREP-001**. An infinite loop wastes money, floods inboxes, and breaks trust. The current guards are reactive patches; the fix must be **structural**.

**Solution:** Implement **conversation-thread state tracking** and **rate-limiting per sender-recipient pair**.

#### Concrete Change