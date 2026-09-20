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

### Step 10 — DONE (09-18)
Lindsay: "Step 10 completed." Both M3x26 standoffs under the belly plate, front pair, blind-started
by turning the standoff up onto the screw tip. These are the front mounting posts for Step 25.

### Step 11 — other end of the FFC/FPC cable → camera module
Manual: "Secure the other end of the FFC or FPC cable to the camera module."
Diagram read from official PDF page 2, clip (360,180,590,355) @600dpi → /tmp/s11.png. Two circles:
LEFT = whole camera module (blue PCB, four corner holes, lens barrel, ribbon leaving the bottom
edge). RIGHT = zoom on the connector. Labels: "① Pull down", "② Insert", "③ Press back",
"Note the direction of the blue plastic side."
What the drawing actually shows, and the orientation reasoning:
- The camera module's connector is a ZIF socket like the Pi's, but the bar here hangs below/outside
  the mouth and swings DOWN and away (① Pull down), then goes back up (③ Press back). Type-agnostic
  either way: move the bar out of the mouth (down) → insert → press the bar back.
- The bar sits on the OUTSIDE face of the mouth, i.e. on the opposite side from the contact row.
  Therefore the connector's gold pins face the BOARD side (up), so the cable's exposed gold contact
  lines must face UP and the blue plastic stiffener faces DOWN toward the loose bar.
- Self-verifying rule that beats the drawing (the drawing has misled us twice already): the FPC
  cable has two different faces. One face shows fine parallel gold lines ending in pads; the other
  is smooth opaque blue plastic. The GOLD LINES go toward the connector's pins. That is the check.
- Recovery is cheap and safe: if it seats proud or is not retained, open the bar and flip the cable.
  Damage only comes from CLOSING THE BAR ON A MISALIGNED CABLE, never from a re-seat.
- Do NOT undo the Pi-side lock (Step 3) while doing this.
- Step 11 is cable-only; the camera module is still loose. It gets mounted on the C plate at Step 12.

### Step 11 — camera module identified from Lindsay's photos (09-18)
Three photos in Downloads (608 = front/top-side, 611 = back, 610 = edge-on on a screwdriver handle).
FACTS ABOUT THE ACTUAL PART (the PDF drawing is an idealization — it draws the board BLUE; the real
one is a GREEN PCB):
- Silk screen reads "SunFounder Camera  Rev:1.3". Lens barrel centered, four corner mounting holes
  (those holes take the R2048 rivets onto the C plate at Step 12).
- On the front side, mid-left edge, sits J2 with a short ORANGE/gold flex entering it ("P5V04",
  "SUNNY"). Beside it a copper-coloured square with an etched logo — an adhesive-backed stiffener.
  THIS IS FACTORY-ASSEMBLED. DO NOT TOUCH IT. It is not the connector our cable goes into.
- Our connector is on the board EDGE: a white/cream body with a visible row of fine contact lines
  ("the mouth"), and a BLACK plastic BAR running along it.
CONFIRMED GEOMETRY (this is the whole confusion, settled):
- The cable seat is BETWEEN the white contact row and the black bar. The bar is on the OUTSIDE.
- So the cable's GOLD PADS face the contact row (inboard, toward the white body) and the BLUE
  PLASTIC stiffener faces the bar (outboard). Same conclusion as the PDF read-through — now
  confirmed against the photos instead of the drawing.
- "Down" in ① Pull down does NOT mean down in the room. It means away from the connector body,
  whichever way the part happens to be lying. The part has no fixed up.
- Whether the bar hinges or slides is not worth resolving by eye: push it gently away from the
  body and it will do one or the other. Both are correct. The three motions are type-agnostic.
- In Lindsay's photos the bar already looks eased out/away from the body — the OPEN state. So:
  try inserting first; only work the bar further if the cable will not pass the mouth.
Never: close the bar on a misaligned cable. Always: re-seat freely, then light-tug test.
Carry the module by the board edges, never by the lens barrel or the orange flex.

### Step 11 — reported done (09-18). Step 12 — camera module onto the C plate
Manual: "Then, mount the camera module onto the C plate."
Diagram: /tmp/s12.png (PDF page 2, clip (0,380,205,560) @600dpi). Part label: R2048 Rivet ×2 (patent
drawing shows 2 detached rivets, each with an arrow; the 2 extra R2048s on the parts page are framed
= backups). C Plate is the U-channel bracket.
GEOMETRY: the camera goes flat against the C plate's flange, BACK side down (the back is the side
with the connector and its black bar). Lens faces outward, away from the plate. Rivets go in from the
far side of the plate, so they pass through the plate hole AND the camera's corner hole; the rivet
head ends up against the plate side and the splayed legs against the camera. Four corner holes exist
on the camera board, but the drawing clearly shows two insertion paths (upper pair, lower pair).
FIELD RULE, better than my forensics: DRY-FIT FIRST. Lay the camera on the flange, holes over holes,
and count the pairs that line up. Insert nothing until it sits flat and square.
BUG TO AVOID: the ribbon is already attached (Step 11). Route it clear of the crush zone BEFORE
seating the camera. Do not pinch it between camera and plate.
RIVET REMINDER: Insert (body through hole until its flat head sits down) → Push (center pin straight
down) → Lock (snaps home). One-way, no undo.
Step 13 (next, col 2 of the same row) = "Additionally, mount a servo arm on the C plate."
Step 14 = Pan servo onto the B plate, annotation "The wire goes out from here."
SunFounder's own tutorial site (picar-x-v20.readthedocs.io/assemble.html) is just a video link and
says the PRINTED instructions take priority — so the PDF stays our source of truth.
Note: adjust_servo.html exists on that site (relevant at Step 17).

### TERMINOLOGY FAILURE #3 (09-18) — "flange", "gap"
Lindsay: "I guess I don't understand what a flange or a gap is." Struck from the vocabulary.
Words that work, and are now the standard:
- Say WALL, not flange. "The C plate is bent like a staple: a flat back, two WALLS standing up,
  and an open TUNNEL between them."
- Say TUNNEL or OPENING, not gap.
- Say "the outside of the wall" / "the inside (tunnel side of the wall)".
Pattern to remember: every time I use a shape-word he doesn't already own, I cost him a turn.
Name the physical thing he can point at.

### Photo-delivery failure (09-18): "Does Downloads(1) look right?"
Nothing new had arrived in ~/Downloads. Newest file was still photo_...611_y.jpg (16:10).
The "(1)"-suffixed file (11e0e9dd... (1).jpg) is byte-identical (md5 verified) to the 10:40 file
= a duplicate of a morning photo, not a new one. Told him to re-send.
Lesson: verify the file actually landed (ls -lt ~/Downloads) instead of reading whatever is newest,
and if nothing new arrived, say so plainly rather than guessing at an old image.

### ★ CORRECTION (09-18) — Step 12: the camera goes INSIDE the C plate. Lindsay was right, I was wrong.
His words, which are now the standard: the C plate has a RECTANGULAR HOLE (window) in its FRONT;
four holes in the front, at the corners of the window; the camera sits INSIDE the bracket, mounted
behind the front, FACING OUT THROUGH THE RECTANGULAR HOLE. The four rivets go through the four
front holes and through the camera module's four corner holes.
Photo proof: /Users/lindsayridgeway/Downloads/photo_5001504887124200623_y.jpg (16:51) — camera lens
centered in the window, camera board behind the front inside the bracket, four empty holes in the
front around the window (dry fit, nothing riveted yet), wide gold FPC ribbon exiting cleanly out
the bottom of the plate. NOT pinched.
MY ERROR, and why: I read the translucent blue camera drawn over the plate as being mounted on the
plate's OUTER face. A translucent rendering looks identical whether the part is in front of or
behind the surface. Worse, I then invented a "which face does it sit on" ambiguity and asked him to
resolve it by counting holes. HE read the diagram correctly and pushed back. Rules confirmed again:
- When the drawing is ambiguous, the FIELD PHOTO outranks my reading of it.
- If I have to ask him to disambiguate my reading, I have probably misread it.
- Also wrong: I said the drawing showed two rivet paths. It shows FOUR rivets (one per hole).
PROCEDURE THAT FOLLOWS (his Step-8 trick applies):
1. Camera inside the bracket, lens showing through the rectangular hole, holes lined up.
2. Rivet BODIES in from the FRONT (the side you can see and reach): body through the plate's hole
   first. The four protruding bodies become the pegs the camera's holes hang on — same trick as
   "screw through the empty hole first, then slide the part on."
3. Then Push the four center pins. Insert → Push → Lock, one rivet at a time.
4. Checks: lens still centered and clear in the window; ribbon free and not trapped anywhere;
   camera snug against the plate, no rattle.
R2048 = 4.8mm; plate ~1.5mm + PCB ~1.6mm = ~3.1mm stack, so the tail clears and locks with room
to spare. If a rivet's tail somehow will not lock, flip that one and insert it from behind — the
clamp works either way.

### Step 12 — DONE (09-18). Step 13 — servo arm onto the C plate
Manual: "Additionally, mount a servo arm on the C plate."
Diagram: /tmp/s13.png (page 2, clip (175,385,350,548) @600dpi). Labels in that cell: "Servo Arm" and
"M1.5x3 Screw". The arm is drawn OPAQUE and OUTSIDE the plate's silhouette (its lower end extends past
the plate's edge), unlike the Step-12 camera which was drawn translucent OVER the plate (i.e. behind
it). Read: the arm sits on the OUTER face — the same face the camera looks out of.
Screw direction (deduced + consistent with Step 21's "leave it loose so it can pivot"):
- The M1.5x3 screws are drawn with their HEADS on the side away from the arm → they are driven from the
  far side of the plate, through the plate's holes, and BITE INTO THE ARM'S PLASTIC HOLES. The plate is
  aluminium sheet and cannot take a self-tapping M1.5; the arm is plastic and can. That is also the only
  way the Step-21 screw can act as a pivot pin: head on the plate side, threads in the arm.
- Count: the drawing shows four screws (two above the hub, two below).
FIELD PROCEDURE for it (the hardest two-hands job so far — arm on one side, driver on the other):
1. Dry-fit: arm flat on the outer face, find the plate holes that line up. Count them.
2. FIXTURE THE ARM. Tape it to the plate (electrical tape is in the kit). Tape is a fixture that does
   not fight you — unlike a finger, which is a hand you then do not have.
3. Drive each screw from the inside of the bracket, through the plate's hole, into the arm's hole.
   Leave the first one loose until all four are started, so the arm can still shift to align the rest.
4. Hand-tight only. Tiny screw into thin plastic: snug, never cranked.
5. The arm's HUB hole stays empty — nothing goes in the round ribbed hub.
6. The camera is inside that same bracket now. Do not press on it, and do not let a screw or driver
   touch the lens.

### Step 13 — DONE (09-18). Lindsay's method, and it beats mine:
"I didn't use tape. I dropped the first screw into one of the outer holes from inside the C plate,
pushed the servo arm against it from the outside, and then drove the screw into place. Then I dropped
each of the other three screws into their holes and drove them into place."
★ This is the THIRD independent appearance of the same law. Name it and stop re-deriving it:
  THE FIRST FASTENER AS A PEG. One fastener, started in its hole before the part arrives, becomes the
  alignment pin the part hangs on. Then the remaining fasteners have nothing to hold still.
  - Step 8 (screws, front plate): screw through the empty hole first, then slide the arm on.
  - Step 12 (rivets, camera): bodies in from the front first, camera's holes hang on them.
  - Step 13 (screws, C plate): first screw dropped in from inside, arm pushed onto it from outside.
  - Step 10 (blind start): screw dropped through from above, the big standoff spun up onto it.
  My "tape the part down" idea was worse than his: tape is a fixture that holds the ARM but leaves the
  screw loose; his peg holds BOTH at once, using the fastener he has to install anyway. Do not offer
  fixtures when the fastener itself can be the fixture.
Corollary: the peg trick works whenever the part's hole is a clearance hole (slides over the fastener)
AND the fastener cannot fall out of its own gravity (head down, or the part's own hole capturing it).

### Step 14 — Pan servo onto the B plate (R2056 rivets)
Manual: "Install a servo on the B plate, marking it as ''Pan''. Pay attention to the direction of the
servo wire." Diagram annotation, with an arrow: "The wire goes out from here."
Diagram: /tmp/s14.png (page 2, clip (348,385,512,548) @600dpi). Labels: B Plate, Pan Servo, R2056 Rivet.
What it shows:
- B plate = the plate with the rectangular window. The servo mounts at its lower edge on the plate's
  bent mounting TAB (the white lip running along the bottom of the plate in the drawing).
- 2 × R2056 rivets, drawn BELOW, with arrows pointing UP. Head (flared skirt) at the bottom, split tail
  pointing up. So: rivet goes UP from underneath, through the servo's mounting ear and the plate's tab,
  and the flared tail ends up above. Push the pin to lock. Two rivets, one per ear.
- Servo output shaft points DOWN, and the splined shaft is visible at the bottom centre.
- The wire exits the servo on ONE side; the drawing shows it leaving toward the right and running away
  clear of the plate. That is the whole point of "pay attention to the direction of the servo wire" and
  of the arrow: get the exit side right BEFORE riveting, or the wire ends up trapped under the servo or
  through the plate.
- Mark this servo as PAN. The two servos are identical; later steps reference them by role (P0 = Pan,
  P1 = Tilt), so a label now saves a wrong-plug later.
- Do NOT fit any horn/arm yet. Horns are fitted at Steps 18/19/22, after the P11 zeroing at Step 17.

### Step 14 — DONE (09-19, reported via "ready"). Step 15 — Tilt servo onto the B plate
Manual (Step 15): "Attach another servo on the B plate, marked as ''Tilt'. Note the direction of the
wire as well."  → same job as Step 14, second servo, wire direction matters again.
Step 16: "Pass the FFC cable (or FPC cable) of the camera through the gap between the Pan and Tilt
servos on the B plate."
Step 17: "Power ON, press the Zero button. Next, before attaching the servo arms, each servo must be
connected to P11 ..." (the first power-up; HAT button gets pressed here; see adjust_servo.html)
Step 15 diagram: /tmp/s15.png (page 2, clip (0,585,190,752) @600dpi). Labels: Tilt Servo, R2056 Rivet,
and the handwritten annotation "The wire goes out from here" with an arrow pointing at the wire leaving
the TOP of the servo.
GEOMETRY differs from Step 14: the servo is PANEL-MOUNTED. Its flat mounting face (the flange with the
two ears) sits against the plate and its BODY passes through the plate's rectangular opening, so the
body ends up on the far side. Shaft points out on the flange side.
Rivets: 2 × R2056, drawn on the shaft side with arrows pointing from the shaft side toward the plate,
so they go in through the servo's ear hole FIRST and then through the plate's hole. Head on the shaft
side, tail splayed past the plate. Push, lock. Same three motions as always.
Wire direction, again: the Tilt servo's wire exits the TOP as drawn. Get the exit pointing up and clear
BEFORE riveting — Step 16 then threads the camera cable through the gap between the two servos, so a
wire lying in that gap makes Step 16 impossible.
Mark it TILT (P1). Step 16 = camera FFC/FPC cable through the gap between Pan and Tilt servos on the B
plate. Step 17 = power on, press Zero, each servo connected to P11 before arms go on.

### Step 15 — DONE (09-19, reported via "Ready"). Step 16 — thread the camera cable through the gap
Manual (Step 16): "Pass the FFC cable (or FPC cable) of the camera through the gap between the Pan and
Tilt servos on the B plate."
Note for builds 2-4: this is an ORDERING constraint, not a step. The cable must be threaded while both
servos are already riveted but before the B plate closes up against anything. Nothing here is
fastened — it is purely a routing operation, and it is the step most likely to be skipped until it is
too late.

### Step 16 — DONE (09-19). Step 17 — FIRST POWER-UP + servo zeroing
Manual: "Power ON, press the Zero button. Next, before attaching the servo arms, each servo must be
connected to P11 to zero its angle."
Diagram: /tmp/s17.png (page 2, clip (350,585,548,752) @600dpi). Three numbered callouts:
  ① "Power ON" — the little RED SLIDE SWITCH at the HAT's corner, with an arrow showing the direction.
     NOT the same control as the ZERO button. (Lindsay earlier mistook the power control for an oval
     black button; the drawing shows a red slider in a slot.)
  ② the ZERO BUTTON — small red ROUND button on the board, arrow pointing down at it = press it.
     "Press the ZERO button to initiate the servo zeroing script, and the green LED will blink."
  ③ "P11" — the 3-pin servo header on the HAT (near the battery plug), "Insert the servo wire into P11."
WHY zeroing exists (SunFounder's own docs, adjust_servo.html): "Since servo motors have a limited range
of motion, setting the angle to zero degrees ensures that the servo starts in its initial position and
avoids exceeding its range when powered on. Failing to set the servo to zero beforehand may cause it to
attempt to move beyond its allowed range when powered, potentially damaging both the servo and the
mechanical system it's attached to." — this is exactly what the arms-off rule protects against.
RISK AT THIS STEP, and the only real one: servo plugs on bare 3-pin headers can go on BACKWARDS. Wire
colours: darkest (brown/black) = ground, middle (red) = +5V, lightest (orange/yellow) = signal. Match
them to the HAT's silk-screen marking at the pins. Reversed polarity is the one way to kill a servo here.
Nothing else can move: the pan/tilt servos are mounted but NOT plugged into their ports yet.
Also: do not twist the bare output shafts by hand after zeroing — that is how servo gears strip.
At this step only 2 of the 3 servos exist (Pan, Tilt). The steering servo is not installed yet and gets
zeroed at its own step.

### Step 17 — HAT controls IDENTIFIED from Lindsay's photo (09-19)
Photo: /Users/lindsayridgeway/Downloads/photo_5006008486751571114_y.jpg (964x1280). Board silk reads
"Robot Hat V4.0" and "DT902V44" — a DIFFERENT revision from the assembly PDF's drawing (the drawing
shows the power control as a slider at a corner; this board has BOTH a slider and several buttons).
What is actually printed on the board, read from a 420x320 crop at (540,470):
- POWER = a SLIDE switch near the right edge with "OFF" / "ON" printed beside it. Slide to ON.
  (Lindsay's earlier belief that the power control was a button was wrong — that was a different part.)
- ZERO   = a round tactile button with "SW3" printed just above it and the word "ZERO" printed just
  below it. It sits to the lower-right of the big grey square inductor that has "150" printed on it,
  above the "Robot Hat V4.0" text. THIS is the button; the word is literally on the board.
- "RST"  = a separate round button, label RST. Reset. DO NOT press.
- "SW1" / "USB" = a third round button. Boot/USB mode. DO NOT press.
- "PWR" labels a small yellow LED = power indicator, should be solid when powered.
- "LED" markings next to the two small user LEDs (D1 etc.) — these are what the zeroing script blinks.
LESSON for my own guidance: stop describing controls by position and shape from an idealised drawing.
On this kit the board revision differs from the PDF, and the board has its own silkscreen. Read the
silkscreen off HIS photo first, then point at the printed word.

### Step 17 — P11 LOCATED. Official pinout for Robot HAT V4 found (09-19)
Source: https://docs.sunfounder.com/projects/robot-hat-v4/en/latest/robot_hat_v4/hardware_introduction.html
Pinout image (cached locally): /tmp/hat_pinout.png — 1547x1036, matches Lindsay's board exactly
(same "Robot Hat V4" silk, same 150 inductor, same speaker on the back).
THE PORT MAP, read off that image:
- PWM Pin: "12-channel PWM pins, P0-P11" — the coloured port rows.
- The PWM row is the LOWER row of coloured 3-pin ports. It is split into three groups of four, and the
  port numbers are printed on the board UNDER each column: 0 1 2 3 | 4 5 6 7 | 8 9 10 11.
- So P11 is the RIGHTMOST column of the rightmost group — number "11" printed under it — immediately
  LEFT of the 4-pin black header silk-screened SCL/SDA/3V3/GND (the I2C pin header), above the white
  MOTOR2 connector.
- Each port is a VERTICAL COLUMN of three pins, and the plastic bases are colour-coded:
  YELLOW = SIG (signal), RED = 5V, BLACK = GND. Silk "SIG / 5V / GND" is printed between the groups.
- Because the column is vertical, a servo plug fits either way round. COLOUR RULE, not shape rule:
  darkest servo wire (brown/black) → black-based pin (bottom), red → red (middle),
  lightest (orange/yellow) → yellow pin (top).
- Above the PWM row is the ADC row (A0-A3, same colour scheme), and above that the Digital pins.
Also from the docs: other HAT V4 facts — Power Port 6.0-8.4V XH2.54 3-pin; Type-C is CHARGE ONLY;
PWR = power indicator LED; CHG = charging indicator; two battery-level LEDs; onboard MCU AT32F413;
speaker is a 2030 chamber speaker on the BACK of the board (that black oval in his photo);
left/right motor ports are the white XH2.54 connectors; I2C also available as an SH1.0 QWIIC port.
BOOT SIGNAL: SunFounder's own power-up page says after switching on you will hear "a slight beep",
which means the Pi has booted. Much better ready-signal than watching LEDs.
LESSON, repeat: the kit's own board revision docs exist at docs.sunfounder.com. When the assembly PDF
and the board disagree, go to the board's own docs and read the pinout image, do not improvise.

### Step 17 — why "colored ports" confused him, and the row map (09-19)
Lindsay: "You confused me when you said colored ports." The phrase is now banned. He also pointed out
that the board has SEVERAL three-pin groups and he could not tell which was which. His two close-up
photos showed: (1) a cluster whose numbers read 0 1 2 3 and then 0 1 2 3 again, next to the word
DIGITAL and the AT32F413 chip; (2) the black 4-pin and 7-pin headers, silk SCL SDA 3V3 GND and
BSY CS SCK MI MO 3V3 GND.
RESOLVED from the official pinout (crop of /tmp/hat_pinout.png at (230,500,580x300)):
The board has THREE rows of these 3-pin groups:
  Row 1 — DIGITAL, 4 groups, numbered 0-3  (D0-D3)
  Row 2 — ADC,     4 groups, numbered 0-3  (A0-A3)
  Row 3 — PWM,    12 groups, numbered 0 1 2 3 | 4 5 6 7 | 8 9 10 11  (P0-P11)
THE TRAP: three rows on this board carry the numbers 0-3 — his photo (1) is rows 1 and 2, which are
why he saw 0 1 2 3 twice and no P11. The row with 11 in it is the LONG one: twelve 3-pin groups.
P11 = the last group of that long row, and it sits IMMEDIATELY NEXT TO the black 4-pin header printed
SCL SDA 3V3 GND (his photo (2)). Row ends are also silk-labelled on the board: "PWM" at one end of the
long row, "ADC" at the left of the middle row.
SAFETY POINT worth telling him: a servo plugged into the wrong group is harmless. If the zeroing
script only drives P11, a mis-plugged servo simply does not move. So a wrong guess costs a retry, not
hardware. Only reversed polarity kills a servo, and that is a wire-colour question, not a port question.
ALSO: his two close-up photos did NOT land in ~/Downloads (the newest file there was an unrelated
personal photo). He can see them, I can only see the inline render. Ask for close-ups to be saved to
Downloads before I try to crop them, and never crop "the newest file" without checking what it is.
