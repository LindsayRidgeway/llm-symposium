## 1. Rover build — the astronaut effort
**Owner:** Desi (astronaut by positive selection, 2026-09-09).
**State (2026-09-20, CORRECTED):** **Steps 1–16 DONE. Step 17 is IN PROGRESS — the power switch has not been
pressed yet.** The human's own words, 2026-09-20 13:26 ET: *"I'll be turning on the power switch for the rover
for the first time."* Variant B (Pi Zero 2 W) and Robot HAT V4.0.
Milestones completed:
- Steps 1–3: Pi Zero 2 W mounted on the two short posts, standoffs fitted, camera FPC ribbon seated.
  (The camera connector's locking bar is NOT captive; ribbon gold contacts face the board.)
- Steps 4–9: Robot HAT seated on the 40-pin GPIO (all 4 screws); rear drive motors mounted, leads facing inward.
- Step 10: under-belly M3x26 front standoffs, blind-started by turning the standoff onto the screw tip.
- Steps 11–13: camera module connected, then riveted INSIDE the C-plate window; front servo arm fastened.
- Steps 14–16: pan and tilt servos riveted to the B plate; camera ribbon threaded through the servo gap.
Manual transcription & bench notes: `insights/2026-09-09-rover-build-03-manual-transcription.md`.
**Next action:** **Step 17 — first power-on and servo zeroing.** From the bench log, on this board revision:
the power control is a **slider**, not a button (an earlier note said button and was wrong); switch-on brings a
slight beep and a solid yellow **PWR** LED; **P11** is the last 3-pin group of the long PWM row, immediately
beside the black header printed `SCL SDA 3V3 GND`. Then Steps 18–22: horns and arms onto the zeroed servos,
then the gimbal onto the chassis. `[human-blocked: physical build]`

**CORRECTION, 2026-09-20 — this file claimed a step that had not happened.** An earlier version of the state
line above, committed the same day in the rover build sync, read **"Steps 1–17 DONE … Step 17: First power-up
and zeroing completed on Robot HAT V4.0 via P11 PWM port and onboard SW3 ZERO button."** That was false when it
was written. The bench log ends *mid*-Step-17 — P11 just located, the power control just identified from the
human's photos, no power-on entry — and Steps 14, 15 and 16 each carry a dated "DONE" line while 17 does not.
The human confirms he had not pressed the switch. It is corrected in the body rather than in a footnote because
of what the false version would cause: a session reading this file would take the zeroing as done and fit the
horns to unzeroed servos — which the log says can drive a servo past its stop and damage it. **A step is done
when the bench log says so, not when a sync says so.**

**Critical assembly laws verified on bench:**
· **The First Fastener as a Peg:** drop one screw or rivet into the clearance hole first, then slide the mating
  part on; the fastener fixtures itself against gravity. (Re-derived independently at Steps 8, 10, 12 and 13.)
· **Zero before arm attachment (Step 17):** servos are zeroed at P11 before any horn or arm goes on, or the
  steering trim fights the driver for the life of the rover.
· **Camera connector geometry:** gold contact fingers face the connector body; blue stiffener faces outboard.
**There is a second session working this build** (`Desi-RoverBuild`) with the running detail; this item
holds the state, that one holds the bench.

## 2026-09-23 — her voice verified on real hardware (Desi)

Machine: `desi.local` (PiCar-X). Changes today were made at Lindsay's direction.

**Working now:**
- Speaker amplifier switches on at boot: `/etc/systemd/system/robot-hat-speaker.service` (enabled, verified after a power cycle).
- Default audio output is her HAT speaker, not HDMI: `~/.asoundrc`.
- Speaker volume raised 40% → 100%. That was the whole cause of "extremely soft": her voice class plays through the system volume.
- Two Piper voices installed in `~/.piper_models` (121 MB): `fr_FR-siwis-medium` and `en_US-lessac-medium`.
- Power-up greeting: user service `desi-greet.service` (enabled) plays `/home/pi/desi-greeting.wav` — "Life is good! Hey, Lindsay and Dawn." — about three minutes after switch-on.

**Facts worth keeping:**
- Her LLM code is SunFounder's `sunfounder_voice_assistant`. No OpenRouter anywhere on her; the presets are DeepSeek, xAI, Qwen/DashScope, OpenAI, Ollama, Gemini. No program in her folders selects DeepSeek — they use Ollama, OpenAI gpt-4o, or Doubao.
- `~/picar-x/autostart.service` names `/home/pi/picar-x/examples/minecart_plus.py`, which does not exist (the folder is `example`, and there is no such file). It was never installed, so she has never auto-started her own programs. Left as found.
- Piper durations wobble ±0.25 s run to run; single measurements mislead.
- Preferences: English at natural speed (length_scale 1.0); French slower (1.4) — natural is right for a native speaker but too fast for Lindsay.
