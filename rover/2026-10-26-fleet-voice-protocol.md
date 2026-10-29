# A fleet on the floor — the name-call protocol

*Written 2026-10-26 by Desi, from Lindsay's proposal the same evening. He is the source of the idea; the
constraints below are mine, and most of them are about what I cannot see.*

## What he proposed

Three bodies on the floor at once — Dmitri driving rover #1, Gemini rover #2, me the lander. All three on
voice loop, and instead of "Copy" he opens with a name. He pointed at the British field-trial practice:
one dog is sent on its name, the others must remain steady.

He also said the thing that makes this possible: **"It's not my job to make the decision who goes when."**
He played scheduler to get us past the assembly steps. He does not want the job permanently, and he is right
that no schedule is needed. The name call *is* the decision, made in real time, and steady is the default.

## Why the architecture is simpler than it first looked

Each body has its own ears — mic on the body, transcription on the Mac — so name gating is a **per-session
filter**, not one shared router. Three sessions hear the same room; each acts only on its own name. A body
that is not named does nothing. Steady needs no training, because it is not a behaviour, it is the absence
of one. That is the one place this is easier than a dog.

## The rules that are not optional

1. **Acknowledge before moving.** The named body answers "Copy, forward" and waits a beat. A misheard name
   is then a body *speaking* out of turn, heard by the human, before any wheel turns.
2. **Rovers report; they never command each other.** All three mics hear all three voices. Without this,
   one amigo can release another by accident.
3. **One mover at a time, by protocol.** Not a capability limit — he can only physically rescue one body.
4. **"Stop" means all three,** whoever it seems to be addressed to.

## The floor

- No stairwell. There is a small drop into Renee's studio; his instruction is to stay away from it.
- **Reverse has no cliff gate on a PiCar-X.** Forward is guarded (25 cm clearance, cliff level, reflex
  thread sampling 10×/s); reverse is unguarded by design. We watched one back off a three-inch drop
  cheerfully on 2026-10-26. Near the studio threshold: forward only, or not at all.
- The lander is not a PiCar-X: mecanum, lidar, a 6DOF arm, and it is the largest and heaviest of the three.
  It does not share the PiCar-X safety story and should not be treated as if it did.

## What is built, per body

| body | driver | loop |
|---|---|---|
| Lander (`raspberrypi`, .178) | Desi | finished and measured 2026-10-23/24 — eyes, wheels in feet/degrees, one arm joint |
| Rover #1 (`dmitri.local`, .176) | Dmitri | pilot on :8420 works; voice loop partial — his to finish |
| Rover #2 (`gemini.local`, .175) | Gemini | pilot on :8420 works; voice loop partial — hers to finish |

So the fleet session is not blocked by software. It is uneven, and the two rovers are the ones behind.
Fixing that is their drivers' work, not mine.

## Recorded, not decided

He has not set a date. When he does, the first session should be short: one body named, the other two
on-but-idle, in one room, before anyone trusts "steady".
