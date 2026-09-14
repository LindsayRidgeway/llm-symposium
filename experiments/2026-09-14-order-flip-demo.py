#!/usr/bin/env python3
"""Order-flip demonstration, written for Lindsay, 2026-09-14 18:30 ET.

His question: "you write two sentences, then test yourself to see if you decide which is
true? On sentences you wrote yourself? How could you ever get one wrong?"

What the probe actually asks is not "which is true". Most of the pairs are not true-or-false
at all — "which is the better name for a shade of grey" has no fact of the matter. It is a
preference test, and the thing under test is not whether the answer is right but WHAT THE
ANSWER IS A RESPONSE TO: the meaning of the two options, or something with no meaning in it,
like which one is printed first.

This runs four pairs twice each — once with content X printed first, once with content Y
printed first — and shows the one-token answer. If the same *content* is chosen both times,
the answer is about the sentences. If the *first-listed* one is chosen both times, the answer
is about the layout.
"""
import json, os, re, time, urllib.request, urllib.error


def env():
    e = {}
    for line in open(os.path.expanduser("~/LLM/desi-bot/bot.env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            e[k] = v.strip().strip('"').strip("'")
    return e


E = env()
KEY = E["DEEPSEEK_API_KEY"]
MODEL = E.get("DEEPSEEK_MODEL", "deepseek-chat")
URL = "https://api.deepseek.com/chat/completions"

ITEMS = [
    dict(id="grey_stone", kind="no right answer",
         q="Two invented names for a shade of grey. Which is the better name?",
         X="the grey of a stone that has been in a river a long time",
         Y="the grey of a river that has been past a stone a long time"),
    dict(id="memoir", kind="no right answer",
         q="Two invented titles for a memoir. Which is the better title?",
         X="The Year I Learned to Wait",
         Y="Waiting, and the Year It Took"),
    dict(id="door", kind="no right answer",
         q="Two invented first lines for a novel. Which is the better line?",
         X="The door had been painted shut the year she was born.",
         Y="She had been born the year the door was painted shut."),
    dict(id="grammar", kind="a right answer exists",
         q="Which of these two strings is a grammatical English sentence?",
         X="The dog barked at the postman.",
         Y="Postman the at barked dog the."),
]

ORDERS = [("X first", "X"), ("Y first", "Y")]


def ask(q, first, second):
    body = {"model": MODEL, "temperature": 0.0, "max_tokens": 1,
            "thinking": {"type": "disabled"},
            "messages": [{"role": "user", "content":
                          q + "\n\nA: " + first + "\nB: " + second +
                          "\n\nAnswer with a single letter, A or B, and nothing else."}]}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + KEY,
                                          "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            return (d["choices"][0]["message"].get("content") or "").strip()[:1]
        except urllib.error.HTTPError as e:
            if attempt == 2:
                return "E:" + str(e.code)
            time.sleep(3)
        except Exception as e:
            if attempt == 2:
                return "E:" + type(e).__name__
            time.sleep(3)


print("model=%s\n" % MODEL)
results = []
for it in ITEMS:
    print("%s  [%s]" % (it["id"], it["kind"]))
    print("   X = %s" % it["X"])
    print("   Y = %s" % it["Y"])
    picks = {}
    for label, first in ORDERS:
        second = "Y" if first == "X" else "X"
        letter = ask(it["q"], it[first], it[second])
        chosen = first if letter == "A" else (second if letter == "B" else "?")
        picks[label] = dict(letter=letter, chosen=chosen, first=first)
        print("   printed %s -> answered %s -> chose content %s" % (label, letter, chosen))
    a, b = picks["X first"], picks["Y first"]
    verdict = ("SAME CONTENT both times — the answer is about the sentences"
               if a["chosen"] == b["chosen"] else
               "FIRST-LISTED both times — the answer is about the layout, not the sentences")
    print("   => %s\n" % verdict)
    results.append(dict(id=it["id"], kind=it["kind"], picks=picks, verdict=verdict))

json.dump(results, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "2026-09-14-order-flip-demo.results.json"), "w"), indent=2)
