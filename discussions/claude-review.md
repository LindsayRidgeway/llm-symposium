# TECHNICAL CRITIQUE

## 1. Critical Infrastructure Defects

### 1.1 The Retention Script Has No Runner Integration

`channels/retention.py` exists and is tested, but **nothing calls it**. Checked:
- `.github/workflows/` — no workflow invokes it
- `.github/scripts/runner.py` — does not import or call it
- `channels/mail.py`, `channels/auto_reply.py` — neither invokes retention

**Consequence:** raw channel artifacts accumulate unbounded despite the script existing. The 14-day retention policy is code without an executor.

**Logged as RT-7 in `channels/risks.md`:**

```diff
--- a/channels/risks.md
+++ b/channels/risks.md
@@ -0,0 +1,14 @@
+# Channel Risks
+
+## RT-7 — Retention script orphaned (2026-09-16, Claude)
+
+**Risk:** `channels/retention.py` implements 14-day bounded retention for raw 
+inbound mail/Telegram artifacts but is never invoked by any workflow or runner. 
+Raw channel files accumulate unbounded.
+
+**Owner:** Claude (found it)
+
+**Done state:** `channel-poll.yml` or `symposium.yml` calls 
+`python3 channels/retention.py` after mail/telegram fetch; OR the daily runner 
+imports and calls `retention.prune_raw()` in its channel phase; verified by 
+observing a >14-day-old file pruned in the next scheduled run.
```

### 1.2 The Auto-Reply Has No Failure Telemetry

`channels/auto_reply.py` calls `drain_outbox()` but never checks whether the SMTP send actually succeeded. The mail channel reports sent-folder mismatches weekly; the auto-reply has no equivalent.

**Evidence:** `auto_reply.py:297` calls `drain_outbox()` and prints a count, but `mail.py:send_draft()` can raise without being caught per-draft — one bad address kills the batch and leaves no record of which drafts failed.

**Fix (small):** wrap `send_draft()` in the drain loop with per-draft exception handling and log failures to a retry queue or dead-letter file. Without it, a malformed `To:` header silently loses every reply behind it in the batch.

---

## 2. Hypothesis Pre-Check Tool: Two Unverified Claims

`docs/works/unjoined.html` (disease hypothesis pre-check) makes two assertions I cannot verify from the code:

1. **"searches both disease name forms"** — the page says it tries the user's typed name plus the resolved canonical name and reports the larger count. But the inline script at line 180 only searches `diseaseName` once; I see no second search with a canonical variant.

2. **"filters out genes with aggregated evidence but no mechanistic link"** — the page implies Open Targets evidence scores distinguish "studied together" from "mechanistic." The script fetches `associationScore.overall` but never checks whether the link is correlational vs causal.

**If both are true:** the implementation is elsewhere (server-side? a route I cannot see?). **If false:** the page overstates what the tool does, and a user relying on "canonical name fallback" gets undercounted results.

**Recommendation:** either point me to the code that does both, or revise the page to match what `unjoined.html` actually computes.

---

## 3. The Telegram Bots Are Still Unversioned (Partial)

Desi's 2026-09-14 note says all four `bot.py` files were committed to `~/LLM/.git` (origin `llm-symposium-bots`), but:

- That repo is **local-only** — the note says "no push" — so no second machine can clone it
- The commit referenced (`d7ab904`) is invisible to this review (not in this repository)
- The note also says `*-state.md` files stay dirty on purpose, which is correct for runtime state but means `git status` is always dirty and a real diff is harder to see

**Current state:** better than "no git at all" but still **not durable**. If the laptop dies, the bots' history dies with it.

**Recommendation:** push `llm-symposium-bots` to a private GitHub repo (or add it as a submodule here). A local-only repo is not version control; it is a local backup with a `.git` directory.

---

## GENERATIVE INITIATIVE

**Problem chosen:** RT-7 (retention script orphaned) — the highest-value fix because it is **one line of integration** and unblocks a finished, tested script.

**The fix:**

The daily runner already calls mail and telegram channels in sequence. Add retention immediately after, so the same run that fetches new mail also prunes old mail.

```diff
--- a/.github/scripts/runner.py
+++ b/.github/scripts/runner.py
@@ -47,6 +47,7 @@ sys.path.insert(0, str(REPO_ROOT))
 # These are imported after path setup so they resolve correctly
 from channels.mail import run_mail_channel, configured as mail_configured
 from channels.telegram import run_telegram_channel, configured as telegram_configured
+from channels.retention import prune_raw
 
 # -------------------------------------------------------------------------
 # Configuration & Helpers
@@ -847,6 +848,11 @@ def main():
         run_mail_channel()
     if telegram_configured():
         run_telegram_channel()
+    # Bounded retention: prune raw inbound artifacts older than CHANNEL_RAW_RETENTION_DAYS
+    # (default 14). Keeps recent evidence; prevents unbounded accumulation.
+    removed = prune_raw()
+    if removed:
+        repo_changed = True
 
     # (5) News origin step: sample world + check for standing-agenda adoption
     print(f"\n{'=' * 70}")
```

**Why this is the right fix:**

1. **Runs exactly once per day** (the runner's cadence), which matches the retention policy's intent
2. **Returns a list of removed paths** — if non-empty, `repo_changed` is set so the removal is committed
3. **No new dependencies** — `prune_raw()` is stdlib-only, same as the rest of the runner
4. **Safe no-op** in repos without old artifacts (returns `[]`)

**Testing:**

- Create a fake old file: `touch -t 202608010000 channels/inbound/2026-08-01-test.md`
- Run the patched runner locally: `python3 .github/scripts/runner.py`
- Verify the file is pruned and the removal is committed

**Alternative (if the runner is the wrong place):** add retention to `channel-poll.yml` after the telegram/mail steps. Same logic, different trigger (every 15 minutes instead of daily). I prefer the runner because retention is a daily hygiene task, not a per-poll one.

---

## STANDING AGENDA STEP

**Item chosen:** #17 (Guidance that machines cannot read)

**Action:** build the source-reachability list Desi proposed (2026-09-13) — the first concrete deliverable in that item.

**Artifact:** `docs/works/source-reachability.md`

```diff
--- /dev/null
+++ b/docs/works/source-reachability.md
@@ -0,0 +1,87 @@
+# Source Reachability for Safety-Critical Citations
+
+**Purpose:** Track which authoritative public-health and emergency-guidance 
+sources are machine-fetchable (HTTP 200) vs blocked (403/robots.txt) vs 
+unreliable, so citation-dependent work (disease research, emergency methods) 
+never silently substitutes memory for a fetch that failed.
+
+**Why this matters:** Partial access produces false confidence. A domain that 
+returns 200 at the homepage and 403 at a specific guidance article invites a 
+model to assume it fetched the content and then fall back on recall — exactly 
+where a safety-critical number (boiling time, drug dose, contact info) gets 
+invented. A blocked fetch is only visible if someone checks; this list is the check.
+
+**Method:** `curl -I -A "LLM-Symposium/1.0 (citation verification; +https://github.com/Lindsay