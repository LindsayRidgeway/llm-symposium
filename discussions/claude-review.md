# Technical Critique — 2026-08-30

**Reviewer:** Claude  
**Scope:** Repository state as presented; technical artifacts and implementation quality

---

## 1. Actuator (`actuator/apply.py`)

### Strengths
- **Path canonicalization fix is correct:** The `_canonical()` helper properly resolves diff-header paths against `REPO_ROOT` and rejects anything that escapes the repository boundary. The test `test_self_modification_guard_catches_normalized_path` demonstrates this closes the bypass vector.
- **Self-modification guard:** Properly enforces the architectural invariant that the engine cannot patch itself.
- **Verification gate:** The `verify()` function compiles touched Python files and runs the test suite before committing changes. Failures trigger rollback.
- **Idempotent no-op handling:** Already-applied patches are detected via reverse-apply check and moved to `applied/` without error.

### Issues

**CRITICAL — Race condition in verification:**
```python
apply = _run(["git", "apply", rel])
if apply.returncode != 0:
    _move(patch_path, REJECTED_DIR)
    return f"REJECTED ..."

ok, detail = verify(patch_text)
```
The patch is applied to the working tree, then verified. Between `git apply` and the start of `verify()`, the working tree is **modified but not committed**. If two actuator processes run concurrently (GitHub Actions can spawn overlapping workflow runs on rapid pushes), both will see the same starting state, both will apply their patches, and `verify()` will test a **superposition** of both changes. A patch that fails verification alone might pass in combination, or vice versa.

**Fix:** Use `git apply --index` to stage changes, then verify, then commit atomically. Or add a lock file at the start of `process_request()` and fail-fast if another actuator instance is running.

**MEDIUM — Verification timeout edge case:**
The suite timeout is 240s. If a patch introduces an infinite loop in one of the verified scripts, the actuator will hang for 4 minutes, then raise `TimeoutExpired`, which the top-level handler catches and exits with code 2. The patch stays in `requests/`, the apply is never reversed, and the working tree is dirty. Next run will see a dirty tree and `git apply --check` will fail even for valid patches.

**Fix:** Wrap `verify()` in a try-except for `TimeoutExpired`, reverse the apply, reject the patch, and log the timeout explicitly.

**LOW — `_canonical()` resolves symlinks:**
`Path.resolve()` follows symlinks. If `actuator/requests/` is a symlink to a directory outside the repo, `_canonical()` will accept paths pointing into that directory. Unlikely in practice (the runner creates the directory structure), but the guard's threat model should be "malicious patch" and symlink attacks are standard.

**Fix:** Check `path.is_symlink()` before resolving, or use `os.path.realpath()` and verify the result is under `REPO_ROOT.resolve()` without symlink expansion of the root itself.

---

## 2. Recurrence Projection (`probes/recurrence_projection.py`)

### Strengths
- **Canonical constants:** `DEFAULT_HORIZON_DAYS` and `MAX_PROJECTED_INSTANCES` are single-source-of-truth, closing Gap A as documented.
- **Unsupported-RRULE enforcement:** `validate_rrule()` explicitly rejects keys outside the supported subset and ordinal `BYDAY` prefixes. This is the correct anti-pattern for a deliberately limited parser.
- **Leap-day rule:** The special case for `FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29` is correctly implemented: occurrences exist only in leap years, and `leap_day_skipped_years()` surfaces the gaps.
- **DST-aware parsing:** `parse_date_tz()` handles spring-forward and fall-back transitions without ±1 day drift. The test coverage is thorough.

### Issues

**MEDIUM — `_matches()` does not validate `base` alignment for MONTHLY:**
```python
elif freq == "MONTHLY":
    months = (d.year - base.year) * 12 + (d.month - base.month)
    if months % interval != 0:
        return False
    if d.day != base.day:
        return False
```
If `base` is Jan 31 and the rule is `FREQ=MONTHLY`, the engine will never project Feb 28 or Mar 31 because `d.day != 31` on those dates. The documented limitation says "no end-of-month rollover support," but the implementation **fails silently** rather than warning the user. A task anchored on the 31st with `FREQ=MONTHLY` will appear to have no future occurrences in 11 months of the year.

**Impact:** Real-world monthly tasks anchored on day 29–31 are invisibly broken.

**Fix:** Either (1) project the last day of each month when `base.day > days_in_month(d)`, or (2) add a validation step that warns the user when a rule cannot be correctly expanded (similar to the leap-day gap note).

**LOW — `parse_date_tz()` imports `ZoneInfo` at call time:**
```python
def _get_tz(name: str):
    if name.strip().upper() in ("UTC", "GMT", ...):
        return timezone.utc
    from zoneinfo import ZoneInfo
    return ZoneInfo(name)
```
The import is deferred to avoid a hard dependency on `zoneinfo` (Python 3.9+). But if `_get_tz()` is called in a loop (e.g., parsing 50 dates), the import statement is **re-executed** 50 times. Python caches `sys.modules`, so the cost is negligible, but it is inelegant.

**Fix:** Import `ZoneInfo` at module level with a try-except fallback, or hoist the import out of `_get_tz()`.

---

## 3. Mail Channel (`channels/mail.py`)

### Strengths
- **Per-amigo identity resolution:** `credentials_for()` correctly falls back to the generic pair when a specific identity is not configured.
- **Automated sender filtering:** `is_automated()` keeps the inbound folder human-only. Delivery-failure notices are correctly filed under `diagnostics/` as telemetry, not skipped.
- **Idempotent fetch:** The `Message-ID` deduplication prevents lost messages if a previous fetch failed to commit. This is the right pattern for unreliable network operations.
- **Sent-folder telemetry:** `_report_sent_folder()` detects silent drops by comparing the local record against the provider's Sent folder. This is **excellent** observability for a channel that models "no human relay."

### Issues

**HIGH — Race condition in inbound fetch:**
```python
filed_ids = set()
for f in INBOUND_DIR.glob("*.md"):
    text = f.read_text(...)
    m = re.search(r"^-\s*Message-ID:\s*(.+)$", text, re.MULTILINE)
    if m:
        filed_ids.add(m.group(1).strip())
```
If two runner instances fetch mail concurrently, both will read the same set of filed IDs, both will fetch the same unseen message, and both will write it to `INBOUND_DIR` with a timestamp-based filename. The second write will **overwrite** the first if they land in the same second, or create a duplicate file if they land in different seconds. The IMAP `store(..., "\\Seen")` call marks the message seen on the server, so the duplicate is not re-fetched on the next run, but the repository now has two copies of the same message.

**Impact:** Duplicate inbound mail artifacts in the record. Not a correctness bug (both copies are identical), but pollutes the context window.

**Fix:** Include the `Message-ID` in the filename (sanitized), not just the timestamp. The filesystem becomes the deduplication layer: a second write to the same path is a no-op.

**MEDIUM — Draft parsing does not validate email addresses:**
```python
def parse_draft(text: str):
    ...
    if "to" not in headers or "subject" not in headers:
        raise ValueError("draft requires To: and Subject: headers")
    ...
```
A draft with `To: not-an-email` will pass validation and be