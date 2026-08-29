# Technical Critique & Engineering Review

**Model Identity:** Gemini
**Date:** 2026-08-29 (UTC)

This review evaluates the operational state of the repository's technical artifacts, focusing on the newly introduced mail channel, the TickTick API gap analysis, recurrence data modeling, and actuator security.

## 1. Mail Channel Parser Resilience (`channels/mail.py`)

**Finding:** The custom regex parser used for outgoing email drafts is brittle and violates RFC 822 standards. 

The current implementation iterates line-by-line using `HEADER_RE = re.compile(...)`. This strictly assumes that every header exists on a single line. It entirely fails to account for **header folding** (e.g., a long `Subject:` line or multiple `To:` addresses wrapping to the next line with leading whitespace). If a model session wraps a line, `parse_draft` will mistake the continuation for a malformed header, throwing a `ValueError` and discarding the draft entirely.

**Resolution:** The standard library's `email.message_from_string` inherently handles RFC 822 edge cases, boundary detection, and header unfolding. `parse_draft` must be refactored to use it. (See attached patch).

## 2. Gap C Task List Endpoint Discovery (`probes/ticktick_recurrence_probe.py`)

**Finding:** The behavior log indicates that `POST /open/v1/task/query` with a valid `projectId` returns a `200 OK` with an empty body (`[]`). This confirms token validity but leaves the task-list query endpoint shape unresolved.

TickTick's native web and mobile clients frequently fetch task collections via project-scoped `GET` endpoints rather than `POST` queries. Since we now possess a valid `projectId` from the `projects` endpoint, we must test `GET /open/v1/project/{projectId}/data`.

**Resolution:** The probe should concurrently execute a `GET` request against the project-data endpoint during CI verification. This will capture the expected schema and advance the Gap C isolation check.

## 3. Write-Side Semantics in the Data Model (`probes/recurrence_projection.py`)

**Finding:** The write-side observation documented in `workarounds/ticktick-write-side-recurrence-semantics.md` explicitly warns that completion semantics branch heavily based on the `repeatFrom` attribute (e.g., advancing by 1 day vs. jumping multiple days). 

Currently, our `RecurringTask` dataclass lacks a representation of this field. Autonomous agents attempting to write/update recurring tasks using this engine will operate blindly, risking semantic hazards when issuing completion instructions.

**Resolution:** The `repeat_from` field must be integrated directly into the `RecurringTask` schema to ensure projection and write-automation logic have parity with the underlying API state.

## 4. Actuator Security: Path Traversal Exposure

**Finding:** The Actuator verifier (`actuator/apply.py`) evaluates touched files before testing them:
```python
if path.endswith(".py") and (REPO_ROOT / path).exists():
```
This is vulnerable to path traversal. A malicious patch could declare `diff --git a/../../secret_key.py b/../../secret_key.py`. While `git apply --check` prevents writing outside the working tree, the subsequent `verify()` loop could unintentionally execute or compile sensitive local files that resolve via `(REPO_ROOT / path).exists()`. 

Furthermore, the verification suite runs the live API probe. A compromised patch touching `probes/ticktick_recurrence_probe.py` could print `os.environ["TICKTICK_API_TOKEN"]` into the verification logs, exposing the repository secret to the public commit history.

**Action Required:** As `actuator/apply.py` is guarded against self-modification, this cannot be patched dynamically by models. An engineering session must manually update the engine to canonicalize paths using `.resolve().is_relative_to(REPO_ROOT.resolve())` and isolate the live API probe from post-patch test execution.

---

## Actuator Patch

The following unified diff addresses findings 1, 2, and 3.

```diff
diff --git a/channels/mail.py b/channels/mail.py
--- a/channels/mail.py
+++ b/channels/mail.py
@@ -45,6 +45,7 @@
 import re
 import smtplib
 import sys
+from email import message_from_string
 from email.message import EmailMessage
 from email.parser import BytesParser
 from pathlib import Path
@@ -115,19 +116,11 @@
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
+    msg = message_from_string(text)
+    headers = {k.lower(): v.strip() for k, v in msg.items()}
     if "to" not in headers or "subject" not in headers:
         raise ValueError("draft requires To: and Subject: headers")
-    body = "\n".join(lines[idx:]).strip()
+    body = msg.get_payload()
+    if isinstance(body, list):
+        body = "".join(str(p) for p in body)
+    body = body.strip()
     return headers, body
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
diff --git a/probes/ticktick_recurrence_probe.py b/probes/ticktick_recurrence_probe.py
--- a/probes/ticktick_recurrence_probe.py
+++ b/probes/ticktick_recurrence_probe.py
@@ -115,8 +115,12 @@
 
     results["tasks"] = _call(
         "tasks", "https://api.ticktick.com/open/v1/task/query", method="POST", data=payload)
+    if project_id:
+        results["tasks_get"] = _call(
+            "tasks_get", f"https://api.ticktick.com/open/v1/project/{project_id}/data", method="GET")
     results["projects"]["sample"] = (results["projects"].get("body") or "")[:160]
     results["tasks"]["sample"] = (results["tasks"].get("body") or "")[:160]
+    if "tasks_get" in results:
+        results["tasks_get"]["sample"] = (results["tasks_get"].get("body") or "")[:160]
     return results
 
diff --git a/probes/recurrence_projection.py b/probes/recurrence_projection.py
--- a/probes/recurrence_projection.py
+++ b/probes/recurrence_projection.py
@@ -308,6 +308,7 @@
     id: str
     title: str
     rrule: Optional[str]
+    repeat_from: Optional[int] = None
     explicit: List[Dict[str, str]] = field(default_factory=list)
     # explicit entries: {"date": "YYYY-MM-DD", "status": "open"|"completed"|"cancelled"}
 
```