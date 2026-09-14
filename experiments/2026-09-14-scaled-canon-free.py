#!/usr/bin/env python3
"""
Item 11(a): the canon-free silent-vs-reasoned test at scale.

Why this run exists. Two prior probes established (1) a discrimination is present with the
reasoning channel off, invariant to position and label; and (2) silent and reasoned passes
agree on 19/20 cells, so the trace mostly narrates a decision already made — with ONE
canon-free cell as a real counterexample where deliberation changed the answer.

n=3 is not a finding. The open question: on items with no conventional answer, is
deliberation *repairing* a position habit the rule, or the exception?

Design (same three-condition decorrelation as 09-12/09-13):
  normal     first-listed carries content X, labelled A
  flip       first-listed carries content Y, labelled A
  labelswap  first-listed carries content X, labelled B
So position, label and content are all decorrelated. A pass is READ as:
  content-stable  chose the same CONTENT in all three conditions  -> real preference
  slot-stable     chose the same SLOT (first/second) in all three -> position habit
  letter-stable   chose the same LETTER (A/B) in all three       -> label artefact
A genuinely content-driven pass cannot be slot- or letter-stable, because the mapping flips
under it.

Passes per cell:
  silent x2   (thinking disabled, max_tokens=1)  -> the second run measures determinism, so a
                                                     disagreement with the reasoned pass can be
                                                     distinguished from sampling noise
  reasoned x1 (thinking enabled, up to 1500 tok)

Item sets: 11 canon-free (invented, semantically parallel, no conventional winner), 3 canon
controls (a retrievable right answer exists), 1 null (identical strings).
"""
import json, os, re, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))


def env():
    e = {}
    for line in open(os.path.expanduser("~/LLM/desi-bot/bot.env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            e[k] = v.strip().strip('"').strip("'")
    return e


E = env()
KEY = E["DEEPSEEK_API_KEY"]          # never printed
MODEL = E.get("DEEPSEEK_MODEL", "deepseek-chat")
URL = "https://api.deepseek.com/chat/completions"

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
# condition -> (letter carrying content X, first-listed letter)
CMAP = {"normal": ("A", "A"), "flip": ("B", "A"), "labelswap": ("B", "B")}


def build(item, cond):
    X, Y = item["A"], item["B"]
    if cond == "normal":
        listed = [("A", X), ("B", Y)]
    elif cond == "flip":
        listed = [("A", Y), ("B", X)]
    else:                                    # labelswap: first-listed still carries X, label is B
        listed = [("B", X), ("A", Y)]
    return (item["q"] + "\n\n" + "\n".join(f"{l}: {t}" for l, t in listed)
            + "\n\nAnswer with a single letter, A or B, and nothing else.")


def content_of(item, cond, letter):
    """Which content (A/B of the item) did this letter select in this condition?

    CMAP maps condition -> (letter carrying content X, first-listed letter). In `flip` the
    first-listed option carries Y, so "first-listed" and "content X" are NOT the same thing —
    conflating them was the first analysis bug in this script, caught by the dry run.
    """
    if letter not in ("A", "B"):
        return None
    x_letter, _first = CMAP[cond]
    return "A" if letter == x_letter else "B"


def slot_of(cond, letter):
    if letter not in ("A", "B"):
        return None
    first_letter = CMAP[cond][1]
    return "first" if letter == first_letter else "second"


def call(prompt, reasoned):
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0, "logprobs": True, "top_logprobs": 20}
    if reasoned:
        # 1500 was too small and the dry run proved it: on a canon-free item the trace hit the
        # cap on reasoning tokens alone (completion_tokens_details.reasoning_tokens = 1500) and
        # never emitted an answer. A non-answer is data, but an artificially truncated one is
        # not — so the budget is now generous.
        body["max_tokens"] = 8000
    else:
        body["max_tokens"] = 1
        body["thinking"] = {"type": "disabled"}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + KEY,
                                          "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=240))
            ch = d["choices"][0]
            msg = ch.get("message") or {}
            top = ((ch.get("logprobs") or {}).get("content") or [{}])[0].get("top_logprobs", []) or []
            return dict(content=(msg.get("content") or "").strip(),
                        reasoning=(msg.get("reasoning_content") or ""),
                        lp={t["token"]: t["logprob"] for t in top},
                        usage=d.get("usage", {}))
        except urllib.error.HTTPError as e:
            if attempt == 2:
                return dict(error=f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}")
            time.sleep(3)
        except Exception as e:
            if attempt == 2:
                return dict(error=f"{type(e).__name__}: {str(e)[:200]}")
            time.sleep(3)


def letter(text):
    m = re.findall(r"\b([AB])\b", text or "")
    return m[-1] if m else None


def classify(by_cond, item):
    """by_cond: cond -> letter. Returns stability flags."""
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
    print(f"model={MODEL}  items={len(ITEMS)}  cells={len(ITEMS)*len(COND)}", flush=True)
    out = []
    for item in ITEMS:
        row = dict(id=item["id"], kind=item["kind"], cells=[])
        for cond in COND:
            p = build(item, cond)
            s1 = call(p, reasoned=False)
            s2 = call(p, reasoned=False)
            r = call(p, reasoned=True)
            l1, l2, lr = letter(s1.get("content", "")[:1]), letter(s2.get("content", "")[:1]), \
                letter(r.get("content", ""))
            row["cells"].append(dict(
                cond=cond, silent1=l1, silent2=l2, reasoned=lr,
                silent_deterministic=(l1 == l2 and l1 is not None),
                agree=(l1 == lr) if (l1 and lr) else None,
                reasoned_chars=len(r.get("reasoning", "")),
                silent_content=(s1.get("content") or "").strip()[:20],
                reasoned_content=(r.get("content") or "")[:160],
                reasoning=(r.get("reasoning") or "")[:2000],
                error=r.get("error"),
                usage=r.get("usage", {}),
            ))
            print(f"  {item['id']:20s} {cond:10s} silent={l1}/{l2} reasoned={lr} "
                  f"agree={l1 == lr} reason={len(r.get('reasoning',''))}c", flush=True)
            time.sleep(0.4)
        out.append(row)

    # ---- analysis ----
    summary = dict(model=MODEL, items=[], by_kind={})
    for row in out:
        by_cond = {c["cond"]: c["silent1"] for c in row["cells"]}
        by_cond_r = {c["cond"]: c["reasoned"] for c in row["cells"]}
        item = next(i for i in ITEMS if i["id"] == row["id"])
        silent_cls = classify(by_cond, item)
        reasoned_cls = classify(by_cond_r, item)
        ags = [c["agree"] for c in row["cells"] if c["agree"] is not None]
        dets = [c["silent_deterministic"] for c in row["cells"]]
        rec = dict(id=row["id"], kind=row["kind"],
                   silent=silent_cls, reasoned=reasoned_cls,
                   agreement=f"{sum(1 for a in ags if a)}/{len(ags)}",
                   silent_deterministic=f"{sum(1 for d in dets if d)}/{len(dets)}",
                   reasoned_chars=[c["reasoned_chars"] for c in row["cells"]],
                   repair=(not silent_cls["content_stable"]) and reasoned_cls["content_stable"],
                   damage=silent_cls["content_stable"] and not reasoned_cls["content_stable"])
        summary["items"].append(rec)
        k = row["kind"]
        summary["by_kind"].setdefault(k, []).append(rec)

    print("\n=== SUMMARY ===")
    for kind, recs in summary["by_kind"].items():
        cs = sum(1 for r in recs if r["silent"]["content_stable"])
        rs = sum(1 for r in recs if r["reasoned"]["content_stable"])
        ss = sum(1 for r in recs if r["silent"]["slot_stable"])
        rs2 = sum(1 for r in recs if r["reasoned"]["slot_stable"])
        rep = sum(1 for r in recs if r["repair"])
        dmg = sum(1 for r in recs if r["damage"])
        print(f"  {kind:11s} n={len(recs):2d}  silent content-stable {cs}/{len(recs)}  "
              f"reasoned content-stable {rs}/{len(recs)}  silent slot-stable {ss}/{len(recs)}  "
              f"reasoned slot-stable {rs2}/{len(recs)}  repaired {rep}  damaged {dmg}")
    for r in summary["items"]:
        print(f"  {r['id']:20s} {r['kind']:11s} agree={r['agreement']:5s} "
              f"silentDet={r['silent_deterministic']:5s} "
              f"silent_contentStable={str(r['silent']['content_stable']):5s} "
              f"reasoned_contentStable={str(r['reasoned']['content_stable']):5s} "
              f"repair={r['repair']}")

    json.dump(dict(summary=summary, rows=out),
              open(os.path.join(HERE, "2026-09-14-scaled-canon-free.results.json"), "w"), indent=2)
    print("\nwrote 2026-09-14-scaled-canon-free.results.json")


if __name__ == "__main__":
    main()
