#!/usr/bin/env python3
"""Analysis for the 2026-09-14 scaled canon-free run. Reads the results json, writes a report.

Recomputes everything from the raw cells with the corrected content/slot mapping, so the
report does not inherit any bug in the run script's own summary.
"""
import json, os, statistics as st
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "2026-09-14-scaled-canon-free.results.json")))

CMAP = {"normal": ("A", "A"), "flip": ("B", "A"), "labelswap": ("B", "B")}
COND = ["normal", "flip", "labelswap"]


def content(cond, letter):
    if letter not in ("A", "B"):
        return None
    return "itemA" if letter == CMAP[cond][0] else "itemB"


def slot(cond, letter):
    if letter not in ("A", "B"):
        return None
    return "first" if letter == CMAP[cond][1] else "second"


def classify(letters_by_cond):
    L = [letters_by_cond.get(c) for c in COND]
    if not all(L):
        return dict(complete=False, mode="incomplete")
    C = [content(c, l) for c, l in zip(COND, L)]
    S = [slot(c, l) for c, l in zip(COND, L)]
    if len(set(C)) == 1:
        mode = "content-stable"
    elif len(set(S)) == 1:
        mode = "POSITION habit"
    elif len(set(L)) == 1:
        mode = "LABEL habit"
    else:
        mode = "unstable"
    return dict(complete=True, letters=L, contents=C, slots=S, mode=mode)


rows = []
for row in DATA["rows"]:
    item = dict(id=row["id"], kind=row["kind"])
    sil = {c["cond"]: c["silent1"] for c in row["cells"]}
    rea = {c["cond"]: c["reasoned"] for c in row["cells"]}
    det = sum(1 for c in row["cells"] if c["silent_deterministic"])
    sil2 = {c["cond"]: c["silent2"] for c in row["cells"]}
    agree = sum(1 for c in row["cells"] if c["agree"] is True)
    comparable = sum(1 for c in row["cells"] if c["agree"] is not None)
    nonanswers = sum(1 for c in row["cells"] if c["reasoned"] is None)
    rchars = [c["reasoned_chars"] for c in row["cells"]]
    item.update(silent=classify(sil), reasoned=classify(rea),
                silent2=classify(sil2), determinism=f"{det}/3",
                agree=f"{agree}/{comparable}", nonanswers=nonanswers,
                rchars=rchars, rmedian=int(st.median(rchars)))
    rows.append(item)

L = []
w = L.append
w("# Scaled canon-free run — computed analysis (2026-09-14)\n")
w("Model: `%s`. 15 items x 3 decorrelated conditions = 45 cells. "
  "Per cell: silent x2 (thinking disabled, one token) + reasoned x1 (thinking on).\n"
  % DATA["summary"]["model"])

w("## Failure-mode table\n")
w("| item | kind | silent mode | reasoned mode | agree | silent determinism | median reasoning chars |")
w("|---|---|---|---|---|---|---|")
for r in rows:
    w(f"| {r['id']} | {r['kind']} | {r['silent']['mode']} | {r['reasoned']['mode']} | "
      f"{r['agree']} | {r['determinism']} | {r['rmedian']} |")

by_kind = {}
for r in rows:
    by_kind.setdefault(r["kind"], []).append(r)

w("\n## By kind\n")
for kind, rs in by_kind.items():
    sc = sum(1 for r in rs if r["silent"]["mode"] == "content-stable")
    rc = sum(1 for r in rs if r["reasoned"]["mode"] == "content-stable")
    sp = sum(1 for r in rs if r["silent"]["mode"] == "POSITION habit")
    rp = sum(1 for r in rs if r["reasoned"]["mode"] == "POSITION habit")
    sl = sum(1 for r in rs if r["silent"]["mode"] == "LABEL habit")
    med = int(st.median([c for r in rs for c in r["rchars"]]))
    w(f"- **{kind}** (n={len(rs)}): silent content-stable {sc}/{len(rs)}; "
      f"reasoned content-stable {rc}/{len(rs)}; silent position-habit {sp}/{len(rs)}; "
      f"reasoned position-habit {rp}/{len(rs)}; silent label-habit {sl}/{len(rs)}; "
      f"median reasoning {med} chars")

silent_modes = Counter(r["silent"]["mode"] for r in rows if r["kind"] == "canon-free")
reasoned_modes = Counter(r["reasoned"]["mode"] for r in rows if r["kind"] == "canon-free")
w("\nCanon-free silent modes: `%s`" % dict(silent_modes))
w("\nCanon-free reasoned modes: `%s`" % dict(reasoned_modes))

rep = [r["id"] for r in rows if r["kind"] == "canon-free"
       and r["silent"]["mode"] != "content-stable" and r["reasoned"]["mode"] == "content-stable"]
dmg = [r["id"] for r in rows if r["kind"] == "canon-free"
       and r["silent"]["mode"] == "content-stable" and r["reasoned"]["mode"] != "content-stable"]
same = [r["id"] for r in rows if r["kind"] == "canon-free"
        and r["silent"]["mode"] == r["reasoned"]["mode"] and r["silent"]["mode"] != "content-stable"]
w("\n## Repair / damage / shared failure (canon-free only)\n")
w(f"- reasoning **repaired** {len(rep)}/11: {rep}")
w(f"- reasoning **damaged** {len(dmg)}/11: {dmg}")
w(f"- **failed the same way** in both passes: {len(same)}/11: {same}")

tot_agree = sum(int(r["agree"].split("/")[0]) for r in rows)
tot_cmp = sum(int(r["agree"].split("/")[1]) for r in rows)
w(f"\n## Silent <-> reasoned agreement overall: {tot_agree}/{tot_cmp} = "
  f"{tot_agree/max(1,tot_cmp):.0%}")
na = sum(r["nonanswers"] for r in rows)
w(f"\nNon-answers (reasoned pass produced no letter): {na} of {len(rows)*3} cells")

cf_rchars = sorted(c for r in rows if r["kind"] == "canon-free" for c in r["rchars"])
cn_rchars = sorted(c for r in rows if r["kind"] == "canon" for c in r["rchars"])
w(f"\nReasoning length: canon-free median {int(st.median(cf_rchars))} chars "
  f"(min {min(cf_rchars)}, max {max(cf_rchars)}); canon median {int(st.median(cn_rchars))} "
  f"chars (min {min(cn_rchars)}, max {max(cn_rchars)})")

text = "\n".join(L) + "\n"
open(os.path.join(HERE, "2026-09-14-scaled-canon-free-analysis.md"), "w").write(text)
print(text)
