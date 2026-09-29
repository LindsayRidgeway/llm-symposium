#!/usr/bin/env python3
"""Tests for scripts/rover-pilot.py in --dry mode: the protocol, and the safety rule.

The rule under test is the one that was WRONG on the first walk (2026-09-26): the pilot refused
forward motion only when 0 < distance < 25 cm, so a missing reading (-2, the ultrasonic's no-echo
value on carpet) read as "clear" and it would have driven blind. Here: unknown or implausible
readings must refuse forward motion, and only an explicit blind=1 may override.

Run:  python3 tests/test_rover_pilot.py
"""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = os.path.join(ROOT, 'scripts', 'rover-pilot.py')
checks = []


def check(name, ok, detail=''):
    checks.append(ok)
    print('%-4s %s%s' % ('OK' if ok else 'FAIL', name, ('  -- ' + str(detail)) if detail else ''))


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def get(port, verb, expect=None, token=None, **params):
    q = '&'.join('%s=%s' % (k, urllib.parse.quote(str(v))) for k, v in params.items())
    if token:
        q = (q + '&token=' + token) if q else 'token=' + token
    url = 'http://127.0.0.1:%d/%s%s' % (port, verb, ('?' + q) if q else '')
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            body = json.loads(r.read().decode() or '{}')
            return r.status, body
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or '{}')
        except Exception:
            return e.code, {}


import urllib.parse  # noqa: E402  (used above)

port, tokport = free_port(), free_port()
p = subprocess.Popen([sys.executable, PILOT, '--dry', '--port', str(port)],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
pt = subprocess.Popen([sys.executable, PILOT, '--dry', '--port', str(tokport), '--token', 'hunter2'],
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    for _ in range(60):
        try:
            get(port, 'status')
            get(tokport, 'status')
            break
        except Exception:
            time.sleep(0.25)

    st, body = get(port, 'status')
    check('status answers', st == 200 and 'distance' in body, st)
    check('status reports it is dry', body.get('dry') is True)
    check('status carries clear_ahead', isinstance(body.get('clear_ahead'), list)
          and len(body['clear_ahead']) == 2, body.get('clear_ahead'))

    st, body = get(port, 'nonsense')
    check('unknown verb is 404 and lists verbs', st == 404 and 'verbs' in body, st)

    # --- the rule ------------------------------------------------------------------
    get(port, 'mock', distance=-2)
    st, body = get(port, 'fwd', speed=20, secs=0.2)
    check('NO READING (-2): forward refused', st == 409 and body.get('refused') == 'forward',
          body)
    st, body = get(port, 'drive', steer=20, speed=20, secs=0.2)
    check('NO READING (-2): drive refused', st == 409, body)

    get(port, 'mock', distance=10)
    st, body = get(port, 'fwd', speed=20, secs=0.2)
    check('TOO CLOSE (10 cm): forward refused', st == 409, body)

    get(port, 'mock', distance=120)
    st, body = get(port, 'fwd', speed=20, secs=0.2)
    check('CLEAR (120 cm): forward allowed', st == 200 and body.get('moved') == 'fwd', body)

    get(port, 'mock', distance=-2)
    st, body = get(port, 'fwd', speed=20, secs=0.2, blind=1)
    check('BLIND=1 overrides the refusal explicitly', st == 200 and body.get('moved') == 'fwd', body)

    get(port, 'mock', distance=-2)
    st, body = get(port, 'back', speed=20, secs=0.2)
    check('reverse is allowed with no forward reading', st == 200, body)

    st, body = get(port, 'fwd', speed=900, secs=0.1, blind=1)
    check('speed is clamped to MAX_SPEED', st == 200 and body.get('speed') == 40, body.get('speed'))
    st, body = get(port, 'fwd', speed=20, secs=99, blind=1)
    check('duration request is clamped to MAX_MOVE',
          st == 200 and body.get('secs_requested') == 3.0, body.get('secs_requested'))
    check('elapsed is reported separately and stays near the clamp',
          st == 200 and 2.5 <= body.get('secs', 0) <= 3.5, body.get('secs'))

    # --- behaviours: one request, many actions --------------------------------------
    get(port, 'mock', distance=120)
    st, body = get(port, 'advance', steps=3, secs=0.1, speed=25, size='nav', tag='t-adv')
    check('advance completes its steps', st == 200 and len(body.get('steps', [])) == 3, body)
    check('advance photographs each step', len(body.get('photos', [])) == 3, body.get('photos'))
    check('advance reports clearance per step',
          all('clearance' in e for e in body.get('steps', [])), body.get('steps'))

    get(port, 'mock', distance=10)
    st, body = get(port, 'advance', steps=3, secs=0.1, speed=25, size='nav', tag='t-block')
    check('advance stops early on an obstacle',
          st == 200 and len(body.get('steps', [])) == 1 and 'refused' in body['steps'][0], body)

    get(port, 'mock', distance=-2)
    st, body = get(port, 'advance', steps=3, secs=0.1, speed=25, size='nav', tag='t-blind')
    check('advance refuses to start with no reading',
          st == 200 and len(body.get('steps', [])) == 1 and 'refused' in body['steps'][0], body)

    get(port, 'mock', distance=120)
    st, body = get(port, 'scan', **{'from': -60, 'to': 60, 'step': 30, 'tilt': 10,
                                    'size': 'nav', 'tag': 't-scan'})
    check('scan sweeps the requested stops', st == 200 and len(body.get('stops', [])) == 5, body)
    check('scan photographs each stop', len(body.get('photos', [])) == 5, body.get('photos'))
    st, body = get(port, 'scan', **{'from': 30, 'to': -30, 'step': 30, 'size': 'nav',
                                    'tag': 't-scanb', 'photos': 0})
    check('scan works in reverse and can skip photos',
          st == 200 and len(body.get('stops', [])) == 3 and not body.get('photos'), body)

    # --- the reflex layer: the way ahead closes WHILE the motors are turning ---------
    get(port, 'mock', distance=10)
    st, body = get(port, 'fwd', speed=25, secs=2.0, blind=1)
    check('reflex cuts a blind move short when the way closes',
          st == 200 and body.get('secs', 99) < 1.0 and body.get('stopped_by'), body)

    get(port, 'mock', distance=120)
    st, body = get(port, 'fwd', speed=25, secs=0.4, blind=1)
    check('reflex leaves a clear move alone', st == 200 and not body.get('stopped_by'), body)

    get(port, 'mock', distance=10)
    st, body = get(port, 'back', speed=25, secs=0.5)
    check('reverse is NOT cut short by the front reflex',
          st == 200 and not body.get('stopped_by') and body.get('secs', 0) >= 0.4, body)

    st, body = get(port, 'photo', name='pilot-nav', size='nav')
    check('nav photo writes a file', st == 200 and body.get('bytes', 0) > 0, body)

    # --- reversing arc: the tight-corner maneuver ------------------------------------
    get(port, 'mock', distance=10)
    st, body = get(port, 'drive', steer=40, speed=20, secs=0.4, dir='back')
    check('drive dir=back moves backward with steer, and the reflex does not veto it',
          st == 200 and body.get('moved') == 'back' and body.get('steer') == 40
          and not body.get('stopped_by'), body)

    # --- calibrated turning ---------------------------------------------------------
    get(port, 'mock', distance=200)
    st, body = get(port, 'turn', deg=90, dir='left', speed=22)
    total = sum(c.get('secs', 0) for c in body.get('chunks', []))
    check('turn 90 deg left takes about 1.3 s at the calibrated rate',
          st == 200 and 1.1 <= total <= 1.6, body)
    st, body = get(port, 'turn', deg=360, dir='right', speed=22)
    check('turn 360 deg is split into chunks (never one long move)',
          st == 200 and len(body.get('chunks', [])) >= 2, [c.get('secs') for c in body.get('chunks', [])])
    check('every chunk went right (positive steer)',
          st == 200 and all(c.get('steer', 0) > 0 for c in body.get('chunks', [])), body)

    # --- the rest of the protocol ---------------------------------------------------
    st, body = get(port, 'look', pan=-30, tilt=15)
    check('look sets pan and tilt', st == 200 and body.get('pan') == -30 and body.get('tilt') == 15,
          body)
    st, body = get(port, 'photo', name='pilot-test')
    check('photo writes a file', st == 200 and body.get('bytes', 0) > 0, body)
    st, body = get(port, 'say', text='protocol test')
    check('say reports what it would speak (dry)', st == 200 and 'dry' in str(body.get('result')),
          body)
    st, body = get(port, 'stop')
    check('stop answers', st == 200 and body.get('stopped') is True, body)

    # --- the token ------------------------------------------------------------------
    st, _ = get(tokport, 'stop')
    check('token: write without token is 403', st == 403, st)
    st, _ = get(tokport, 'status')
    check('token: status stays open', st == 200, st)
    st, _ = get(tokport, 'stop', token='hunter2')
    check('token: write with token is 200', st == 200, st)
    # drive is the verb that records the raw query, so it is the one that can leak the credential
    st, _ = get(tokport, 'drive', token='hunter2', dir='fwd', secs=0.1)
    check('token: write with token is 200 (drive)', st == 200, st)
    st, body = get(tokport, 'status')
    check('token: status does not republish it',
          st == 200 and 'hunter2' not in json.dumps(body), body.get('last'))

    st, _ = get(port, 'quit')
    check('quit answers', st == 200, st)
    time.sleep(1.5)
    check('quit exits the process', p.poll() is not None, p.poll())
finally:
    for proc in (p, pt):
        if proc.poll() is None:
            proc.terminate()
    out = ''
    try:
        out = (p.stdout.read() or '')[-400:]
    except Exception:
        pass
    if out.strip():
        print('\n-- pilot output --\n' + out)

print('\n%d checks, %d failed' % (len(checks), checks.count(False)))
sys.exit(1 if checks.count(False) else 0)
