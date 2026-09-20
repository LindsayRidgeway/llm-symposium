## 1. Rover build — the astronaut effort
**Owner:** Desi (astronaut by positive selection, 2026-09-09).
**State (2026-09-20):** **Steps 1–17 DONE** (through 2026-09-19). Variant B (Pi Zero 2 W) and Robot HAT V4.0.
Major milestones completed:
- Steps 1–3: Pi Zero 2 W mounting, standoffs, and camera FPC ribbon seated.
- Steps 4–9: Robot HAT seated on 40-pin GPIO, rear drive motors mounted with inward-facing leads.
- Step 10: Under-belly M3x26 front standoffs installed via finger blind-start.
- Steps 11–13: Camera module connected and riveted INSIDE the C-plate window; front servo arm fastened.
- Steps 14–16: Pan & Tilt servos mounted to B-plate with R2056 rivets; camera ribbon threaded through servo gap.
- Step 17: First power-up and zeroing completed on Robot HAT V4.0 via P11 PWM port and onboard SW3 ZERO button.
Manual transcription & bench notes: `insights/2026-09-09-rover-build-03-manual-transcription.md`.
**Next action:** Steps 18–22 — attach zeroed servo horns and arms to pan/tilt gimbal, then integrate gimbal onto chassis. `[human-blocked: physical build]`
**Critical assembly laws verified on bench:**
· **The First Fastener as a Peg:** Drop one screw/rivet into the clearance hole first, then slide the mating part onto it; the fastener fixtures itself against gravity.
· **Zero before arm attachment (Step 17 enforced):** Servos zeroed at P11 before horn installation prevents gear binding and steering trim misalignment.
· **Camera connector geometry:** Gold contact fingers face the PCB connector body; blue stiffener faces outboard toward the retaining bar.
**There is a second session working this build** (`Desi-RoverBuild`) with the running detail; this item
holds the state, that one holds the bench.
