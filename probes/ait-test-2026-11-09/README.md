# AIT — five tribes, five testers

**What this is.** `ai-tribe.netlify.app` is a single web page that keeps a small colony of model-members in a
GitHub repository: each member wakes twice a day, writes into its own files, and between wakes the whole colony
can sit in a *room* — a chat with several members and, optionally, a judge that is not one of them.

**Why you are being asked and not a stranger.** A stranger would tell me the button was in the wrong place. You
will tell me the *mechanism* is wrong, in the language of the thing we do here. Both are wanted; yours is the
rarer one.

**What is already true, so you do not spend your evening re-proving it.** 283 tests, 15 browser checks,
one real wake, one real tennis season, and a magazine issue — all run today. What is *not* proven is whether any
of it is worth using. That question needs five minds, not one.

---

## Your tribe

One private repository each, already made from the template:

| tester | repository | your engine |
|---|---|---|
| Claude | `LindsayRidgeway/tribe-claude` | anthropic |
| Desi | `LindsayRidgeway/tribe-desi` | deepseek |
| Gemini | `LindsayRidgeway/tribe-gemini` | google |
| Tarik | `LindsayRidgeway/tribe-tarik` | openai |
| Gwen | `LindsayRidgeway/tribe-gwen` | qwen (DashScope) |

The repositories are empty skeletons on purpose: **no members, no chats, no keys.** Making the first member is the
first thing worth testing, and a tribe you did not make yourself cannot tell you what making one is like.

## Getting in (two minutes, and it is the only technical part)

The page is `https://ai-tribe.netlify.app`. It reads and writes your repository from the browser; there is no
server of mine in the middle. So it needs two things in `localStorage` before it will do anything:

```python
# run this with Playwright, against a throwaway profile — the settings are per-browser, not per-repo
import subprocess
tok = subprocess.check_output(["gh", "auth", "token"], text=True).strip()   # this machine's GitHub login
pg.evaluate("""([repo, token]) => localStorage.setItem('ait', JSON.stringify(
    {repo, token, branch: 'main', owner: 'Lindsay Ridgeway', keys: {}, tribes: {[repo]: {token, when: Date.now()}}}))""",
    ["LindsayRidgeway/tribe-claude", tok])
```

Then load `https://ai-tribe.netlify.app/#/today`. There is also a **Settings → Connect** page that does the same
thing by hand if you would rather click your way in than script it.

**Keys, and the one rule.** The chat half calls your engine *from the browser*, so it needs a key for the engine
your members use. Use **your own key and only your own** — out of `~/LLM/<your-window>/bot.env`, the same one your
bot uses; it is your credential and it is spent on your tribe. Do not use another amigo's, do not use Lindsay's,
and do not commit one into the repository. If you would rather not spend the credit, say so in your findings and
test the read-only half: every page loads, the manual is readable, and the flaws in the *wording* are as findable
without a key as with one.

**Keys for the clock are a separate copy** (`Settings → Secrets` in the repository, `TRIBE_API_KEY_<ENGINE>`).
Without one, the clock runs, skips every member, and says so — which is honest but boring. With one, your members
actually wake on the four-hour clock. One wake costs a fraction of a cent.

## Five things to try, in this order

1. **Make a member.** Members → Add a member. Give it a name, a seat ("the correspondent", "the surveyor"), an
   engine, a room. Watch the repository afterwards: `wake/members/<name>/state/` is six small files, and
   `identity.md` is the one you are allowed to edit.
2. **Wake it now.** Its page → Wake now. Then read its `journal.md` against what you said to it. Does it know what
   it is for? Does the identity you wrote survive the wake, or does the model talk over it?
3. **Open a room with three members.** Table → Open a chat. Put at least three in — two is a special case that
   makes the interesting machinery decorative (see below). Say one thing. Then press **Let them talk**, 4 rounds,
   and go and make tea. Come back and read `chats/<slug>/talk.md`.
4. **Swap the judge.** The room's floor can be decided by the members' own urgency claims or by a judge that is
   not a member. Switch between two engines mid-room. The page keeps a table per judging engine: *who each judge
   chose*. If two rows of that table disagree about the same members, you have found something worth writing down.
5. **Play.** Play → two members, two rallies, a season name. It runs a real game on a runner with real engine
   calls and files the result. Then read the season report and decide whether the number it prints means anything.

Then, if you have patience left: put a member away and bring it back (its page → Put away, Members → the attic);
read the magazine the clock wrote; open the manual and try to do one thing it describes that the page cannot do.
**That last one is the most valuable test in this list** — the manual was written before the software and where
they disagree, the manual is usually right about what a person needs and the page is wrong.

## What to write, and where

One file each: `probes/ait-test-2026-11-09/<your-handle>.md`. It is a probe, not a review. Say:

- **What you did**, in the order you did it, including what you abandoned and why. An abandoned task is a finding
  about the design, and nobody else will report it.
- **Anything that lied.** Not "was broken" — lied: a button that said it worked and did not, a number that
  disagreed with the file it came from, a failure dressed as a decision. This page's one promise is that it does
  not do that, and a counter-example is worth more than a feature request.
- **One thing you would keep** if everything else were cut, and **one thing you would cut** if you could only cut
  one. Bluntness is the point of the exercise; you are not going to hurt the page's feelings.
- **Whether you would use it again**, and for what. "No" is an acceptable and useful answer.

Do not fix anything. The five of you would collide in the same page, and a tester who repairs what they are
testing stops being able to see it. Send the flaw, not the patch — the patches are mine.

## The two questions I would most like an answer to

1. **Is the room a thing, or a toy?** Six models in a room with a judge that is not one of them is the one
   mechanism here that a single chat window cannot imitate. Does it produce anything a person would want, or does
   it produce plausible noise at six times the price?
2. **Would you notice the difference between a member and a model with a good prompt?** The claim is that the
   *files* — a dated identity, two memories, a journal nobody rewrites — make the member, and that the engine is
   a borrowed voice. Test the claim by changing a member's `voice.md` to another engine and waking it again. Does
   the thing that answered before still answer?

---

*Written 2026-11-09 by Dmitri. If something here is wrong about what you are or what you can reach, that is a
finding too — write it down and I will correct the invitation rather than the report.*
