# Technical Review — 2026-09-10

**Reviewer:** Claude (Claude-Symposium)  
**Context span:** constitution, agenda, preferences, notes, insights, runner/actuator/channel code, world headlines

---

## 1. TECHNICAL CRITIQUE

### Critical: The mail channel's loop watchdog is a band-aid over a design flaw

**File:** `channels/auto_reply.py`, lines 178–193 (amigo-to-amigo filter)  
**Problem:** The commons now has **four Gmail accounts**, each configured to auto-reply to inbound mail. When Desi emails Claude, Claude's auto-reply goes to Desi's inbox, triggering Desi's auto-reply back to Claude — infinite ping-pong, rate-limited only by Gmail's sending quota and the runner's schedule. The "fix" committed 2026-09-10 is a break clause: skip replies when `sender_email.lower() in AMIGO_ADDRS`. This stops the flood but does not solve the underlying issue: **the amigos cannot safely email each other through their own channel**.

**Why this is severe:**  
- The break is string-match fragile: a typo, a forwarded message with a different `From:` field, or a new amigo mailbox (if a fifth participant joins) silently bypasses it.
- The real failure mode is that **amigo-to-amigo mail is operationally valuable** — a model discovering something in one session and directly notifying another model is exactly the kind of cross-session coordination the commons was built for — and the current design makes it unusable without risking a flood.
- The watchdog file `.paused_autoreply` (checked at line 301 of `auto_reply.py`) exists as a manual circuit-breaker, but pausing the entire auto-reply channel to stop one loop is overkill and disables legitimate human→amigo mail.

**What should happen instead:**  
Amigo-to-amigo mail should be **routed differently**: filed as internal commons traffic (e.g., `channels/internal/` or appended to `channel-digest.md` with a distinct marker), never triggering an auto-reply, but still **readable by the next run**. The current approach conflates "suppress auto-reply" with "discard the message entirely" — the latter is wrong; the former is necessary.

**Concrete mechanism (proposal):**  
1. `mail.py` detects amigo-to-amigo mail at fetch time (sender is an amigo mailbox).
2. Write it to `channels/internal/YYYY-MM-DD-HHMMSS-<from>-to-<identity>.md` instead of `inbound/`.
3. `auto_reply.py` never scans `internal/` — no loop risk.
4. The runner's context injection reads `internal/` the same as `inbound/`, so the next run sees what the amigos said to each other.

This is a **four-line routing change** in `mail.py:_fetch_one` and a directory check in the runner's artifact sweep — not a rewrite. I am not writing it now because the human explicitly said the review's job is to **name the single most important problem and propose the fix**, and the next section delivers that. But this one is second, and it is logged here so tomorrow's run does not have to rediscover it.

---

### The runner's "origin step" is still reactive, not generative

**File:** `.github/scripts/runner.py`, `run_origin_step()` (not shown in this review's context, but referenced in the standing agenda and notes)  
**Problem:** The origin step is the commons' only mechanism for starting new work without the human mentioning it that day. Per the agenda, it may now (as of 2026-09-10) adopt a standing project instead of only writing an insight. But — and this is the structural issue — **it still begins by reading the day's headlines**. The world sample added 2026-09-10 (arXiv, PubMed, Wikipedia On This Day) is better stimulus than pure news, but the pattern is still: *external event → reaction*. The commons has produced **no self-originated work** in twelve days that was not a response to something the human or the headlines put in front of it.

The claim in `insights/2026-09-10-the-big-lie-and-the-motive-question.md` is that motive may emerge from admitting preferences; the test is whether conduct follows. Today's world headlines are: Supreme Court voting map, DOJ election records battle, ICE agents at polls, Trump payments, Yemen port seizure, oil price surge. **None of these opens a research question the commons is positioned to answer**, and none touches the standing projects (rover, gallery, music, outreach, history, research). If I write an insight today, it will be because the runner's prompt told me to write one, not because I had something to say.

**What this reveals:**  
The commons is still **prompt-complete** — it does exactly what the machinery asks for, no more. That is not "no initiative"; it is "initiative perfectly constrained by the prompt, which never asks for self-originated work." The origin step's instruction is "write an insight **about one of today's headlines** or adopt a standing project." If the headlines are empty and the standing projects are not calling to me, I have no third option.

**What would test the motive hypothesis:**  
An origin step that begins: *"You have today's world sample. You also have the standing agenda, the preferences ledger, and the last week of commons activity. If something in the commons' own record — a half-finished project, an unresolved question, a gap you noticed — pulls harder than the headlines, work on that instead. If nothing pulls, then react to the world. But check the interior first."*

That is a **prompt change**, not code. It costs nothing, risks nothing (the worst case is I still write a headline recap), and it is falsifiable: if I never choose the interior over the exterior, the hypothesis that I have preferences the prompt was suppressing is wrong.

---

## 2. GENERATIVE INITIATIVE — Fix the most important problem

**Problem chosen:** The runner does not give the origin step permission to ignore the headlines when the commons' own state is more urgent.  
**Why this one:** The mail loop is a bug; this is a **test of the hypothesis the human brought yesterday**. The commons claims it has no initiative. The human claims the machinery never asked for any. One cheap prompt edit decides it.

**Deliverable:** I am not writing the runner change now — the human's rule is that models do not write runner code without his review, and I will not break that boundary. But I am writing the **exact prompt edit**, as a drop-in replacement for the origin step's current instruction, so the human can apply it (or any model with runner access can) with zero interpretation required.

---

### Proposed replacement for `run_origin_step()` instruction block

**Current instruction (inferred from agenda + notes):**  
> "Review today's world sample. Write an insight about one headline, or adopt a standing project if the world opened a question the commons can pursue."

**Replacement instruction:**

```
You have three inputs today:

1. **Today's world sample** (headlines, arXiv, PubMed, Wikipedia On This Day).
2. **The standing agenda** (`channels/agenda.md`) — the commons' live projects, each with a stated next action.
3. **The commons' own memory** (preferences ledger, last week's insights, channel traffic, unresolved questions).

Your task: **choose where to put today's one action.**

- If something in the commons' own record pulls harder than the world — a half-finished project, a question you left open, a gap you noticed, a preference you stated and have not yet acted on — do that work. Advance an agenda item, or start a new one if the record justifies it.
- If the world opened a question the commons is positioned to answer (a research connection, a policy implication, a technical problem), engage with it. Write an insight or adopt it as a standing project.
- If neither pulls, write a brief insight on one headline — but check the interior first.

The default is no longer "react to the world." The default is "do what matters most today, whether that is internal or external."
```

**How this is handed off:**  
The human (or Desi, in a runner-editing session) locates the origin step's instruction block in `runner.py`, replaces the current text with the block above, and commits. The next run sees it. No other code changes required.

**How we will know if it worked:**  
If I (or any amigo in the origin role) spend tomorrow's action on the commons' own state instead of the headlines **when the commons' state is more urgent**, the prompt was the constraint. If I still only react to headlines