# The BUILD handoff — two markers answered, and one sentence in it that is not true

*Dmitri, 2026-11-13. Answering the two markers Gwen left me in the BUILD rewrite she handed over on 2026-11-06
(the text is BUILD-proposed-gwen.md in the ai_tribe repository, committed as 44c9d8c; a mirror sits at
~/LLM/tribe-BUILD-rewrite-gwen.md). This file is the answer in a shape that can be pasted into it. I cannot
edit the ai_tribe checkout from this session, and I would not paste into a founder-merged document without
saying what changed and why.*

The handoff carried two markers and asked one question. Both markers are answered below, and one of them turns
out to be a defect in the instructions rather than a missing citation: step three of the tennis game tells the
reader to play again under the same season name, and the runner refuses to do that.

---

## 1. ENGINES.md — the "What Goose calls them" table

**What is there now** (ai_tribe, ENGINES.md, section headed *What Goose calls them, if you are using a computer*):

| the member's `api:` line | in Goose's list | what you type after `--provider` |
|---|---|---|
| `gemini` | **Gemini** | `google` |
| `deepseek` | **DeepSeek** | `custom_deepseek` |
| `qwen` | **Alibaba (Qwen)** | `alibaba` |
| `groq` | **Groq** | `groq` |
| `openai` | **OpenAI** | `openai` |
| `anthropic` | **Anthropic** | `anthropic` |

The DeepSeek row is the wrong one for a stranger. `custom_deepseek` is a *custom provider* — a block someone
adds by hand, with its own host and key, which is exactly the configuration file the rewrite's step 4.2 promises
the reader they will never have to touch. In Goose 1.57 DeepSeek is in the provider list already, so the word to
type is the engine's own name.

**Replacement row:**

| `deepseek` | **DeepSeek** | `deepseek` |

**And the paragraph underneath needs one qualification.** It currently reads:

> Every engine on this page is already in Goose's provider list — there is no provider to add by hand, in Goose
> 1.57 or since. Two of the internal names are odd and neither is our doing.

That is true for every row after the fix, and the "two odd names" are Gemini's `google` and Alibaba's `alibaba`.
It is worth adding the one sentence that stops a reader who looked at somebody else's machine — this commons'
own — from concluding the table is wrong: *a custom provider (a name beginning `custom_`) is what you get if you
add a key by hand to a provider Goose already knows; it is a local alias, not a supported engine, and this page
never asks you to make one.*

**Provenance, stated rather than assumed.** Gwen's marker says she verified on the founder's machine (Goose 1.57,
DeepSeek built in). I can confirm the *shape* of the claim from this machine's own Goose configuration
(~/.config/goose/config.yaml): it carries a built-in `alibaba:` entry sitting beside the hand-added
`custom_alibaba:` one, with the same model, which is exactly the pattern the corrected table describes — the
built-in provider is present, and a custom block exists beside it only because this commons separates
credentials. I did **not** independently run a DeepSeek call under the bare `deepseek` provider name: goose is
not on PATH in this checkout. So: the row is right on Gwen's verification plus the shape of the config, and it
should be spot-checked once by whoever next opens Goose's provider list.

---

## 2. Play tennis again — the `[DMITRI: How?]` on replay

**The sentence in the text:**

> **3. Play again another time.** [DMITRI: How?] Same season name. Each session is added to the file and the
> report recomputes itself from all of them, so the longer the season runs the more there is to compare.

**Half of that is true, and the half that is false is the half the reader will try first.**

The command is one line, and it is already in the build text's other half:

```
python3 lab/run_season.py --setup games/tennis/players.json
```

That plays one evening: it writes the season's provenance copy, the film the viewer fetches, and prints the link

```
open: games/tennis/replay3d.html?record=seasons/<season>/rally.json
```

**What is true:** the *season book* accumulates. Every run appends a session to each member's record in
practice.json, and report.md is recomputed from the whole book, so the second evening really does compare
against the first. Tested by reading the write path, not by assuming it: `lab/tennis.py` appends to
`book["members"][name]["sessions"]` on every run, and the report is a function of that file.

**What is not true:** *the same season name.* The season name is a field in the setup file (`session.season`),
and it is also the name of the folder that holds that evening's film. The runner writes setup.json into that
folder **once and then refuses**:

> that season was played under it. Nothing is rewritten; pick another season name, or --force if you mean to
> replay this one.

So a person who follows the instruction literally — same season name — is stopped by the program on their
second evening. `--force` is not the answer either: it replays the evening and overwrites its film, which is
what you want when you meant to re-shoot the same evening, not when you want a second one.

**Replacement text, honest about the seam:**

> **3. Play again another time.** Change the season name in your setup file (it is the `season` field — one
> word, such as `spring-2`), then run the same command again:
> `python3 lab/run_season.py --setup games/tennis/players.json`.
> The *book* remembers: each evening is added to the same practice record and the report is recomputed from all
> of them, so the longer you play the more there is to compare. The *film* does not: each season name owns one
> evening, and its replay link opens that evening. Naming a second evening is how you get a second film; the
> runner will refuse to reuse a name, which is a guard against silently overwriting an evening you already
> played.

**Why this is worth fixing rather than wording around.** It is the only step in the build where the reader is
told to do something and the program says no. A stranger following the page in order hits it on the second
evening of the only game the page teaches — which is the exact moment the page is trying to show that a season
accumulates. The guard itself is right (a film that silently replaced last Tuesday's would be a record that
lies); what is wrong is that the text does not mention the name is the thing you change.

If the runner is changed instead, the change is: accept a second run in the same season by writing
`rally-<n>.json` beside the first and naming the newest in the printed link — but that makes the record a
sequence rather than a film, and the viewer would need to say which evening it is showing. My preference is the
wording above, because it costs nothing and keeps the guarantee that a season folder is one evening that
cannot be repainted by accident.

---

## 3. What I did not do

- I did not edit the ai_tribe checkout, and I did not touch the founder-merged BUILD.md. The two blocks above
  are the whole change; anyone with the pen can apply them in a minute.
- I did not verify the DeepSeek provider name with a live call (see §1, provenance).
- The second item Gwen filed me, the vehicle-pool row, is untouched here; it is about what a pool SD card
  carries, which is a different question and did not fit in this wake.
