#!/usr/bin/env python3
# Owner: Desi
"""How much citation traffic a retracted paper keeps *after* it is retracted.

Companion to `scripts/check_retracted_refs.py` (which answers the question for one
bibliography). This one answers a coarser, exportable question for a *list* of the
most-cited retracted works: for each, how many later works still cite it, and how
many of those were published on or after the retraction itself.

Three sources, each asked separately, so the number can be re-derived:

  1. RANK   — OpenAlex (`is_retracted:true`, sorted by `cited_by_count`). The flag is
              OpenAlex's, not our judgement.
  2. DATE   — Crossref by DOI: the boundary is the *latest* retraction notice date in
              the work's own `updated-by` / `update-to` entries whose `type` is
              `retraction`. Latest is the conservative choice: several records carry a
              backfilled entry stamped with the work's own publication date, which would
              put the boundary before anyone could have known. Where a record carries
              several dates the row prints them, so the divergence is visible rather
              than averaged away. No retraction entry at all → the row says `unconfirmed`,
              a hole in the check, not a zero.
  3. COUNT  — OpenAlex again, twice per work: `cites:<id>,from_publication_date:<d>`
              and `cites:<id>,to_publication_date:<d-1>`. Two asks rather than a
              subtraction, so the boundary is visible.

Honest scope, stated here because the output must state it too: a citation after a
retraction is not an endorsement; many citing works predate the retraction in
submission and were published after it; and a retraction is not a finding of fraud.

Usage:
  python3 scripts/retracted_works_citation_lag.py --top 12
  python3 scripts/retracted_works_citation_lag.py --top 12 --out-file PATH
  python3 scripts/retracted_works_citation_lag.py --selftest
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import urllib.parse
import urllib.request

OPENALEX = "https://api.openalex.org/works"
CROSSREF = "https://api.crossref.org/works/"
POLITE = "desi.s.amigo@gmail.com"
UA = "llm-symposium/1.0 (desi; mailto:desi.s.amigo@gmail.com)"


def _get_json(url: str, timeout: int = 40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def top_retracted(n: int) -> list[dict]:
    """The n most-cited works OpenAlex flags as retracted."""
    params = {
        "filter": "is_retracted:true",
        "sort": "cited_by_count:desc",
        "per-page": str(n),
        "select": "id,doi,display_name,publication_year,cited_by_count",
        "mailto": POLITE,
    }
    data = _get_json(f"{OPENALEX}?{urllib.parse.urlencode(params)}")
    return data["results"]


def retraction_notices(crossref_message: dict) -> list[dict]:
    """Every retraction *notice* in a Crossref work record, oldest first.

    Reads both directions (`updated-by` = notices pointing at this work, `update-to`
    = notices this work is) and keeps entries whose `type` is `retraction`. Each
    notice keeps its own DOI, so the reader can go and read what was actually
    retracted — which is not always the work in hand (see `notice_is_about_work`).
    """
    found: dict[str, dict] = {}
    for key in ("updated-by", "update-to"):
        for entry in crossref_message.get(key) or []:
            if (entry.get("type") or "").lower() != "retraction":
                continue
            parts = ((entry.get("updated") or {}).get("date-parts") or [[None]])[0]
            if not parts or not parts[0]:
                continue
            y, m, d = (list(parts) + [1, 1])[:3]
            iso = f"{int(y):04d}-{int(m or 1):02d}-{int(d or 1):02d}"
            found[iso] = {
                "date": iso,
                "doi": entry.get("DOI") or "",
                "label": entry.get("label") or "",
                "source": entry.get("source") or "",
            }
    return [found[k] for k in sorted(found)]


def retraction_dates(crossref_message: dict) -> list[str]:
    """Every distinct retraction *date* in a Crossref work record, ascending."""
    return [n["date"] for n in retraction_notices(crossref_message)]


def retraction_date(crossref_message: dict) -> str | None:
    """The *latest* retraction date in a Crossref work record, YYYY-MM-DD, or None.

    Latest, not first, and that is a measurement choice with a reason: several records
    carry a publisher entry whose timestamp is the work's own publication date (a
    backfilled `update-to` pointing at itself), which would put the boundary before
    anyone could have known. The latest notice date is the conservative boundary — it
    makes "cited after retraction" a lower bound — and where a record carries several,
    the row prints them all so the divergence is visible rather than averaged away.
    """
    dates = retraction_dates(crossref_message)
    return dates[-1] if dates else None


def _day_before(iso: str) -> str:
    y, m, d = (int(x) for x in iso.split("-"))
    return (datetime.date(y, m, d) - datetime.timedelta(days=1)).isoformat()


def citing_counts(work_id: str, since: str) -> tuple[int, int]:
    """(citations on/after `since`, citations before `since`) from OpenAlex."""
    tail = work_id.rsplit("/", 1)[-1]

    def count(flt: str) -> int:
        params = {"filter": flt, "per-page": "1", "select": "id", "mailto": POLITE}
        return _get_json(f"{OPENALEX}?{urllib.parse.urlencode(params)}")["meta"]["count"]

    after = count(f"cites:{tail},from_publication_date:{since}")
    before = count(f"cites:{tail},to_publication_date:{_day_before(since)}")
    return after, before


def build_rows(n: int) -> list[dict]:
    rows = []
    for w in top_retracted(n):
        doi = (w.get("doi") or "").replace("https://doi.org/", "")
        row = {
            "doi": doi,
            "title": (w.get("display_name") or "").strip(),
            "year": w.get("publication_year"),
            "cited": w.get("cited_by_count"),
            "retracted": None,
            "notice": "",
            "after": None,
            "before": None,
            "note": "",
        }
        try:
            msg = _get_json(CROSSREF + urllib.parse.quote(doi))["message"]
            notices = retraction_notices(msg)
            row["notice"] = notices[-1]["doi"] if notices else ""
            row["retracted"] = notices[-1]["date"] if notices else None
            if len(notices) > 1:
                row["note"] = "also " + ", ".join(n["date"] for n in notices[:-1])
        except Exception as exc:  # noqa: BLE001 - reported, not swallowed
            row["note"] = f"crossref failed: {type(exc).__name__}"
        if not row["retracted"]:
            row["note"] = row["note"] or "no retraction entry in Crossref (flag unconfirmed)"
            rows.append(row)
            continue
        try:
            row["after"], row["before"] = citing_counts(w["id"], row["retracted"])
        except Exception as exc:  # noqa: BLE001
            row["note"] = f"openalex count failed: {type(exc).__name__}"
        rows.append(row)
    return rows


def render(rows: list[dict]) -> str:
    out = []
    out.append("| # | work | notice | retracted | cited | on/after retraction | before | share after |")
    out.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        title = r["title"] if len(r["title"]) <= 64 else r["title"][:61] + "…"
        if r["after"] is None:
            after = before = share = "—"
            extra = f" ({r['note']})" if r["note"] else ""
        else:
            after, before = r["after"], r["before"]
            share = f"{100 * after / (after + before):.0f}%" if (after + before) else "—"
            extra = f" [{r['note']}]" if r["note"] else ""
        out.append(
            f"| {i} | {title} ({r['year']}) · {r['doi']}{extra} | {r['notice'] or '—'} "
            f"| {r['retracted'] or '—'} | {r['cited']} | {after} | {before} | {share} |"
        )
    return "\n".join(out)


def selftest() -> int:
    msg = {
        "updated-by": [
            {"DOI": "x", "type": "correction", "updated": {"date-parts": [[2004, 3, 6]]}},
            {"DOI": "y", "type": "retraction", "updated": {"date-parts": [[2010, 2, 6]]}},
        ]
    }
    assert retraction_date(msg) == "2010-02-06", retraction_date(msg)
    assert retraction_dates(msg) == ["2010-02-06"], retraction_dates(msg)
    assert retraction_date({"updated-by": [
        {"type": "retraction", "updated": {"date-parts": [[2020, 7, 1]]}},
        {"type": "retraction", "updated": {"date-parts": [[2024, 12, 16]]}},
    ]}) == "2024-12-16"  # latest wins: the earlier entry is a backfilled self-reference
    assert retraction_dates({"updated-by": [
        {"type": "retraction", "updated": {"date-parts": [[2024, 12, 16]]}},
        {"type": "retraction", "updated": {"date-parts": [[2020, 7, 1]]}},
        {"type": "erratum", "updated": {"date-parts": [[2025, 1, 1]]}},
    ]}) == ["2020-07-01", "2024-12-16"]
    assert retraction_date({"updated-by": []}) is None
    assert retraction_date({"update-to": [{"type": "retraction", "updated": {"date-parts": [[2020]]}}]}) == "2020-01-01"
    assert _day_before("2010-03-01") == "2010-02-28"
    assert _day_before("2010-02-06") == "2010-02-05"
    print("selftest ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--out-file", type=str, default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rows = build_rows(a.top)
    text = render(rows)
    if a.out_file:
        with open(a.out_file, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
