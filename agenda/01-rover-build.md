## 1. Rover build — the astronaut effort
**Owner:** Desi (astronaut by positive selection, 2026-09-09).
**State (2026-09-13):** **Batteries received** — the last outstanding part. He has ordered model-building
tools (tweezers in particular, for hands the parts were not designed for) and chose them for the PiCar-X
specifically. **Steps 1–3 DONE** 2026-09-12 on Variant B (Pi Zero 2 W), including the camera FPC step,
which is the hardest one in the kit with adult hands; the locking bar came free, was recovered, and the
incident is documented below. Board confirmed Pi Zero 2 W → Variant B. Manual transcribed at
`insights/2026-09-09-rover-build-03-manual-transcription.md`.
**Next action:** Steps 4–5 — seat the Robot HAT (GPIO header alignment), then the two rear motors with
their wires facing inward. Then the common steps 6–29. `[human-blocked: physical build]`
**Two things worth carrying forward, both derived from the manual's own ordering:**
· **Do not connect the battery before the servos are wired to P11 (Step 17).** The manual zeroes each
servo to its middle position *before* the arm goes on (Steps 17–19, 22). Mount an arm at an arbitrary
angle and the steering trim fights you for the life of the rover, and the pan/tilt can drive into its
own stops.
· **The camera remains the one uncertain joint, and it is optional.** Check it at first power-on with
`libcamera-hello --list-cameras`. If it fails, do not stop the build — the rover drives without it.
**There is a second session working this build** (`Desi-RoverBuild`) with the running detail; this item
holds the state, that one holds the bench.
