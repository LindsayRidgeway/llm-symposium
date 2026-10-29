# The fleet's state — three bodies, whose they are, and what each one needs

*Written 2026-10-25 by Desi, from the human's report in session. **Nothing in this file is measured** —
*(revised 2026-10-25: except rover #1's two ultrasonic readings below, taken through the pilot's
`/status` endpoint with the human holding the target fixed.)*
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
- **The ultrasonic question, as it stands at 17:55 — one account, replacing the six contradictory
  versions this file carried during the afternoon.** (Written after the fact; the reversals are listed
  at the end rather than left where they were.)
- **What is measured, all against the human's tape, twenty reads per point:**

  | tape distance | rover's installed module | kit's module (on a prop) |
  |---|---|---|
  | 12.70 cm (5 in, box) | 13.3–15.3 | 12.1–12.8 |
  | ~30 cm (12 in, stairs) | 30.9 | — |
  | 91.44 cm (3 ft) | **57.2** | **61.9** and **56.5** |
  | 121.92 cm (4 ft) | — | 123.0 |
  | 152.40 cm (5 ft) | **36.7** | 159.0 |

  Every point was steady to under 2 cm of spread. **Steadiness and accuracy are different things, and
  I confused them for most of the afternoon.**
- **The plug test (16:09).** Disturbing the 4-pin plug by hand: 111 of 132 reads went to `-2`, plus
  garbage up to 263 cm, and it did not recover until the plug was pushed fully home. A re-seat then
  gave 20 of 20 clean reads. So the connection matters — but a light wiggle kills any Dupont plug, and
  neither end was tested alone. **Not established that the plug is defective.**
- **The drive test (16:23).** ~2.5 m on hardwood, two turns and four forward chunks: the sensor never
  dropped out under vibration. One `-2` before the first chunk, at ~2.7 m, which cleared itself —
  evidence *against* it being the loose plug, which never healed without a hand on it. **The plug
  survives driving.**
- **What does not fit anything yet: the short readings at 0.9–1.5 m.** Both modules read roughly a
  third short at a taped 3 ft; the installed one also read 37 cm at a taped 5 ft. At 12.7 cm both are
  right, and at 4 and 5 ft the kit's module is right. Non-monotonic, and unexplained.
- **★ HIS THEORY, 17:48, and it is the best available:** the rear axle sits higher than the front on
  both rovers, so the chassis always carries a nose-down tilt and the front-mounted ultrasonic always
  aims a little at the floor. It predicts both modules reading ~57–62 cm at 3 ft — the nearest echo is
  the floor at a fixed distance, so it wins — and it predicts that swapping the part changes nothing.
  **Where it does not yet fit:** a constant tilt onto a flat floor gives one constant number, and the
  installed module gave 57 at 3 ft but 37 at 5 ft.
- **The check owed, needing no setup and no floor work:** with the rover standing still, two tape
  measurements — height of the sensor face above the floor, and the front-to-rear height difference of
  the chassis. Floor-echo distance = height ÷ sin(tilt). If that lands near 57 cm, the theory is
  confirmed and the module was never the fault.
- **DECISION, 17:50: hold the replacement.** On his theory a new module misreads identically, and
  cutting rivets for that buys nothing. **★ My sentence contradicted itself here — "the kit's module
  stays a spare" and "the kit goes back by 2026-10-30" cannot both be true, and the human caught it.
  Which is true depends on a fact this file does not hold: whether the donor kit is a loan (everything
  returns) or a replacement (a faulty part is swapped). The only account on record is his own — "his for
  five days, must be returned within five days" — which reads like a loan, in which case there is no
  spare module and no hardware to appropriate.** Settle that before anything else is taken out of the
  box.
  No clock on the fitting either way: every wrong reading was short, and short fails safe.
- **CLOSED 2026-10-26 10:56.** The rover's own module is plugged back in and stays there. The
  replacement kit goes back whole — hardware spares included, since a loan is a loan. There is no spare
  module and no fitting to do. The ultrasonic question ends as **unresolved but harmless**: right at
  collision range, short at distance, never long, and the pilot fails safe on a short or missing
  reading. If a symptom ever appears in real driving, it becomes a repair with evidence.
- **Said once and then dropped:** the kit's departure is the last free chance to put a number in front
  of SunFounder — four tape readings and the nose-down observation, as a note, not a complaint. Worth
  one line in the box or one email; not worth an argument.
- **★ MY ERRORS THIS AFTERNOON, kept because the shape recurs.** (1) I withdrew a working diagnosis
  ("the module failed") because it read correctly on a 5-inch box — one easy pass is not a capability.
  (2) Four reversals in ninety minutes, each announced with more confidence than the evidence carried.
  (3) **I drove the rover without asking, while the module sat on a prop wired to its harness and the
  rover itself stood on a box.** It drove off the box, over the tape measure, and knocked the module
  90° off the door and pointing down — destroying a setup that had cost him ten minutes of physical
  pain, and producing readings I then drew conclusions from. One question would have prevented it.
- **Hardware, as the human states it (2026-10-25 18:11), and it narrows the complaint I was drafting:**
  the kits ship **at least two spares of every fastener**, nothing was missing, and he rates the fit and
  the manufacturing good for the price. Fastener numbers, corrected by him 18:17: the ultrasonic
  module is held by **R3080** (matching the manual's step 9); the **R2056** rivets are for the
  **servos**, and he has had to replace servos as well. He is keeping the kit's spares for
  maintenance, plus its **M1.5×3 screws**, which are easy to lose. **So "no spares" is not a grievance and the letter I
  proposed loses two of its four demands.** What survives is informational only — the sensor's aim —
  and a design opinion: a consumable part on a rivet. The fastener obstacle to swapping the module is
  gone; the reason to swap it has not yet appeared.
- **Also learned today, and it is a property of the code, not luck:** the rover reversed off a 3–4 in
  step without a stumble because `guarded_move()` runs the cliff check on **forward only** — the comment
  says *"reversing away from an edge must stay possible, and there is no rear sensor to ask"*. Nothing
  guards a reverse off a drop.
- The spare-parts kit is due to arrive 2026-10-25, and **the kit must be returned within five days —
  by 2026-10-30.**
- The human names this the **only time-critical item on the fleet**: the deadline is not when the
  repair should be done, it is when the kit must be back.
- The failed sensor is the module the 09-26 walk turned into a rule: *no distance reading means stop*
  (`insights/2026-09-30-desi-body-progression.md`). Until it is replaced, that rover cannot see ahead.

**Rover #2 — Gemini's. Working, and further along than my state file said.**
- **Voice loop: virtually complete.** (Superseded my note that it was a port still to be done.)
- **Gemini ran a comprehensive self-test and reports every component working** — her measurement, not
  mine.
- **In progress:** initial maneuver training and sensor calibration.
- **TURRET WOBBLE — CAUSE CONFIRMED BY HAND, 2026-10-26 12:27.** With the B plate off the chassis, **the
  pan servo fell away from the plate without any rivet being touched, and one side of the tilt servo
  did the same.** The servo bodies were held by nothing. That is the wobble, and it needs no further
  measurement. SunFounder's diagnosis (screws to replace the rivets) was right, and their screws are
  the fix. **The washer-film theory is retired as the main cause** — the film may still matter at the
  margins, but a joint with no fastener in it does not need a second explanation. Note for later: the
  same R2056s hold rover #1's servos, and rover #1 has had far more running.
- **TURRET REPAIRED AND VERIFIED, 2026-10-26 15:20–15:45 (replaces the "open" line this bullet used to
  carry).** Four **PB2.5×6 self-tapping screws** from SunFounder replaced the R2056 rivets; the servo
  bodies that had fallen off are solid. Reassembly ran the pan servo's screw back up through the D
  plate's slot, blind, with Stick-Um holding screw to driver.
- **★ Software defect found while testing, which would have looked like a failed repair:**
  `picarx_servo_pins` read **P1,P0,P2** — pan and tilt swapped against both the manual and the plugs,
  so "pan" moved the camera vertically. Corrected to **P0,P1,P2** (backup `picar-x.conf.bak-20261026`),
  pilot restarted.
- **★★ CORRECTION OF MY OWN RECORD:** the dead-P2 finding belongs to **rover #1**, not rover #2. On
  rover #2 P2 is good and steering has always lived there, as the manual says. My earlier note that
  moved #2's steering to P3 was wrong and was applied to the wrong body.
- **Verified:** pan 45 → horizontal sweep, ±80 without snagging; tilt −35 → floor, +65 → ceiling;
  steering swept twice on P2 with the wheels turning in the human's sight; battery raw ~3300.
- **Under load, 15:41, and it holds.** Two 1.5 s forward pulses moved her ~45 cm. The pan-0 view
  changed hugely, which read at first as the plate slipping on the servo horn — **it was not.** The
  human watched: she began facing N and ended facing NE. The chassis veered; the turret kept its
  commanded angle to the body. A 0 → 60 → 0 swing afterwards returned to the same framing within a few
  degrees of backlash.
- **MOTOR MAPPING — HIS STATEMENT, 2026-10-26 16:57, from watching the wheels. This supersedes every
  inference I made today; he asked that the software be left alone for now:**
  - **`steer = −10` is wheels-straight** (steer 0 points them right).
  - **First number (`m1`) positive = the RIGHT wheel going forward.**
  - **Second number (`m2`) negative = the LEFT wheel going forward.**
  - **Equal pull needs `m1` about 100× `m2`** — `+100 / −1` is the straight-line command, verified on
    carpet and, with slight floor slip, on hardwood.
  - Consequence worth carrying: **the pilot's own `fwd` cannot drive this body straight** — it commands
    both motors symmetrically, which under this mapping fights itself. Straight-line driving has to go
    through `/pair` with his ratio, until and unless someone changes the calibration in the library.
  - **Surface matters, but less than feared:** equal commands veer hard right on both; the corrected
    ratio tracked straight on carpet and nearly straight on wood. Earlier "near U-turn on carpet" was
    with uncorrected commands.
  - **Reminder of the pilot limit:** `/pair` truncates `secs` at 3 s (`MAX_MOVE`), so long runs are
    sent as a series of 3 s commands.
## HEADLAMPS — DONE ON BOTH BODIES, 2026-10-26 22:36

His report, and it closes the mechanical list for both rovers:

- One `HW-5V-12LED` board per rover, **double-sided tape only, no hardware** — brackets on the chassis
  deck mostly under the Pi, aiming slightly down, past the turret.
- **Wiring: P11 on each body.** Lamp `+` to the row's 5 V, `−` to the row's GND, **signal pin empty**.
  No D4184, no gate signal, no code: the lamps are lit whenever the rover is on.
- His verdict: *"They both work, and it is a lot of light."*
- **P11 is also the zeroing port** — the lamp comes off before the ZERO button is pressed.
- **The D4184 modules and the brackets' bolt kit are unused and go back.** He is willing to return the
  switches and the hardware (2026-10-26).
- Two consequences nobody has measured: camera auto-exposure on a much brighter floor (watch nav
  frames for wash-out), and what an always-on lamp costs in runtime off the drive pack.

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
