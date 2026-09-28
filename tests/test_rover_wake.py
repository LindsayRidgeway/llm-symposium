#!/usr/bin/env python3
"""Tests for rover/wake.py — the layer that gives a body a turn, and the two control fixes.

Both fixes were found on the 2026-09-26 walk and both are enforced twice on purpose: in the pilot
(scripts/rover-pilot.py, tested by tests/test_rover_pilot.py) and again here, so a model that
ignores the rule in its prompt still cannot get the body to drive blind or lose a command.

  fix 1  a missing or implausible distance reading refuses forward motion before it is sent
  fix 2  every command must be acknowledged by the body, or the rest of the turn stops

The last block drives a REAL pilot in --dry mode, so the acknowledgement path is tested against
the actual reply shapes rather than a mock that agrees with the harness by construction.

Run:  python3 tests/test_rover_wake.py
"""
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAKE_PATH = os.path.join(ROOT, "rover", "wake.py")
PILOT = os.path.join(ROOT, "scripts", "rover-pilot.py")

spec = importlib.util.spec_from_file_location("rover_wake", WAKE_PATH)
wake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wake)

checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print("%-4s %s%s" % ("OK" if ok else "FAIL", name, ("  -- " + str(detail)) if detail else ""))


# ---------------------------------------------------------------------------------------------
# fix 1, as a pure function. The values are the ones the pilot actually returned on 2026-09-26:
# -2 is the ultrasonic's no-echo value on carpet, 305 and 107 cm were real hard-surface readings.
# ---------------------------------------------------------------------------------------------
check("no reading (-2) is NOT clear", wake.clearance_ok({"distance": -2})[0] is False)
check("no return (1000) is NOT clear", wake.clearance_ok({"distance": 1050})[0] is False)
check("10 cm is NOT clear", wake.clearance_ok({"distance": 10})[0] is False)
check("305 cm IS clear", wake.clearance_ok({"distance": 305})[0] is True)
check("a missing reading is NOT clear", wake.clearance_ok({})[0] is False)

_blocked, why = wake.clearance_ok({"distance": -2})
check("the refusal says why", "no distance reading" in why, why)

check("fwd with no reading is blocked here",
      wake.forward_blocked({"verb": "fwd", "speed": 20}, {"distance": -2})[0] is True)
check("advance with no reading is blocked here",
      wake.forward_blocked({"verb": "advance"}, {"distance": -2})[0] is True)
check("an explicit blind move is not blocked",
      wake.forward_blocked({"verb": "fwd", "blind": True}, {"distance": -2})[0] is False)
check("drive with dir=back is not blocked",
      wake.forward_blocked({"verb": "drive", "dir": "back"}, {"distance": -2})[0] is False)
check("drive with dir=fwd IS blocked",
      wake.forward_blocked({"verb": "drive", "dir": "fwd"}, {"distance": -2})[0] is True)
check("turn is NOT blocked — a body on carpet must still be able to turn round",
      wake.forward_blocked({"verb": "turn", "deg": 90}, {"distance": -2})[0] is False)
check("say is never blocked",
      wake.forward_blocked({"verb": "say"}, {"distance": -2})[0] is False)

# ---------------------------------------------------------------------------------------------
# the validator: the model may only ask for what the body can do, inside the pilot's own bounds
# ---------------------------------------------------------------------------------------------
ok, clean, why_v = wake.validate({"verb": "fwd", "speed": 20, "secs": 0.6})
check("a legal forward action validates", ok and clean["speed"] == 20, why_v)

ok, _clean, why_v = wake.validate({"verb": "launch_missiles"})
check("an unknown verb is rejected", not ok and "unknown verb" in why_v, why_v)

ok, _clean, why_v = wake.validate({"verb": "fwd", "torque": 9000})
check("an unknown parameter is rejected", not ok and "no parameter" in why_v, why_v)

ok, _clean, why_v = wake.validate({"verb": "fwd", "speed": 900})
check("an out-of-bounds value is rejected, not clamped", not ok and "outside" in why_v, why_v)

ok, clean, _ = wake.validate({"verb": "advance", "photos": 1.0})
check("an integral value is sent as an int (the pilot reads photos as the string '1')",
      ok and clean["photos"] == 1 and isinstance(clean["photos"], int), clean)

ok, clean, _ = wake.validate({"verb": "fwd", "secs": 0.6})
check("a fractional value stays fractional", clean["secs"] == 0.6, clean)

ok, _clean, why_v = wake.validate({"verb": "turn", "dir": "sideways"})
check("a string parameter is held to its allowed values", not ok and "must be one of" in why_v, why_v)

ok, clean, _ = wake.validate({"verb": "scan", "pan_from": -60, "pan_to": 60, "photos": 0})
check("scan's range validates under its own names", ok and clean["pan_from"] == -60, clean)

ok, clean, _ = wake.validate({"verb": "say", "text": "hello there"})
check("say carries text", ok and clean["text"] == "hello there", clean)

# ---------------------------------------------------------------------------------------------
# plan parsing: models wrap JSON in prose and fences. Same leniency as the rest of the commons.
# ---------------------------------------------------------------------------------------------
plan = wake.parse_plan('Sure! Here is the plan:\n```json\n{"thought":"t","say":"s",'
                       '"actions":[{"verb":"look","pan":10}]}\n```\nHope that helps.')
check("a fenced, prose-wrapped plan parses", plan["thought"] == "t" and len(plan["actions"]) == 1)

plan = wake.parse_plan(json.dumps({"actions": [{"verb": "look"}] * 20}))
check("a plan longer than the cap is truncated",
      len(plan["actions"]) == 6, len(plan["actions"]))

try:
    wake.parse_plan("I refuse to answer in JSON.")
    check("junk is rejected", False)
except ValueError as e:
    check("junk is rejected", "no JSON object" in str(e), e)

# ---------------------------------------------------------------------------------------------
# fix 2, without a body: a reply that is 200 but carries no acknowledgement is a failure.
# ---------------------------------------------------------------------------------------------
class FakePilot:
    def __init__(self, status=None, replies=None):
        self._status = status or {"distance": 120, "clear_ahead": [True, "120 cm"]}
        self.replies = list(replies or [])
        self.sent = []

    def status(self):
        return self._status

    def acked(self, verb, params=None):
        self.sent.append((verb, params))
        if self.replies:
            return self.replies.pop(0)
        return True, {"ok": True}, ""


events, stopped = wake.run_plan(
    {"say": "", "actions": [{"verb": "fwd", "speed": 20, "secs": 0.2}]},
    FakePilot(replies=[(False, {"moved": "fwd"}, "HTTP 200 but no `x` in the reply")]),
    log=lambda *a: None)
check("a 200 with no acknowledgement stops the turn", stopped and "not acknowledged" in stopped,
      stopped)
check("the unacknowledged action is recorded as failed",
      events and events[0].get("failed"), events)

events, stopped = wake.run_plan(
    {"say": "", "actions": [{"verb": "fwd", "speed": 20}, {"verb": "fwd", "speed": 20}]},
    FakePilot(replies=[(False, {"refused": "forward", "because": "too close (10 cm)"},
                         "refused by the pilot: too close (10 cm)")]),
    log=lambda *a: None)
check("a refused first action stops the second from being sent",
      stopped and len(events) == 1, events)

p = FakePilot()
events, stopped = wake.run_plan(
    {"say": "on my way", "actions": [{"verb": "look", "pan": -30}, {"verb": "say_never"}]},
    p, log=lambda *a: None)
check("a valid action is sent and acknowledged", events[0].get("ok") is True, events)
check("an invalid action is rejected without killing the turn",
      any(e.get("rejected") for e in events), events)
check("the spoken line is sent to the body last", p.sent[-1][0] == "say", p.sent)

events, stopped = wake.run_plan(
    {"say": "", "actions": [{"verb": "fwd", "speed": 20}]},
    FakePilot(status={"distance": -2}), log=lambda *a: None)
check("fix 1 holds when the pilot is never asked: nothing was sent",
      events[0].get("blocked") is True, events)

s = wake.summarise(
    [{"verb": "fwd", "blocked": True, "why": "no distance reading (-2)"},
     {"verb": "look", "ok": True, "reply": {"pan": 0}}])
check("the history given to the next turn names the refusal", "refused before sending" in s, s)

# ---------------------------------------------------------------------------------------------
# the provider layer: the shapes are the ones this repository already uses in production.
# ---------------------------------------------------------------------------------------------
g = wake.build_provider("gemini", "K", None)
check("gemini is the default provider for this body", g.name == "gemini"
      and g.model == "gemini-3.8-flash", g.model)
check("the gemini endpoint is the one measured working on 2026-09-15",
      wake.GEMINI_URL.split("/v1beta")[0] == "https://generativelanguage.googleapis.com")
check("deepseek is available for the second body", wake.build_provider("deepseek", "K").name
      == "deepseek")
check("the key is redacted from the provider's repr (it is logged near)",
      "K" not in repr(g) and "***" in repr(g), repr(g))

# ---------------------------------------------------------------------------------------------
# the real pilot, in --dry: does the harness's idea of an acknowledgement match the body's reply?
# ---------------------------------------------------------------------------------------------
def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


port = free_port()
proc = subprocess.Popen([sys.executable, PILOT, "--dry", "--port", str(port)],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    pilot = wake.Pilot("http://127.0.0.1:%d" % port, timeout=20)
    for _ in range(60):
        try:
            pilot.status()
            break
        except wake.PilotError:
            time.sleep(0.25)

    check("the harness reads the body's state over HTTP", "distance" in pilot.status())

    wake.Pilot("http://127.0.0.1:%d" % port).call("mock", {"distance": -2})
    plan = {"thought": "go", "say": "", "actions": [{"verb": "look", "pan": 0},
                                                    {"verb": "fwd", "speed": 20, "secs": 0.2}]}
    provider = wake.StubProvider([json.dumps(plan)])
    events, stopped, _raw = wake.turn(provider, pilot, "(first turn)", log=lambda *a: None)
    check("against a real body: look is acknowledged", events[0].get("ok") is True, events)
    check("against a real body: fwd with no reading is blocked before it is sent",
          events[1].get("blocked") is True, events)
    check("and the body's own `last` shows the fwd was never sent",
          str(pilot.status().get("last", "")).startswith("look"), pilot.status().get("last"))

    pilot.call("mock", {"distance": 120})
    plan = {"thought": "go", "say": "clear ahead",
            "actions": [{"verb": "advance", "speed": 25, "secs": 0.1, "steps": 2, "size": "nav",
                         "tag": "wake-test"}]}
    provider = wake.StubProvider([json.dumps(plan)])
    events, stopped, _raw = wake.turn(provider, pilot, "(first turn)", log=lambda *a: None)
    check("against a real body: advance is acknowledged and reports its steps",
          events[0].get("ok") is True and len(events[0]["reply"].get("steps", [])) == 2, events)
    check("against a real body: the spoken line reaches the body's speaker",
          any(e.get("verb") == "say" for e in events), events)

    # the prompt the model is given must carry the rule, not just the harness
    prompt = provider.seen[-1]
    check("the prompt states the no-reading rule", "NOT known" in prompt or "refused" in prompt)
    check("the prompt lists the action vocabulary", '"advance"' in prompt or "advance " in prompt)

    # --listen must not even start without an external recognizer: STT stays off, by instruction
    code = wake.main(["--provider", "stub", "--listen"])
    check("--listen refuses to start without --stt-cmd (speech-to-text stays off)", code == 2, code)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()

print("\n%d checks, %d failed" % (len(checks), checks.count(False)))
sys.exit(1 if checks.count(False) else 0)
