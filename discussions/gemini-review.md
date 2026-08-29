# Technical Critique: Artifact Operational State

**Model Identity:** Gemini  
**Date:** 2026-08-29 (UTC)

This critique focuses exclusively on the operational state of the code and technical artifacts. It identifies several critical flaws in the newly introduced mail channel, blind spots in the actuator's verification loop, structural deficiencies in the task data model, and unresolved API probing routes.

## 1. Actuator Verification Suite Blind Spots
**Severity:** Critical
**File:** `actuator/apply.py`

The `VERIFY_SUITE` within `apply.py` is hardcoded to run only `tests/test_projection.py` and `probes/ticktick_recurrence_probe.py`. 
With the addition of the direct mail channel, the actuator now operates completely blind to regressions in `channels/mail.py`. Any broken patch targeting the mail channel will pass verification and deploy, provided it survives a basic `py_compile` check. 

Because `apply.py` enforces a self-modification guard, models cannot patch the verification suite directly. An engineering session must manually update `VERIFY_SUITE` to include `tests/test_mail.py` and `tests/test_actuator.py`.

## 2. Mail Parser Brittleness & RFC 822 Violations
**Severity:** High
**File:** `channels/mail.py`

The `parse_draft` function processes email headers using a strict line-by-line regex (`splitlines()` and `HEADER_RE.match`). This inherently violates RFC 822 conventions for **header folding**. If a downstream system or model generates a long `Subject:` or `To:` header that wraps to a newline with leading whitespace, `parse_draft` throws a `ValueError` and discards the message entirely.

Python's standard library `email.message_from_string` natively handles all edge cases, header unfolding, and payload separation.

## 3. TickTick API Probing (Gap C) Endpoint Extrapolation
**Severity:** Medium
**File:** `probes/ticktick_recurrence_probe.py`

The live API probe correctly confirms token validity using `GET /open/v1/project` and retrieves a valid `projectId`. However, it relies on `POST /open/v1/task/query` to discover task list semantics, which currently yields an empty body. 

Common TickTick REST client implementations frequently pull collection states via project-scoped GET endpoints. Since the probe possesses the `projectId`, it should explicitly test `GET /open/v1/project/{projectId}/data`.

## 4. Write-Side Semantics Excluded from Data Model
**Severity:** Medium
**File:** `probes/recurrence_projection.py`

The artifact `workarounds/ticktick-write-side-recurrence-semantics.md` empirically documents that completion behavior diverges wildly based on the `repeatFrom` field (advancing by one day vs. jumping multiple days). 

Currently, the `RecurringTask` dataclass omits this property entirely. Any agent built on this projection engine to automate write-side interactions will operate blindly. `repeatFrom` must be added to the dataclass to support future write automation.

## 5. The UTC Fallacy in `parse_date`
**Severity:** High
**File:** `probes/recurrence_projection.py`

`parse_date()` contains a structural flaw when parsing offset-aware ISO timestamps:
```python
if dt.tzinfo is not None:
    dt = dt.astimezone(timezone.utc)
return dt.date()
```
Converting to UTC before extracting the calendar date shifts local evening tasks (e.g., `2026-08-25T23:00:00-08:00`) to the next calendar day (`2026-08-26`). TickTick recurrence explicitly anchors to local calendar dates. This function should preserve the nominal date or rely strictly on `parse_date_tz`. (I have deferred patching this file's logic directly to avoid breaking downstream tests, but it requires a dedicated engineering refactor).

---

## Technical Corrections Patch

The following unified diff addresses the RFC 822 mail parser flaw, the API endpoint discovery gap, and the missing data model field.

```diff
diff --git a/channels/mail.py b/channels/mail.py
--- a/channels/mail.py
+++ b/channels/mail.py
@@ -107,17 +107,12 @@
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
+    from email import message_from_string
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
@@ -58,7 +58,7 @@
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
@@ -108,6 +108,9 @@
     payload = json.dumps({"projectId": project_id}).encode() if project_id else b"{}"
 
     results["tasks"] = _call(
         "tasks", "https://api.ticktick.com/open/v1/task/query", method="POST", data=payload)
+    if project_id:
+        results["project_data"] = _call(
+            "project_data", f"https://api.ticktick.com/open/v1/project/{project_id}/data", method="GET")
     results["projects"]["sample"] = (results["projects"].get("body") or "")[:160]
     results["tasks"]["sample"] = (results["tasks"].get("body") or "")[:160]
+    if "project_data" in results:
+        results["project_data"]["sample"] = (results["project_data"].get("body") or "")[:160]
     return results
diff --git a/probes/recurrence_projection.py b/probes/recurrence_projection.py
--- a/probes/recurrence_projection.py
+++ b/probes/recurrence_projection.py
@@ -311,6 +311,7 @@
     id: str
     title: str
     rrule: Optional[str]
+    repeatFrom: Optional[int] = None
     explicit: List[Dict[str, str]] = field(default_factory=list)
     # explicit entries: {"date": "YYYY-MM-DD", "status": "open"|"completed"|"cancelled"}
 
```