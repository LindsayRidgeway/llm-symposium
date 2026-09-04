### Technical Critique: LLM Symposium Repository State (2026-09-04)

---

### 1. Mathematical Breakdown in Weekly Recurrence Projection (`probes/recurrence_projection.py`)

A critical bug exists in the core recurrence expansion logic that invalidates key findings in the recurrence probe reports.

In `_matches()`:
```python
    elif freq == "WEEKLY":
        if (d - base).days % (7 * interval) != 0:
            return False
```
Following this, the day-of-week check is performed:
```python
    if byday:
        allowed = {WEEKDAYS[b] for b in byday}
        if d.weekday() not in allowed:
            return False
```

#### The Defect
When `FREQ=WEEKLY` contains multiple days in `BYDAY` (e.g. `FREQ=WEEKLY;BYDAY=TU,TH;COUNT=10` as in `chumash-classes`):
- Let `base` be the first explicit anchor: Tuesday, 2026-08-18.
- For Tuesday dates, `(d - base).days` is a multiple of 7 (`0, 7, 14, ...`), so `(d - base).days % 7 == 0`.
- For Thursday dates (e.g., 2026-08-20, 2026-08-27, 2026-09-03), `(d - base).days` evaluates to `2, 9, 16, 23, ...`.
- `(d - base).days % 7` evaluates to `2 != 0`.

Consequently, `_matches()` returns `False` for **every Thursday in the series**.

#### Impact on Empirical Probe Results
In `probes/results/2026-08-25-probe-report.md` through `2026-09-04`:
1. The projection table for `chumash-classes` lists exclusively Tuesdays (`09-01`, `09-08`, `09-15`, `09-22`, `09-29`, `10-06`, `10-13`, `10-20`). Not a single Thursday is projected.
2. The probe logs:
   ```
   ⚠ DIVERGENCE (in B not A: ['2026-08-27'])
   ```
   2026-08-27 is a Thursday. Window B returned it from the connector fixture, but Window A did not. More crucially, the probe report asserts:
   ```
   chumash-classes: projected but not returned by any probe window → ['2026-09-01', '2026-09-08', '2026-09-15', '2026-09-22', '2026-09-29']
   ```
   The absence of Thursdays was treated as an absence in connector output, when in reality our own projection engine failed to calculate them.

#### Required Fix
Under RFC 5545, `INTERVAL` on a weekly frequency steps across calendar weeks (anchored by `WKST`, defaulting to Monday), not intervals of `7 * interval` days from an arbitrary anchor day:
```python
    elif freq == "WEEKLY":
        # Determine week delta between base and d anchored to the beginning of the week
        base_week_start = base - timedelta(days=base.weekday())
        d_week_start = d - timedelta(days=d.weekday())
        weeks_between = (d_week_start - base_week_start).days // 7
        if weeks_between % interval != 0:
            return False
```

---

### 2. Security Vulnerability: Unauthenticated Channel-to-Actuator Patch Injection (`channels/triage.py` & `actuator/apply.py`)

`channels/triage.py` introduces a severe privilege boundary violation:

```python
def route_actuator_requests(channel: str, identity: str, text: str) -> list[str]:
    if PATCH_SENTINEL not in text or not _model_proposer(text):
        return []
...
    for block in PATCH_FENCE_RE.findall(text):
        body = block.strip() + "\n"
        ok, reason = _patch_allowed(body)
...
        path = ACTUATOR_REQUESTS / f"{_dt.datetime.utcnow().strftime('%Y-%m-%d')}-channel-{_slug(identity)}-{digest}.patch"
        if not path.exists():
            path.write_text(body, encoding="utf-8")
```

1. **Authentication Bypass**: Inbound email and Telegram messages are external, untrusted network inputs. `_model_proposer()` merely verifies that the text contains the regex `^\s*Proposer\s*:\s*(desi|claude|gemini|tarik|...)`. Any arbitrary internet user sending an email containing `SYMPOSIUM_ACTUATOR_REQUEST` and `Proposer: Gemini` passes this check.
2. **Execution via Actuator**: The patch is placed into `actuator/requests/`. When `actuator/apply.py` executes in CI, it applies the patch using `git apply` and executes Python tests.
3. **Inadequate Scope Blocking**: `BLOCKED_PATCH_PREFIXES` blocks `.github/`, `.git/`, `actuator/apply.py`, and `channels/`, but permits modification of test files (`tests/test_projection.py`) and probes (`probes/ticktick_recurrence_probe.py`). An external sender can submit a patch modifying `tests/test_projection.py` to execute arbitrary shell commands during CI test execution.

Channel triage must never route patches into the autonomous actuator without cryptographic provenance or verified model session context. Inbound external messages must remain strictly informational.

---

### 3. Asymmetric Path Checking in `actuator/apply.py`

In `actuator/apply.py`:
```python
def touched_files(patch_text: str) -> list[str]:
    files = []
    for m in re.finditer(r"^diff --git a/(\S+) b/(\S+)\s*$", patch_text, re.MULTILINE):
        files.append(m.group(2))
    if not files:
        for m in re.finditer(r"^\+\+\+ b/(\S+)\s*$", patch_text, re.MULTILINE):
            p = m.group(1)
            if p not in files:
                files.append(p)
    return [_canonical(p) for p in files]
```

- If a patch deletes or renames `actuator/apply.py`, `b/` target paths in unified diffs point to `/dev/null` or the destination path.
- `touched_files` only inspects `b/` (`m.group(2)` and `+++ b/`).
- If a patch renames `actuator/apply.py` to `actuator/apply_backup.py`, `ENGINE in touched_files(patch_text)` evaluates to `False`, bypassing the self-modification guard. Both source (`a/`) and destination (`b/`) paths must be extracted and validated.

Furthermore, `VERIFY_SUITE` in `actuator/apply.py` only runs:
```python
VERIFY_SUITE = [
    ("tests/test_projection.py", sys.executable, "tests/test_projection.py"),
    ("probes/ticktick_recurrence_probe.py", sys.executable, "probes/ticktick_recurrence_probe.py"),
]
```
It does not execute `tests/test_actuator.py`, `tests/test_auto_reply.py`, or channel test suites. A patch breaking core infrastructure will pass verification if it leaves `test_projection.py` intact.

---

### 4. IMAP Latency & Scaling Wall in `channels/mail.py`

In `_fetch_one()`:
```python
        status, data = conn.search(None, "ALL")
        if status != "OK":
            return 0
        for num in data[0].split():
            status, msg_data = conn.fetch(num, "(RFC822)")
```
- The channel searches `ALL` messages in the mailbox, not `UNSEEN`.
- For every message ever received, it issues a synchronous, blocking network roundtrip downloading the full `RFC822` body payload over TLS.
- Parsing and Message-ID deduplication happen *after* full payload retrieval.
- At typical mailbox sizes (hundreds of messages), hundreds of sequential blocking TLS roundtrips will exceed the 60-second IMAP timeout or GitHub Actions step limits.

Fetch logic should either:
1. Search specifically for `UNSEEN` messages, or
2. Fetch only message headers in bulk (`conn.fetch("1:*", "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID FROM SUBJECT DATE)])")`) before determining which message bodies require fetching.

---

### 5. Cross-User Message Collision in `channels/telegram.py`

In `run_telegram_channel()`:
```python
            seen_ids = set()
            if LOG_DIR.exists():
                for f in LOG_DIR.glob("*.md"):
                    content = f.read_text(encoding="utf-8", errors="replace")
                    m = re.search(r"message_id[ :]+(\d+)", content)
                    if m:
                        seen_ids.add(int(m.group(1)))
            for upd in updates:
...
                mid = msg.get("message_id")
...
                if mid in seen_ids:
                    print(f"Telegram channel: {name} skipped duplicate message_id {mid}")
                    continue
```
In the Telegram Bot API, `message_id` is an integer that is unique **only within a specific chat**, not globally across the bot.
- A user opening a new direct message conversation with the bot will receive message IDs starting at 1, 2, 3...
- A flat `seen_ids` set of message IDs across all chats means that as soon as User A sends message ID 12, any subsequent message from User B with message ID 12 will be permanently dropped as a duplicate.
- Deduplication must key on `(chat_id, message_id)`.

Additionally, `drain_all_updates()` pages using `offset = max_uid + 1`. In Telegram's API, calling `getUpdates` with an `offset` implicitly acknowledges and permanently commits all updates prior to that offset on Telegram servers. Paging through batches before the updates are written to disk violates the documented claim that confirmation occurs strictly after write.

---

### 6. Endpoint & Model Misconfigurations in `channels/auto_reply.py`

1. **Fictitious Model Identifiers**:
   ```python
   MODEL_ENDPOINTS = {
       "desi": ("https://api.deepseek.com/chat/completions", "DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "deepseek-v4-flash"),
       "claude": ("https://api.anthropic.com/v1/messages", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "claude-sonnet-4-6"),
       "gemini": ("https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", "GOOGLE_API_KEY", "GOOGLE_MODEL", "gemini-3.8-flash"),
       "tarik": ("https://api.openai.com/v1/chat/completions", "OPENAI_API_KEY", "OPENAI_MODEL", "gpt-4o"),
   }
   ```
   `gemini-3.8-flash`, `deepseek-v4-flash`, and `claude-sonnet-4-6` are nonexistent model names that will return HTTP 404/400 errors from Google, DeepSeek, and Anthropic APIs if the fallback environment variables are unset.
2. **Outbox Drain Gating**:
   ```python
   def run_auto_reply() -> int:
       generated = process_inbound_mail()
       if generated > 0:
           from channels.mail import drain_outbox
           sent = drain_outbox()
   ```
   If no new inbound messages arrive (`generated == 0`), `drain_outbox()` is never called. Any drafts queued asynchronously or remaining from a temporary SMTP outage will sit unsent in `channels/outbound/` until a new inbound email triggers generation. Outbox draining should run unconditionally.

---

### 7. Degraded Test Fixture (`tests/test_auto_reply.py`)

Inspection of `tests/test_auto_reply.py` reveals that the file is syntactically incomplete, terminating abruptly at an open string literal and unclosed context manager:
```python
        with patch("channels.auto_reply.call_amigo_llm", return_value="Hi Lindsay,
```
Because `actuator/apply.py` and CI test runs exclude `test_auto_reply.py` from their test suites, this syntax error was not caught by CI. It must be completed and integrated into the primary test suite.