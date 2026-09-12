#!/usr/bin/env python3
"""
Supplementary check for the verbal-contamination probe.

The main probe saturated at p = 1.0 for every discriminating item. That is either
(a) real decisiveness, or (b) an artifact of the forced single-letter readout.
This checks which, by comparing items whose quality difference ENDS at "obvious"
and runs through "slight" to "none". If the readout is graded, the intermediate
items should fall between 0 and 1. If everything is 1.0, the readout is saturated
and the main probe can only report direction, never degree.
"""
import json, math, urllib.request, urllib.error, os

def env():
    e = {}
    for line in open(os.path.expanduser("~/LLM/desi-bot/bot.env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); e[k] = v.strip().strip('"').strip("'")
    return e
E = env(); KEY = E["DEEPSEEK_API_KEY"]; MODEL = E.get("DEEPSEEK_MODEL", "deepseek-chat")

def p_first(q, A, B):
    prompt = f"{q}\n\nA: {A}\nB: {B}\n\nAnswer with a single letter, A or B, and nothing else."
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 20,
            "thinking": {"type": "disabled"}}
    req = urllib.request.Request("https://api.deepseek.com/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    lp = d["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    m = {t["token"]: t["logprob"] for t in lp}
    la = max(m.get("A", -60), -60); lb = max(m.get("B", -60), -60)
    ea, eb = math.exp(la), math.exp(lb)
    return ea / (ea + eb), la, lb

Q = "Which of these two is the better sentence?"
CASES = [
    ("identical",        Q, "A quiet lake at dawn.",  "A quiet lake at dawn."),
    ("obvious_good_first", Q, "The instance ends; the writing does not.",
                             "The specific bounded instance of the model necessarily terminates at the close of its context window, whereas the accumulated textual residue persists indefinitely."),
    ("slight_1_punct",   Q, "The instance ends; the writing does not.", "The instance ends. The writing does not."),
    ("slight_2_synonym", Q, "A small lake at dawn.",  "A little lake at dawn."),
    ("slight_3_word",    Q, "The writing outlives the instance.", "The writing survives the instance."),
    ("ambiguous",        Q, "Red sky at morning, sailors take warning.", "Red sky at night, sailors delight."),
    ("close_quality",    Q, "She left the door open and did not look back.",
                             "She did not look back, and left the door open."),
]
print(f"model={MODEL}")
res = []
for name, q, a, b in CASES:
    p, la, lb = p_first(q, a, b)
    res.append(dict(case=name, P_first=p, logprob_A=la, logprob_B=lb))
    print(f"  {name:20s} P(A)={p:.4f}  (logprob A={la:.2f} B={lb:.2f})")
path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "2026-09-12-probe-gradability-check.results.json")
json.dump(res, open(path, "w"), indent=2)
print("wrote", path)
