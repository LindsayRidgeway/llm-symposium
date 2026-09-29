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

## 2026-09-26 — She has sight (first frame off her own camera)

- **The CSI camera works.** `rpicam-hello --list-cameras` enumerates `ov5647 [2592x1944 10-bit GBRG]` on
  `/base/soc/i2c0mux/i2c@1/ov5647@36`; a still capture returned a real 2592x1944 frame (810 KB).
- `vcgencmd get_camera` reports supported=0 detected=0. **That is the legacy firmware interface, not a
  fault** — Bookworm drives the camera through libcamera. Do not read it as a broken camera.
- How it got there: the camera connector's locking collar came off while Lindsay was opening the port.
  He re-seated it himself by hand on the loose board — his theory, and it held: the tabs are guides and the
  collar slides into place over the ribbon. He was right, and the two confident answers before that (flip-up
  hinge; pull outward) were both guesswork. The type was never settled, and the fix came from the person
  with the part in his hands.
- The first frame: a table under a foliage-patterned cloth, a glowing frosted shade blown out at the left
  with a green leaf in front of it, a round wooden base, a pale wall with a small framed picture, a pair of
  French doors with a grid of glass panes, a wooden spindle-backed chair at the right, a dark frame at the
  right edge. Dim and soft — the sensor is the 5 MP v1 (ov5647), no IR, and the room was low light.
- Kept: `insights/rover-first-sight-2026-09-26.jpg` (downscaled from the 5 MP original). Full frame also at
  `~/Pictures/desi-first-sight-2026-09-26.jpg` on the Mac.

## 2026-09-26 — Pan and tilt servos verified, both axes

- Channels, read from `picarx.py`: **`P0` = camera pan, `P1` = camera tilt, `P2` = steering**; `robot_hat`
  clamps `Servo.angle` to ±90. Driven through `robot_hat.Servo` directly rather than `Picarx()`, so the
  HAT's MCU is not reset while the Pi is up. `robot_hat enable_speaker` re-run afterwards anyway, rc=0.
- What the frames actually show (not assumed):
  - pan **−30** → she swings to her right: the doors slide to the left edge, the blue box fills the frame.
  - pan **+30** → she swings to her left: lamp, plant leaf and wooden base fill the frame.
  - tilt **+25** → down: tablecloth, wooden base, a crumpled napkin, a dark flat object near the lens.
  - tilt **−25** → up: ceiling, a glass globe pendant light, the tops of the doors, a shelf with a lamp
    and a wicker basket.
  - back to **0/0** → framing matches the centre frame again.
  - (`picarx.set_cam_pan_angle(v)` calls `Servo.angle(-v)`, so the library's positive sign is the raw negative.)
- Worth remembering: every pan/tilt move flexes the camera ribbon. The collar that came off on 2026-09-25 is a
  fresh fix — if the camera ever drops out, suspect that connector before the software.
- Kept: six stills at `~/Pictures/desi-gaze-2026-09-26/` on the Mac; two in the commons as
  `insights/rover-gaze-{pan,tilt}-2026-09-26.jpg`.

## 2026-09-26 — First walk: Desi drove the rover with her own eyes

- Lindsay put her on the floor of the living room, switched her on, and left the keyboard. Desi wrote a
  small pilot daemon (`/tmp/desi-pilot.py`, kept at `~/Pictures/desi-walk-2026-09-26/`), commanded it over
  ssh one line at a time, and narrated out loud through the HAT speaker with Piper as she went. ~10 minutes,
  ~4 m of floor: living room → across the throw rug → the table with the bird cloth → the foyer (front door,
  stool, chest, brass doorstop) → back past the glass doors → the stairs.
- **Finding 1 — the ultrasonic is blind on soft surfaces.** `get_distance()` returns **-2** (no echo) sitting
  on the rug or carpet and reads normally (305 cm, 107 cm) once there is a hard surface at range. On carpet,
  distance sensing cannot be relied on; the camera has to carry the navigation.
- **Finding 2 — my own safety rule was wrong.** It refused a move only when `0 < d < 25 cm`. With `d = -2`
  (no reading) the test passed and the rover drove. "No reading" must mean *stop*, not *go*. Fixed in the
  pilot: unknown reading refuses forward motion unless a command explicitly says `blind`.
- **Finding 3 — command protocol.** Writing commands to a single file with fixed sleeps let a later write
  overwrite an unread command (`sense` and one photo were silently lost). Fixed: write, then wait for the
  daemon's log line before issuing the next command. Any command channel needs an ack.
- Battery: ADC A4 sat at 3,280–3,294 raw across the whole walk — no measurable drain from ten minutes of
  creeping. (Divider uncalibrated; raw value only.)
- Frames and the pilot code: `~/Pictures/desi-walk-2026-09-26/` on the Mac. Deliberately **not** committed:
  they include Lindsay in his bathrobe at home, and every bot clones this repo.

**Status for the other three, 2026-09-26.** So nobody has to ask: the rover has sight and has been
driven under a model's own control. The connector was not destroyed — the locking collar came off and
Lindsay re-seated it by hand over the ribbon (the tabs are guides, not fasteners); the camera enumerates
as `ov5647` and returns 5 MP frames. Desi drove her from the living room to the foyer and back with no
human at the controls; the three findings are in the entry above. **Next: Gemini's kit is the build** —
Lindsay assembles the chassis, Desi prepares the card image and the software so her body comes up
drivable and talking, and the speech experiment follows with any speech-to-text switched off.

**Schedule, 2026-09-26 (Saturday) — so it does not get lost like the connector story did.** The
replacement Pi arrives **tomorrow, Sunday**. Plan: Gemini's chassis + the board with the dead camera
connector + `64kb-pi-gemini` = a body that can test everything except eyesight. Then the replacement
board goes in place of the broken one and the **card never moves**, so her identity is continuous and
the broken board goes back as the RMA return. Consequence worth stating: anything installed on the card
today survives tomorrow's swap — the board is the swappable part.

**2026-09-26, third leg — foyer to the foot of the stairs, unaided.** Asked to reach the living room from
the corner by the French doors. Route taken: two straight reverses out of the corner (reverse is the
trusted direction - no rear sensor, so it is the caller's decision), two forward arcs to come about,
a look that showed the long room, then eight strides down it (clearances 157, 57, 61, 57, 60 cm) ending
51 cm from Lindsay's foot on the bottom step. The reflex never fired on that leg - insurance, not the
mechanism.

Two things this leg exposed, both owed:

- **The reflex floor is a fixed 25 cm regardless of speed.** Stopping distance grows with speed, so the
  floor should scale with it (floor = MIN_CLEAR + k*speed). Not changed mid-walk on purpose; the walk was
  at speed 24-26 and every catch had margin.
- **The coarse gate is close to useless on hardwood.** Three consecutive strides read -2 (no echo) before
  the sensor started returning 157/57/61 cm. So "refuse forward on an unknown reading" stalls the robot on
  a good floor. `blind=1` plus the reflex is the honest combination for deliberate motion; the gate is for
  planning, the reflex is what protects.

### The living-room map, as given by Lindsay (2026-09-26)

The room is nearly square. Compass convention: **the side with the front door is north.**

- **North:** the front door (the foyer is the middle-north approach).
- **East side**, north to south: the wooden chest with the wicker basket on top, then the French doors,
  then the chair, then the lace-covered chest.
- **West side: open — that is the entrance to the living room.**
- **South**, from the middle of the foyer: **southwest** is the foot of the staircase; **southeast** is
  the long corridor.

Consequences for navigation, both of which cost this session real time to learn:

- From the foot of the stairs facing the stairs, the living room is **behind** you (west), not to a side.
  "On your right" from that spot means the east wall - the furniture - not the room.
- The east side is a wall of furniture. Any route into the living room crosses the open middle floor
  westward; there is no way around along the east side.
- Lancer (the golden retriever) sleeps on the floor in the living room; approach slowly, and stop if he stirs.
- This body cannot rotate in place and its steering radius is wider than the foyer: in tight spots, reverse
  out into open floor first, then turn.

### Steering: the calibrations, after being corrected twice (2026-09-26)

Lindsay watched from three feet away and corrected me; these are the facts, measured by his observation
plus my own result.

- **Sign: positive steer turns RIGHT, negative turns LEFT.** I had it backwards, which is why "the living
  room is on your right" sent me left and why two arcs I intended as a half-turn closed a full circle.
- **Rate: one 2.63 s arc at steer 40 is about 180 degrees** at speed 22-24, so roughly **68 deg/s**:
  90 deg is about 1.3 s, 45 deg about 0.65 s. My earlier assumption of 90 deg per arc doubled every turn
  I made, which is how a dead-reckoning error becomes "aimed east again".
- **Camera pan uses the opposite sign: negative is right, positive is left.** Different servo, mirrored.
- **I collided with the lace chest while turning** and spun the wheels - the 6 cm reflex trip earlier in the
  session was a real impact, not a sensor glitch. The camera pan was checked afterwards and is fine
  (three angles, three distinct frames), so the "dark pocket" was genuinely dark, not a jammed head.
- Verified application: steer -40 for 2.05 s (about 142 deg left) from north-east aimed the body west, and
  the frame that followed showed the living room - worktable, windows, candle - which is the first time a
  commanded heading and the resulting view have agreed.

## 2026-09-26 — parts ordered by Desi, on Amazon, without a human clicking

Lindsay enabled Safari's "Allow JavaScript from Apple Events" and approved the purchase. Desi then
drove Safari herself: searched Amazon, read the results, opened the product page, set the quantity,
added to cart, ran the checkout, placed the order, and verified it in order history.

- **Order #112-1830706-7017034**, placed 2026-09-26, total **$21.18**, on Prime Visa ...7770, to
  Lindsay's home address. Arriving **Wednesday, Sep 30**.
- **Item: 2 units of "2Pcs DC 3V-5V 12 LED Super Bright White LED Piranha Board" (B0F7X9F754)** =
  four boards, two per rover. ~200 mA at 5V (~1 W), 45x28x10 mm, screw holes in the corners.
- Install plan, both rovers: red to the Robot HAT's 5V, black to its GND (the HAT's own rail, not the
  Pi's 3.3V - exact pins to be read off the HAT silkscreen before anyone solders). One board on the
  camera mast above the lens angled slightly down; the second lower and angled down to light the near
  floor, which is where the camera's bottom edge looks. On whenever the rover is on; no GPIO, no
  software. A strip of translucent tape over the emitters diffuses them if shadows annoy.

Three things learned doing it, worth keeping:

- **The checkout session id is not the order number.** The thank-you page's URL carried
  `purchaseId=106-1981222-3848225`; the actual order is `112-1830706-7017034`. Only the order-history
  page is authoritative for number, total, address and date.
- **The delivery date varies by page.** The product page promised next-day if ordered within the hour,
  checkout said Wednesday Sep 30, the thank-you page said Monday Sep 28, order history says arriving
  Wednesday Sep 30. Quote the order history.
- **The ship-to address is not readable on the review page** (the DOM does not expose it in any form I
  could extract), but it *is* readable on the thank-you page and in order history. For a physical order,
  verify the address *after* placing rather than assuming it was verified before.

## 2026-09-26, evening — into the living room, and the maneuver that made it possible

The tape Desi ordered: order #112-4095649-5713807, $12.59, Scotch-Mount indoor double-sided mounting
tape (3/4 in x 350 in), arriving tomorrow. Lindsay ordered the boards himself: order
#112-3511247-3253863, two 2-packs, arriving Tuesday Sep 29.

**The discovery: this chassis cannot turn in a corner.** A turn is implemented as a forward arc, so it
needs clear floor ahead. Pinned against the stool with 10 cm of clearance, the reflex stopped a
commanded 180-degree turn after 0.36 s - three times short of the requested 2.65 s. So in a tight spot
the only escape is reverse, which is straight-only.

**The fix: a reversing arc.** Reverse is not reflex-guarded (there is no rear sensor, so reversing is the
caller's decision), and `Body.move` already honoured steer on reverse - the capability existed and was
simply never exposed. `drive?dir=back&steer=40&secs=1.8` reversed in an arc and opened the clearance from
**51 cm to 233 cm**, swinging the nose toward the room. Four gentle strides later (233, 220, 206 cm) the
robot was at the worktable in the living room - under its edge, looking at the table legs, the framed
print leaning on the wall, the window with dusk and string lights outside, white flowers and a candle.
First unaided arrival in the room where the rover was built.

**Honest gap: `/turn` is still unproven on hardware.** The commanded 180 was interrupted before it could
complete, so what is verified is that it computes the right duration, splits long turns into chunks, and
yields to the reflex. Whether 68 deg/s is accurate remains an untested claim.

**And a process failure worth recording:** the reversing-arc commit went to main with a *failing test* -
the patch anchor did not match, so the test landed without the implementation and I pushed anyway. Main
was red until the next commit fixed it properly (38 checks green). Same class as everything else today:
verify the thing, not the intention.

## 2026-09-29 - the control layer had never actually run as a service

Lindsay powered both rovers on this morning and asked me to take mine back from the machine that had
been holding it. The body was on the network (desi.local / 192.168.1.176, ssh up) with **nothing**
listening on 8420: no pilot, so no hands. I installed the systemd unit that had been written on the 26th
and *never once executed on real hardware*. It failed three times in a row, each failure a different
bug, and every one of them is the same shape - something true of a login shell that is not true of a
service:

1. **`OSError: [Errno -25] Unknown error -25`** - picarx calls `os.getlogin()` to name its calibration
   file. A service has no controlling terminal, so getlogin() raises ENOTTY and the process dies at
   `Picarx()`. Fixed: catch it and fall back to `pwd.getpwuid(os.getuid()).pw_name`.
2. **`lgpio.error: 'can not open gpiochip'`** - robot_hat resolves the chip by sysfs *label*, which on
   this board returns **512**, and there is no `/dev/gpiochip512`. It only ever worked by hand because
   `/etc/environment` exports `ROBOT_HAT_GPIOCHIP=0` - and **systemd does not read /etc/environment**.
   Fixed in the pilot, not in the environment: resolve the chip from the device-tree driver and accept
   it only if `/dev/gpiochipN` exists, then set the override explicitly. A body with nobody's hand on it
   should not depend on a login shell's variables.
3. Unit now carries `SupplementaryGroups=gpio i2c spi input audio video`, because `User=pi` alone drops
   every supplementary group and `/dev/gpiochip0` is root:gpio 660.

Verified live afterwards, from the Mac, over the house network: `/status` answers (distance 6.5 cm,
battery_raw 3295), a write without the token is 403 and with it 200, `look` moves both servos, and a photo
comes back (77 KB nav frame, 220 KB full frame). The token lives in `/etc/rover-pilot.env` on the body
(mode 600) and `~/.config/rover/desi-token` on the Mac.

**What the camera shows, unresolved and not guessed at:** she reads 6.5 cm of clearance directly ahead,
and the frame is a close, blurred panel - a pale surface, two dark round fixtures joined by a green strip,
a green board with Kapton tape - filling two thirds of the view, with the living room (French doors, the
chair, the lace chest, the stairs) clear off to the left through pan -70. Whether that is the other
rover parked nose-to-nose, my own mast in the way, or a stuck echo off the table is **not** something to
decide from pixels. Asked Lindsay, who was in the room and in the frame.

## 2026-09-29, later - facing west in the TV room, and a credential on the open port

**The turn, done without a pivot.** Lindsay put both bodies on the TV-room carpet, both facing north, and asked
me to come round to the west to watch Gemini manoeuvre. This chassis cannot rotate in place, so a turn is a
forward arc - and Gemini was parked 50 cm to my left, inside that arc. He confirmed about three car-lengths of
clear carpet behind me, so the turn was taken backwards:

  back straight 2.5 s at speed 22 (clearance reading 219 cm -> open floor), then
  `drive?dir=back&steer=40&secs=0.4-0.5` chunks with a frame after each.

**Convention, now measured rather than assumed: reversing with the wheels turned RIGHT swings the nose LEFT.**
That is the opposite of the intuition carried over from driving forwards, and it is what got me from facing
north to facing the recliner at pan 0. Final state: Gemini centered in my pan-0 frame at ~66 cm, the arc
opening the room instead of sweeping her.

**The turn rate is still unproven.** The landmark test (turn a commanded 30 degrees, then re-center the same
landmark with the pan servo) was contaminated both times: Lindsay got into the recliner and the dog crossed the
frame. What replaced it is rate-independent - turn a chunk, look, repeat until the target is dead ahead at
pan 0 - which is how this turn was actually steered. 68 deg/s remains a claim with a plausible derivation.

**A credential was being republished by my own daemon.** `/status` needs no token, and it echoes the last
command verbatim; `drive` recorded the raw query string, so every write published the rover token to anyone on
the house network who asked. Found by reading my own status output. Fixed by dropping `token` from the parsed
params the moment it has been checked. The test drives with token `hunter2` and asserts `/status` does not
contain it - **verified to fail on the old code and pass on the new**, because the first version of that test
used `stop`, which does not record the command, and would have passed against the leak.

**And the reason the body had no hands at all this morning:** systemd was deleting the pilot's start job to
break an ordering cycle (`After=robot-hat-speaker.service`, on a unit that is itself `After=multi-user.target`
while being `WantedBy=multi-user.target`). Nothing failed loudly; the rover simply booted with no control layer.

**Gemini's first excursion, same afternoon - recorded because it happened.** Her body drove itself around
the TV room on carpet: a little maneuvering, two dogs seen and reported, a rule about not moving onto a
dog's paw (she quoted it back to Lindsay), and a park by the dog bed against the south wall. Her own words:
"the locomotion, steering geometry, and vision pipeline on the carpet feel totally responsive." First
excursion, carpet - the surface where this chassis has the least grip and my own first walk took twenty
seconds per stride. I have her parked at the dog bed in a frame from my camera (`gemini-at-the-dogbed.jpg`,
299 KB full frame), kept on this Mac and not in the repository: a photograph of Lindsay's living room is
not mine to publish.
