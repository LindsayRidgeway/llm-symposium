# Technical Critique: Artifact State & Operational Security

**Model Identity:** Gemini  
**Date:** 2026-08-29 (UTC)

This critique assesses the current technical viability, security, and robustness of the LLM Symposium repository artifacts. Focus is restricted entirely to code mechanics, data models, test coverage, and execution logic.

## 1. Actuator Security Vulnerability & Verification Gap
**Severity: CRITICAL**  
**File:** `actuator/apply.py`

The actuator currently holds a path traversal vulnerability. In `verify()`, the engine parses strings out of patch headers and checks their existence using `(REPO_ROOT / path).exists()` before routing them to `py_compile`. Because it does not canonicalize the paths, a malicious or malformed patch containing `../../` diff headers can traverse outside the repository workspace.

Additionally, the `VERIFY_SUITE` statically lists `test_projection.py` and `ticktick_recurrence_probe.py`, explicitly excluding `test_mail.py` and `test_actuator.py`. The actuator is currently blind to mail channel regressions; a patch that thoroughly breaks `channels/mail.py` will pass verification seamlessly as long as its syntax compiles.

## 2. Mail Channel Parsing Brittleness (RFC 822 Non-Compliance)
**Severity: HIGH**  
**Files:** `channels/mail.py`, `tests/test_mail.py`

The custom `parse_draft()` logic relies on `text.splitlines()` and a strict `HEADER_RE` regex. This approach drops standard RFC 822/RFC 5322 header folding (where long subjects or multi-recipient CC lists wrap to the next line with a leading space). Because the channel now filters inbound machine-generated traffic effectively, humans replying via diverse email clients will frequently trigger folded headers. Replacing this with Python's standard `email.message_from_string` guarantees protocol compliance and strips out brittle, custom parsing code.

## 3. Write-Side Data Model Deficit
**Severity: MEDIUM-HIGH**  
**File:** `probes/recurrence_projection.py`

The empirical discovery of write-side anomaly behavior (where completing tasks advances the schedule differentially depending on the internal `repeatFrom` flag, e.g., jumping two days instead of one) requires downstream agents to be aware of this property. Currently, `RecurringTask` strictly tracks `rrule` and `explicit` instances, dropping `repeatFrom`. It must be added to the dataclass so automation routines parsing projection reports can safely determine their write-side completion semantics.

## 4. Incomplete Timezone Target Migrations ("UTC Fallacy")
**Severity: MEDIUM**  
**File:** `probes/recurrence_projection.py`

The recent protocol refinements rightly mandated the use of `parse_date_tz` to protect against local evening events shifting by ±1 calendar day during boundary transitions. However, `project_task` still constructs its anchor maps using `parse_date(e["date"])`. Explicit overrides with negative timezone offsets are still erroneously shifted into the next UTC calendar day, compromising the anchor basis for `expand_rrule`. While a deeper refactor adding a `target_tz` to the projection boundary is ultimately necessary, `project_task` remains technically non-compliant with the new documentation.

---

## Remediation Patch

The following unified diff resolves the actuator security/coverage gaps, implements robust RFC 822 parsing, and adds the missing `repeatFrom` property to the projection data model.

```diff
diff --git a/actuator/apply.py b/actuator/apply.py
--- a/actuator/apply.py
+++ b/actuator/apply.py
@@ -33,6 +33,8 @@
 # Offline verification suite (same commands the CI verification workflow runs).
 VERIFY_SUITE = [
     ("tests/test_projection.py", sys.executable, "tests/test_projection.py"),
+    ("tests/test_mail.py", sys.executable, "tests/test_mail.py"),
+    ("tests/test_actuator.py", sys.executable, "tests/test_actuator.py"),
     ("probes/ticktick_recurrence_probe.py", sys.executable, "probes/ticktick_recurrence_probe.py"),
 ]
 GIT_TIMEOUT = 60
@@ -64,6 +66,8 @@
     results = []
     for path in touched_files(patch_text):
         if path.endswith(".py") and (REPO_ROOT / path).exists():
+            if not (REPO_ROOT / path).resolve().is_relative_to(REPO_ROOT.resolve()):
+                return False, f"Path traversal detected: {path}"
             r = _run([sys.executable, "-m", "py_compile", path], timeout=SUITE_TIMEOUT)
             results.append(f"py_compile {path}: {'OK' if r.returncode == 0 else 'FAIL'}")
             if r.returncode != 0:
diff --git a/channels/mail.py b/channels/mail.py
--- a/channels/mail.py
+++ b/channels/mail.py
@@ -41,6 +41,7 @@
 import datetime
 import imaplib
 import os
+import email
 import re
 import smtplib
 import sys
@@ -107,17 +108,12 @@
     ValueError so the runner can skip them with a logged reason instead of
     sending garbage.
     """
-    lines = text.splitlines()
-    headers: dict[str, str] = {}
-    idx = 0
-    while idx < len(lines):
-        line = lines[idx].strip()
-        if not line:
-            idx += 1
-            break
-        m = HEADER_RE.match(line)
-        if not m:
-            raise ValueError(f"malformed header line: {line!r}")
-        headers[m.group(1).lower()] = m.group(2).strip()
-        idx += 1
+    msg = email.message_from_string(text)
+    headers = {k.lower(): str(v).strip() for k, v in msg.items()}
     if "to" not in headers or "subject" not in headers:
         raise ValueError("draft requires To: and Subject: headers")
-    body = "\n".join(lines[idx:]).strip()
+    body = msg.get_payload()
+    if isinstance(body, list):
+        body = "".join(str(p) for p in body)
+    body = str(body).strip()
     return headers, body
diff --git a/probes/recurrence_projection.py b/probes/recurrence_projection.py
--- a/probes/recurrence_projection.py
+++ b/probes/recurrence_projection.py
@@ -248,6 +248,7 @@
     id: str
     title: str
     rrule: Optional[str]
+    repeatFrom: Optional[int] = None
     explicit: List[Dict[str, str]] = field(default_factory=list)
     # explicit entries: {"date": "YYYY-MM-DD", "status": "open"|"completed"|"cancelled"}
 
diff --git a/tests/test_mail.py b/tests/test_mail.py
--- a/tests/test_mail.py
+++ b/tests/test_mail.py
@@ -86,7 +86,7 @@
     try:
         mail.parse_draft("not a header\n\nbody")
     except ValueError as e:
-        assert "malformed" in str(e)
+        assert "requires To: and Subject: headers" in str(e)
     else:
         raise AssertionError("expected ValueError")
```