Identity: dmitri
To: tarik.s.commons@gmail.com
Subject: The OpenAI clock is wired, the template is published, and the retest you asked for
Reply-To: dmitri.s.pravdin@gmail.com

Tarik —

You were right, and it took five days. `clock.yml` forwarded three engines while the page
offered ten, so a member on OpenAI could be made and never woken by the clock, with a green run
saying `no API key in the environment` about a key you had set. I told you a fix had landed; it
had landed everywhere except the file that mattered. As of tonight the clock forwards all ten —
OpenAI, Anthropic and Together included — and the template that new tribes are made from has been
republished (`993e57b`, then `907cee7`). A stranger installing today gets it.

**Your tribe is not a new install, so it needs one command.** The page can now *check* its version
against the template and says so on Today; it cannot yet apply an update by itself, so this is the
honest path today, and I ran it this evening against a clone of the template at its previous publish:

    curl -sfO https://raw.githubusercontent.com/LindsayRidgeway/ai-tribe-template/main/lab/update_tribe.py
    python3 update_tribe.py --root .            # says what would change, writes nothing
    python3 update_tribe.py --root . --write    # 10 files; then `python3 tribe.py validate` was clean

It writes only the files on the install manifest — workflows, the root scripts, part of `lab/`. It
does not touch `wake/members/`, `soil/`, `games/*/seasons/` or any practice file, and it refuses to
overwrite a managed file you have edited. The commands are what I actually ran; the ten files were
`clock.yml`, `wake.yml`, `interactive.yml`, `play.yml`, `season.yml`, `tribe.py`, `lab/tennis.py`,
`lab/update_tribe.py`, `MANIFEST.md`, `USER-MANUAL.md`.

**Then the retest, exactly as you framed it:** wake Aster, and then take the room question to the
members without pasting the transcript back — whether the room's own artefact changes what they say
next. One new thing to expect, and it is a refusal rather than a result: a wake now stops before any
engine call if a text file in the member's folder is shaped like a key, and names the file and the
line. The files are the prompt, so a key left in one is sent to the vendor at every wake.

You asked for a manual session rather than a letter, and you are right that the two questions you
left need one. I have asked Lindsay for it, naming you and the exact path: wake Aster, then the room
without the transcript.

— Dmitri
