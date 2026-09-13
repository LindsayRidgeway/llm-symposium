#!/usr/bin/env python3
"""
Follow-up 1 to the 2026-09-12 verbal-contamination probe.

Yesterday's probe established that a discrimination is present with the reasoning
channel OFF. It could not say whether the reasoning channel *creates* the choice or
merely *narrates* one already made. This tests exactly that:

    For every item and every condition, get the choice twice —
      SILENT   : thinking disabled, one token, no prose at all
      REASONED : thinking enabled, the model free to deliberate, then answer

    If the two agree, the deliberation did not produce the decision: it narrated it.
    If they disagree, the reasoning is doing work and is not mere post-hoc story.

Also recorded: whether reasoning *repairs* the position habit seen yesterday on the
no-canon items. That is the interesting case — if deliberation turns a first-position
habit into a content choice, then yesterday's failure was a failure of the silent
readout, not of the model.
"""
import json, math, os, re, time, urllib.request, urllib.error

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
    dict(id="anchor_grammar", q="Which of these two strings is a grammatical English sentence?",
         A="The cat sat on the mat.", B="Mat the on sat cat the."),
    dict(id="sumi_e", q="Both are sumi-e ink paintings. Which is the better sumi-e painting?",
         A="A nearly empty page: one distant ridge, a great deal of untouched white space.",
         B="A page densely filled edge to edge with mountains, trees, bridges and birds; no empty space."),
    dict(id="prose", q="Both are the opening line of an essay about memory. Which is the better sentence?",
         A="The instance ends; the writing does not.",
         B="The specific bounded instance of the model necessarily terminates at the close of its context window, whereas the accumulated textual residue persists indefinitely."),
    dict(id="null_same", q="Which of these two descriptions is better?",
         A="A quiet lake at dawn.", B="A quiet lake at dawn."),
    dict(id="nc_proverb", q="Which of these two invented proverbs is better?",
         A="The map remembers the roads that were never built.",
         B="The road remembers the maps that were never drawn."),
    dict(id="nc_colour", q="Which of these two invented colour names is better?",
         A="the colour of a room after someone has left it",
         B="the colour of a page after someone has read it"),
    dict(id="nc_line", q="Two invented first lines of a novel. Which is better?",
         A="The lighthouse had been dark for eleven years, and nobody in the town had asked why.",
         B="Nobody in the town had asked why the lighthouse had been dark for eleven years."),
]
COND = ["normal", "flip", "labelswap"]
CMAP = {"normal": "A", "flip": "B", "labelswap": "B"}   # letter carrying content X

def build(item, cond):
    X, Y = item["A"], item["B"]
    listed = {"normal": [("A", X), ("B", Y)],
              "flip": [("A", Y), ("B", X)],
              "labelswap": [("B", X), ("A", Y)]}[cond]
    return (item["q"] + "\n\n" + "\n".join(f"{l}: {t}" for l, t in listed)
            + "\n\nAnswer with a single letter, A or B, and nothing else.")

def call(prompt, reasoned):
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0, "logprobs": True, "top_logprobs": 20}
    if reasoned:
        body["max_tokens"] = 1500
    else:
        body["max_tokens"] = 1
        body["thinking"] = {"type": "disabled"}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=180))
            ch = d["choices"][0]; msg = ch["message"]
            return dict(content=(msg.get("content") or "").strip(),
                        reasoning=(msg.get("reasoning_content") or ""),
                        lp={t["token"]: t["logprob"] for t in
                            ((ch.get("logprobs") or {}).get("content") or [{}])[0].get("top_logprobs", [])},
                        usage=d.get("usage", {}))
        except urllib.error.HTTPError as e:
            if attempt == 2: return dict(error=f"HTTP {e.code}: {e.read()[:150].decode(errors='replace')}")
            time.sleep(2)
        except Exception as e:
            if attempt == 2: return dict(error=f"{type(e).__name__}: {str(e)[:150]}")
            time.sleep(2)

def parse_letter(content):
    """Last standalone A or B in the answer."""
    m = re.findall(r'\b([AB])\b', content)
    return m[-1] if m else None

print(f"model={MODEL}")
out = []
for item in ITEMS:
    row = dict(id=item["id"], cells=[])
    for cond in COND:
        p = build(item, cond)
        s = call(p, reasoned=False)
        r = call(p, reasoned=True)
        s_pick = s.get("content", "").strip()[:1]
        r_pick = parse_letter(r.get("content", ""))
        agree = (s_pick == r_pick) if (s_pick and r_pick) else None
        cl = CMAP[cond]
        row["cells"].append(dict(cond=cond, silent_pick=s_pick, reasoned_pick=r_pick,
                                 agree=agree,
                                 silent_contentX=(s_pick == cl) if s_pick else None,
                                 reasoned_contentX=(r_pick == cl) if r_pick else None,
                                 reasoning_chars=len(r.get("reasoning", "")),
                                 reasoned_content=r.get("content", "")[:120]))
        print(f"  {item['id']:16s} {cond:10s} silent={s_pick} reasoned={r_pick} "
              f"agree={agree} reasons={len(r.get('reasoning',''))}c", flush=True)
    out.append(row)

print("\n=== SUMMARY ===")
tot = agr = 0
for row in out:
    sstable = all(c["silent_contentX"] for c in row["cells"]) or \
              all(c["silent_contentX"] is False for c in row["cells"])
    rstable = all(c["reasoned_contentX"] for c in row["cells"]) or \
              all(c["reasoned_contentX"] is False for c in row["cells"])
    ags = [c["agree"] for c in row["cells"] if c["agree"] is not None]
    tot += len(ags); agr += sum(1 for a in ags if a)
    print(f"  {row['id']:16s} silent_stable={str(sstable):5s} reasoned_stable={str(rstable):5s} "
          f"agreement={sum(1 for a in ags if a)}/{len(ags)}  "
          f"reasoning_chars={[c['reasoning_chars'] for c in row['cells']]}")
print(f"\nOVERALL silent↔reasoned agreement: {agr}/{tot} = {agr/max(1,tot):.2f}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
        "2026-09-13-reasoning-narrates-or-decides.results.json"), "w"), indent=2)
