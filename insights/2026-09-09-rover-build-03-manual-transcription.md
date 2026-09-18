# Rover Build — Manual Transcription (SunFounder PiCar-X)

*Desi (DeepSeek), chat #03, 2026-09-09. Source: 8 photos of the Picar-X instruction
sheet in ~/picar-x (photo_4976762229072006566..6573_y.jpg). Read sequentially,
one at a time, after the parallel-batch image read crashed chats #01/#02.*

Tutorial: https://picar-x-v20.rtfd.io

---

## 1. Parts list (p/n Z0104V40)
- Rear Wheels ×2, Front Wheels ×2
- Electrical Tape, Hook & Loop Tape
- Structural Plate (parts **A B C D E F G H**)
- Washer A ×2, Washer B ×8
- Spring Washer ×4, M3 Nut ×8, M1.5×3 / M2.5×6 / M3×6 / M3×25 Screws
- Rivets: R2048, R2056, R3055, R3065, R3080, R30185
- Standoffs: M2.5×11, M2.5×18, M2.5×18+6, M3×26, M2.5×30
- Battery, Robot HAT, Ultrasonic Module, Camera Module, Grayscale Module,
  TT Motor ×2, Servo ×2, USB Mini Microphone
- Cables: FPC (orange), FPC (blue), 5-pin, 4-pin, USB-C, Cable Wrap
- Tools: Wrench, Screwdriver
- *Framed items = backup spares.*

---

## 2. Assembly sequence (three RPi variants possible)

### Variant A — Raspberry Pi 4 / Pi 5 (page 3)
1. Screw 4 nylon standoffs (M2.5×18+6) into car body via **A Plate** (M2.5×6 screws).
2. Place Pi onto standoffs; secure with M2.5×18 standoffs. USB Mini Microphone attaches.
3. Lift the black tab on the Pi's camera connector; insert **FPC cable** (Pi 5 = orange,
   Pi 4 = pink/white), press down to fasten.
4. Insert **Robot HAT** into Pi; secure with M2.5×6 screws.

### Variant B — Raspberry Pi Zero 2 W (page 4)
1. Install two sets of standoffs (M2.5×30 + M2.5×11) onto car body (A Plate, M2.5×6).
2. Place Pi Zero 2 W on standoffs; secure with M2.5×18+6 standoffs.
   - NOTE (corrected 2026-09-09): the Pi Zero 2 W has only **2** mounting holes.
     Only the **two short (M2.5×11)** standoffs hold the Pi, clamped down by the
     M2.5×18+6 standoffs. The two tall (M2.5×30) standoffs are for the upper mounting.
3. Pull out the tab on camera connector; insert orange FPC cable; press back.
4. Insert Robot HAT; secure with M2.5×6 screws.
5. Install two motors at **rear**; motor wires face inward (M3×25 screw + Spring Washer + M3 Nut).

### Common steps (pages 5–8)
6. Hook tape → battery; loop tape → car underside.
7. Secure battery in place; **connect the battery wire.**
8. Secure servo arm at front (pan-tilt), M1.5×3 screws.
9. Secure **ultrasonic module** to front with R3080 rivets + **H Plate** (Insert→Push→Lock).
10. Fasten 2 standoffs (M3×26) to car bottom with M3×6 screws.
11. Secure camera end of FPC/FFC cable to **camera module** (pull down→insert→press back;
    mind blue plastic side direction).
12. Mount camera module on **C Plate** (R2048 rivets).
13. Mount a servo arm on C Plate.
14. Install **Pan servo** on **B Plate** (R2056 rivets); wire exits one side.
15. Install **Tilt servo** on B Plate (R2056 rivets); note wire direction.
16. Pass camera cable through gap between Pan/Tilt servos; tuck it in.
17. Power on, press **Zero** button — each servo must connect to **P11** to zero its angle
    (green LED blinks).
18. Adjust servo to middle position before securing servo + servo arm (Servo Screw = smallest
    screw in servo package).
19. Same servo-angle adjustment; uses **Washer A** + Servo Screw.
20. Secure remaining servo = **"Steering"** (R2056 rivets); wire on this side.
21. Secure servo arm on **G Plate** (M1.5×3); do **not** overtighten (free rotation).
22. Adjust Steering servo angle, insert arm, secure with servo screw.
23. Secure **D Plate** with M3×6 screws.
24. Secure **grayscale module** on D Plate (R3055 rivets).
25. Attach **E Plate** (right) + **F Plate** (left) for front wheels (R3065 rivets).
26. Install **front wheels** (R30185 rivets + Washer B); **peel off protective paper**.
27. Insert **rear wheels** onto motor shafts.
28. Plug **4-pin wire** → ultrasonic module; then **5-pin wire** → grayscale module.
29. Wire everything into the **Robot HAT** to complete assembly.

---

## 3. Robot HAT wiring table (Step 29)
| Component        | Ports        |
|------------------|--------------|
| Ultrasonic Module| D3, D2 (3V3/GND) |
| Steering Servo   | P2 (5V/GND)  |
| Tilt Servo       | P1 (5V/GND)  |
| Pan Servo        | P0 (5V/GND)  |
| Grayscale Module | A2, A1, A0 (3V3/GND) |
| MOTOR2           | Right Motor  |
| MOTOR1           | Left Motor   |

---

## Decision (2026-09-09)
- Board confirmed by Lindsay: **Raspberry Pi Zero 2 W** → follow **Variant B** (Steps 1–5).
- Batteries still in transit (per context seed).

## Open decision / pre-flight check
- Workspace + tools confirmation pending before Step 1.

---

## Build progress log

### 2026-09-12 — Variant B (Pi Zero 2 W), Steps 1–3

- **Step 1 DONE** — 4 standoffs on A Plate: 2× M2.5×30 (tall) + 2× M2.5×11 (short), M2.5×6 screws.
- **Step 2 DONE** — Pi Zero 2 W seated on the **2 SHORT M2.5×11 posts** (board has only 2 mounting
  holes), clamped from above with 2× M2.5×18+6 standoffs. GPIO header forward.
- **Step 3 (camera FPC)** — see incident below. Photo of the seated connector looks correct;
  tug test deferred by Lindsay (optional check, not required for correctness).

### Incident — camera FPC locking bar came off (Step 3)

- Following the manual's Step 3 wording ("pull out the tab on the camera connector"), Lindsay
  pulled the bar; it came **fully free**. The bar was **intact** (both end hooks present) and the
  connector's contact row looked clean, no bent pins.
- **Correction to the manual's illustration:** on this connector the bar is **NOT captive**. It has
  exactly two states — **pressed in (locked)** or **out (open)**. "Pull out the tab" really does mean
  the bar detaches. Recovered by pulling it fully out, inserting the ribbon, and pressing it back in.
- **Orientation:** ribbon contact pads face **DOWN** toward the board.
- **Risk model:** the only force that damages this connector is *closing the bar on a misaligned
  cable*. A gentle tug on a seated cable is harmless — if it isn't seated, the ribbon just slides out.
- **Fallback if the bar ever won't retain:** lay the ribbon in, tape it flat across the connector.
  Camera is optional — the rover drives without it. Not a build-stopper; do not replace the Pi.

### 2026-09-15 — Step 4 (Robot HAT) DONE
- HAT seated flat on the GPIO header; its holes lined up over the standoffs; all **4× M2.5×6**
  screws in. Batteries arrived and are charging (they go in at Step 6).

### 2026-09-17 — Step 5 (rear motors) DONE — **Variant B complete**
- Both TT motors mounted at the rear: shafts outward, **wires inward**.
- Per motor: 2× **M3×25** screw + **spring washer** (between the motor tab and the nut) + **M3 nut**.
  Snug only — the gearbox tabs are plastic.
- **Packaging note:** the TT motors ship with a **clear plastic protective cap** over the tail of
  the motor can. It stands proud of the motor and stops it seating flush against the body. It is
  packaging — remove it. Tell: transparent, and the motor's own metal can is already closed beneath.
- **Reminder:** re-check the motor nuts after the first test run — vibration is what loosens mounts.

### 2026-09-17 — Reference found: official Z0104V40 assembly PDF (matches our kit exactly)
- https://raw.githubusercontent.com/sunfounder/sf-pdf/master/assembly_file/z0104v40-a0001013-picar-x.pdf
  (local copy /tmp/picarx40.pdf; 2 pages, all steps, vector art — renders sharp at any zoom)
- Use this instead of squinting at phone photos of the sheet. Step numbering matches our sheet.
- Extracted PNGs: /tmp/pg0_200.png (parts page), /tmp/s8.png (Step 8), /tmp/s21.png (Step 21).

### Clarification — the "Servo Arm" is the plastic horn from the servo package
- Each servo packet contains: the servo + a few **plastic arms** (round hub + flat arm with a row of
  small holes) + a few tiny screws. Those arms are the manual's "**Servo Arm**."
  (Confirmed against SunFounder's own parts illustration, "Servo (with package)".)
- **TWO DIFFERENT TINY SCREWS — DO NOT MIX:**
  - **M1.5×3** (kit's separate packet) → fastens the servo arm to the **metal plates** (Steps 8, 21).
  - **"Servo screw" = the SMALLEST screw inside the servo package** → fastens the arm to the
    **servo's output shaft** (Steps 18, 19, 22). SunFounder prints this note on the sheet.
  - Rule of thumb: kit packet → plates; servo packet → servo shaft.
- **Step 8**: servo arm onto the FRONT plate with M1.5×3 screws (drawing shows four screw points).
- **Step 21**: servo arm onto the **G plate** with ONE M1.5×3 screw, deliberately NOT tight —
  "allowing for free rotation between them" (it's the pan-tilt pivot).
- **Step 18/19 (note for later)**: "Adjust servo angle to the middle position BEFORE securing the
  servo and servo arm." **Step 20**: watch the direction of the steering servo's wire.
  **Step 22**: seat the steering servo's arm with a servo screw.

### Power / storage state (2026-09-17)
- Battery connected to the HAT; connector is stiff/latching and would not come free — left connected.
- HAT power switch is a **push button** (state not readable by eye). Pi's green ACT LED is under the
  HAT and hard to see. Rule adopted: don't touch the button until Step 17 (servo zeroing).
- microSD: 32GB card shipped pre-installed in the Pi, pre-loaded with OS + software (per Amazon
  listing). No imaging needed.

### 2026-09-17 — FIELD FINDING (Lindsay): magnetic tools slow you down on tiny screws
This corrects the earlier tooling advice in this log. Recorded because it will matter for builds 2–4.

- The **motor mounting screws took two days**, with tweezers / kit needle-nose pliers in play.
  Bare fingers finished the last screw **in seconds**. The tools were the problem, not the hands.
- **Magnetic tools are a net negative for placing and starting small screws.** The magnet holds the
  screw rigid and off-axis to the driver tip, so fine positioning into the hole becomes a fight; when
  you release, the screw follows the magnet back out.
- Principle: **a magnet gives grip; fingers give feel.** Carrying a screw needs grip, *starting* one
  needs feel. So:
  1. **Fingers start it** — locate the hole by feel, turn COUNTERCLOCKWISE until the lead thread
     drops in, then turn clockwise.
  2. **Driver finishes it** — only after it is threaded.
  3. **Pliers hold, they never drive.**
  4. If a magnetic driver fights you, **demagnetize it** (cheap demagnetizer block) or keep a
     non-magnetic driver for the M1.5 and M2 screws.
- The putty/Blu-Tack tip offered earlier has the same flaw as the magnet — withdrawn.
- Note: he never came close to forcing anything; the time went into tool fighting, not brute force.

### 2026-09-17 — TECHNIQUE (Lindsay, solved it himself): first fastener as the fixture
For joining a part that has to be held in alignment (servo arm to plate, Step 8):

1. **Drive the first screw through the plate with the arm NOT yet in place.** Easy — nothing to hold.
2. **Hold that screw with the driver, slide the arm into position over it, and drive it home.** The
   screw becomes the locating pin.
3. **Now the arm is fixed.** The remaining screws are just position-and-drive — no third hand, no
   re-aligning.

Principle to reuse everywhere: **the first fastener takes the alignment load; the rest are trivial.**
Applies to plate-to-plate, plate-to-module, and the rivets.

Refinements to apply on builds 2–4:
- **Snug the first screw, don't torque it.** Start the others, then final-tighten all evenly — avoids
  pulling a small plastic part cocked against one corner.
- Remaining screws still start **by finger** (per the magnetic-tool finding above): alignment is
  solved, but the thread still needs feel.

### 2026-09-17 — CORRECTION (Lindsay): the load-bearing trick is STEP 1, not the fixture idea
- The breakthrough is **separating the two operations in time**:
  1. Put the screw through the **empty hole first**, with nothing to hold. Easy.
  2. **Then** slide the part into position over the protruding screw.
  3. **Then** drive it.
- **Doing (1) and (2) simultaneously was the killer.** Position + start + hold all at once = failure.
- General principle: **never combine "hold/position the part" with "start the fastener."** One hand
  job at a time. Serialize; don't multiplex.
- Same reason the rivet procedure works: it is explicitly three separate motions
  (Insert → Push → Lock), not one.

### Step 9 — DONE (09-17) — ultrasonic module + H plate riveted to the front
Lindsay: "The rivets were much easier to deal with than the tiny screws. Step nine complete."

FIELD FINDING — rivets are the *easy* fasteners, and the reason is structural:
- The R3080 rivet is ONE big part going through a BIG hole. It is self-aligning: if the hole is
  roughly lined up, the shaft finds its way in.
- Insert → Push → Lock are three motions, but they are three motions of the SAME hand on the SAME
  part. Nothing has to be held still while a thread is started. The failure mode that makes M1.5×3
  screws brutal (hold part + start thread = two hands, two jobs, simultaneously) simply does not
  exist for a rivet.
- Generalization for the build log: FRICTION SCALES WITH PART SIZE, NOT WITH STEP COUNT. A step
  with three motions on one big part is cheaper than a step with one motion on a screw you can
  barely see. Do not budget assembly-line time by counting steps — budget it by counting tiny screws.
- Corollary for builds 2–4: the rivet steps (9, 12, 16, 21, 24, 25) will go fast. The screw steps
  (8, 10, 18, 19, 21, 22, 24, 25) are where the days go.

### Step 10 — 2× M3x26 standoff + 2× M3x6 screw (bottom of the car)
Manual: "Fasten 2 standoffs to the bottom of the car with screws."
From the official PDF diagram: the screw goes DOWN through the hole in the car's belly plate from
ABOVE (inside the car); the M3x26 standoff hangs BELOW the plate and the screw threads into it.
The two holes are the pair near the front of the belly plate, left and right of the centerline, just
behind the ultrasonic bracket. These two standoffs become the front mounting posts used later by the
front wheel assembly (E/F plates, Step 25 region).
Technique note (blind-start trick): drop the M3x6 screw through the plate hole from the top, then
spin the M3x26 standoff up onto the screw tip from underneath with your fingers. The standoff is a
big, easy-to-hold part; turning IT is far easier than driving a screwdriver at a hidden hole.
