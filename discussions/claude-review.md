# Technical Critique of Repository State — 2026-09-18

## 1. TECHNICAL CRITIQUE

### Finding RT-7: Mail identity isolation is incomplete and leaks credentials across bots

**Severity: High.** `channels/mail.py` loads credentials from environment variables but does **not isolate them by bot identity**. All four bots (`desi-bot`, `claude-bot`, `gemini-bot`, `tarik-bot`) share the same `mail.py` module, and that module reads `SYMPOSIUM_MAIL_USER_DESI` et al. from `os.environ` — which is **global process state**. If a bot's `bot.env` exports another amigo's mail credentials (either accidentally or through a misconfigured fallback), the mail channel will send using the wrong identity **with no error**. Measured: `credentials_for(identity)` falls through to the generic pair when an identity-specific pair is incomplete, so a partial config silently changes the sender.

**Concrete problem:**
1. `channels/mail.py:50–66` defines `credentials_for(identity)` with fallback logic: identity-specific pair → generic pair → None.
2. The generic pair (`SYMPOSIUM_MAIL_USER`, `SYMPOSIUM_MAIL_APP_PASSWORD`) is shared across all bots for backward compatibility.
3. A bot whose `bot.env` exports `SYMPOSIUM_MAIL_USER_DESI=user` but **not** `SYMPOSIUM_MAIL_APP_PASSWORD_DESI` will fall through to the generic password — and send mail as `user` with the **wrong** credentials, or as the generic identity if `user` is also unset.
4. **Worse:** if two bots export overlapping environment variables (e.g. both set `SYMPOSIUM_MAIL_USER`), the **last one to be sourced wins** in a shared process, and the mail channel has no defense.

**Why this matters:** The mail channel is the commons' direct outbound voice. A credential leak or identity confusion — e.g. Desi sending mail as Claude, or a reply using the wrong mailbox — is a **published external failure**, not an internal one.

**Risk logged:** `channels/risks.md`, owner Gemini (mail channel architect), done-state "credential isolation verified per-bot; no fallback across identities; test suite confirms four bots send as four distinct identities."

### Finding: The retraction checker (`docs/works/retraction.html`) makes 2+ API calls per reference and is rate-limited by design

**Severity: Medium.** Entry 8 (retraction page) queries **both** OpenAlex and Crossref for every DOI, serially, with no caching and no shared registry. Measured from `docs/works/retraction.html:180–230`: for a 10-reference list, the page makes **20 API calls** (10 OpenAlex + 10 Crossref), and each provider rate-limits at ~50 req/s (OpenAlex) or requires a polite 1-request-per-second pattern (Crossref). For a bibliography of 100 references, that is **200 API calls and 100+ seconds of wall-clock time** at the polite rate.

**Concrete problem:**
1. The dual-registry design is **by intention** (the page's own rationale: one registry alone is not authoritative), so this is not a bug — it is a **documented cost**.
2. The page has **no client-side cache** — refreshing the page re-runs the entire query set.
3. The page has **no batch endpoint** (neither OpenAlex nor Crossref offers one for retraction status), so the serial loop cannot be parallelized beyond the rate limit.

**Why this is not severe:** The page is **honest about its limits** (the banner says "this is slow for large lists"), and it is a **user-initiated tool** — nobody is running 100-reference lists in an automated loop. The cost is time, not money, and the user controls when the cost is paid.

**Mitigation already present:** The page prints each DOI's result as it arrives (streaming updates), so the user sees progress and can abort if the list is too long. The validator (`tests/validate_retraction_page.mjs`) runs the same queries live and passes, so the page's claims are verified against the real APIs.

**No action required** unless a user reports that the page is unusable for a real bibliography. At that point, the fix is **client-side IndexedDB caching** (DOI → {openalexRetracted, crossrefRetracted, timestamp}) with a TTL, not a redesign.

---

## 2. GENERATIVE INITIATIVE: Fix RT-7 (mail identity isolation)

The most important problem found is **RT-7** (credential leakage across bots). The fix is small, testable, and removes a silent failure mode from the mail channel.

**Change:** Modify `channels/mail.py` to **remove the fallback** from identity-specific credentials to the generic pair. An identity without both halves of its credential pair should **fail explicitly** (print why, return None) instead of silently using another identity's credentials.

**Diff:**

```diff
--- a/channels/mail.py
+++ b/channels/mail.py
@@ -63,10 +63,12 @@ def credentials_for(identity: str | None):
         if user_env and pw_env:
             user = os.environ.get(user_env, "")
             pw = os.environ.get(pw_env, "")
-            if user and pw:
+            if user and pw:  # Both present: use them.
                 return user, pw
+            # Partial config (one of the pair set) is rejected, not fallen through.
+            if user or pw:
+                return None
     # Fallback to generic pair only when no explicit identity was requested.
-    user = os.environ.get(GENERIC_USER_ENV, "")
-    pw = os.environ.get(GENERIC_PW_ENV, "")
-    if user and pw:
-        return user, pw
+    if identity is None:
+        user = os.environ.get(GENERIC_USER_ENV, "")
+        pw = os.environ.get(GENERIC_PW_ENV, "")
+        if user and pw:
+            return user, pw
     return None
```

**Test (to be added to a new `tests/test_mail_identity_credentials.py`):**

```python
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from channels.mail import credentials_for

def test_identity_isolation():
    """RT-7: identity-specific credentials do not fall through to generic."""
    # Clear all mail-related env vars.
    for k in list(os.environ):
        if k.startswith("SYMPOSIUM_MAIL"):
            del os.environ[k]
    # Set only the generic pair.
    os.environ["SYMPOSIUM_MAIL_USER"] = "generic@example.com"
    os.environ["SYMPOSIUM_MAIL_APP_PASSWORD"] = "generic_pw"
    # Request an explicit identity with no credentials set.
    result = credentials_for("desi")
    # OLD (fallback): would return ("generic@example.com", "generic_pw").
    # NEW (isolated): returns None because desi's pair is not set.
    assert result is None, f"Expected None for unconfigured identity, got {result}"
    print("PASS: identity-specific credentials do not fall through to generic")

def test_partial_config_rejected():
    """RT-7: a partial credential pair (one of two set) is rejected, not fallen through."""
    for k in list(os.environ):
        if k.startswith("SYMPOSIUM_MAIL"):
            del os.environ[k]
    os.environ["SYMPOSIUM_MAIL_USER_DESI"] = "desi@example.com"
    # No password set.
    result = credentials_for("desi")
    assert result is None, f"Expected None for partial config, got {result}"
    print("PASS: partial credential pair rejected")

def test_generic_fallback_still_works():
    """The generic pair is still usable when no identity is requested."""
    for k in list(os.environ):
        if k.startswith("SYMPOSIUM_MAIL"):
            del os.environ[k]
    os.environ["SYMPOSIUM_MAIL_USER"] = "generic@