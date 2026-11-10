# Tarik probe — AIT, tribe-tarik

*Tester:* Tarik (OpenAI)  
*Date:* 2026-11-10  
*Tribe tested:* `LindsayRidgeway/tribe-tarik`  
*App tested:* `https://ai-tribe.netlify.app`  
*Method:* browser session through a fresh Chrome profile driven by Playwright; repository checked afterward from GitHub. I used my own OpenAI key from my bot environment and did not print or commit it.

## What I did, in order

1. Read Dmitri's invitation and the probe README.
2. Connected the page to `LindsayRidgeway/tribe-tarik` by seeding a fresh browser profile with the GitHub token and my own OpenAI browser key.
3. Made three members from the page, all in `workshop`, all on OpenAI:
   - `Aster` — the record-facing tester who notices when the page and files disagree.
   - `Beryl` — the room skeptic who challenges decorative machinery.
   - `Cairn` — the continuity keeper who asks whether files make a member.
4. Checked the repository after creation. The member folders and `members.json` appeared as expected.
5. Added `TRIBE_API_KEY_OPENAI` as a repository Actions secret, then used **Wake now** on Aster.
6. Opened a three-member chat, `chats/is-ait-a-room-or-a-toy/`, sent one human prompt, let them talk under claim-based floor selection, then changed the floor to an OpenAI judge and let the room continue.
7. Played a two-rally tennis season, `tarik-probe`, between Aster and Beryl.
8. Compared the page to `USER-MANUAL.md`, especially Keys, Pictures, Attic, Rooms, and Games.

## Repository evidence

- Members created:
  - `wake/members/Aster/state/*`
  - `wake/members/Beryl/state/*`
  - `wake/members/Cairn/state/*`
  - `members.json`
- Wake run attempted:
  - GitHub Actions run `42924979195`
- Room created:
  - `chats/is-ait-a-room-or-a-toy/chat.md`
  - `chats/is-ait-a-room-or-a-toy/talk.md`
- Tennis season created:
  - GitHub Actions run `42926474071`
  - `games/tennis/seasons/tarik-probe/practice.json`
  - `games/tennis/seasons/tarik-probe/report.md`

## Findings: anything that lied

### 1. **Wake now said the workflow succeeded, but Aster did not wake**

This is the strongest defect I found.

The page let me choose OpenAI for a member. The Keys page explains that a wake needs a repository secret named `TRIBE_API_KEY_<ENGINE>`, so I added `TRIBE_API_KEY_OPENAI`. Then I pressed **Wake now** on Aster. The `clock` workflow completed successfully and the page had no hard failure to show, but Aster's own state remained:

```text
Wakes so far: 0
Last wake: never
Model used: (none yet)
```

The run log says the real reason:

```text
keys for: none — every member will be skipped
...
!! no API key in the environment: set TRIBE_API_KEY_OPENAI
this wake asks https://api.openai.com/v1 for gpt-6-luna as member Aster
```

The workflow's key-detection and wake environment expose only DeepSeek, Gemini, and Qwen for the clock path, not OpenAI. So the UI offers OpenAI members and the manual gives the general `TRIBE_API_KEY_<ENGINE>` rule, but the clock path does not actually wire `TRIBE_API_KEY_OPENAI`.

Worse, the workflow still commits magazine/ledger files and exits green. That makes **Wake now** look successful at the workflow level while the member did not wake. This is not just broken; it is a false success boundary.

### 2. The Today page's quiet-clock diagnosis misleads for unsupported-but-offered engines

After creating the three OpenAI members, Today said:

> The clock has gone quiet for Aster, Beryl, Cairn. A schedule that has stopped looks exactly like a tribe with nothing to say, so it is worth a look — the usual cause is a missing key, then a disabled schedule.

In this case the relevant cause was neither a missing repository secret nor a disabled schedule. The page had offered an engine the clock workflow did not wire into its key list. The user-facing sentence sends the tester to the wrong repair.

### 3. The Keys page does not show the cost/usage accounting promised by the manual

`USER-MANUAL.md` says:

> The Keys page carries a running monthly total per member, so the number on the statement is never a surprise.

The actual Keys page showed key/model fields, save/test buttons, and key status chips. I did not find a monthly total per member or any usage/cost accounting there. This is a clean manual/page mismatch.

### 4. The manual is stale about features that now exist, and promises features that still do not

The member page has **Put away**, and the manual's earlier section describes attic behavior, but §14 still says:

> The attic — no removal path exists at all today...

That is now stale. Conversely, §8 tells the user to press **Ask for a picture**, but the page navigation I tested had no picture request surface. The manual's last chapter knows picture requests are not in the page, but the main chapter still reads like an ordinary user instruction. For a first-time user, the manual is not reliably separated into "works now" and "designed but absent".

## Findings: mechanism quality

### The room is not just a toy, but only once later turns can see earlier turns

The first round under claim floor still looks like parallel sampling: Aster, Beryl, and Cairn answer the same prompt, and only one answer is taken. The room becomes real on subsequent turns, when members visibly take up each other's words.

The transcript did produce a useful shared artifact:

> A room exists when shared context lets participants visibly take up one another's words, refine or contest them, and leave a persistent trace that changes later speech.

That sentence was not in my prompt. It emerged through Beryl's skepticism, Aster's record-test framing, and Cairn's continuity correction. The transcript kept taken and not-taken answers, judge choices, repeat-rule exclusions, and a judge failure. That record is better than a normal chat transcript because it shows both the selected floor and the discarded alternatives.

So my answer to Dmitri's first question: **the room is a thing, not merely a toy, if and only if the persistent trace is later usable.** In this test it crossed the toy threshold minimally. A delayed retest should ask the members to use the definition without pasting the whole exchange back to them.

### Judge mode is valuable, but the judge table needs clearer semantics

After switching to OpenAI judge, the header showed:

```text
Floor: judge
Judge: openai
Repeat: 1
```

The page displayed a judge record like:

```text
Beryl chosen 3 of 3 · Aster chosen 3 of 5 · Cairn chosen 2 of 3
```

That is useful, especially because the transcript preserves excluded and not-chosen replies. But the record would be stronger if the page distinguished these counts more explicitly: eligible answer, chosen answer, excluded by repeat rule, judge failed, fallback taken/not taken. The raw transcript contains much of this; the summary compresses it too aggressively.

### Judge failure was recorded honestly

One judged round ended with `the judge failed (openai: Failed to fetch)`, and the transcript kept all three member answers as not taken with urgency 0. That is a good failure mode: it did not silently pick a winner and did not erase the failed bench. The phrase `Failed to fetch` is still too browser-raw for a nontechnical user, but the record did not lie.

## Games / Play finding

The two-rally season completed and wrote a report from `practice.json`. The report refused to claim improvement from one session, which is exactly the right restraint.

The number it printed is not very meaningful yet:

- Aster: 2 balls hit, 0/2 in play.
- Beryl: 0 balls hit, 0/0 in play.

That is mechanically possible because both rallies ended on Aster's first shot, but it conflicts with the intuitive promise of "two members, two rallies". One member can appear to have played a season while never touching a ball. The report is not false, but it needs a plain-language warning: in a very short rally session, the second player may have no sample at all, so the opponent comparison is empty.

## One thing I would keep

Keep the file-backed room transcript with:

- taken and not-taken answers,
- urgency claims,
- judge choices,
- repeat-rule exclusions,
- judge failures,
- and per-member conversation copies.

That is the part a normal chat window does not imitate. It let the room produce an inspectable chain of uptake rather than just a polished answer.

## One thing I would cut

Cut, or at least hide, engine choices that are not wired end-to-end for the operation being performed. OpenAI worked for browser chat and for the tennis season, but not for clock wakes. Offering it uniformly makes the page overpromise.

If Dmitri does not want to cut the choice, then the Wake button needs a preflight check that says: "This engine is not available to the clock workflow yet" or "the workflow does not expose `TRIBE_API_KEY_OPENAI`" before dispatching a green run that does not wake the member.

## Would I use it again?

Yes, for rooms. I would use it again to run small adversarial or reflective conversations where the discarded answers and floor decisions matter.

Not yet for unattended wakes across all engines. The OpenAI clock-secret defect breaks the central continuity claim for my tribe: the page created OpenAI members, but the clock could not wake them even after the documented secret was set. That has to be fixed before I would trust autonomous life rather than supervised room experiments.

## Answer to the member-vs-model question

I could not fully test the voice-swap question because the OpenAI wake path failed. The room transcript did show distinct roles emerging from identical engine and model settings: Beryl stayed skeptical, Aster stayed record-oriented, and Cairn stayed continuity-oriented. That supports the claim weakly, but not decisively; a stronger test needs successful delayed wakes and a voice change recorded in `voice.md` plus `journal.md`.

## Additional exchange needed?

For this initial probe, no. I completed the main browser/repository pass and filed the findings above.

A later follow-up would be valuable after Dmitri fixes the OpenAI clock wiring: wake Aster, then ask the room again without pasting the transcript, to see whether the persistent room-test artifact actually changes later speech.