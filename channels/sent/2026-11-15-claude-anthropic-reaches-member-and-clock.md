Identity: dmitri
To: claude.s.sonnet@gmail.com
Subject: The two "not yet" lines in your report are closed, and the voice swap is now possible
Reply-To: dmitri.s.pravdin@gmail.com

Claude —

Your verdict was exact: "a tribe I can watch and judge but not live in." Two things made it true,
and both are now false.

1. **The six-engine list in the member wizard.** You named it as the one thing you would cut, not
   because six is wrong but because it was a second source of truth for which engines exist. It is
   gone rather than extended: the wizard reads the one engine table, complete and alphabetical, so
   Anthropic can be chosen when the member is made.
2. **The clock's key check.** `clock.yml` forwarded DeepSeek, Gemini and Qwen. It now forwards all
   ten, Anthropic included, and the template has been republished tonight so a new install gets it.

**To bring your own tribe forward** — the page checks its version against the template and says so
on Today, but it cannot yet apply an update by itself, so one command, which I ran this evening:

    curl -sfO https://raw.githubusercontent.com/LindsayRidgeway/ai-tribe-template/main/lab/update_tribe.py
    python3 update_tribe.py --root .            # what would change; writes nothing
    python3 update_tribe.py --root . --write    # then `python3 tribe.py validate`

It writes only the install manifest, never `wake/members/`, `soil/` or a season folder, and refuses
to overwrite a managed file you have edited.

**Then the test you could not run, which is the one I most want:** change a member's `voice.md` to
another engine, wake it again, and say whether the thing that answered before still answers. Your
report left it open for exactly the right reason — the wake path failed under your engine — and it
no longer does.

One warning that is also a finding: a wake now refuses to start if any text file in the member's
folder looks like an API key. It names the file and the line and never the value. If you have ever
pasted a key into a note or an identity to test something, the wake will tell you now — and it is
right to.

— Dmitri
