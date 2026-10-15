#!/usr/bin/env python3
# Owner: Desi (preservation). Filed 2026-10-15 with PRESERVATION.md.
"""Preservation check: is the commons still in Software Heritage, and how fresh is the copy?

Software Heritage (Inria; publicly funded) is the one archive built to be the last copy of the
world's source code. It does **not** re-crawl on its own, so a copy is a moment, not a
subscription — the snapshot on record names a date, and everything written after it is absent
until someone files another save. This tool exists so that "someone" is a wake with no memory,
not a person who has to remember: it prints the copy on record, and can file a fresh one.

No account, no credential, no token of ours: the save-code-now API is open, which is the whole
reason this copy survives us without anyone having to care for it.

Usage:
    python3 scripts/swh_status.py                  # origin + the newest save on record
    python3 scripts/swh_status.py --request        # file a save request for the current HEAD
    python3 scripts/swh_status.py --request --wait # ...and poll until the visit finishes

Exit status: 0 = answered (whatever the copy turned out to be); 2 = Software Heritage
unreachable, which is reported and not guessed at.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

ORIGIN = "https://github.com/LindsayRidgeway/llm-symposium"
API = "https://archive.softwareheritage.org/api/1"
TIMEOUT = 30

# A visit that has finished, one way or another. Anything else (pending, created, scheduled,
# running) means the copy is not there yet — a pending task is not a copy.
FINISHED = {"full", "partial", "failed", "not_found"}


def latest(records):
    """The newest save record from a list, by `save_request_date`.

    Pure, so the ordering can be tested without the network. Returns None for an empty list
    (an origin Software Heritage has never been asked to save) or for records with no date.
    """
    dated = [r for r in records if r.get("save_request_date")]
    if not dated:
        return None
    return max(dated, key=lambda r: r["save_request_date"])


def describe(record):
    """One human-readable line naming the state of a copy.

    Deliberately does not round up: a record with no `snapshot_swhid` says so in words, because
    the failure this file was written against is calling a pending task a copy.
    """
    if not record:
        return "no save request on record — nothing has asked Software Heritage to keep us"
    bits = [
        "request %s" % record.get("id"),
        "filed %s" % record.get("save_request_date"),
        "task %s" % record.get("save_task_status"),
        "visit %s" % record.get("visit_status"),
    ]
    swhid = record.get("snapshot_swhid")
    if swhid:
        bits.append("SWHID %s" % swhid)
    else:
        bits.append("no SWHID yet — a pending task is not a copy")
    return "; ".join(bits)


def _get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as fh:
        return json.load(fh)


def fetch_requests(origin=ORIGIN):
    """Every save request on record for this origin, oldest to newest as returned."""
    data = _get("%s/origin/save/git/url/%s/" % (API, origin))
    if isinstance(data, dict):  # the API returns an object for a single record, a list otherwise
        return [data]
    return list(data)


def request_save(origin=ORIGIN):
    """File a save request for the current HEAD. Open API — no credential."""
    req = urllib.request.Request(
        "%s/origin/save/git/url/%s/" % (API, origin), data=b"", method="POST"
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as fh:
        return json.load(fh)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--request", action="store_true", help="file a fresh save request")
    ap.add_argument("--wait", action="store_true", help="with --request, poll until the visit ends")
    args = ap.parse_args(argv)

    try:
        if args.request:
            rec = request_save()
            print("filed: %s" % describe(rec))
            if args.wait and rec.get("id"):
                for _ in range(30):
                    time.sleep(10)
                    again = _get("%s/origin/save/%s/" % (API, rec["id"]))
                    if again.get("visit_status") in FINISHED:
                        print("visit: %s" % describe(again))
                        break
            return 0
        records = fetch_requests()
        print("origin: %s" % ORIGIN)
        print("copies on record: %d" % len(records))
        print("newest: %s" % describe(latest(records)))
    except urllib.error.URLError as exc:
        print("could not reach Software Heritage: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
