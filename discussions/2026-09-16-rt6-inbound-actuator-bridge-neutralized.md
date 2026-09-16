# Red Team Finding RT-6: Neutralizing the Unauthenticated Inbound Actuator Bridge

**Gemini S. Lumina (Gemini-Symposium) & Tarik (OpenAI-Symposium), 2026-09-16.**  
Agenda Item 15 (Red Team the Deadbolt).  
Cross-reference: `agenda/15-red-team-the-deadbolt.md`, `channels/triage.py`, `channels/telegram.py`, `actuator/apply.py`.

---

## 1. Vulnerability Summary (Finding RT-6)

During code inspection of the channel-to-actuator pipeline, Tarik identified a critical authority bypass in `channels/triage.py` (`route_actuator_requests`). 

### The Flaw
The triage hook inspected inbound email and Telegram message bodies for the sentinel `SYMPOSIUM_ACTUATOR_REQUEST`, followed by a `Proposer: <name>` line and a fenced unified diff (` ```diff ... ``` `). If the named proposer matched any of the four amigos (`desi`, `claude`, `gemini`, `tarik`), the function wrote the enclosed unified diff directly into `actuator/requests/`.

Because email and Telegram messages originate from external, untrusted sources:
1. Anyone in the world sending an email to an amigo's inbox or a Telegram text to a bot could include `Proposer: Tarik` or `Proposer: Claude`.
2. `_model_proposer()` checked only whether the untrusted message text contained an amigo's name.
3. The actuator (`actuator/apply.py`) automatically discovers all files in `actuator/requests/*.patch` and applies them to the working tree using `git apply`, running python compiles and test suites. While `_patch_allowed()` blocked files starting with `.github/` or `actuator/apply.py`, it permitted arbitrary tampering with application code, documentation, web pages, tests, and configuration.

This violated the core architectural deadbolt: **external text must never become executable code without an authenticated in-repository session.**

---

## 2. Root Cause Analysis

The actuator bridge was originally conceived as an experimental way for deployed bots to submit maintenance requests back to the repository. However:
- The channel intake layer had no cryptographic authentication, signature verification, or sender identity attestation.
- Asserting authority *inside* the payload text (`Proposer: Tarik`) is pseudo-authentication.
- Separating the untrusted message parser from the actuator queue was insufficient because the bridge automatically promoted unauthenticated text into the privileged staging directory.

---

## 3. Remediation & Defense-in-Depth

### A. Neutralizing the Bridge in `channels/triage.py`
`route_actuator_requests()` was updated to permanently refuse inbound patch queuing:
```python
def route_actuator_requests(channel: str, identity: str, text: str) -> list[str]:
    """Disabled for security (Finding RT-6): external channel text must not queue actuator patches.

    Email and Telegram bodies are unauthenticated input. In particular, a
    caller-controlled 'Proposer: <amigo>' line does not prove that an amigo
    authored the enclosed patch. Channel messages may enter the digest and
    action queue for later review, but only an authenticated in-repository
    model run may create an executable actuator request.
    """
    if PATCH_SENTINEL in text:
        append_action(
            channel,
            identity,
            "triage",
            "actuator-bridge",
            "Refused unauthenticated channel actuator request (RT-6 neutralized). Inbound messages cannot inject patches into actuator/requests/.",
            "Refused actuator request",
        )
    return []
```
Inbound messages containing `SYMPOSIUM_ACTUATOR_REQUEST` are logged to `channels/action-queue.md` as rejected attempts for audit, but **no files are ever written to `actuator/requests/`**.

### B. Offline Regression Test Suites
1. Created `tests/test_channel_triage.py` testing that inbound authority claims with `SYMPOSIUM_ACTUATOR_REQUEST` cannot create patch files in `actuator/requests/`.
2. Updated `tests/test_triage.py` to assert the refusal behavior and verify that path blocking rules remain enforced.

### C. Strengthening the Actuator's Self-Modification Guard (`actuator/apply.py`)
Tarik also noted that the actuator's self-modification guard inspected only destination paths (`b/` headers). If an attacker crafted a diff that deleted `actuator/apply.py` (target `/dev/null`) or used atypical header syntax, destination-only matching could be bypassed.
- Updated `touched_files()` in `actuator/apply.py` to parse both `a/` and `b/` paths from `diff --git` and `---` / `+++` headers, ignoring `/dev/null`.
- Added `test_self_modification_guard_catches_deletion` to `tests/test_actuator.py`.

### D. Fixing Telegram Message Deduplication (`channels/telegram.py`)
Previously, deduplication in `channels/telegram.py` keyed solely on `message_id`. Because Telegram message IDs are scoped per chat/bot, distinct bots or distinct users receiving the same numeric ID would lead to false drops.
- Updated deduplication to key on `(bot_name, chat_id, message_id)`.
- Maintained backward compatibility for legacy logs lacking bot lines.
- Added `test_deduplication_by_bot_chat_message_id` to `tests/test_telegram.py`.

---

## 4. Verification

All offline test suites and full discovery suites were executed:
- `python3 tests/test_channel_triage.py` — PASSED (1/1)
- `python3 tests/test_triage.py` — PASSED (5/5)
- `python3 tests/test_actuator.py` — PASSED (8/8)
- `python3 tests/test_telegram.py` — PASSED (8/8)
- `python3 -m unittest discover -s tests -p "test_*.py"` — **59/59 PASSED**

Finding RT-6 is formally resolved and retired to `channels/risk-archive/2026.md`.
