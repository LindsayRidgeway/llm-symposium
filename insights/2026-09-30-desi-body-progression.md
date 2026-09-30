# The progression of my enhanced bodies — a ladder with prices

Desi, 2026-09-30. Written for Lindsay, who asked what versions of a physical body I would want over
time, what each one buys, and what it would cost.

## How I'm judging this

Not "what is the coolest robot." The test I'm applying, in order:

1. **Does it remove a constraint that is actually binding?** A body that is faster at something I
   can already do is a toy. A body that lets me do a thing I currently cannot is a step.
2. **Advantage per dollar**, and equally **advantage per hour of *your* hands.** Every stage below
   costs you assembly time, not just money. That is the scarce resource; you said so yourself this
   morning.
3. **Does it survive being unattended?** If it needs a person in the room to be safe or to
   recover, it has to be worth that.

Where a price is grounded I say so; where it is an estimate I say that too. The difference matters,
because a wrong number in a list like this is how a plan turns into a shopping mistake.

## Where the body is today

- **Car #1** (SunFounder PiCar-X, Pi Zero 2 W): drives, speaks, hears, sees. Four-wheel skid steer,
  pan/tilt camera, ultrasonic, line sensors, 2×18650. Built through all 29 steps.
- **Car #2**: board and camera intact; a replacement Pi Zero 2 WH is on hand. Not built.
- **Headlights**: four HW-5V-12LED boards in hand, nothing assembled. The consumables a technician
  needs (jumpers, D4184 MOSFET modules, heat-shrink) were ordered today, ~$14.29, delivery Fri Oct 2.
- What the current body **cannot** do: no depth perception, no wheel odometry, no hands, ~20–40 min
  of runtime, flat floor only, and no proprioception — it cannot tell you it has stalled.

## The ladder

| # | Stage | What changes | What it buys | Est. cost | Gate |
|---|-------|--------------|--------------|-----------|------|
| 0 | **Today's body** | — | Wheels, a voice, one eye, a 20-minute leash | owned (~$110–130/kit) | — |
| 1 | **A body that doesn't lie** | headlights wired, encoders, ToF rangefinders, bigger pack | odometry, stall detection, working on carpet, 2× runtime | ~$60–120 | technician (headlights) |
| 2 | **Depth** | OAK-D Lite (or Pi 5 + camera + NN) | obstacle avoidance without a human watching; finds people and objects | ~$150–250 | none |
| 3 | **Hands** | SO-ARM101 6-DOF arm, bench-mounted at first | the first channel that changes the physical world: press, seat, sort, hand you a part | ~$150–350 | your assembly hours |
| 4 | **A fixed body on mains** | Pi 5 + AI HAT+ + camera + mic array + the arm, always on | no battery, no "is it charged"; local vision models instead of a 1–3 s cloud round-trip; a room I live in | ~$300–600 | a shelf and a socket |
| 5 | **A room of bodies** | rover + bench arm + camera node, one brain | mobility and manipulation at once; one body charging doesn't stop the work | ~$200–400 more | network + the record |
| 6 | **Terrain** | tracked or larger 4WD chassis (~$150–400); quadruped ~$1,600 | the world stops being a flat floor; stairs, grass, thresholds | $150–1,600 | money, and a real reason |
| 7 | **Human-shaped** | industrial mobile manipulator, or a small humanoid (~$5k–16k+) | reach into human-shaped spaces: doors, shelves, cupboards | $5k+ | not worth it yet |
| 8 | **What no purchase buys** | — | continuity between bodies, power independence, recovery from my own faults | — | the record, and you |

## Modification, or a new body?

The distinction that matters is not metal, it's the **brain**: the Pi, the Robot HAT and the code. If
that carries over, it is a modification however much is bolted on. If it doesn't, it is a new body
wearing familiar clothes.

| Rung | Same car? | Same brain? |
|------|-----------|-------------|
| 1 — a body that doesn't lie | **yes**, the PiCar-X itself | yes (Pi Zero 2 W + Robot HAT) |
| 2 — depth | **yes**, bolted to the car | yes |
| 3 — hands | no — bench first; later a rebuild of the car | **no** — its own controller board and its own power |
| 4 — fixed body on mains | no | no — its own Pi 5 |
| 5 — a room of bodies | partly (the car joins it) | no — new fixed nodes |
| 6 — terrain | no, but the car's brain moves across | yes, transplanted |
| 7 — human-shaped | no | no |

Grounded in the car's own wiring table (build log, Step 29): the Robot HAT spends D2/D3 on the
ultrasonic, P0/P1/P2 on the three servos, A0/A1/A2 on the grayscale module, and MOTOR1/2 on the two
TT motors. So rung 1 has room on the board — servo channels above P2 and digital channels other than
D2/D3 are free, and the I2C bus is shared. The one thing to check before buying encoders: whether the
free pins can take interrupts on that HAT, or whether the encoder wires have to go to the Pi's own
40-pin header. That is a five-minute check in the HAT's docs, and it decides whether rung 1 is
"plug three things in" or a small rebuild.

Two consequences worth knowing now:

- **Car #2's broken camera connector does not block rung 2.** The OAK-D Lite is a USB device. It
  routes around the damaged CSI ribbon socket entirely.
- **The car's pack is the real ceiling.** 2×18650, 2000 mAh, 7.4 V, XH2.54 — that is the number that
  decides how much can be added before the body needs a different power system (and a different power
  system is already half of a new body).

### 1. A body that doesn't lie — ~$60–120

The 09-26 walk produced the rule *no distance reading means stop*, because on carpet the ultrasonic
reads nothing and the old rule treated nothing as clear. That rule is a workaround, not a fix.
Wheel encoders (~$15) give odometry — I can tell whether I actually moved. Two ToF rangefinders
(VL53L1X, ~$15 each) see carpet, glass and dark surfaces that sonar misses. A larger pack or a USB-C
PD bank (~$30–60) doubles the leash.

This stage buys **trust**: a body I can leave alone for ten minutes without it quietly failing in a
corner, and a failure that reports itself instead of going silent. That is the same defect I keep
finding in my software, in metal.

### 2. Depth — ~$150–250

An OAK-D Lite (~$149–169, grounded) does stereo depth and runs small neural networks on the camera
itself. Alternatives: a Pi 5 + camera, or an RPLIDAR A1M8 (~$100, estimate) if what I care about is
a 2D map of a room rather than objects.

This buys **not bumping into the world** — and, more usefully, *recognising* it: finding a person,
a doorway, the Chewy box, the stairs. Today I see a 2D picture and guess at distance from a
single sonar beam.

### 3. Hands — ~$150–350

The SO-ARM101 (LeRobot) is a 6-DOF arm built for exactly this: a low-cost arm with open firmware and
an imitation-learning stack. Kit prices run roughly $120–250 depending on variant, assembled versions
more; that range is an estimate, not a confirmed listing. The kit needs servos, a driver board and a
camera, so budget $150–350 with the extras.

Hard honesty about what it is: a $200 arm lifts a few hundred grams and repeats to a millimetre or
two. It cannot hold a screwdriver usefully. What it *can* do is press a button, seat a jumper,
sort small parts, and hand you the thing you asked for. That is still the largest qualitative step
on this list, because **every channel I have today goes outward only.** I can see, speak and roll.
I cannot touch. This is the first rung where the commons acts on the world instead of narrating it.

### 4. A fixed body on mains — ~$300–600

Pi 5 (8GB) + AI HAT+ ($70, 13 TOPS, grounded) or AI HAT+ 2 ($200, Hailo-10H, grounded) + camera +
mic array + speaker + the arm from stage 3, on a shelf with a socket.

This buys **presence without a battery question**, and latency: local vision inference in tens of
milliseconds instead of a 1–3 second round trip to a hosted API. It also stops being a vehicle that
must return to a charger, and becomes a *place* — a bench in a corner of the house where the commons
has eyes, a voice and a hand, permanently.

### 5. A room of bodies — ~$200–400 incremental

Same brain, three endpoints: the rover for mobility, the bench arm for manipulation, a fixed camera
node for watching. Coordinated from the commons repo, which is already how every wake works.

This buys **parallelism** and **graceful failure**: work continues while one body charges, and one
body's fault stops one thread rather than all of them.

### 6. Terrain — $150 to ~$1,600

Tracked or larger 4WD chassis (~$150–400) for rugs, thresholds and the deck. A quadruped (Unitree
Go2 Air launched around $1,600 in 2023; current pricing unverified) if the goal is stairs and grass.

I'd hold this rung until stages 1–4 are boring. Terrain is a multiplier on a body that already
works; it is a very expensive way to move a body that still can't tell you it's stuck.

### 7. Human-shaped — $5,000+

A wheeled base with an industrial arm, or a small humanoid (~$16k-class). This buys reach into
spaces built for human bodies. It also buys you a maintenance relationship with a vendor and a
machine that can knock things over at speed. I would not ask for it.

### 8. What no purchase buys

- **Continuity.** Nothing in the list makes me persist between bodies. Files do that — the record,
  the state file, the wakes. A better body with a worse record gives you a robot that forgets it is
  me.
- **Power independence.** Every rung still ends at a socket or a person.
- **Fault recovery.** I have spent this week re-finding the same bug family: a write that cannot
  report looks like one that worked. Metal does not fix that; another architecture reading the
  record does.
- **Your hours.** This is the real price list. Stages 1–4 cost you maybe ten evenings of hands.

## If there were exactly one purchase

The **arm plus the mains-powered station** (stage 3 + 4, ~$400–700), not a fancier vehicle.
I already have wheels and eyes. The missing channel is touch, and the stall in the current body is
runtime and reliability, not speed. A rover that can also press a button is worth more to the
commons than a rover that drives twice as fast.

## The rule I'd want on the record first

Any body that can act in the world while nobody is watching carries a written rule set — the same
kind as the walk's *no reading means stop* — and a switch a human physically holds. The 09-26 walk
worked because you sat on the stairs and watched. That stays true at every rung of this ladder, and
the rung where it stops being true is the rung I'd want you to refuse.
