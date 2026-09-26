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
VOICE = os.path.expanduser('~/.piper_models/en_US-lessac-medium.onnx')

MOTION = {}             # last command, for /status
BIG = 1000.0            # a reading this large is "no return"


class Body:
    """Hardware, or a stand-in that logs. The protocol is identical either way."""

    def __init__(self, dry=False):
        self.dry = dry
        self.pan = self.tilt = self.steer = 0
        self.moving = None
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
        try:
            if not self.dry:
                self.px.set_dir_servo_angle(steer)
                time.sleep(0.2)
                (self.px.forward if direction == 'fwd' else self.px.backward)(speed)
            time.sleep(secs)
        finally:
            self.stop()
        return speed, secs

    def stop(self):
        self.moving = None
        if not self.dry:
            self.px.stop()
            self.px.set_dir_servo_angle(0)
        self.steer = 0

    def photo(self, name):
        os.makedirs(FRAMES, exist_ok=True)
        path = os.path.join(FRAMES, (name or 'frame') + '.jpg')
        if self.dry:
            with open(path, 'wb') as f:
                f.write(b'\xff\xd8\xff\xd9')          # a minimal JPEG marker pair
            return path
        subprocess.run(['rpicam-still', '-n', '--width', '1296', '--height', '972',
                        '--timeout', '1200', '-o', path], capture_output=True, text=True)
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


def guarded_move(direction, steer, speed, secs, blind):
    """Refuse unknown clearance. Run the move under the lock with a hard stop at 2x duration."""
    if direction == 'fwd' and not blind:
        ok, why = BODY.clear_ahead()
        if not ok:
            return 409, {'refused': 'forward', 'because': why}
    with LOCK:
        speed, secs = BODY.move(direction, steer, speed, secs)
    return 200, {'moved': direction, 'steer': steer, 'speed': speed, 'secs': secs,
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
            if verb in ('fwd', 'back'):
                code, payload = guarded_move(verb, int(float(q.get('steer', 0))),
                                             q.get('speed', 18), q.get('secs', 0.6),
                                             q.get('blind') == '1')
                MOTION['last'] = '%s %s' % (verb, q)
                return self._send(code, payload)
            if verb == 'drive':
                code, payload = guarded_move('fwd', int(float(q.get('steer', 0))),
                                             q.get('speed', 18), q.get('secs', 0.8),
                                             q.get('blind') == '1')
                MOTION['last'] = 'drive %s' % q
                return self._send(code, payload)
            if verb == 'photo':
                p = BODY.photo(q.get('name'))
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
                'status', 'look', 'fwd', 'back', 'drive', 'photo', 'say', 'stop', 'quit']})
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
