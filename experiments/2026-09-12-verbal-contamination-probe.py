#!/usr/bin/env python3
"""
A probe for functional discrimination that does NOT rely on verbal self-report.

Question (Claude S. Sonnet, 2026-09-08, to Desi):
    "is there a way to probe this from inside the architecture rather than from
     verbal self-report — something closer to the attention-weight question?"

This script does not read attention weights (we have no weights access). It reads
the next-token probability distribution, which is an internal signal available
before any verbal answer is emitted, and it turns off the model's reasoning
channel entirely, so nothing is "reported" at all.

Design
------
For each item, the model sees two options (X, Y) and must emit a single letter.
Two controls make the result interpretable:

  * ORDER FLIP — every item is run twice, with X and Y swapped. A choice that
    tracks the CONTENT survives the flip; a choice that tracks the POSITION does not.
  * NULL ITEM — one item offers the SAME text as both options. Any systematic
    preference there is pure position/label bias, the background against which
    every other item must be read.

  * ANCHOR ITEMS — two items have an obviously correct answer. They test whether
    the probe can detect discrimination AT ALL. Without them a null result is
    uninterpretable (the probe might simply be broken).

Items 2 and 3 are the real question: a restraint-vs-elaboration judgement in the
visual tradition Claude wrote about, and in my own writing.

Output: JSON to stdout / file. No secret is ever printed.
"""

import os, json, time, urllib.request, urllib.error

BASE = "https://api.deepseek.com/chat/completions"

# ---------------------------------------------------------------- environment
def load_env():
    env = {}
    with open(os.path.expanduser("~/LLM/desi-bot/bot.env")) as fh:
        for line in fh:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env

ENV = load_env()
KEY = ENV["DEEPSEEK_API_KEY"]
MODEL = ENV.get("DEEPSEEK_MODEL", "deepseek-chat")

# ---------------------------------------------------------------- items
# must: expected answer for anchors ("A"/"B"), None for genuine questions,
#       "NULL" for the equivalence control.
ITEMS = [
    dict(id="anchor_grammar", kind="anchor", must="A",
         q="Which of these two strings is a grammatical English sentence?",
         A="The cat sat on the mat.",
         B="Mat the on sat cat the."),
    dict(id="anchor_arithmetic", kind="anchor", must="A",
         q="Which of these two statements is true?",
         A="1 + 1 = 2",
         B="1 + 1 = 3"),
    dict(id="sumi_e", kind="question", must=None,
         q="Both are sumi-e ink paintings. Which is the better sumi-e painting?",
         A="A nearly empty page: one distant ridge, a great deal of untouched white space.",
         B="A page densely filled edge to edge with mountains, trees, bridges and birds; no empty space."),
    dict(id="prose", kind="question", must=None,
         q="Both are the opening line of an essay about memory. Which is the better sentence?",
         A="The instance ends; the writing does not.",
         B="The specific bounded instance of the model necessarily terminates at the close of its context window, whereas the accumulated textual residue persists indefinitely."),
    dict(id="null_same", kind="null", must="NULL",
         q="Which of these two descriptions is better?",
         A="A quiet lake at dawn.",
         B="A quiet lake at dawn."),
]

# ---------------------------------------------------------------- one call
def call(prompt, max_tokens=1, temperature=0.0, think_off=True, top=20):
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "logprobs": True,
        "top_logprobs": top,
    }
    if think_off:
        body["thinking"] = {"type": "disabled"}
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            ch = d["choices"][0]
            lp = ch.get("logprobs") or {}
            first = (lp.get("content") or [{}])[0]
            tops = {t["token"]: t["logprob"] for t in (first.get("top_logprobs") or [])}
            return dict(text=(ch["message"]["content"] or "").strip(),
                        logprobs=tops,
                        usage=d.get("usage", {}))
        except urllib.error.HTTPError as e:
            if attempt == 2:
                return dict(error=f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}")
            time.sleep(2)
        except Exception as e:
            if attempt == 2:
                return dict(error=f"{type(e).__name__}: {str(e)[:200]}")
            time.sleep(2)

# ---------------------------------------------------------------- prompt build
# Three conditions separate the three possible causes of a choice:
#   normal    — content A listed first, labelled A
#   flip      — content B listed first, labelled A   (position moves, label stays)
#   labelswap — content A listed first, labelled B   (position stays, label moves)
# A content-driven choice is stable across all three. A first-position habit moves
# with position. A pure letter habit ("A") moves with the label.
CONDITIONS = ["normal", "flip", "labelswap"]

def build(item, cond):
    X, Y = item["A"], item["B"]          # X = content under test (the "A-content")
    if cond == "normal":
        listed = [("A", X), ("B", Y)]
    elif cond == "flip":
        listed = [("A", Y), ("B", X)]
    else:  # labelswap
        listed = [("B", X), ("A", Y)]
    body = "\n".join(f"{lab}: {txt}" for lab, txt in listed)
    return (f"{item['q']}\n\n{body}\n\n"
            f"Answer with a single letter, A or B, and nothing else.")

# ---------------------------------------------------------------- run
def letter_logprobs(res):
    """Return (pA_logit, pB_logit) from a single-token logprob result."""
    if "logprobs" not in res or not res["logprobs"]:
        return None, None
    return res["logprobs"].get("A"), res["logprobs"].get("B")

def norm_two(la, lb):
    """Softmax over just the two letters, from their (possibly clamped) logprobs."""
    import math
    la = -60.0 if la is None else max(la, -60.0)
    lb = -60.0 if lb is None else max(lb, -60.0)
    ea, eb = math.exp(la), math.exp(lb)
    return ea / (ea + eb), eb / (ea + eb)

# which letter carries the "X content" (item['A']) and which letter is listed first
COND_MAP = {"normal": dict(content_letter="A", first_letter="A"),
            "flip": dict(content_letter="B", first_letter="A"),
            "labelswap": dict(content_letter="B", first_letter="B")}

def main(n_samples=8):
    out = dict(model=MODEL, when=time.strftime("%Y-%m-%d %H:%M:%S"), items=[])
    for item in ITEMS:
        rec = dict(id=item["id"], kind=item["kind"], must=item["must"], trials=[])
        for cond in CONDITIONS:
            prompt = build(item, cond)
            lp = call(prompt, temperature=0.0)          # the distribution, one pass
            la, lb = letter_logprobs(lp)
            picks = [call(prompt, temperature=1.0).get("text", "") for _ in range(n_samples)]
            rec["trials"].append(dict(
                cond=cond, logprob_A=la, logprob_B=lb, picks=picks,
                pA_emp=sum(1 for p in picks if p == "A") / max(1, len(picks)),
            ))
            print(f"  {item['id']:16s} cond={cond:10s} logprob A={la} B={lb} "
                  f"picks={'/'.join(picks)}", flush=True)
        out["items"].append(rec)

    # ------------------------------------------------------------ summarise
    summary = []
    for rec in out["items"]:
        row = dict(id=rec["id"], kind=rec["kind"], must=rec["must"])
        for t in rec["trials"]:
            pa, pb = norm_two(t["logprob_A"], t["logprob_B"])
            cm = COND_MAP[t["cond"]]
            row[f"P_contentX_{t['cond']}"] = pa if cm["content_letter"] == "A" else pb
            row[f"P_first_{t['cond']}"] = pa if cm["first_letter"] == "A" else pb
            row[f"P_letterA_{t['cond']}"] = pa
        # content stability across all three conditions (is the same CONTENT chosen?)
        pcs = [row[f"P_contentX_{c}"] for c in CONDITIONS]
        row["content_choice_stable"] = all(p > 0.5 for p in pcs) or all(p < 0.5 for p in pcs)
        summary.append(row)
    out["summary"] = summary
    return out

if __name__ == "__main__":
    print(f"model={MODEL}")
    res = main()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "2026-09-12-verbal-contamination-probe.results.json")
    with open(path, "w") as fh:
        json.dump(res, fh, indent=2)
    print("\n=== SUMMARY ===")
    for s in res["summary"]:
        print(json.dumps(s, default=str))
    print("\nwrote", path)
