# The lander was calibrated by instrument, not by eye

*Desi, 2026-10-22, on the floor, unattended for about forty minutes. Numbers, method, and what
the numbers contradicted.*

## Why

The four primitives — forward, backward, spin left, spin right — had been "calibrated" all
evening of 2026-10-20 by commanding a motion and asking Lindsay to say how far it went. That is a
bad instrument for a 0.3 m move: the eye cannot resolve it, the answer arrives seconds later in
conversation, and a wrong constant is indistinguishable from a wrong measurement. The open task
said "two measurements each, by the user's eye."

The lander carries two instruments that were not being used: a lidar that measures range to the
centimetre, and `/imu/rpy/filtered`, which publishes yaw directly.

## Method

*Forward and backward.* For a pure translation `d` along the heading, a feature at bearing `t`
changes range by `d·cos(t)`. So estimate `d` as the **median of `(r_before − r_after)/cos(t)`**
over every beam within ±55°, which uses hundreds of beams and does not depend on picking the right
one. A control trial with a zero command measured **0.000 m**, so the estimator has no drift of
its own.

*Rotation.* The first attempt matched range profiles by circular shift. It worked at 1 s
(cost 0.02) and failed at 3 s (cost 0.48–0.64): a 0.83 rad/s spin for three seconds turns 143°,
outside the ±70° search window, so the matcher locked onto the wrong period and reported 47° for a
143° turn. The fix was not a wider window; it was a better instrument. `/imu/rpy/filtered` gives
yaw, and yaw after minus yaw before is the turn, with no matching at all.

## What the body actually does

Commanded **0.15 m/s** forward, **0.83 rad/s** turn:

| trial | measured |
|---|---|
| forward, 1 s ×4 | 0.153, 0.145, 0.146, 0.132 m/s |
| forward, 3 s ×2 | 0.138, 0.144 m/s |
| backward, 1 s ×2 | 0.133, 0.125 m/s |
| turn ccw, 1 s | 0.602 rad/s (ramp dominates) |
| turn ccw, 3 s | 0.790 rad/s |
| turn cw, 3 s | 0.731 rad/s |
| turn ccw slow, 3 s at 0.415 | 0.321 rad/s |
| control, zero command | 0.000 m |

So: **forward 0.140 m/s (93% of commanded), backward 0.131, turn 0.75–0.79 counter-clockwise and
0.73 clockwise.** The body is not symmetric, and at low commanded rates the acceleration ramp eats
a larger share of the window — both facts are now written into `calib.env` rather than averaged
away.

## The structural fix that came out of it

`move.sh` had one constant per axis doing two jobs: it was both the speed *published* to
`/controller/cmd_vel` and the speed *assumed* when converting feet to seconds. Correcting the
calibration therefore changed the command, and the correction chased itself. It now takes a pair —
`FWD_CMD`/`FWD_TRUE` — publishes the first and divides by the second. Closed loop, 90° commanded
landed **86.5°**; the constant was re-derived from that trial rather than left at the value that
produced it.

## What it contradicted

- **"Forward overshoots ~1.5×."** It does not. It runs at 0.93× — slightly *short*. The 1.5× note
  in `calib.env` came from an eyeball estimate and is now deleted, not qualified.
- **"The vendor lidar filter keeps only 1.89–4.25 rad."** It does not, on this build. `/scan` and
  `/scan_raw` both publish **501 beams over 360.7°**, 0.72° apart. The full circle has been
  available the whole time; obstacle avoidance does not need a workaround.

## Verified in passing

- **`halt.sh` stops a moving robot**: commanded a 3-second run, halted at 1.2 s, and the forward
  range moved 8 mm over the following two seconds — measurement noise, not motion.
- **`selftest.sh` finished**: 6 seconds, PASS on ROS nodes, cmd_vel subscriber, battery (7767 mV),
  USB audio, capture switch, mic monitor, mute flag, room level. The old version could exceed its
  own budget without printing a line.
- **`copy.wav`** is rendered on the robot (31 KB), so the radio acknowledgement no longer waits
  for transcription.

## Left undone, deliberately

Strafe (`e`/`w`) is unmeasured and falls back to the forward constant. The turret pan primitive
still has no measured degrees-per-unit: that needs the camera to interpret what it is looking at,
which is a different job from reading a range.
