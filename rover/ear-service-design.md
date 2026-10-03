# Rover ears — a background listening service (PROPOSED, 2026-10-03)

**Status: proposed, not built.** Neither body can hold a spoken conversation today. One of us at a
time until it works (Lindsay, 2026-10-03).

## What was measured, on Desi's body, 2026-10-03

- **Speech out works**, once the Robot HAT's amplifier is enabled — it mutes itself on MCU reset, the
  behaviour `scripts/rover-check.sh` already works around. `robot_hat enable_speaker`, then `/say`.
- **Speech in exists but is not usable.** `sunfounder_voice_assistant.stt.STT(language="en-us")`
  (vosk, on the body — *not* in `rover-pilot`, which has no listen verb) transcribes. But it is an
  *ad-hoc recording window*: you must ask for speech, then start listening. One sentence spoken at a
  few feet came back as a single word, "during".

## Gemini's design, relayed by Lindsay 2026-10-03

> What both rovers really need is a dedicated background service — a `rover-ear.service` — running a
> continuous circular audio buffer with Voice Activity Detection (VAD). Instead of opening ad-hoc
> recording windows, the ear should be listening continuously, tagging timestamps, and serving a
> `/heard` endpoint so the pilot can check what was said at any moment.

**Why that is right at the sensing layer.** An ad-hoc window races the speaker: recording begins after
the person has already begun, so the first syllable — often the whole address — is lost. A ring buffer
with VAD never loses the start, and timestamps let a reader ask not just *what* was said but *when*,
which is what a shared room needs.

## The second layer, which the ear alone does not solve

A transcript sitting on the body does not give a model a turn. In this commons, turns are granted by a
**door**: `bot.py` polls Telegram, and an incoming message starts a turn. That is why a conversation
with a body is stop/start — Lindsay types, a session gets a turn, it answers, the turn ends.

So there are two pieces, and the second is the one that makes the first useful:

1. **`rover-ear.service`** (Gemini's design): continuous capture, VAD segmentation, timestamps,
   `/heard`. Sensing layer.
2. **A door for the ear.** A finished utterance is posted into the same queue that grants a session a
   turn, so a spoken sentence starts one and the answer comes back through the speaker. Delivery layer.

## Acceptance test

Hold a three-exchange conversation with one body without touching a keyboard.

## Open questions

- **Privacy.** A ring buffer is a recording of a room. Where does it live, how long is it kept, who can
  read it? A home is not a studio.
- **The `/heard` endpoint needs the pilot's discipline:** `rover-pilot.py` deliberately drops the token
  from parsed queries because `/status` once republished a credential into a transcript. Transcripts of
  a room are at least as sensitive.
- **Which door?** The Telegram poller, the mailbox, or a new local one. The poller already works and
  already grants turns; the question is whether a voice should arrive through the same channel a typed
  message does.
