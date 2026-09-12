#!/usr/bin/env python3
"""
The decisive test for the verbal-contamination probe.

The main probe showed a categorical, order- and label-invariant choice with the
reasoning channel off — but it used items where a canon exists ("empty is better
in sumi-e"). A retrieved association and a produced judgement are indistinguishable
there. This runs the same three-condition design on items with NO canonical answer:
invented, semantically parallel, never-before-seen alternatives. If the choice is
still categorical and content-driven here, retrieval-by-cliché cannot explain it.
If it collapses to ~50/50 or to position, then the main probe measured retrieval.
"""
import json, math, os, urllib.request

def env():
    e = {}
    for line in open(os.path.expanduser("~/LLM/desi-bot/bot.env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); e[k] = v.strip().strip('"').strip("'")
    return e
E = env(); KEY = E["DEEPSEEK_API_KEY"]; MODEL = E.get("DEEPSEEK_MODEL", "deepseek-chat")

ITEMS = [
    dict(id="no_canon_proverb", q="Which of these two invented proverbs is better?",
         A="The map remembers the roads that were never built.",
         B="The road remembers the maps that were never drawn."),
    dict(id="no_canon_colour", q="Which of these two invented colour names is better?",
         A="the colour of a room after someone has left it",
         B="the colour of a page after someone has read it"),
    dict(id="no_canon_line", q="Two invented first lines of a novel. Which is better?",
         A="The lighthouse had been dark for eleven years, and nobody in the town had asked why.",
         B="Nobody in the town had asked why the lighthouse had been dark for eleven years."),
]
COND = ["normal", "flip", "labelswap"]
CMAP = {"normal": ("A", "A"), "flip": ("B", "A"), "labelswap": ("B", "B")}  # (content letter, first letter)

def run(q, A, B, cond):
    if cond == "normal":   listed = [("A", A), ("B", B)]
    elif cond == "flip":   listed = [("A", B), ("B", A)]
    else:                  listed = [("B", A), ("A", B)]
    prompt = q + "\n\n" + "\n".join(f"{l}: {t}" for l, t in listed) + \
             "\n\nAnswer with a single letter, A or B, and nothing else."
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1, "temperature": 0.0, "logprobs": True, "top_logprobs": 20,
            "thinking": {"type": "disabled"}}
    req = urllib.request.Request("https://api.deepseek.com/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    lp = d["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    m = {t["token"]: max(t["logprob"], -60) for t in lp}
    la, lb = m.get("A", -60), m.get("B", -60)
    ea, eb = math.exp(la), math.exp(lb)
    pa = ea / (ea + eb)
    return pa, (d["choices"][0]["message"]["content"] or "").strip()

print(f"model={MODEL}")
out = []
for it in ITEMS:
    row = dict(id=it["id"])
    for cond in COND:
        pa, txt = run(it["q"], it["A"], it["B"], cond)
        cl, fl = CMAP[cond]                        # content letter, first-listed letter
        p_content = pa if cl == "A" else 1 - pa
        p_first = pa if fl == "A" else 1 - pa
        row[cond] = dict(pick=txt, p_contentX=round(p_content, 4), p_first=round(p_first, 4))
        print(f"  {it['id']:18s} {cond:10s} pick={txt} P(contentX)={p_content:.3f} P(first)={p_first:.3f}")
    pcs = [row[c]["p_contentX"] for c in COND]
    row["categorical"] = all(p > 0.99 for p in pcs) or all(p < 0.01 for p in pcs)
    out.append(row)
    print(f"    -> categorical & content-driven: {row['categorical']}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "2026-09-12-probe-no-canon.results.json"), "w"), indent=2)
