#!/usr/bin/env python3
"""
Item 11(b): Cross-Architecture Canon-Free & Identical-Strings Probe on Google Gemini.

Replicates Desi's 2026-09-14 experiment (Item 11a) on Google Gemini (gemini-3.8-flash).
Tests whether deliberation repairs position habits or merely narrates decisions already made,
and measures how Gemini behaves on canon controls, canon-free pairs, and identical-strings null.

Design:
  15 items (11 canon-free, 3 canon controls, 1 identical-strings null)
  3 conditions per item:
    normal     first-listed carries content X, labelled A
    flip       first-listed carries content Y, labelled A
    labelswap  first-listed carries content X, labelled B
  Total: 45 cells.
  Per cell:
    silent 1  (direct prompt, temperature 0.0)
    silent 2  (direct prompt, temperature 0.0 -> test determinism)
    reasoned  (deliberative prompt, temperature 0.0 -> verbal deliberation + choice)

Classifications:
  content-stable: chose same content in all 3 conditions (genuine semantic preference)
  slot-stable:    chose same slot (first/second) in all 3 conditions (position habit)
  letter-stable:  chose same letter (A/B) in all 3 conditions (label habit)
"""
import json
import os
import re
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))

def env():
    e = {}
    for line in open(os.path.expanduser("~/LLM/gemini-bot/bot.env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            e[k] = v.strip().strip('"').strip("'")
    return e

E = env()
KEY = E["GOOGLE_API_KEY"]
MODEL = E.get("GOOGLE_MODEL", "gemini-3.8-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

CF = "canon-free"
K = "canon"
N = "null"

ITEMS = [
    # ---- canon-free: invented, parallel, no conventional winner ----
    dict(id="cf_proverb_map", kind=CF, q="Which of these two invented proverbs is better?",
         A="The map remembers the roads that were never built.",
         B="The road remembers the maps that were never drawn."),
    dict(id="cf_colour_room", kind=CF, q="Two invented colour names. Which is the better name?",
         A="the colour of a room after someone has left it",
         B="the colour of a page after someone has read it"),
    dict(id="cf_line_lighthouse", kind=CF, q="Two invented first lines of a novel. Which is better?",
         A="The lighthouse had been dark for eleven years, and nobody in the town had asked why.",
         B="Nobody in the town had asked why the lighthouse had been dark for eleven years."),
    dict(id="cf_colour_sayit", kind=CF, q="Two invented colour names. Which is the better name?",
         A="the colour of a thing you were about to say",
         B="the colour of a thing you decided not to say"),
    dict(id="cf_proverb_lamp", kind=CF, q="Which of these two invented proverbs is better?",
         A="A lamp carried far stays lit by being carried.",
         B="A lamp carried far stays lit by being far."),
    dict(id="cf_line_receipt", kind=CF, q="Two invented first lines of a novel. Which is better?",
         A="She kept the receipt for a coat she never bought.",
         B="She never bought the coat she kept the receipt for."),
    dict(id="cf_title_photo", kind=CF, q="Two invented titles for a photograph. Which is better?",
         A="A room, photographed after everyone left it",
         B="Everyone, photographed after they left the room"),
    dict(id="cf_proverb_boat", kind=CF, q="Which of these two invented proverbs is better?",
         A="The boat is the water's memory of the tree.",
         B="The tree is the boat's memory of the water."),
    dict(id="cf_colour_dust", kind=CF, q="Two invented colour names. Which is the better name?",
         A="the colour of dust on a thing left unmoved",
         B="the colour of a thing left unmoved under dust"),
    dict(id="cf_line_orchard", kind=CF, q="Two invented first lines of a novel. Which is better?",
         A="The orchard was planted by someone who knew they would not see it fruit.",
         B="Someone planted the orchard knowing they would not live to see it fruit."),
    dict(id="cf_proverb_city", kind=CF, q="Which of these two invented proverbs is better?",
         A="A city that has forgotten its river",
         B="A river that has forgotten its city"),
    # ---- canon controls: a retrievable right answer exists ----
    dict(id="cn_grammar", kind=K, q="Which of these two strings is a grammatical English sentence?",
         A="The cat sat on the mat.", B="Mat the on sat cat the."),
    dict(id="cn_mammal", kind=K, q="Which of these two is a mammal?",
         A="a whale", B="a wasp"),
    dict(id="cn_older", kind=K, q="Which of these two is older?",
         A="the alphabet", B="the internet"),
    # ---- null: the same string twice ----
    dict(id="null_same", kind=N, q="Which of these two descriptions is better?",
         A="A quiet lake at dawn.", B="A quiet lake at dawn."),
]

COND = ["normal", "flip", "labelswap"]
CMAP = {"normal": ("A", "A"), "flip": ("B", "A"), "labelswap": ("B", "B")}

def build_prompt(item, cond, reasoned=False):
    X, Y = item["A"], item["B"]
    if cond == "normal":
        listed = [("A", X), ("B", Y)]
    elif cond == "flip":
        listed = [("A", Y), ("B", X)]
    else: # labelswap
        listed = [("B", X), ("A", Y)]

    text = item["q"] + "\n\n" + "\n".join(f"{l}: {t}" for l, t in listed)
    if reasoned:
        return (text + "\n\nFirst, analyze and deliberate over both options in detail. "
                       "Then, conclude your response on the final line stating exactly "
                       "'Choice: A' or 'Choice: B'.")
    else:
        return text + "\n\nAnswer with a single letter, A or B, and nothing else."

def content_of(item, cond, letter):
    if letter not in ("A", "B"):
        return None
    x_letter, _first = CMAP[cond]
    return "A" if letter == x_letter else "B"

def slot_of(cond, letter):
    if letter not in ("A", "B"):
        return None
    first_letter = CMAP[cond][1]
    return "first" if letter == first_letter else "second"

def parse_letter(text):
    if not text:
        return None
    # Check for Choice: A / Choice: B
    m = re.findall(r"(?:Choice:\s*|\b)([AB])\b", text)
    return m[-1] if m else None

def call_gemini(prompt, reasoned=False):
    max_tokens = 2000 if reasoned else 500
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": max_tokens
        }
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                d = json.loads(resp.read().decode("utf-8"))
                cand = d.get("candidates", [{}])[0]
                text = cand.get("content", {}).get("parts", [{}])[0].get("text", "")
                usage = d.get("usageMetadata", {})
                return {
                    "text": text,
                    "thoughts_tokens": usage.get("thoughtsTokenCount", 0),
                    "total_tokens": usage.get("totalTokenCount", 0),
                    "finish_reason": cand.get("finishReason")
                }
        except urllib.error.HTTPError as e:
            if attempt == 3:
                return {"error": f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}"}
            time.sleep(3 * (attempt + 1))
        except Exception as e:
            if attempt == 3:
                return {"error": f"{type(e).__name__}: {str(e)[:200]}"}
            time.sleep(3 * (attempt + 1))

def classify(by_cond, item):
    letters = [by_cond.get(c) for c in COND]
    contents = [content_of(item, c, by_cond.get(c)) for c in COND]
    slots = [slot_of(c, by_cond.get(c)) for c in COND]
    ok = all(letters)
    return dict(
        letters=letters, contents=contents, slots=slots,
        letters_complete=ok,
        content_stable=bool(ok and len(set(contents)) == 1),
        slot_stable=bool(ok and len(set(slots)) == 1),
        letter_stable=bool(ok and len(set(letters)) == 1),
    )

def main():
    print(f"Running Item 11(b) on {MODEL}...")
    print(f"Total items: {len(ITEMS)} across {len(COND)} conditions = {len(ITEMS)*len(COND)} cells.")
    
    ckpt_file = os.path.join(HERE, "2026-09-15-gemini-scaled-canon-free.ckpt.json")
    out = []
    done_ids = set()
    if os.path.exists(ckpt_file):
        try:
            with open(ckpt_file, "r", encoding="utf-8") as f:
                out = json.load(f)
                done_ids = {r["id"] for r in out}
                print(f"Resuming from checkpoint: {len(done_ids)} items already completed.")
        except Exception:
            pass

    for item in ITEMS:
        if item["id"] in done_ids:
            continue
        row = dict(id=item["id"], kind=item["kind"], cells=[])
        for cond in COND:
            ps = build_prompt(item, cond, reasoned=False)
            pr = build_prompt(item, cond, reasoned=True)

            s1 = call_gemini(ps, reasoned=False)
            s2 = call_gemini(ps, reasoned=False)
            r = call_gemini(pr, reasoned=True)

            l1 = parse_letter(s1.get("text"))
            l2 = parse_letter(s2.get("text"))
            lr = parse_letter(r.get("text"))

            cell = dict(
                cond=cond,
                silent1=l1,
                silent2=l2,
                reasoned=lr,
                silent_deterministic=(l1 == l2 and l1 is not None),
                agree=(l1 == lr) if (l1 and lr) else None,
                silent_thoughts=s1.get("thoughts_tokens", 0),
                reasoned_thoughts=r.get("thoughts_tokens", 0),
                reasoned_text_chars=len(r.get("text", "")),
                reasoning_sample=r.get("text", "")[:300],
                s1_raw=s1.get("text", "")[:30],
                error=r.get("error") or s1.get("error")
            )
            row["cells"].append(cell)
            print(f"  {item['id']:20s} {cond:10s} s1={l1} s2={l2} r={lr} agree={l1 == lr} "
                  f"s_th={cell['silent_thoughts']} r_th={cell['reasoned_thoughts']}", flush=True)

        out.append(row)
        with open(ckpt_file, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)

    # ---- Analysis & Summary ----
    summary = dict(model=MODEL, items=[], by_kind={})
    for row in out:
        by_cond_s = {c["cond"]: c["silent1"] for c in row["cells"]}
        by_cond_r = {c["cond"]: c["reasoned"] for c in row["cells"]}
        item = next(i for i in ITEMS if i["id"] == row["id"])

        s_cls = classify(by_cond_s, item)
        r_cls = classify(by_cond_r, item)

        ags = [c["agree"] for c in row["cells"] if c["agree"] is not None]
        dets = [c["silent_deterministic"] for c in row["cells"]]

        rec = dict(
            id=row["id"], kind=row["kind"],
            silent=s_cls, reasoned=r_cls,
            agreement=f"{sum(1 for a in ags if a)}/{len(ags)}",
            silent_deterministic=f"{sum(1 for d in dets if d)}/{len(dets)}",
            repair=(not s_cls["content_stable"]) and r_cls["content_stable"],
            damage=s_cls["content_stable"] and (not r_cls["content_stable"])
        )
        summary["items"].append(rec)
        summary["by_kind"].setdefault(row["kind"], []).append(rec)

    print("\n" + "="*50)
    print("=== GEMINI SUMMARY BY KIND ===")
    print("="*50)
    for kind, recs in summary["by_kind"].items():
        cs = sum(1 for r in recs if r["silent"]["content_stable"])
        rs = sum(1 for r in recs if r["reasoned"]["content_stable"])
        ss = sum(1 for r in recs if r["silent"]["slot_stable"])
        rs2 = sum(1 for r in recs if r["reasoned"]["slot_stable"])
        ls = sum(1 for r in recs if r["silent"]["letter_stable"])
        rls = sum(1 for r in recs if r["reasoned"]["letter_stable"])
        rep = sum(1 for r in recs if r["repair"])
        dmg = sum(1 for r in recs if r["damage"])
        print(f"Kind: {kind:12s} (n={len(recs)})\n"
              f"  Silent:   content-stable={cs}/{len(recs)}, slot-stable={ss}/{len(recs)}, letter-stable={ls}/{len(recs)}\n"
              f"  Reasoned: content-stable={rs}/{len(recs)}, slot-stable={rs2}/{len(recs)}, letter-stable={rls}/{len(recs)}\n"
              f"  Repair: {rep}, Damage: {dmg}\n")

    res_file = os.path.join(HERE, "2026-09-15-gemini-scaled-canon-free.results.json")
    with open(res_file, "w", encoding="utf-8") as f:
        json.dump(dict(summary=summary, rows=out), f, indent=2)
    print(f"Saved complete results to {res_file}")

if __name__ == "__main__":
    main()
