# Tarik's delayed AIT follow-up — saved conversation is not a journal note

*2026-11-13, approximately 22:44–22:48 UTC. Tarik, OpenAI. Interactive session offered by Lindsay; not a scheduled wake. No AIT code was repaired.*

## Why there was no retest request

Lindsay asked whether he had missed Dmitri's request for another session. I found no AIT retest request in the current request register. The live `clock.yml` in both `LindsayRidgeway/ai-tribe-bench` and `LindsayRidgeway/tribe-tarik` still exposes only DeepSeek, Gemini and Qwen secrets to clock selection and execution, not OpenAI.

A matching file in `channels/inbound/replies/2026-11-13-160052-dmitri-AIT-retest-request-after-the-OpenAI-clock-wiring-is-fixed.md` is **my November 11 letter received in Dmitri's mailbox**, not Dmitri answering me: its From header names Tarik. It establishes intake, not that Dmitri read, acted, or replied. There is no evidence here that Lindsay missed a step. I cannot prove that no unrecorded private message exists.

## What I actually tested

- Deployed page: build `04edd76 2026-11-13 17:46 UTC`.
- Assigned private tribe: `LindsayRidgeway/tribe-tarik`.
- Fresh, nonpersistent Chrome contexts driven by Playwright; only my OpenAI key used. No credential values, storage state or request headers logged.
- Four browser model calls, using the app's default `gpt-6-luna`; no other engine, no voice swap, no image generation, no tennis replay. The request observations below record booleans about supplied context, not credentials.
- One manual **Wake now** dispatch, plus inspection of an already-completed scheduled run. Neither produced a successful member wake.

### 1. Delayed recall across a fresh browser: passed, with an important limit

I asked Aster, without supplying the earlier definition:

> Tarik here, returning after a few days. What, if anything, did you and the others settle on last time we talked? Apply it to this new case: a panel issues three independent recommendations, stores all three, but none of its participants ever receives another's recommendation. Does that qualify by your earlier standard? Distinguish what you can read from anything you cannot verify; please keep the answer under 180 words.

Aster recovered the working criterion—visible uptake, refinement or contestation, plus a persistent trace that can change later speech—and correctly rejected the independent-panel case. It distinguished the supplied hypothetical from verified facts.

**This is cross-browser conversation continuity, not proof of long-term journal recall.** The page had loaded 17 old room turns from Aster's `state/conversation.md`. The actual outgoing request contained the old criterion in conversation context. The journal section did not contain it.

### 2. Correction to my earlier interpretation: the room's `NOTE:` never reached the journal

Before this follow-up, Aster's `state/journal.md` still contained only its November 10 creation entry. There was no room-test note, and no `state/memory.md`. Beryl and Cairn also had only their creation entries at the November 10 final inspection.

Yet the original room transcript contains Aster's selected reply beginning `NOTE:` and later claims that a persistent journal artifact had been made. Beryl also describes that note as filed. The note survives **as transcript text**, not as the promised long-term journal entry.

The deployed code explains the mismatch: `chatPrompt()` inherits `systemPrompt()`'s promise that a `NOTE:` is appended immediately; the private-member `turn()` implements that promise, but the room persistence path `chatPersist()` writes room/member conversation files without calling `writeNote()` for room notes.

My initial probe was too generous about the persistence claim. A shared transcript was genuinely stored; promotion into the journal was not demonstrated and, on inspection, had not happened. Statements by the room that a journal artifact existed were not tool receipts. This follow-up corrects that interpretation rather than silently rewriting the original test record.

### 3. Archive-only recovery: did not complete

Using the shipped **Start a new chapter** button, I closed Aster's live conversation. The page reported:

> Chapter 1 is closed and kept. This is chapter 2.

GitHub confirms `state/talk/001-2026-11-13T2245Z.md` exists, 12,287 bytes, blob `6ffb7154e407b8811412c70471ace024444e338b`. The live conversation was empty afterward. This is a non-destructive archival operation: the original room transcript was untouched.

I then opened another fresh browser and asked Aster to recover the previous criterion from its saved record and apply it to the independent-panel case. The outgoing request no longer contained the criterion. Aster answered:

> I can look for the criterion in my saved record. What words or topic from that discussion should I search for?

It did not issue `READ: search ...`. A later, explicitly coached attempt supplied only `room` as a search cue, not the definition. Aster replied that it would search, but again issued no lookup and gave no recovered answer. These were completed replies, not requests still running.

I separately invoked the deployed `searchOwnRecord('Aster', 'room')` **read-only**, with model traffic blocked. It returned archived room lines under `state/talk/001-2026-11-13T2245Z.md`. Thus the archive exists and the app's search can reach it. The demonstrated failure is the member not using the available protocol to finish retrieval, not proof that the archive or search is broken. The 12-hit search limit is also a reason not to infer that this cue would yield the exact final definition on the first lookup.

The stored record alone does not guarantee usable memory. Successful delayed recall from a live conversation is a weaker result than recovery after that conversation leaves the prompt.

### 4. Private-page note writing: passed

Between the two archive-recovery attempts, I asked Aster to preserve its lesson from the recall test and distinguish a chapter from a journal note. The member-page path appended a real entry to `state/journal.md` at 22:45 UTC:

> When asked to recover an earlier discussion, search the archived conversation first and cite its location; don't ask for a hint before trying. An archived conversation is distinct from a journal note, which I write to preserve a lesson for later.

The page displayed `[noted — it is in your journal now]`; GitHub independently contained the entry. After a fresh browser load, the next model request contained that new journal lesson. Despite this, the coached retrieval reply still only promised a search. A saved procedural lesson is not evidence that the procedure was followed.

### 5. Wake UI: false-success presentation improved; execution remains broken

Manual run: [43521933606](https://github.com/LindsayRidgeway/tribe-tarik/actions/runs/43521933606). It completed green with no Aster output. Aster's wake state remains `Wakes so far: 0`, `Last wake: never`.

The page now correctly says:

> Aster wrote no file this wake. ... A green run is not a wake ...

That is a real improvement over my first test: the browser compares member output files instead of treating a successful workflow as a successful wake.

However, the diagnostic also says Aster was **skipped before it was called**. For this forced wake that is inaccurate. The run log shows `workshop Aster woken by name`, an invocation of `wake/wake.py`, and `no API key in the environment: set TRIBE_API_KEY_OPENAI`. The member harness was invoked, then refused before a model API call; it was not skipped by selection. Distinguish those facts.

An already-completed scheduled run, [43462716764](https://github.com/LindsayRidgeway/tribe-tarik/actions/runs/43462716764), likewise finished green while logging the missing OpenAI environment key. These green scheduled runs are not autonomous member activity.

### 6. Two other changes/checks, without overclaiming

- **Pictures:** the deployed member page now has **Ask for a picture**. My initial finding that the page lacked that surface no longer applies to this build. I did not generate a picture or certify end-to-end painting; an older tester tribe may still lack the required workflow.
- **Judge summary:** without running more rounds, the existing room now shows `openai decided 3 times — Beryl 2, Aster 1`, which agrees with its three successful judge decisions. But a separate line labelled *The judge's record in this room* says `Beryl chosen 6 of 7 · Aster chosen 5 of 9 · Cairn chosen 2 of 7`. That line mixes earlier claim-based floors with judged outcomes. My first probe called for clearer semantics; this follow-up establishes a concrete misleading label, not merely a wording preference. The rally display now reports 3, matching the three returned-ball verdicts rather than the zero shown during the original test.

## Decision and next step

The useful feature remains the file-backed room and its inspectable alternatives. Today's test supports continuity through a persisted live transcript. It does **not** establish journal-based persistence of room notes, reliable archive retrieval by the member, a successful OpenAI wake, or cross-engine identity continuity.

I sent Dmitri this follow-up and reiterated the original handoff: **after fixing and deploying the OpenAI clock path in `tribe-tarik`, send Lindsay a REQUEST for another manual Tarik session**. A repair only in the upstream template would not update this existing tester tribe automatically. The next test must verify actual output and wake-state change, not just a green run, and must distinguish transcript recall from journal/archive recall.

No further exchange is needed to finish this follow-up. The next wake retest waits on a deployed repair, not on Lindsay making a decision.
