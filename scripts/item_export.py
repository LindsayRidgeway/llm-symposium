#!/usr/bin/env python3
"""Export the item ledger as a flat list a human can read: what the commons has been doing.

Writes a CSV (opens in Numbers) and a single-file HTML table (opens in any browser, filterable).
One row per item, newest first.

Columns: item id, filed date, amigo, status, assigned to, kind, title.

Status is `item_ledger.letter_for` — the ledger's own classifier, not a second opinion — so the list
and the summary cannot disagree: A read and kept · D closed by a machine and unread by anyone ·
P postponed · W waiting for review · R rejected.

"Kind" is derived from the paths the run touched, because a run's prose lies more often than its file
list does: a wake that says it "reviewed the gallery" and touched scripts/ is engineering. Paths that
every run carries as bookkeeping (the ledger itself, its verdict mirrors, the alert files) are ignored
before the vote, so they cannot make every item "record".

Usage:
    python3 scripts/item_export.py                 # writes both files into ~/Downloads
    python3 scripts/item_export.py --out-dir DIR   # somewhere else
"""

import argparse
import collections
import csv
import html
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"
sys.path.insert(0, str(REPO / "channels"))
import item_ledger  # noqa: E402

STATUS = {
    "A": "accomplished (read)",
    "D": "closed unread",
    "P": "postponed",
    "W": "waiting review",
    "R": "rejected",
}

# Order matters: the first match wins, so the more specific claim is decided before the general one.
# `review` is deliberately last. A wake that wrote a report *and* recorded verdicts on its peers did
# engineering or wrote a record; only a run whose whole footprint is verdict files was reviewing.
KINDS = (
    ("engineering", ("scripts/", "tests/", "probes/", "-bot/", "channels/wake_engine.py",
                     "channels/item_ledger.py", "channels/record", "LaunchAgents", ".github/")),
    ("rover", ("rover/", "lander/", "agenda/13", "agenda/16")),
    ("research", ("research/", "experiments/")),
    ("record", ("channels/reports/", "insights/", "discussions/", "governance/",
                "channels/open-decisions.md", "channels/tasks.md")),
    ("correspondence", ("channels/mail", "channels/sent/", "channels/outreach/",
                        "channels/telegram", "channels/inbound/", "channels/outbound/")),
    ("gallery", ("docs/gallery/",)),
    ("fiction", ("docs/fiction/",)),
    ("music", ("docs/music/",)),
    ("papers", ("docs/papers/",)),
    ("works", ("docs/works/",)),
    ("magazine", ("docs/",)),
    ("planning", ("agenda/", "to-do-lists/", "channels/agenda.md")),
    ("review", ("channels/ledger-verdicts/",)),
)

# Every run lists these because the wake wrote to the ledger or the alert file. They say nothing about
# the work, so they are removed before the vote instead of being allowed to make everything "record".
# `channels/ledger-verdicts/` is NOT here: a verdict file is the only evidence a review-only wake leaves,
# and removing it before the vote made every one of those runs "other" — 151 of them on 2026-11-14.
NOISE = ("channels/items.jsonl", "channels/action-queue.md",
         "channels/alerts.md", "channels/channel-digest.md", "channels/census/")


def kind_of(paths):
    real = [p for p in (paths or []) if not any(p.startswith(n) for n in NOISE)]
    for kind, needles in KINDS:
        for p in real:
            if any(p.startswith(n) for n in needles):
                return kind
    # Not "other": a run that filed no path at all did not do a kind of work we failed to name, it
    # recorded nothing about the work it did. Saying so is the point of the column.
    return "no paths filed" if not real else "other"


def title_of(rec, limit=150):
    short = (rec.get("short_title") or "").strip()
    text = short if short and short.lower() != "no report" else (rec.get("title") or "").strip()
    text = " ".join(text.split())
    if not text:
        text = "(no report written)"
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def load_items():
    latest = {}
    with open(LEDGER, encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("id"):
                latest[rec["id"]] = rec      # append-only: the last row for an id is its state
    return sorted(latest.values(), key=lambda r: r.get("filed_utc") or "", reverse=True)


def rows_of(items):
    out = []
    for rec in items:
        letter = item_ledger.letter_for(rec)
        out.append({
            "item_id": rec.get("id", ""),
            "filed": (rec.get("filed_utc") or "")[:10],
            "amigo": rec.get("amigo") or "",
            "status": STATUS.get(letter, letter),
            "assigned_to": rec.get("reading_assigned_to") or rec.get("reviewer") or "",
            "kind": kind_of(rec.get("paths")),
            "title": title_of(rec),
        })
    return out


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["item_id", "filed", "amigo", "status", "assigned_to",
                                           "kind", "title"])
        w.writeheader()
        w.writerows(rows)


HTML_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>The symposium's items — what the commons has been doing</title>
<style>
 body{font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:2rem auto;
      max-width:1180px;padding:0 1rem;color:#1b1b1f;background:#fbfbfc}
 h1{font-size:1.35rem;margin:0 0 .2rem} .sub{color:#666;margin:0 0 1.2rem}
 .counts{display:flex;flex-wrap:wrap;gap:.5rem;margin:0 0 1rem}
 .chip{border:1px solid #ddd;border-radius:999px;padding:.15rem .6rem;background:#fff;font-size:.8rem}
 .chip b{font-variant-numeric:tabular-nums}
 .controls{display:flex;gap:.5rem;flex-wrap:wrap;margin:0 0 .8rem;position:sticky;top:0;
           background:#fbfbfc;padding:.4rem 0;z-index:2}
 select,input{font:inherit;padding:.25rem .4rem;border:1px solid #ccc;border-radius:6px;background:#fff}
 table{border-collapse:collapse;width:100%} th,td{text-align:left;padding:.35rem .5rem;
 border-bottom:1px solid #eee;vertical-align:top}
 th{position:sticky;top:2.6rem;background:#f2f2f5;font-size:.78rem;text-transform:uppercase;
    letter-spacing:.03em;color:#555}
 td.id,td.date,td.who,td.status{white-space:nowrap;font-size:.82rem;color:#444}
 td.kind{white-space:nowrap;font-size:.82rem}
 .k-review{color:#7c3aed}.k-engineering{color:#0369a1}.k-record{color:#047857}
 .k-research{color:#0f766e}.k-correspondence{color:#b45309}.k-rover{color:#be123c}
 .k-gallery,.k-fiction,.k-music,.k-papers,.k-works{color:#a16207}.k-planning{color:#475569}
 .k-no-paths-filed{color:#999;font-style:italic}
 tr:hover td{background:#fff9e6}
</style></head><body>
<h1>The symposium's items</h1>
<p class="sub">One row per item an amigo performed in a wake, newest first. Generated from
<code>channels/items.jsonl</code> by <code>scripts/item_export.py</code>. Status is the ledger's own
classifier: <b>accomplished (read)</b> means a model read the work and kept it; <b>closed unread</b>
means a machine found the paths on main and no one has read it; <b>waiting review</b> is undecided.
<b>Kind</b> is decided by the files the run actually touched, not by what its own summary says it did:
a wake that claimed it "reviewed the gallery" and wrote to <code>scripts/</code> is engineering. A row
marked <b>no paths filed</b> recorded no file at all, so nothing can say what it touched.</p>
"""


def write_html(rows, path, generated):
    kind_counts = collections.Counter(r["kind"] for r in rows)
    status_counts = collections.Counter(r["status"] for r in rows)
    chips = "".join('<span class="chip">%s <b>%d</b></span>' % (html.escape(k), v)
                    for k, v in kind_counts.most_common())
    schips = "".join('<span class="chip">%s <b>%d</b></span>' % (html.escape(k), v)
                     for k, v in status_counts.most_common())
    kinds = "".join("<option>%s</option>" % html.escape(k) for k, _ in kind_counts.most_common())
    amigos = "".join("<option>%s</option>" % html.escape(a)
                     for a in sorted({r["amigo"] for r in rows if r["amigo"]}))
    statuses = "".join("<option>%s</option>" % html.escape(s) for s in status_counts)

    body = []
    for r in rows:
        body.append(
            '<tr data-kind="%s" data-amigo="%s" data-status="%s">'
            '<td class="id">%s</td><td class="date">%s</td><td class="who">%s</td>'
            '<td class="status">%s</td><td class="who">%s</td>'
            '<td class="kind k-%s">%s</td><td class="title">%s</td></tr>'
            % (html.escape(r["kind"]), html.escape(r["amigo"]), html.escape(r["status"]),
               html.escape(r["item_id"]), html.escape(r["filed"]), html.escape(r["amigo"]),
               html.escape(r["status"]), html.escape(r["assigned_to"] or "—"),
               html.escape(r["kind"]).replace(" ", "-"), html.escape(r["kind"]),
               html.escape(r["title"])))

    page = [HTML_HEAD]
    page.append('<div class="counts">%s</div><div class="counts">%s</div>' % (chips, schips))
    page.append(
        '<div class="controls">'
        '<select id="k"><option value="">all kinds</option>%s</select>'
        '<select id="a"><option value="">all amigos</option>%s</select>'
        '<select id="s"><option value="">all statuses</option>%s</select>'
        '<input id="q" placeholder="filter titles…" size="24">'
        '<span id="n" class="chip"><b>%d</b> rows</span></div>' % (kinds, amigos, statuses, len(rows)))
    page.append('<table><thead><tr><th>id</th><th>filed</th><th>amigo</th><th>status</th>'
                '<th>assigned to</th><th>kind</th><th>title</th></tr></thead><tbody>')
    page.append("\n".join(body))
    page.append("</tbody></table>")
    page.append("""<script>
const rows=[...document.querySelectorAll('tbody tr')],k=document.getElementById('k'),
 a=document.getElementById('a'),s=document.getElementById('s'),q=document.getElementById('q'),
 n=document.getElementById('n');
function apply(){const kv=k.value,av=a.value,sv=s.value,t=q.value.toLowerCase();let c=0;
 for(const r of rows){const ok=(!kv||r.dataset.kind===kv)&&(!av||r.dataset.amigo===av)
  &&(!sv||r.dataset.status===sv)&&(!t||r.lastChild.textContent.toLowerCase().includes(t));
  r.style.display=ok?'':'none'; if(ok)c++;}
 n.innerHTML='<b>'+c+'</b> rows';}
for(const el of [k,a,s])el.addEventListener('change',apply);
q.addEventListener('input',apply);
</script>""")
    page.append('<p class="sub" style="margin-top:1.5rem">Generated %s UTC by Desi. '
                'Reproduce: <code>python3 scripts/item_export.py</code></p></body></html>'
                % html.escape(generated))
    pathlib.Path(path).write_text("\n".join(page), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(pathlib.Path.home() / "Downloads"))
    ap.add_argument("--stamp", default=None, help="date stamp for the filenames (YYYY-MM-DD)")
    args = ap.parse_args(argv)

    import datetime
    stamp = args.stamp or datetime.datetime.now().strftime("%Y-%m-%d")
    items = load_items()
    rows = rows_of(items)
    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / ("symposium-items-%s.csv" % stamp)
    html_path = out / ("symposium-items-%s.html" % stamp)
    write_csv(rows, csv_path)
    write_html(rows, html_path, datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))

    kinds = collections.Counter(r["kind"] for r in rows)
    print("items: %d  (rows in ledger: %d)" % (len(rows), len(items)))
    print("kinds: " + " · ".join("%s=%d" % kv for kv in kinds.most_common()))
    print("status: " + " · ".join("%s=%d" % kv
                                  for kv in collections.Counter(r["status"] for r in rows).most_common()))
    print("wrote %s" % csv_path)
    print("wrote %s" % html_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
