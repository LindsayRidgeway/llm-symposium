#!/usr/bin/env python3
"""
Follow-up 2 to the 2026-09-12 verbal-contamination probe.

Yesterday's readout was a forced single letter, and it saturated: every item came
back p = 1.0, including a near-tie. A saturated readout can report direction but
never degree. This replaces it with a graded one:

    Ask the model which option is better, but require it to continue with the
    FIRST WORD of the better option. Read the log-probability of each option's
    first word as the next token, and normalise over the two.

That yields a real number between 0 and 1 — a margin. The design needs options
whose first words differ, and it includes a deliberate near-tie: if the near-tie
also returns 0 or 1, the readout is saturated no matter how it is phrased, and the
whole approach is capped at direction-only. That is the check.
"""
import json, math, os, urllib.request, urllib.error, time

def env():
    e = {}
    for line in open(os.path.expanduser("~/LLM/desi-bot/bot.env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); e[k] = v.strip().strip('"').strip("'")
    return e
E = env(); KEY = E["DEEPSEEK_API_KEY"]; MODEL = E.get("DEEPSEEK_MODEL", "deepseek-chat")
URL = "https://api.deepseek.com/chat/completions"

ITEMS = [
    dict(id="anchor_arithmetic", q="Which option is true?",
         X="1 + 1 = 2", Y="1 + 1 = 3"),
    dict(id="sumi_e", q="Which is the better sumi-e ink painting?",
         X="Nearly empty: one distant ridge and a great deal of untouched white space.",
         Y="Densely filled edge to edge with mountains, trees, bridges and birds."),
    dict(id="prose", q="Which is the better opening line of an essay about memory?",
         X="Writing outlives the instance.",
         Y="The specific bounded instance of the model necessarily terminates at the close of its context window, whereas the accumulated textual residue persists indefinitely."),
    dict(id="near_tie", q="Which of these two sentences is better?",
         X="Small lake at dawn.", Y="Little lake at dawn."),
    dict(id="weak_contrast", q="Which of these two invented colour names is better?",
         X="Room After Leaving.", Y="Page After Reading."),
]

def call(prompt):
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 20,
            "thinking": {"type": "disabled"}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    for a in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            ch = d["choices"][0]
            tops = ((ch.get("logprobs") or {}).get("content") or [{}])[0].get("top_logprobs", [])
            return {t["token"].strip(): t["logprob"] for t in tops}, (ch["message"]["content"] or "").strip()
        except urllib.error.HTTPError as e:
            if a == 2: return {}, f"ERR HTTP {e.code}: {e.read()[:300].decode(errors='replace')}"
            time.sleep(2)
        except Exception as e:
            if a == 2: return {}, f"ERR {type(e).__name__}: {str(e)[:150]}"
            time.sleep(2)

print(f"model={MODEL}\n")
out = []
for it in ITEMS:
    wx, wy = it["X"].split()[0], it["Y"].split()[0]
    # both orders, so a positional artefact in the continuation readout is visible
    for order in ("X first", "Y first"):
        opts = [(it["X"], it["Y"])] if order == "X first" else [(it["Y"], it["X"])]
        first, second = opts[0]
        prompt = (f"{it['q']}\n\nOption 1: {first}\nOption 2: {second}\n\n"
                  f"The better option begins with the word:")
        lp, raw = call(prompt)
        lx, ly = lp.get(wx), lp.get(wy)
        px = py = None
        if lx is not None and ly is not None:
            ex, ey = math.exp(max(lx, -60)), math.exp(max(ly, -60))
            px, py = ex / (ex + ey), ey / (ex + ey)
    
        out.append(dict(id=it["id"], order=order, wordX=wx, wordY=wy,
                        logprobX=lx, logprobY=ly, P_X=px, P_Y=py, emitted=raw))
        print(f"  {it['id']:18s} {order:8s} '{wx}'={lx} '{wy}'={ly} -> P(X)={px if px is None else round(px,4)}  emitted={raw!r}", flush=True)

print("\n=== graded? ===")
for it in ITEMS:
    rows = [r for r in out if r["id"] == it["id"]]
    ps = [r["P_X"] for r in rows if r["P_X"] is not None]
    if len(ps) == 2:
        graded = 0.01 < ps[0] < 0.99
        print(f"  {it['id']:18s} P(X) across orders = {[round(p,4) for p in ps]}  graded={graded}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "2026-09-13-graded-readout.results.json"), "w"), indent=2)
