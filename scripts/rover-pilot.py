#!/usr/bin/env python3
"""rover-pilot — the control layer for a Picar-X body driven by a model over the network.

Written after the first walk (2026-09-26), where two defects cost the walk its fluidity:

  1. SAFETY. The first pilot refused forward motion only when 0 < distance < 25 cm. On carpet the
     ultrasonic returns -2 (no echo), the test passed, and it would have driven blind. Here, a
     missing or implausible reading REFUSES forward motion unless the caller explicitly says blind=1.
  2. LATENCY. One ssh per command plus a file to poll cost seconds per half-second of wheel. This
     is a small HTTP service instead: one request per action, a persistent link, and /status cheap
     enough to poll while moving.

Every move is bounded (speed <= 40, duration <= 3.0 s) and every move runs in a thread with a
hard stop, so a lost connection cannot leave the motors running.

  python3 rover-pilot.py                 # real hardware, binds 127.0.0.1
  python3 rover-pilot.py --token SECRET  # also reachable off-box; every write needs ?token=
  python3 rover-pilot.py --dry           # no hardware: exercises the protocol, logs motion
"""
import argparse
import json
import os
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FRAMES = '/tmp/walk'
MIN_CLEAR = 25          # cm
MAX_SPEED = 40
MAX_MOVE = 3.0          # seconds
# Calibrated 2026-09-26 by Lindsay's observation from three feet away: one 2.63 s arc at steer 40
# is about 180 degrees at speed 22-24, so ~68 deg/s. Positive steer is RIGHT, negative is LEFT.
DEG_PER_SEC = 68.0
TURN_STEER = 40
VOICE = os.path.expanduser('~/.piper_models/en_US-lessac-medium.onnx')

MOTION = {}             # last command, for /status
BIG = 1000.0            # a reading this large is "no return"


class Reflex(threading.Thread):
    """The fast layer: while the motors are turning, check the way ahead ten times a second and stop
    them the moment it closes. The first walk only checked *between* steps, which is fine at a
    creep and useless at speed. Unknown readings do not trip it (that is the coarser gate's job),
    but a real obstacle does."""

    def __init__(self, floor=MIN_CLEAR):
        super().__init__(daemon=True)
        self.floor = floor
        self.tripped = None
        self._on = True

    def halt(self):
        self._on = False

    def run(self):
        while self._on:
            d = BODY.distance()
            if d > 0 and d < BIG and d < self.floor:
                self.tripped = d
                try:
                    BODY.stop()
                except Exception:
                    pass
                return
            time.sleep(0.1)


class Body:
    """Hardware, or a stand-in that logs. The protocol is identical either way."""

    def __init__(self, dry=False):
        self.dry = dry
        self.pan = self.tilt = self.steer = 0
        self.moving = None
        self.last_reflex = None
        if not dry:
            from picarx import Picarx          # noqa: PLC0415
            from robot_hat import ADC          # noqa: PLC0415
            self.px = Picarx()
            time.sleep(0.3)
            # constructing Picarx resets the HAT's MCU, which mutes the speaker amp
            subprocess.run(['/usr/local/bin/robot_hat', 'enable_speaker'],
                           capture_output=True, text=True)
            self.adc = ADC('A4')
            self.px.set_cam_pan_angle(0)
            self.px.set_cam_tilt_angle(0)

    # --- sensing ------------------------------------------------------------------
    def distance(self):
        if self.dry:
            return float(MOTION.get('mock_distance', 120.0))
        try:
            return float(self.px.get_distance())
        except Exception:
            return -2.0

    def grayscale(self):
        if self.dry:
            return [1500, 1500, 1500]
        try:
            return list(self.px.get_grayscale_data())
        except Exception:
            return []

    def battery(self):
        if self.dry:
            return 3280
        try:
            return self.adc.read()
        except Exception:
            return None

    def clear_ahead(self):
        """(ok, why). Unknown is not clear."""
        d = self.distance()
        if d <= 0 or d >= BIG:
            return False, 'no distance reading (%s)' % d
        if d < MIN_CLEAR:
            return False, 'too close (%s cm)' % d
        return True, '%.0f cm' % d

    # --- acting -------------------------------------------------------------------
    def look(self, pan, tilt):
        self.pan, self.tilt = pan, tilt
        if not self.dry:
            self.px.set_cam_pan_angle(pan)
            self.px.set_cam_tilt_angle(tilt)

    def move(self, direction, steer, speed, secs):
        speed = max(0, min(int(speed), MAX_SPEED))
        secs = max(0.0, min(float(secs), MAX_MOVE))
        self.steer = steer
        self.moving = direction
        # FORWARD ONLY. On 2026-09-26 the reflex watched the front sensor and cut a REVERSE short:
        # it stopped the robot backing away from the very obstacle it was guarding. There is no rear
        # sensor, so reverse has to be trusted to the caller - who is the one who chose to reverse.
        reflex = Reflex() if direction == 'fwd' else None
        if reflex:
            reflex.start()
        t0 = time.time()
        try:
            if not self.dry:
                self.px.set_dir_servo_angle(steer)
                time.sleep(0.2)
                (self.px.forward if direction == 'fwd' else self.px.backward)(speed)
            deadline = t0 + secs
            while time.time() < deadline and not (reflex and reflex.tripped):
                time.sleep(0.05)
        finally:
            self.stop()
            if reflex:
                reflex.halt()
        self.last_reflex = reflex.tripped if reflex else None
        return speed, round(time.time() - t0, 2)

    def stop(self):
        self.moving = None
        if not self.dry:
            self.px.stop()
            self.px.set_dir_servo_angle(0)
        self.steer = 0

    def photo(self, name, size='full'):
        """'nav' is for looking while moving: small and fast, ~1 s on a Zero 2 W instead of ~3 s."""
        os.makedirs(FRAMES, exist_ok=True)
        path = os.path.join(FRAMES, (name or 'frame') + '.jpg')
        if self.dry:
            with open(path, 'wb') as f:
                f.write(b'\xff\xd8\xff\xd9')          # a minimal JPEG marker pair
            return path
        if size == 'nav':
            args = ['rpicam-still', '-n', '--width', '640', '--height', '480',
                    '--timeout', '300', '-o', path]
        else:
            args = ['rpicam-still', '-n', '--width', '1296', '--height', '972',
                    '--timeout', '1200', '-o', path]
        subprocess.run(args, capture_output=True, text=True)
        return path if os.path.exists(path) else None

    def say(self, text):
        if self.dry:
            return 'dry: would speak %d chars' % len(text)
        try:
            wav = '/tmp/say.wav'
            p = subprocess.run(['/usr/local/bin/piper', '-m', VOICE, '-f', wav],
                               input=text, capture_output=True, text=True, timeout=60)
            if p.returncode != 0:
                return 'speak failed: %s' % (p.stderr or '')[:120]
            subprocess.Popen(['aplay', '-q', wav], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return 'speaking %d chars' % len(text)
        except Exception as e:
            return 'speak error: %r' % e


BODY = None
LOCK = threading.Lock()


def behaviour_advance(speed, secs_per_step, steps, photos, tag, size, blind):
    """One request, many actions. Creep forward in bounded steps, stopping early on an obstacle or
    a lost reading, photographing each step. This is the fluidity fix: the slow part of the first
    walk was never the wheels, it was me deliberating between every half-second of them."""
    events = []
    for i in range(steps):
        ok, why = BODY.clear_ahead()
        if not ok and not blind:
            events.append({'step': i, 'refused': why})
            break
        with LOCK:
            BODY.move('fwd', 0, speed, secs_per_step)
        ev = {'step': i, 'secs': min(float(secs_per_step), MAX_MOVE), 'clearance': why}
        if BODY.last_reflex:
            ev['stopped_by'] = 'reflex %.0f cm' % BODY.last_reflex
        if photos:
            ev['photo'] = BODY.photo('%s-%02d' % (tag, i), size)
        events.append(ev)
        if BODY.last_reflex:
            break
    return events


def behaviour_scan(pan_from, pan_to, step, tilt, photos, tag, size):
    """Sweep the camera through a range, photographing each stop. One request for a whole look."""
    events = []
    angle = int(float(pan_from))
    limit = int(float(pan_to))
    tilt = int(float(tilt))
    step = max(1, abs(int(float(step))))
    sign = 1 if limit >= angle else -1
    while (sign > 0 and angle <= limit) or (sign < 0 and angle >= limit):
        BODY.look(angle, tilt)
        time.sleep(0.35)
        ev = {'pan': angle, 'tilt': tilt}
        if photos:
            ev['photo'] = BODY.photo('%s-p%+03d' % (tag, angle), size)
        events.append(ev)
        angle += sign * step
    return events


def guarded_move(direction, steer, speed, secs_raw, blind):
    """Refuse unknown clearance. Run the move under the lock with a hard stop at 2x duration."""
    secs = secs_raw
    if direction == 'fwd' and not blind:
        ok, why = BODY.clear_ahead()
        if not ok:
            return 409, {'refused': 'forward', 'because': why}
    with LOCK:
        speed, actual = BODY.move(direction, steer, speed, secs)
    return 200, {'moved': direction, 'steer': steer, 'speed': speed, 'secs': actual,
                 'secs_requested': min(float(secs_raw), MAX_MOVE),
                 'stopped_by': 'reflex %.0f cm' % BODY.last_reflex if BODY.last_reflex else None,
                 'clearance_before': None if blind else BODY.clear_ahead()[1]}


class Handler(BaseHTTPRequestHandler):
    server_version = 'rover-pilot/1'

    def log_message(self, fmt, *a):                       # quiet by default
        pass

    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
        verb = u.path.strip('/') or 'status'
        write = verb != 'status'

        if write and TOKEN and q.get('token') != TOKEN:
            return self._send(403, {'error': 'token required for write commands'})

        try:
            if verb == 'status':
                d = BODY.distance()
                return self._send(200, {'distance': d, 'grayscale': BODY.grayscale(),
                                        'battery_raw': BODY.battery(), 'pan': BODY.pan,
                                        'tilt': BODY.tilt, 'moving': BODY.moving,
                                        'dry': BODY.dry, 'last': MOTION.get('last'),
                                        'clear_ahead': BODY.clear_ahead()})
            if verb == 'look':
                BODY.look(int(float(q.get('pan', 0))), int(float(q.get('tilt', 0))))
                MOTION['last'] = 'look %s %s' % (q.get('pan', 0), q.get('tilt', 0))
                return self._send(200, {'pan': BODY.pan, 'tilt': BODY.tilt})
            if verb == 'turn':                      # turn?deg=90&dir=left - calibrated, not guessed
                deg = float(q.get('deg', 90))
                sign = -1 if q.get('dir', 'left') in ('left', 'l', '-1') else 1
                speed = q.get('speed', 22)
                left = abs(deg) / DEG_PER_SEC
                chunks = []
                while left > 0.01:
                    piece = min(left, 2.9)
                    code, payload = guarded_move('fwd', sign * TURN_STEER, speed, piece, True)
                    chunks.append(payload)
                    left -= piece
                    if code != 200 or payload.get('stopped_by'):
                        break
                MOTION['last'] = 'turn %s %s' % (deg, q.get('dir', 'left'))
                return self._send(200, {'turned_deg': deg * (1 if sign > 0 else -1),
                                        'deg_per_sec': DEG_PER_SEC, 'chunks': chunks})
            if verb in ('fwd', 'back'):
                code, payload = guarded_move(verb, int(float(q.get('steer', 0))),
                                             q.get('speed', 18), q.get('secs', 0.6),
                                             q.get('blind') == '1')
                MOTION['last'] = '%s %s' % (verb, q)
                return self._send(code, payload)
            if verb == 'drive':
                # dir=back: a reversing arc. A forward arc needs clear floor ahead - in a corner the
                # reflex stops it almost immediately - and reverse is not reflex-guarded, so this is
                # the maneuver that gets this chassis out of a tight spot.
                _rev = q.get('dir', 'fwd') in ('back', 'b', 'reverse')
                code, payload = guarded_move('back' if _rev else 'fwd', int(float(q.get('steer', 0))),
                                             q.get('speed', 18), q.get('secs', 0.8),
                                             q.get('blind') == '1')
                MOTION['last'] = 'drive %s' % q
                return self._send(code, payload)
            if verb == 'advance':
                ev = behaviour_advance(q.get('speed', 28), q.get('secs', 0.8),
                                       int(float(q.get('steps', 6))), q.get('photos', '1') == '1',
                                       q.get('tag', 'adv'), q.get('size', 'nav'),
                                       q.get('blind') == '1')
                MOTION['last'] = 'advance %s step(s)' % len(ev)
                return self._send(200, {'steps': ev, 'photos': [e['photo'] for e in ev if e.get('photo')]})
            if verb == 'scan':
                ev = behaviour_scan(q.get('from', -60), q.get('to', 60), q.get('step', 30),
                                    q.get('tilt', 10), q.get('photos', '1') == '1',
                                    q.get('tag', 'scan'), q.get('size', 'nav'))
                MOTION['last'] = 'scan %d stop(s)' % len(ev)
                return self._send(200, {'stops': ev, 'photos': [e['photo'] for e in ev if e.get('photo')]})
            if verb == 'photo':
                p = BODY.photo(q.get('name'), q.get('size', 'full'))
                return self._send(200 if p else 500, {'path': p, 'bytes':
                                                      (os.path.getsize(p) if p else 0)})
            if verb == 'say':
                MOTION['last'] = 'say'
                return self._send(200, {'result': BODY.say(q.get('text', ''))})
            if verb == 'mock':
                if not BODY.dry:
                    return self._send(403, {'error': 'mock is dry-run only'})
                MOTION['mock_distance'] = float(q.get('distance', 120))
                return self._send(200, {'mock_distance': MOTION['mock_distance'],
                                        'clear_ahead': BODY.clear_ahead()})
            if verb == 'stop':
                BODY.stop()
                return self._send(200, {'stopped': True})
            if verb == 'quit':
                BODY.stop()
                JSONNED = {'stopping': True, 'centred': True}
                self._send(200, JSONNED)
                threading.Thread(target=lambda: (time.sleep(0.4), os._exit(0)), daemon=True).start()
                return
            return self._send(404, {'error': 'unknown command', 'verbs': [
                'status', 'look', 'fwd', 'back', 'drive', 'advance', 'scan', 'photo', 'say',
                'turn', 'stop', 'quit', 'mock']})
        except Exception as e:
            try:
                BODY.stop()
            except Exception:
                pass
            return self._send(500, {'error': repr(e)})


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8420)
    ap.add_argument('--token', default=os.environ.get('ROVER_TOKEN', ''))
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--host', default=None)
    a = ap.parse_args()
    TOKEN = a.token
    host = a.host or ('0.0.0.0' if TOKEN else '127.0.0.1')
    BODY = Body(dry=a.dry)
    print('rover-pilot on %s:%d dry=%s token=%s' % (host, a.port, a.dry, bool(TOKEN)), flush=True)
    ThreadingHTTPServer((host, a.port), Handler).serve_forever()
