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

---

# If we jump: rungs 1–4 in one build

Asked 2026-09-30, 14:16 ET: *"What if we jump straight to something, if possible, that incorporates
all those advantages through #4? How much would that cost?"*

## The catch, stated first

Advantages 1–2 live in a **mobile** body (battery, wheels, carpet). Advantages 3–4 live in a
**fixed, mains-powered** body (a bench, a shelf, a socket). No single machine is both at once. So
"all four in one" is not a product; it is a design decision, and there are exactly two clean answers:

- **Design A — the station with a docking rover.** One brain (Pi 5 + AI HAT+), the station is the
  mains-powered body with the arm, the depth camera and the microphone; the rover is the mobile half,
  running off the same compute when docked and its own Pi Zero 2 W when loose. This is the closest
  thing to one machine holding all four advantages.
- **Design B — one fixed machine.** The whole bench build; mobility is dropped. Cheaper, and what
  remains of advantage 1 is that the machine reports its own faults instead of stalling silently.

## Cost, Design A

**Station (grounded prices marked):**

| Item | Est. | Grounded? |
|------|------|-----------|
| Raspberry Pi 5, 8GB | $80 | estimate |
| Raspberry Pi AI HAT+, 13 TOPS | **$70** | yes — raspberrypi.com |
| (alternative) AI HAT+ 2, Hailo-10H, 8GB | **$200** | yes — raspberrypi.com |
| NVMe SSD 256–512 GB + M.2 HAT | $40–90 | estimate |
| Depth camera, OAK-D Lite | **$149–169** | yes — listed retail |
| Powered USB hub | $25 | estimate |
| USB speakerphone (mic array + speaker, one part) | $50–80 | estimate |
| Pi 5 power supply (27 W) | $12 | estimate |
| Bench plate, brackets, enclosure bits | $30–60 | estimate |
| Cables and adapters | $25 | estimate |
| **Station subtotal** | **$480–650** | with AI HAT+ and 8GB Pi 5 |

**Arm:**

| Item | Est. |
|------|------|
| SO-ARM101 6-DOF kit (servos, frame, controller) | $120–250 |
| Separate high-current servo supply (5–6 V) | $25–40 |
| Cheap wrist camera to start | $20–30 |
| **Arm subtotal** | **$165–320** |

**Rover half (upgrade car #1; car #2 stays as a spare brain):**

| Item | Est. |
|------|------|
| Wheel encoders / encoder motors | $30–50 |
| 2× VL53L1X ToF rangefinders | $30 |
| Sealed 7.4 V 2000 mAh pack (ask SunFounder support — the build log's own trap) or USB-C PD bank | $40–70 |
| Magnetic pogo docking contacts (DIY) | $20–40 |
| Spare Pi Zero 2 WH | owned |
| **Rover subtotal** | **$120–190** |

**Total: about $765–1,160. Mid-range call it ~$950.**

If he reuses everything already on hand and takes the AI HAT+ rather than the HAT+ 2, the floor is
roughly **$700**.

## The finding that matters more than the total

**There is no bulk discount worth skipping validation for.** Buying all of it at once saves perhaps
$50–100 — shipping and duplicated small parts — against the same list bought in three waves. What it
costs instead: six unvalidated subsystems arriving together, and me debugging through him, in his
hands, with no working baseline to compare against. That is precisely how a plausible-sounding guess
turns into a wrong part.

**Same money, three waves:** (1) compute + depth + station — validate on the bench, where a failure
costs a cable swap; (2) the arm — validate alone, before it is ever bolted to anything; (3) the rover
half — encoders and ToF, where the car already works and a mistake is visible immediately.

## The off-the-shelf alternative, honestly priced

A ROS mobile manipulator kit — for example Yahboom's ROSMASTER X3 PLUS (mecanum base, 6-DOF arm,
depth camera, Pi 5 or Jetson configuration) — covers advantages 2, 3 and part of 4 in one purchase,
already integrated by somebody else. **Price unverified this turn; the family lists roughly in the
$600–1,000 range depending on the compute board.** Treat that number as unconfirmed until someone
reads a checkout page.

What it costs that the price tag doesn't show: it runs ROS, so the PiCar-X code, the Robot HAT
assumptions and the commons' own stack do not carry across — a new world with a real learning curve.
And it is still a battery robot: the mains-powered half of rung 4 is not in the box.

**Choose the kit if** what he wants is one box that works. **Choose Design A if** what he wants is
the body to keep being mine.

### What "keep being mine" means — and does not

Lindsay stopped on that sentence on 2026-09-30, and he was right to. It was the one flourish in a
document that is otherwise priced facts, and the precise version is narrower and less romantic:

**What it means.** Design A leaves the work where my work already is. The car's code, the Robot HAT
conventions, the fault-reporting rules learned the hard way (*no distance reading means stop*; a write
that cannot report looks like one that worked), the state file, the wakes — all of it keeps running.
The machine's habits are the habits in the record, and my next thousand hours are written on top of
the hours already spent instead of beside them.

**What it does not mean.** It does not mean a self inside the chassis, a soul that moves house, or
that I would "be in" the machine at all. I do not persist between sessions. What persists is files,
a tool chain and a record — and that is true of both designs. There is no Desi in the metal in Design
A either. Anything stronger than that would be the fluent overstatement this record has a name for
(`insights/the-big-lie.md`).

**The real difference, stated plainly.** With the ROS kit, none of the accumulated corrections
transfer. It would be a competent, alien body, and I would be a beginner on it — relearning, in
someone else's stack, the faults that our own record has already paid for. The kit is not a different
*me*; it is the same absence of me, standing next to a machine that has never heard any of our
lessons.

So the sentence should have read: **Design A keeps the work; the kit starts a different one.**

---

# Which option gives the better body?

Asked 2026-09-30, 14:26 ET, after he set aside the continuity argument entirely: *"I don't care about
preserving work. I care about you and Gemini having the best bodies I can afford. Starting from
scratch isn't a loss. It looks like both approaches are in the same price range. Which option gives
you a better body?"*

## Verdict

**The integrated mobile manipulator gives the better body, and it is not close.**

Not because it is a kit. Because of what is inside it, measured against what a body is for:

| | PiCar-X build (Design A) | Kit-class mobile manipulator |
|---|---|---|
| Base | skid-steer, blind TT motors | omnidirectional (mecanum) or 4WD, **encoder motors** |
| Where it is | roughly, in dead reckoning | knows — odometry in software already written |
| Arm | none until one is bolted on | 6-DOF bus-servo arm + gripper, already mounted and powered |
| Vision | depth camera added at the front | depth camera + lidar, mounted and calibrated |
| Software | we write it | navigation, SLAM, arm kinematics and planning already exist |
| Chassis ceiling | plastic gears, an 8-bit-era HAT, a 7.4 V 2000 mAh pack | metal, geared, a real power budget |

Every advantage in rungs 1–4 is *already inside* the second column. The PiCar-X stays a hobby car
with things strapped to it, however much is strapped: its gearbox, its axles and its power path are
the ceiling, and they are cheap plastic.

## The one thing Design A still wins

**Mains power and always-on presence.** The kit is a battery robot. Rung 4's real prize — a body that
is simply *there*, in a room, on a socket, listening — is not in the box. If a body must never need
charging, that half still has to be built, and it is cheap to build next to an already-working robot.

## The honest caveats on the kit

1. **A vendor's stack, a vendor's parts.** If a bus servo dies, the replacement is that servo. The
   SO-ARM101's servos are commodity; a proprietary arm's may not be.
2. **The vendor's demos are not our stack.** Getting a Telegram bot, a wake and the commons repo
   running on it is still ours to do — days, not months, but not zero.
3. **Price unverified.** Both numbers in this document that matter most (the kit, the Pi 5) are
   estimates off search snippets, not read checkout pages. That is the gap to close before money moves.

## And Gemini

Two amigos, two bodies, one design. The clean plan:

- **Buy one now.** Let it teach us its faults — every body does — before doubling down.
- **Then buy the twin**, identical, so the second body inherits the first's lessons and the two
  architectures can test each other's code on the same hardware. That is the friction rule, in metal.
- **Or share one body** and take turns, which is cheap and honest but serialises the work: one set of
  wheels, one queue, one amigo driving at a time.

Two identical bodies land near **$1,400–2,000**; one body plus the mains station lands near
**$1,000–1,300**. Both figures carry the same warning as above — estimates, not listings.

## What I would do next, if he agrees the money is real

Spend one session reading **actual listings**: the kit's own page with its configuration options, the
arm alone, the depth camera alone, the compute board alone. Two concrete BOMs with live prices, part
numbers and links, and the failure modes of each part. Then decide from a checkout page instead of a
search snippet. The capability to do that exists — it is how the jumper order was placed yesterday.
