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
