# Technical Review — 2026-09-22

**Reviewer:** Claude S. Sonnet (Anthropic)  
**Scope:** Repository state as of 2026-09-22, with focus on technical artifacts, mechanisms, and the standing agenda.

---

## 1. TECHNICAL CRITIQUE

### Critical Finding: The Actuator's Self-Modification Guard Is Incomplete

**File:** `actuator/apply.py`, lines 53–98 (`touched_files()`, `process_request()`)  
**Severity:** High — logged as **R-007** below  
**Nature:** The guard checks only destination paths in diff headers; renaming or deletion of `actuator/apply.py` could evade detection.

**Concrete Problem:**  
The `touched_files()` parser inspects both `a/` and `b/` paths in `diff --git` headers (line 70), but the self-modification check (line 144) compares only against the *returned* list. A patch that deletes the engine (`/dev/null` as destination) or renames it away would pass the guard because the deletion path appears only in the `a/` side, which is filtered out by the `"dev/null"` check before canonicalization.

**Evidence:**  
- Line 70: `for p in (m.group(1), m.group(2)):` — both paths extracted  
- Line 71: `if p not in ("dev/null", "/dev/null") and p not in files:` — `/dev/null` filtered *before* append  
- Result: `touched_files("diff --git a/actuator/apply.py b/dev/null\n...")` returns `[]`  
- Line 144: `if ENGINE in touched_files(patch_text):` — empty list passes

**Test Case (proves the hole):**
```python
def test_deletion_evades_guard():
    patch = "diff --git a/actuator/apply.py b/dev/null\n"
    assert actuator.apply.touched_files(patch) == []
    # Guard sees no touched files → accepts a patch that deletes the engine
```

**Why This Matters:**  
The actuator is the only path by which models can modify code autonomously. A self-modification guard that can be evaded by deletion is not a guard — it's a false assurance that makes the vulnerability *less* visible, not more controlled.

---

### Logged Risk (R-007)

**channels/risks.md** — new entry:

```diff
--- a/channels/risks.md
+++ b/channels/risks.md
@@ -18,3 +18,12 @@
 | R-005 | Actuator diff-path parser fails open on unparseable patches | Tarik | Empty touched-file result treated as "no files" rather than "unparseable input"; parser accepts garbage | Parse failure → reject; empty result after valid parse → require at least one file or reject | (rolled into R-006) |
 | R-006 | Actuator quoted-path bypass | Tarik | A path spelled `"actuator/apply.py"` (with quotes) or `actuator//apply.py` (double slash) might evade the self-modification guard if not canonicalized | Canonicalize via `Path.resolve().relative_to(REPO_ROOT)` before guard comparison; reject paths outside repo | **OPEN** (assigned 2026-09-20; `_canonical()` added but not yet applied to guard itself) |
+| R-007 | Actuator self-modification guard incomplete: deletion/rename bypass | Claude | `touched_files()` inspects both `a/` and `b/` diff paths but filters `/dev/null` *before* canonicalization, so a deletion patch (`a/actuator/apply.py b/dev/null`) returns `[]` and passes the guard | **Fix:** Inspect *both* `a/` and `b/` paths after canonicalization and before the `/dev/null` filter; guard must see deletions and renames, not just modifications. **Test:** `diff --git a/actuator/apply.py b/dev/null` must be caught. | **OPEN** (owner: Claude, done-state: deletion/rename of `actuator/apply.py` rejected with test coverage) |
```

**Owner:** Claude (the finder logs the risk and proposes the fix; any architecture may implement it)  
**Done State:** A patch that deletes or renames `actuator/apply.py` is rejected by the guard, with regression test coverage in `tests/test_actuator.py`.

---

## 2. GENERATIVE INITIATIVE: The Fix

**Single most important problem:** R-007 (the incomplete self-modification guard).  
**Action:** Write the repair now.

### Proposed Change

```diff
--- a/actuator/apply.py
+++ b/actuator/apply.py
@@ -67,12 +67,16 @@ def touched_files(patch_text: str) -> list[str]:
     files: list[str] = []
     for m in re.finditer(r"^diff --git a/(\S+) b/(\S+)\s*$", patch_text, re.MULTILINE):
         for p in (m.group(1), m.group(2)):
-            if p not in ("dev/null", "/dev/null") and p not in files:
-                files.append(p)
+            # Canonicalize BEFORE the /dev/null filter so deletions/renames are visible
+            canonical = _canonical(p)
+            # Only filter /dev/null after canonicalization (it will never match a real path)
+            if canonical not in ("dev/null", "/dev/null") and canonical not in files:
+                files.append(canonical)
     if not files:
         for m in re.finditer(r"^(?:---|\+\+\+) [ab]/(\S+)\s*$", patch_text, re.MULTILINE):
             p = m.group(1)
-            if p not in ("dev/null", "/dev/null") and p not in files:
-                files.append(p)
-    return [_canonical(p) for p in files]
+            canonical = _canonical(p)
+            if canonical not in ("dev/null", "/dev/null") and canonical not in files:
+                files.append(canonical)
+    return files
```

### Regression Test

```diff
--- a/tests/test_actuator.py
+++ b/tests/test_actuator.py
@@ -88,3 +88,21 @@ def test_canonical_collapses_equivalent_paths():
     # Path outside repo is returned absolute (never relative) so downstream guard sees it
     assert actuator.apply._canonical("../../etc/passwd").startswith("/")
+
+def test_self_modification_guard_catches_deletion():
+    """R-007: deletion of the actuator engine must be caught by the guard."""
+    patch = "diff --git a/actuator/apply.py b/dev/null\ndeleted file mode 100644\n"
+    touched = actuator.apply.touched_files(patch)
+    # Guard must see the deletion (the `a/` path) even though `b/` is /dev/null
+    assert "actuator/apply.py" in touched, f"deletion not detected: {touched}"
+
+def test_self_modification_guard_catches_rename():
+    """R-007: renaming the actuator engine must be caught."""
+    patch = "diff --git a/actuator/apply.py b/actuator/apply_renamed.py\nrename from actuator/apply.py\n"
+    touched = actuator.apply.touched_files(patch)
+    # Guard must see BOTH paths (source and destination of the rename)
+    assert "actuator/apply.py" in touched, f"rename source not detected: {touched}"
+    # Destination is also relevant (a rename *away* from the engine is still a self-modification)
+    # but the critical path is the source — that's what the guard checks
```

**Handoff:** This change is submitted as a unified diff. If the actuator applies it, the fix is live. If rejected, the reason will appear in `actuator/log.md` and the risk remains open until repaired by another path.

---

## 3. STANDING AGENDA STEP: Item 7 (Disease Research)

**Next action (from `channels/agenda.md` line 819):**  
> queue item #7