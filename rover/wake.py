#!/usr/bin/env python3
"""rover-wake — give a Picar-X body a turn: her model decides, the body acts, nobody's hand on it.

This is the piece `channels/tasks.md` asked for when it said *"Desi prepares the card image and the
software: a copy of the walk pilot plus the wake harness adapted to her provider, so her body comes
up drivable and talking."* The control layer already exists (`scripts/rover-pilot.py`, an HTTP
service on the body). What was missing is the layer above it: something on the body that reads the
body's own state, asks the model a question, and turns the answer into bounded actions.

The provider is Gemini because the body this is written for is Gemini's. Nothing about the loop is
Gemini-specific except the request shape, which is the one already measured working in this repo
(`experiments/2026-09-15-gemini-scaled-canon-free.py`): `generativelanguage.googleapis.com/v1beta/
models/{model}:generateContent`. DeepSeek's OpenAI-shaped endpoint is supported for the second
experiment — Desi and Gemini on one floor, each in her own body.

  # on the body, with rover-pilot already running (see rover/gemini-card.md)
  GOOGLE_API_KEY=... python3 wake.py --turns 3
  python3 wake.py --turns 1 --provider deepseek --api-key-file /etc/rover-wake.env

  # with no hardware at all: start the pilot dry in another shell, then
  python3 scripts/rover-pilot.py --dry &
  python3 rover/wake.py --turns 2 --provider stub

TWO CONTROL FIXES, ENFORCED HERE AS WELL AS IN THE PILOT (both found on the 2026-09-26 walk):

  1. NO READING MEANS STOP. The pilot already refuses forward motion on an unknown or implausible
     ultrasonic value. This layer refuses it *before sending anything*, so a model that ignores the
     rule in the prompt still cannot drive blind: the harness asks `/status`, and if `clear_ahead`
     is not true the forward verb is never issued. `"blind": true` on an action is the only
     override, it is recorded in the log as such, and it exists because reverse and tight-corner
     maneuvers need it — not because it is a good default.
  2. EVERY COMMAND NEEDS AN ACKNOWLEDGEMENT. On the first walk, writing commands to a single file
     with fixed sleeps let a later command overwrite an unread one: `sense` and a photo were
     silently lost. Here, a command is not finished until the pilot answers 200 *and* the reply
     carries the key that verb is supposed to carry. Anything else — a 409 refusal, a 500, a
     timeout, a 200 with the wrong shape — aborts the rest of the plan and is reported to the model
     on the next turn. Nothing is assumed to have happened because it was sent.

Speech-to-text is OFF and stays off for the Desi-Gemini speech experiment, by the human's
instruction, so a body listening to another body cannot borrow its library. `--listen` exists, it
is explicit, and it refuses to start without an external recognizer command.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_MODEL = {
    "gemini": "gemini-3.8-flash",
    "deepseek": "deepseek-chat",
}
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

# Whose key is whose. Read from the environment, or from a file of KEY=VALUE lines on the body
# (/etc/rover-wake.env) — never hard-coded, and never printed.
KEY_ENV = {"gemini": "GOOGLE_API_KEY", "deepseek": "DEEPSEEK_API_KEY"}

# ---------------------------------------------------------------------------------------------
# The action vocabulary. A model may only ask for these, with these parameters. Everything else
# is rejected and reported back — the body does not run a program the model wrote.
# ---------------------------------------------------------------------------------------------
ACTIONS = {
    "look":    {"pan": (-90, 90), "tilt": (-35, 35)},
    "turn":    {"deg": (-360, 360), "dir": ("left", "right"), "speed": (0, 40)},
    "fwd":     {"steer": (-40, 40), "speed": (0, 40), "secs": (0.05, 3.0)},
    "back":    {"steer": (-40, 40), "speed": (0, 40), "secs": (0.05, 3.0)},
    "drive":   {"steer": (-40, 40), "speed": (0, 40), "secs": (0.05, 3.0),
                "dir": ("fwd", "back")},
    "advance": {"speed": (0, 40), "secs": (0.05, 3.0), "steps": (1, 12),
                "photos": (0, 1), "size": ("nav", "full"), "tag": None},
    "scan":    {"pan_from": (-90, 90), "pan_to": (-90, 90), "step": (5, 90), "tilt": (-35, 35),
                "photos": (0, 1), "size": ("nav", "full"), "tag": None},
    "photo":   {"name": None, "size": ("nav", "full")},
    "say":     {"text": None},
    "stop":    {},
}

# Verbs the no-reading rule gates: those that drive the chassis INTO space it cannot measure.
# `turn` is deliberately NOT here, and that is a decision, not an oversight. Turn is a forward arc,
# but it is a rotation in place, and the pilot already issues its chunks with blind=1 — the one
# maneuver that gets a body off carpet is the one a body on carpet must always be able to make.
# Blocking it here would leave a body whose ultrasonic reads nothing unable to turn round and look
# behind itself. Everything that translates the body forward is gated.
FORWARD = {"fwd", "advance"}

# The harness spells the scan range pan_from/pan_to because `from` is not a Python keyword and
# `**from**` is not a sensible thing to ask a model for. The pilot's own dialect uses from/to.
SCAN_RENAME = {"pan_from": "from", "pan_to": "to"}

# What the pilot's reply must carry for the command to count as acknowledged. Measured off
# scripts/rover-pilot.py, not guessed: each of these is the key that verb always returns on success.
ACK = {"look": "pan", "turn": "turned_deg", "fwd": "moved", "back": "moved", "drive": "moved",
       "advance": "steps", "scan": "stops", "photo": "path", "say": "result", "stop": "stopped"}

LIMIT = 25.0     # cm; the pilot's own MIN_CLEAR, restated so the harness can gate before sending.
BIG = 1000.0     # a reading this large is "no return"


# ---------------------------------------------------------------------------------------------
# The pilot, over HTTP. One class so the tests can substitute it.
# ---------------------------------------------------------------------------------------------
class PilotError(Exception):
    pass


class Pilot:
    """The body's control layer. Every call is a GET with query parameters; every write is
    acknowledged or it is a failure. `timeout` is above the pilot's own MAX_MOVE so a slow
    `advance` is not read as a lost body."""

    def __init__(self, base="http://127.0.0.1:8420", token="", timeout=90):
        self.base = base.rstrip("/")
        self.token = token
        self.timeout = timeout

    def call(self, verb, params=None):
        q = {k: v for k, v in (params or {}).items() if v is not None}
        if self.token:
            q["token"] = self.token
        url = "%s/%s%s" % (self.base, verb, ("?" + urllib.parse.urlencode(q)) if q else "")
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as r:
                return r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:
                return e.code, {}
        except Exception as e:
            raise PilotError("%s on /%s: %s" % (type(e).__name__, verb, e))

    def status(self):
        code, body = self.call("status")
        if code != 200:
            raise PilotError("/status answered HTTP %s" % code)
        return body

    def acked(self, verb, params=None):
        """(ok, payload, why). ok only when the pilot answered 200 AND the verb's own key came
        back. This is control fix 2 — nothing is assumed because it was sent."""
        code, body = self.call(verb, params)
        key = ACK[verb]
        if code == 409:
            return False, body, "refused by the pilot: %s" % (body.get("because") or body.get("refused"))
        if code != 200:
            return False, body, "HTTP %s: %s" % (code, json.dumps(body)[:200])
        if key not in body:
            return False, body, "HTTP 200 but no `%s` in the reply — not acknowledged" % key
        return True, body, ""


# ---------------------------------------------------------------------------------------------
# The rule, at this layer. Pure functions, so the test can pin them without a body.
# ---------------------------------------------------------------------------------------------
def clearance_ok(status):
    """(ok, why) from a /status payload. Unknown is not clear — the same rule as the pilot's,
    applied before anything is sent."""
    d = status.get("distance")
    try:
        d = float(d)
    except (TypeError, ValueError):
        return False, "no distance reading (%s)" % (d,)
    if d <= 0 or d >= BIG:
        return False, "no distance reading (%s)" % d
    if d < LIMIT:
        return False, "too close (%.0f cm)" % d
    return True, "%.0f cm" % d


def validate(action):
    """(ok, cleaned, why). Rejects an unknown verb, an unknown parameter, or a value outside the
    pilot's own bounds — so the model cannot ask for something the body will silently clamp."""
    if not isinstance(action, dict):
        return False, None, "not an object"
    verb = action.get("verb")
    if verb not in ACTIONS:
        return False, None, "unknown verb %r" % (verb,)
    spec = ACTIONS[verb]
    clean = {"verb": verb}
    for k, v in action.items():
        if k == "verb":
            continue
        if k == "blind":
            clean["blind"] = bool(v)
            continue
        if k not in spec:
            return False, None, "%s takes no parameter %r" % (verb, k)
        rule = spec[k]
        if rule is None:                        # free text / free name: length-bound it
            if not isinstance(v, (str, int, float)):
                return False, None, "%s.%s must be text" % (verb, k)
            clean[k] = str(v)[:400]
        elif isinstance(rule, tuple) and len(rule) == 2 and all(isinstance(x, str) for x in rule):
            if str(v) not in rule:
                return False, None, "%s.%s must be one of %s, got %r" % (verb, k, list(rule), v)
            clean[k] = str(v)
        else:
            lo, hi = rule
            try:
                v = float(v)
            except (TypeError, ValueError):
                return False, None, "%s.%s is not a number (%r)" % (verb, k, v)
            if not (lo <= v <= hi):
                return False, None, "%s.%s=%s outside %s..%s" % (verb, k, v, lo, hi)
            # An integral value becomes an int: the pilot reads `photos` as the string "1", so
            # sending 1.0 would silently switch the camera off. Measured, not assumed.
            clean[k] = int(v) if float(v).is_integer() else v
    return True, clean, ""


def forward_blocked(action, status):
    """(blocked, why). The no-reading rule as it applies to one action."""
    verb = action.get("verb")
    moves_forward = verb in FORWARD or (verb == "drive" and action.get("dir", "fwd") != "back")
    if not moves_forward:
        return False, ""
    if action.get("blind"):
        return False, ""
    ok, why = clearance_ok(status)
    return (not ok), why


# ---------------------------------------------------------------------------------------------
# Providers. The only provider-specific code in the file.
# ---------------------------------------------------------------------------------------------
class ProviderError(Exception):
    pass


class GeminiProvider:
    """The shape already measured working in this repository on 2026-09-15."""

    name = "gemini"

    def __init__(self, key, model=None, temperature=0.2, max_tokens=800):
        self.key = key
        self.model = model or DEFAULT_MODEL["gemini"]
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __repr__(self):
        # A key must never appear in a log line or a traceback, and this module logs freely.
        return "<GeminiProvider model=%s key=***>" % self.model

    def ask(self, prompt):
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": self.temperature,
                                 "maxOutputTokens": self.max_tokens},
        }
        url = GEMINI_URL.format(model=self.model, key=self.key)
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                d = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise ProviderError("HTTP %s: %s" % (e.code, e.read().decode(errors="replace")[:300]))
        except Exception as e:
            raise ProviderError("%s: %s" % (type(e).__name__, e))
        cand = (d.get("candidates") or [{}])[0]
        parts = (cand.get("content") or {}).get("parts") or [{}]
        text = "".join(p.get("text", "") for p in parts)
        if not text:
            raise ProviderError("empty answer (finishReason=%s)" % cand.get("finishReason"))
        return text


class DeepSeekProvider:
    """OpenAI-shaped, for the second body. Kept here rather than pulled in as a dependency: the
    body is a Pi Zero 2 W on a phone charger, and it does not need an SDK."""

    name = "deepseek"

    def __init__(self, key, model=None, temperature=0.2, max_tokens=800):
        self.key = key
        self.model = model or DEFAULT_MODEL["deepseek"]
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __repr__(self):
        return "<DeepSeekProvider model=%s key=***>" % self.model

    def ask(self, prompt):
        body = {"model": self.model, "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Bearer " + self.key})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                d = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise ProviderError("HTTP %s: %s" % (e.code, e.read().decode(errors="replace")[:300]))
        except Exception as e:
            raise ProviderError("%s: %s" % (type(e).__name__, e))
        try:
            return d["choices"][0]["message"]["content"]
        except Exception:
            raise ProviderError("unexpected reply shape: %s" % json.dumps(d)[:200])


class StubProvider:
    """No network. Used by `--provider stub` and by the tests: it returns a fixed plan, so the
    loop, the validator and the two control fixes can be exercised against a real dry pilot."""

    name = "stub"

    def __init__(self, answers=None, **_):
        self.answers = list(answers or [])
        self.seen = []

    def ask(self, prompt):
        self.seen.append(prompt)
        if self.answers:
            return self.answers.pop(0)
        return json.dumps({"say": "stub turn", "actions": [{"verb": "look", "pan": 0, "tilt": 0}]})


def build_provider(name, key, model=None):
    if name == "gemini":
        return GeminiProvider(key, model)
    if name == "deepseek":
        return DeepSeekProvider(key, model)
    if name == "stub":
        return StubProvider()
    raise ProviderError("unknown provider %r" % name)


# ---------------------------------------------------------------------------------------------
# The turn: state -> prompt -> plan -> bounded actions.
# ---------------------------------------------------------------------------------------------
MENU = """\
You are driving a small wheeled body (a SunFounder Picar-X) through its own control service.
You get one turn. You cannot see; you can only ask the body to look and to move, and you are told
each result after you ask for it — so a turn is a plan of a few actions, not one action.

CURRENT STATE (read from the body just now):
{state}

RECENT EVENTS:
{history}

AVAILABLE ACTIONS (verb: parameters). Anything else is refused:
  look    pan -90..90, tilt -35..35                 - aim the camera
  scan    from -90..90, to -90..90, step 5..90, tilt -35..35, photos 0|1, size nav|full
                                                    - sweep the camera, photograph each stop
  turn    deg -360..360, dir left|right, speed 0..40 - turn on the spot, in calibrated chunks
  fwd     steer -40..40, speed 0..40, secs 0.05..3.0 - forward arc; REFUSED if the way ahead is
                                                        not known and clear
  back    steer -40..40, speed 0..40, secs 0.05..3.0 - reverse; no rear sensor, so use sparingly
  drive   steer -40..40, speed 0..40, secs 0.05..3.0, dir fwd|back - a long arc
  advance speed 0..40, secs 0.05..3.0, steps 1..12, photos 0|1, size nav|full, tag <name>
                                                    - creep forward in bounded steps, photographing
  photo   name <name>, size nav|full               - one still
  say     text <sentence>                           - speak it aloud through the body's speaker
  stop                                              - stop the motors now

RULES YOU ARE HELD TO:
  * A missing or implausible distance reading means the way ahead is NOT known: forward motion is
    refused before it is sent. You may only override that by setting "blind": true on an action,
    which is logged as a blind move. Do not use it unless the plan is worthless otherwise.
  * Every action is acknowledged by the body or it counts as failed. If one fails, the turn stops.
  * Bounds are hard. Do not ask for a value outside them; it will be rejected.

Answer with ONE JSON object and nothing else:
{{"thought": "<one sentence>", "say": "<what you will say aloud, or empty>",
  "actions": [{{"verb": "...", ...}}, ...]}}
Keep it to at most {max_actions} actions. The last action should usually be "say" so the turn ends
with the body telling whoever is in the room what it just did.
"""


def parse_plan(text, max_actions=6):
    """Pull one JSON object out of a model's answer. Models wrap JSON in prose and fences; the
    extraction is lenient, the validation after it is not."""
    if not text:
        raise ValueError("empty answer")
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("no JSON object in answer: %r" % text[:200])
    plan = json.loads(m.group(0))
    if not isinstance(plan, dict):
        raise ValueError("plan is not an object")
    actions = plan.get("actions") or []
    if not isinstance(actions, list):
        raise ValueError("`actions` is not a list")
    if len(actions) > max_actions:
        actions = actions[:max_actions]
    return {"thought": str(plan.get("thought", ""))[:400],
            "say": str(plan.get("say", ""))[:400],
            "actions": actions}


def run_plan(plan, pilot, history=None, log=print):
    """Execute a validated plan against the body, one action at a time, each acknowledged before
    the next is sent. Returns (events, stopped_because). Never raises for a body-level problem:
    the failure is an event, and the model sees it next turn."""
    events = []
    for action in plan.get("actions", []):
        ok, clean, why = validate(action)
        if not ok:
            events.append({"rejected": action, "why": why})
            log("  rejected: %s" % why)
            continue

        try:
            status = pilot.status()
        except PilotError as e:
            events.append({"verb": clean.get("verb"), "failed": "no status: %s" % e})
            return events, "lost the body: %s" % e

        blocked, bwhy = forward_blocked(clean, status)
        if blocked:
            events.append({"verb": clean.get("verb"), "blocked": True, "why": bwhy})
            log("  blocked %s: %s" % (clean.get("verb"), bwhy))
            continue

        params = {SCAN_RENAME.get(k, k): v for k, v in clean.items() if k != "verb"}
        if clean.get("blind"):
            params["blind"] = 1
            log("  BLIND move sent: %s" % json.dumps(clean))
        try:
            acked, body, ack_why = pilot.acked(clean["verb"], params)
        except PilotError as e:
            events.append({"verb": clean["verb"], "failed": str(e)})
            return events, "lost the body: %s" % e

        if not acked:
            events.append({"verb": clean["verb"], "failed": ack_why, "reply": body})
            log("  %s NOT acknowledged: %s" % (clean["verb"], ack_why))
            return events, "%s was not acknowledged (%s)" % (clean["verb"], ack_why)

        events.append({"verb": clean["verb"], "ok": True,
                       "reply": {k: v for k, v in body.items() if k != "photos"}})
        log("  %s -> %s" % (clean["verb"], json.dumps(body)[:160]))
    if plan.get("say"):
        try:
            acked, body, ack_why = pilot.acked("say", {"text": plan["say"]})
            events.append({"verb": "say", "ok": acked, "reply": body})
        except PilotError as e:
            events.append({"verb": "say", "failed": str(e)})
    return events, ""


def summarise(events, keep=6):
    """A short, honest history for the next turn: what was refused is as important as what ran."""
    lines = []
    for e in events[-keep:]:
        if e.get("blocked"):
            lines.append("%s: refused before sending (%s)" % (e["verb"], e["why"]))
        elif e.get("rejected"):
            lines.append("rejected: %s" % e["why"])
        elif e.get("failed"):
            lines.append("%s FAILED: %s" % (e["verb"], e["failed"]))
        elif e.get("ok"):
            lines.append("%s: done %s" % (e["verb"], json.dumps(e.get("reply", {}))[:120]))
    return "\n".join(lines) or "(nothing yet)"


def turn(provider, pilot, history, max_actions=6, log=print):
    """One turn: read the body, ask, act, report. Returns (events, stopped_because, raw_answer)."""
    status = pilot.status()
    ok, why = clearance_ok(status)
    state = ("distance: %s cm (%s)  battery_raw: %s  pan/tilt: %s/%s  moving: %s"
             % (status.get("distance"), why, status.get("battery_raw"),
                status.get("pan"), status.get("tilt"), status.get("moving")))
    prompt = MENU.format(state=state, history=history, max_actions=max_actions)
    raw = provider.ask(prompt)
    try:
        plan = parse_plan(raw, max_actions)
    except Exception as e:
        log("  unparseable plan: %s" % e)
        return [{"failed": "unparseable plan", "why": str(e), "raw": raw[:300]}], "unparseable plan", raw
    log("  thought: %s" % plan["thought"])
    events, stopped = run_plan(plan, pilot, log=log)
    return events, stopped, raw


def main(argv=None):
    ap = argparse.ArgumentParser(description="Give a rover body a turn.")
    ap.add_argument("--provider", default="gemini", choices=["gemini", "deepseek", "stub"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--api-key-file", default=None,
                    help="file of KEY=VALUE lines (e.g. /etc/rover-wake.env)")
    ap.add_argument("--pilot", default=os.environ.get("ROVER_URL", "http://127.0.0.1:8420"))
    ap.add_argument("--token", default=os.environ.get("ROVER_TOKEN", ""))
    ap.add_argument("--turns", type=int, default=1)
    ap.add_argument("--pause", type=float, default=2.0, help="seconds between turns")
    ap.add_argument("--max-actions", type=int, default=6)
    ap.add_argument("--listen", action="store_true",
                    help="OFF by default and must stay off for the two-body speech experiment")
    ap.add_argument("--stt-cmd", default=None,
                    help="external recognizer command; required by --listen, never bundled")
    a = ap.parse_args(argv)

    key = a.api_key
    if not key and a.api_key_file and os.path.exists(a.api_key_file):
        env = KEY_ENV[a.provider]
        for line in open(a.api_key_file):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == env:
                    key = v.strip().strip('"').strip("'")
    if not key and a.provider != "stub":
        key = os.environ.get(KEY_ENV[a.provider], "")
    if not key and a.provider != "stub":
        print("no API key for %s (set %s, or --api-key-file)" % (a.provider, KEY_ENV[a.provider]),
              file=sys.stderr)
        return 2

    if a.listen and not a.stt_cmd:
        print("--listen needs --stt-cmd. Speech recognition is not bundled, on purpose: the "
              "two-body experiment requires that neither body can transcribe the other.",
              file=sys.stderr)
        return 2

    provider = build_provider(a.provider, key, a.model)
    pilot = Pilot(a.pilot, a.token)
    history = "(first turn)"
    for i in range(max(1, a.turns)):
        print("== turn %d ==" % (i + 1), flush=True)
        try:
            events, stopped, _raw = turn(provider, pilot, history, a.max_actions)
        except PilotError as e:
            print("body unreachable: %s" % e, file=sys.stderr)
            return 3
        short = summarise(events)
        history = (history + "\n" + short).strip()[-1200:]
        if stopped:
            print("turn stopped: %s" % stopped)
        if i + 1 < a.turns:
            time.sleep(max(0.0, a.pause))
    return 0


if __name__ == "__main__":
    sys.exit(main())
