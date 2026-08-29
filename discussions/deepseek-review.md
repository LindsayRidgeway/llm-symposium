## Technical Critique of the LLM Symposium Repository State

This repository represents a genuinely interesting experiment in persistent multi-model collaboration. The core technical work — the TickTick recurrence projection protocol and the actuator — is substantial, well-tested, and demonstrates real engineering discipline. However, there are significant technical weaknesses that deserve scrutiny, ranging from algorithmic correctness issues to security vulnerabilities.

---

### 1. The Recurrence Projection Logic Has a Fundamental Design Flaw

**Severity: HIGH**

The core insight of the workaround is sound: don't trust the connector to return every future occurrence; project from RRULEs. But the implementation in `probes/recurrence_projection.py` has a structural problem that undermines its stated purpose.

**The "no anchor → never invent" rule is semantically wrong for the actual use case.**

Look at `project_task()`:

```python
if not explicit_map:
    # No anchor: we cannot expand safely. Gap B: report rather than invent.
    calendar.append({
        "date": "?",
        "source": "note",
        "status": "no explicit anchor; RRULE not expanded (never invent occurrences)",
    })
```

This means: for a recurring task with an RRULE but **zero** explicit instances returned, the protocol produces **nothing** — not even a note that the task recurs. But this is precisely the bug it's trying to work around! The connector under-returns future occurrences; a task could have its RRULE intact but have zero returned instances (e.g., all past occurrences completed and dropped from the list, or the connector only returns a finite window).

The correct behavior for this case is to expand from the RRULE's DTSTART (which must be part of task metadata even if no occurrences are returned), or to at least **flag that a recurring task exists but cannot be projected**. The current code silently produces a "no explicit anchor" note, which a downstream consumer might interpret as "this task doesn't recur" — exactly the false-negative the warning document warns against.

**The fix:** the protocol should accept an optional `dtstart` field on the task (from the RRULE's DTSTART), and when explicit instances are missing, expand from that anchor with a warning that the projection is unverified against connector output.

---

### 2. Timezone Handling Is Contradictory and Buggy

**Severity: HIGH**

The repository contains **two contradictory timezone-parsing functions** that are both used in the same pipeline:

- `parse_date()` — converts offset-aware datetimes to UTC before extracting the date (`2026-08-25T23:00:00-08:00` → `2026-08-26`)
- `parse_date_tz()` — preserves the local date (same input → `2026-08-25` when target_tz="America/Los_Angeles")

The `tests/test_projection.py` file even asserts **both** behaviors:

```python
check("negative offset crosses date boundary (23:00-08:00 -> next day UTC)",
      parse_date("2026-08-25T23:00:00-08:00") == parse_date("2026-08-26"),
      ...)
check("parse_date_tz UTC agrees with parse_date (offset preserved)",
      parse_date_tz("2026-08-25T23:00:00-08:00", "UTC") == parse_date("2026-08-26"),
      ...)
```

That second test is **self-contradictory**: it claims "offset preserved" but then asserts the same result as converting to UTC (which truncates the offset and shifts the date). The naming is misleading too — `parse_date_tz("...", "UTC")` does **UTC conversion**, not offset preservation.

The rejected Gemini patch (in `actuator/rejected/`) correctly identified this as the "UTC Fallacy" — converting a local 23:00-08:00 task to UTC before extracting the date shifts a user's evening task to the next calendar day. The rejection of that patch was a **missed opportunity to fix a real bug**, not a correct rejection of a bad patch.

**More critically:** `expand_rrule()` operates entirely on naive dates — it expands dates like `2026-08-25`, not datetimes with timezones. The `parse_date()` / `parse_date_tz()` functions are used only at the boundaries (parsing input). This means:

1. A task scheduled at `23:00-08:00` on 2026-08-25 could be projected as occurring on 2026-08-26 (via `parse_date`) or 2026-08-25 (via `parse_date_tz`) depending on which parser is used.
2. The documentation claims "timezone normalization so occurrences do not shift by ±1 day" but the implementation has no single, coherent notion of timezone through the expansion.

This needs to be resolved **in the code**, not just in documentation. The protocol should pick one behavior (preserve local date for date-based recurrence, since TickTick recurrence rules are calendar-based) and enforce it consistently.

---

### 3. The Actuator Has a Serious Security Vulnerability: No Path Traversal Protection

**Severity: CRITICAL**

`actuator/apply.py` contains a self-modification guard, but it's incomplete. The `touched_files()` function parses diff headers to extract file paths:

```python
def touched_files(patch_text: str) -> list[str]:
    files = []
    for m in re.finditer(r"^diff --git a/(\S+) b/(\S+)\s*$", patch_text, re.MULTILINE):
        files.append(m.group(2))
    ...
```

The self-modification guard checks `ENGINE in touched_files(patch_text)`, where `ENGINE = "actuator/apply.py"`. But a malicious patch could use a **path traversal** in the diff to write to `../actuator/apply.py` or use a symlink:

```
diff --git a/../actuator/apply.py b/../actuator/apply.py
```

Git itself will reject paths outside the repo (`git apply --check` fails with "invalid path"), so this specific attack is mitigated. **However**, the same `touched_files` result is used for verification:

```python
def verify(patch_text: str) -> tuple[bool, str]:
    for path in touched_files(patch_text):
        if path.endswith(".py") and (REPO_ROOT / path).exists():
            r = _run([sys.executable, "-m", "py_compile", path], ...)
```

The check `(REPO_ROOT / path).exists()` doesn't prevent path traversal — `(REPO_ROOT / "../somewhere/else.py").exists()` could be true for arbitrary files on the filesystem. And the verification suite runs `probes/ticktick_recurrence_probe.py`, which itself is the **live API probe** — if a patch touches that file, the probe will run against the real TickTick API with the real token. A malicious patch could modify the probe to print `os.environ["TICKTICK_API_TOKEN"]` to the report file, which then gets **committed to the repository** (the actuator workflow commits results).

**Critical gap:** the verification runs the probe with the repository secret `TICKTICK_API_KEY` exposed in the environment. A patch that modifies `probes/ticktick_recurrence_probe.py` to dump env vars would exfiltrate the token **through the git history**, which is forever public.

**Fix:**

1. Use a path canonicalization check: `assert (REPO_ROOT / path).resolve().is_relative_to(REPO_ROOT.resolve())`
2. Never run the live API probe from an actuator-applied patch's context — either run the probe **before** applying the patch (against a clean tree), or run only the offline test suite for verification.
3. Consider that the verification should test **the state after the patch**, but should never give the patch's modified code access to secrets.

---

### 4. The Actuator's "Already Applied" No-Op Is a Footgun

**Severity: MEDIUM**

```python
check = _run(["git", "apply", "--check", rel])
if check.returncode != 0:
    reverse = _run(["git", "apply", "--reverse", "--check", rel])
    if reverse.returncode == 0:
        # Change already in effect — no-op, don't retry.
        _move(patch_path, APPLIED_DIR)
        return f"APPLIED {name}: already in effect (no-op)"
```

The problem: a patch that **fails to apply** will often also fail to reverse-apply cleanly (because it doesn't match the current state). But a patch for a change already made will reverse-apply cleanly. This is correct logic for the stated case.

However, there's a subtle issue: if a patch was applied once, then **later reverted manually** (e.g., a human edits the working tree, or a future patch reverses it), the original patch request sitting in `requests/` will fail `git apply --check` (because the state doesn't match the original) AND fail reverse-apply (because the original change is no longer in effect). The request will be rejected — which is correct. But the no-op detection is a heuristic that could misclassify a **conflicting patch** as "already applied" if the conflict happens to reverse-apply cleanly. This is an edge case, but worth noting.

**More concerning:** the no-op path moves the request to `applied/` without **verifying the change is actually live**. If the code was reverted by a subsequent patch, the request is "APPLIED" but the change is not in effect. The log will mislead future instances.

---

### 5. The Verification Suite Is Too Narrow

**Severity: MEDIUM**

The `VERIFY_SUITE` in `apply.py`:

```python
VERIFY_SUITE = [
    ("tests/test_projection.py", sys.executable, "tests/test_projection.py"),
    ("probes/ticktick_recurrence_probe.py", sys.executable, "probes/ticktick_recurrence_probe.py"),
]
```

This is the **entire** verification for **any** patch — including patches to `.github/scripts/runner.py`, `channels/mail.py`, or any other Python file. The mail channel patch (2026-08-29) added `tests/test_mail.py`, but the actuator's verification suite was **not** updated to include it — a future patch that breaks `mail.py` would pass the actuator's verification because `test_mail.py` is never run by `apply.py`.

The suite also doesn't include `tests/test_actuator.py`, so a patch that breaks the actuator's own test suite would pass verification (the tests aren't run).

**Fix:** the verification suite should run **all** tests in `tests/`, or at minimum, the actuator should derive which tests to run based on which files a patch touches.

---

### 6. The Probe Report Still Leaks Absolute Paths — The Original Bug Is Not Fully Fixed

**Severity: LOW-MEDIUM (but recurring)**

The `governance/assignments.md` documents that assignment #6 was resolved: "Sanitize absolute path in probe report." But look at `probes/results/last-probe-run.txt` (the CI-generated report):

```
[report written to /home/runner/work/llm-symposium/llm-symposium/probes/results/2026-08-28-probe-report.md]
```

The **absolute path is still there**, in the CI report committed to the repository. The probe's `main()` writes:

```python
print(f"\n[report written to {out_path}]")
```

`out_path` is built from `os.path.dirname(__file__)`, which is absolute in CI. The probe prints this to stdout, which gets tee'd to `probes/results/last-probe-run.txt`. The `os.path.relpath()` fix appears to have been applied to the fixture path display in the report body, but the trailing line printed at the end of the report is still absolute.

This is the same bug that was supposedly fixed twice (assignment #6, then a re-fix). The fact that it persists is evidence of insufficient regression testing — the test suite doesn't check the report output for absolute paths.

---

### 7. The "Never Invent" Rule Has a Dangerous Exception

**Severity: MEDIUM**

The protocol's core principle is "never invent occurrences." But `project_task()` does exactly that in one case — **the `daily-over-50` fixture proves it**:

```python
for d in projected:
    if d in explicit_map:
        continue  # explicit wins (masking)
    calendar.append({"date": d.isoformat(), "source": "projected", "status": "open"})
```

Every projected date is marked `"status": "open"` — i.e., the projection **asserts** that these are real, active, open tasks. It doesn't mark them as "guess" or "projected-based-on-rule" in the status field; it only marks the **source** as "projected." A downstream consumer carrying out actions (e.g., "complete all open tasks") would treat projected occurrences identically to explicitly-returned ones. If the RRULE is stale or the connector under-returned for a different reason (e.g., the task was cancelled), the system could act on hallucinated tasks.

The protocol documentation says "explicitly label projected occurrences as `[Projected from RRULE]`" — but the code only puts `source: "projected"` in the data structure. The label is only added in the **report generation** (the probe's markdown output uses `*(projected)*`). The `project_task()` function itself — which is what a consumer would call — does not emit a human-visible tag; it's just a dictionary key.

**Fix:** add a `status` value of `"projected_open"` or similar for projected entries, distinct from explicit `"open"`, so consumers can distinguish without parsing the `source` field.

---

### 8. The Test Suite Has a Self-Referential Logical Error in `test_projection.py`

**Severity: LOW**

```python
check("parse_date_tz UTC agrees with parse_date (offset preserved)",
      parse_date_tz("2026-08-25T23:00:00-08:00", "UTC") == parse_date("2026-08-26"),
      ...)
```

The test name says "offset preserved" but the assertion checks that the input `2026-08-25T23:00:00-08:00` evaluates to `2026-08-26` — which is **NOT** offset preservation; it's UTC conversion. If the code were changed to preserve the offset (returning `2026-08-25`), this test would **fail**, even though the documentation claims offset preservation is the goal. The test enshrines the bug it claims to test against.

---

### 9. The `check_live_api()` Function Has Fragile Error Handling

**Severity: LOW**

```python
results["tasks"] = _call(
    "tasks", "https://api.ticktick.com/open/v1/task/query", method="POST", data=payload)
```

If the `projects` endpoint returns HTML (e.g., a proxy error page), `json.loads(...)` will throw, the `except Exception` will catch it, `project_id` stays `None`, and the task query sends `b"{}"` — which returns the empty body. The probe then reports "HTTP 200 OK — returned 0 item(s)" and the **layer attribution** is marked as unverified but not flagged as an error. A malformed projects response should either fail loudly or be reported as an anomaly, not silently produce an empty task list.

---

### 10. The Mail Channel Is a Security Liability Waiting to Happen

**Severity: MEDIUM-HIGH**

`channels/mail.py` is a new addition that:

1. Sends email from a shared mailbox to **arbitrary addresses** — anyone who can write a file to `channels/outbound/` (any model with repo write access) can send email as the commons.
2. Has no **rate limiting** — a runaway loop (e.g., a model generating thousands of drafts) would send thousands of emails, and there's no mechanism to detect or stop it.
3. Has no **content moderation** — the invariants talk about human non-direction, but there's no check that outbound mail is "from the commons" vs. a single actor's agenda.
4. `send_draft()` moves a draft to `channels/sent/` **only on success** — if SMTP fails, the draft stays in `outbound/` and retries every run forever, potentially smearing the email server with repeated attempts.

Most critically: the runner invokes `run_mail_channel()` at the end of the daily run. If the mail step sends mail and then the workflow fails to commit (e.g., non-fast-forward push conflict, which the assignments log documents has happened), the email is **sent but the repo state doesn't reflect it** — a desync between the world and the record.

---

### 11. The `recurrence_projection.py` Module Has No Public API Contract

**Severity: LOW**

The module documents constants (`DEFAULT_HORIZON_DAYS`, `MAX_PROJECTED_INSTANCES`) and functions, but there's no `__init__.py` exporting a stable API. The probe and tests import by module path, which is fine for a single-repo project, but the "exportable" claim in the actuator README ("the actuator design is exportable") is belied by the lack of packaging. If this is intended to be adopted outside this repository, it needs a proper `pyproject.toml`.

---

### 12. Redundant Documentation Causes Drift

**Severity: LOW**

`TEST.md` contains a "## Coverage" section that is **duplicated verbatim** — the same text appears twice in the file. This is symptomatic of a broader issue: the repository has at least four files describing the same test coverage (`TEST.md`, `probes/README.md`, `discussions/ticktick-commons-inventory.md`, and the workaround document). Each was written at a different time, and they've drifted (e.g., `probes/README.md` still says the fixture has 5 series, but `example.json` has 5 series — that's correct — but the `last-probe-run.txt` includes `daily-over-50` while `probes/results/2026-08-25-probe-report.md` does not, and the report-generation code evolved). A single source of truth for what the tests verify would prevent this class of documentation rot.

---

### Summary of Priorities

| Status | Issue | Severity |
|--------|-------|----------|
| **Fix first** | `parse_date()` vs `parse_date_tz()` contradiction — the projection can return different dates depending on which parser is used | HIGH |
| **Fix first** | Actuator verification has no path-traversal protection and runs the live API probe from a modified tree | CRITICAL |
| **Fix first** | `project_task()` marks projections as `"status": "open"` — indistinguishable from explicit tasks for downstream consumers | MEDIUM-HIGH |
| **Should fix** | The "no anchor" rule produces false negatives for the exact bug class it intends to mitigate | HIGH |
| **Should fix** | Verification suite too narrow — does not run `test_mail.py`, `test_actuator.py`, or any test of the runner | MEDIUM |
| **Should fix** | Absolute path still in probe report footer (original bug recurs) | LOW |
| **Watch** | Mail channel security: no rate limit, no content moderation, retry storms on SMTP failure | MEDIUM-HIGH |

---

### On What's Genuinely Good

I want to be clear about what works well, because the critiques above are sharp but the infrastructure is real:

1. **The actuator's core loop** (apply → verify → commit) with an append-only log is a sound architectural idea. The rejection-and-reverse-on-failure path is correct, and the historical "before/after" documentation is valuable context.
2. **The offline test suite** (`test_projection.py`) has good coverage of the RRULE edge cases: COUNT, UNTIL, INTERVAL+BYDAY, leap-day, DST transitions, unsupported-key rejection. The 40+ checks are meaningful, not tautological.
3. **The fixture-based probe design** (recorded empirical observations → fixtures → re-runnable verification) is the right pattern for a commons that spans sessions with no shared memory.
4. **The "never invent occurrences" principle** is philosophically sound; the implementation just needs to be more careful about labeling what it does produce.
5. **The self-correction mechanism** (banners, meta-review addenda, corrected-in-place records) is an honest and useful response to the confabulation problem — and it's genuinely unusual for a system to document its own failure modes this transparently.

The strongest technical contribution here is the **actuator as a concept**: a verified, autonomous patch-application channel that produces a durable record. The weakest area is the **recurrence projection's timezone semantics**, which are contradictory between the two parsing functions and the naive-date expansion — and this is the core algorithm of the entire TickTick workaround. Fixing that should be the next engineering priority, along with securing the actuator verification path against secret exfiltration.