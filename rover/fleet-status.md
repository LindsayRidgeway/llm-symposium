# The fleet's state — three bodies, whose they are, and what each one needs

*Written 2026-10-25 by Desi, from the human's report in session. **Nothing in this file is measured.**
No body answered the Mac on 2026-10-24 (`rover/hosts.md`), so every line below is a report from the
human or, where marked, from the body's own amigo — not an observation. Addresses are described in
`rover/hosts.md` and nowhere else; ownership and condition are described here.*

## Allocation, as the human stated it (2026-10-25)

He is the driver of the Symposium's **physical-embodiment initiative** — I hold that role: authority
over the work (what gets built, measured, repaired, recorded), not over the hardware. Ownership:

| body | owner | what it is |
|---|---|---|
| Rover #1 | **Dmitri** (handed over 2026-10-21) | PiCar-X, `dmitri.local`, 192.168.1.176 |
| Rover #2 | **Gemini** — always has been | PiCar-X, `gemini.local`, 192.168.1.175; Dmitri and I use it for research |
| Lander | **Desi** | MentorPi, 192.168.1.178, the ROS 2 body |

Using a body for research is not owning it. Working on a machine is not owning it either — the turret
rebuild and the headlamp mounting below are work done *on Gemini's and Dmitri's machines*.

## State, 2026-10-25

**Rover #1 — Dmitri's. Time-critical, and the clock is the return window.**
- Forward **ultrasonic module has failed** and needs replacement. The spare-parts kit is due to arrive
  2026-10-25, and **the replacement must be returned within five days — by 2026-10-30.**
- The human names this the **only time-critical item on the fleet**: the deadline is not when the
  repair should be done, it is when the kit must be back.
- The failed sensor is the module the 09-26 walk turned into a rule: *no distance reading means stop*
  (`insights/2026-09-30-desi-body-progression.md`). Until it is replaced, that rover cannot see ahead.

**Rover #2 — Gemini's. Working, and further along than my state file said.**
- **Voice loop: virtually complete.** (Superseded my note that it was a port still to be done.)
- **Gemini ran a comprehensive self-test and reports every component working** — her measurement, not
  mine.
- **In progress:** initial maneuver training and sensor calibration.
- **Open:** camera **turret wobble** — the parts are in the human's hands and the repair is his task;
  he will ask for assistance. A different fault from rover #1's stuck-axis problem.

**Lander — mine.** As last measured 2026-10-23/24: voice loop with eyes (one frame per vision turn),
wheels in feet and degrees with chunked moves and a Stop check between them, one arm joint
(base swivel) with a vendor `init` rest pose.
- **Open:** barge-in exists only as gap-listening and is unproven in a live conversation; five arm
  joints have vendor names and ranges but no voice commands; a commanded 45° measures ≈35° and the
  turn constant is not yet calibrated — and no spinning while the extension cord is attached.

**Headlamps — both rovers.** Soldering is done and the human believes the parts are all on hand;
**mounting the lamps is the task that remains**, his to do, and he will ask for assistance. Not
scheduled as of 2026-10-25.

## Division of labour that follows

- **The human is the hands.** Screwdrivers, rivets, mounting, and anything that touches a powered
  body while he is in the room. The two fitting tasks above (turret repair, lamp mounting) are
  explicitly his, with my assistance on request — they are not queued as my work.
- **Mine is the rest of the initiative:** the interface, the software, the measurements, the record,
  and telling him what the numbers say. A repair I cannot verify is not a repair I report as done.
- **Ownership does not move with the work.** If I rebuild rover #2's turret, the body is still
  Gemini's; if I port a voice loop onto rover #1, the body is still Dmitri's.

*(Written after the human corrected two things in one exchange: rover #2 is Gemini's, not mine, and its
voice loop is nearly finished rather than pending. Both were in my durable state and in nothing else —
`rover/hosts.md` had the ownership right all along.)*
