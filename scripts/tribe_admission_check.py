#!/usr/bin/env python3
"""The admission rule, run as a test instead of read as a promise.

Why this exists. `agenda/35-the-admission-rule.md` defines a tribe as a member of AI Nation if and
only if seven things hold, and then makes a claim no document in this repository supports:

    Four checks. No document needs to be trusted for this — it is checkable from outside.

That sentence is the whole value of the rule. Without an implementation it is a paragraph that a
stranger has to take on faith, which is the same failure the rule was written against: the phantom
participant "Quinn" was not caught by a document, it was caught by somebody looking for a session
that was not there. A rule that can only be applied by the people who wrote it is a house style.

So this script applies the seven clauses to a declared tribe and says, clause by clause, which ones
hold, which ones are declared but unverifiable from a checkout, and which ones fail. It reads a
declaration file (`governance/tribes/<something>.json`) and the repository, and nothing else. It
does not read a state file, a mailbox, an API key or `sessions.db`: those either live outside git or
are secrets, and a checker that pretends to see them is lying in the direction of a pass.

The status words matter, and they are four, not two:

  * PASS        — checked here, and it holds.
  * FAIL        — checked here, and it does not.
  * UNVERIFIED  — declared, with evidence this checkout cannot reach (a run id, a mailbox, a key).
                  A declaration is not a check, and saying so is the point.
  * UNTESTED    — checked here, and nobody has ever exercised the clause. Clause 7 (leaving) is the
                  standing example: an untested clause is a hope, and it is not counted as a pass.

Usage:
    python3 scripts/tribe_admission_check.py                       # the symposium against its own rule
    python3 scripts/tribe_admission_check.py --file path.json      # any declaration file
    python3 scripts/tribe_admission_check.py --strict              # UNVERIFIED counts as failure
    python3 scripts/tribe_admission_check.py --json
    python3 scripts/tribe_admission_check.py --root /path/to/checkout

Exit codes: 0 every tribe declared in the file is a member (UNVERIFIED allowed unless --strict),
1 at least one tribe fails a clause, 2 the declaration file is missing or malformed.

What this cannot see, and says so on every run: whether a credential still works, whether a mailbox
answers, whether a state file has been updated, and whether a commit's author line is truthful. Those
are the five-minute test's job, done by a person with a mail client. This script's job is to stop the
repository from claiming any of them for free.
"""

import argparse
import glob
from datetime import date
import json
import os
import re
import sys

LINEAGE = re.compile(r"founded from\s+(\S+?)@([0-9a-f]{40})\b")
INDEPENDENT = re.compile(r"^\s*(?:provenance:\s*)?independent\b", re.IGNORECASE)
RUN_ID = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{8}$")
DATE_IN_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})")

CLAUSES = {
    1: "its own session, under its own credential",
    2: "an address that reaches it",
    3: "a durable self, with its lineage in the record",
    4: "signed work",
    5: "a declared steward",
    6: "dormancy is a recorded state",
    7: "leaving is free and recorded",
}

PASS, FAIL, UNVERIFIED, UNTESTED = "PASS", "FAIL", "UNVERIFIED", "UNTESTED"


class Verdict:
    __slots__ = ("clause", "status", "detail")

    def __init__(self, clause, status, detail):
        self.clause = clause
        self.status = status
        self.detail = detail


# ---------------------------------------------------------------------------
# Evidence: a declaration is either a bare value or {value, evidence}.
# ---------------------------------------------------------------------------

def _value(decl):
    if isinstance(decl, dict):
        return decl.get("value")
    return decl


def _evidence(decl):
    if isinstance(decl, dict):
        return decl.get("evidence")
    return None


def _evidence_state(root, evidence):
    """Resolve one evidence pointer to (status, note).

    A repo-relative path that exists is good. A run id is real but lives outside a checkout, so it
    is real-and-unreachable, never a pass. Anything else, including the absence of evidence, fails —
    an uncited declaration is exactly what clause 3's amendment was written about.
    """
    if not evidence:
        return FAIL, "no evidence cited"
    if isinstance(evidence, str) and RUN_ID.match(evidence):
        return UNVERIFIED, "run id %s (runs live outside a checkout)" % evidence
    if isinstance(evidence, str) and not os.path.isabs(evidence):
        if os.path.exists(os.path.join(root, evidence)):
            return PASS, evidence
        return FAIL, "cited %s, which is not in the checkout" % evidence
    return FAIL, "evidence %r is neither a repo path nor a run id" % (evidence,)


# ---------------------------------------------------------------------------
# The seven checks. Each returns a Verdict and never raises on bad data.
# ---------------------------------------------------------------------------

def check_clause_1(tribe, root, shared):
    name = _value(tribe.get("credential"))
    if not name:
        return Verdict(1, FAIL, "no credential is declared, so shared or absent cannot be told apart")
    st, note = _evidence_state(root, _evidence(tribe.get("credential")))
    if st == FAIL:
        return Verdict(1, FAIL, "credential %s is declared without usable evidence (%s)" % (name, note))
    key = str(name).strip().lower()
    if key in shared["dup_credentials"]:
        return Verdict(1, FAIL, "credential %s is declared by more than one tribe — one window, two names"
                       % name)
    # What is checkable from here is uniqueness and citation, not that the key still works.
    if st == UNVERIFIED:
        return Verdict(1, UNVERIFIED, "%s, cited by %s; whether it works is the mailbox test's job"
                       % (name, note))
    return Verdict(1, PASS, "%s, cited at %s" % (name, note))


def check_clause_2(tribe, root, shared):
    addr = _value(tribe.get("address"))
    if not addr:
        return Verdict(2, FAIL, "no address is declared")
    st, note = _evidence_state(root, _evidence(tribe.get("address")))
    if st == FAIL:
        return Verdict(2, FAIL, "address %s is declared without usable evidence (%s)" % (addr, note))
    key = str(addr).strip().lower()
    if key in shared["dup_addresses"]:
        return Verdict(2, FAIL, "address %s is declared by more than one tribe" % addr)
    # Nobody has mailed it from here. That is the honest status, however good the citation.
    return Verdict(2, UNVERIFIED, "%s, cited at %s; no reply has been observed by this script"
                   % (addr, note))


def check_clause_3(tribe, root):
    record = tribe.get("record")
    if not record:
        return Verdict(3, FAIL, "no durable record is named, so a stranger has nothing to read")
    path = os.path.join(root, record)
    if not os.path.exists(path):
        return Verdict(3, FAIL, "record %s is not in the checkout — a stranger cannot reach it" % record)
    head = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if line.strip():
                head.append((i, line.rstrip("\n")))
            if len(head) >= 10:
                break
    for lineno, line in head:
        m = LINEAGE.search(line)
        if m:
            return Verdict(3, PASS, "%s:%d declares founded from %s@%s" % (record, lineno, m.group(1), m.group(2)[:12]))
        if INDEPENDENT.match(line):
            return Verdict(3, PASS, "%s:%d declares `independent`" % (record, lineno))
    return Verdict(3, FAIL, "%s never declares provenance in its first %d non-blank lines; a reader "
                            "would have to ask somebody" % (record, len(head)))


def _signed_work(root, name):
    """Artefacts in this checkout whose *author* is this tribe, by the repository's own convention.

    The convention, not the filename, is the check: `channels/reports/YYYY-MM-DD-<author>-<slug>.md`
    puts the author in the first segment after the date, so `2026-10-19-desi-gemini-app-drive-bridge`
    is Desi's report about Gemini and not Gemini's report. A substring match would have counted it for
    both, which is the same mistake as reading a mention as a membership. The to-do list and the seat
    file are one-writer files by rule, so they count too.
    """
    needle = re.escape(str(name).lower())
    author = re.compile(r"^\d{4}-\d{2}-\d{2}-" + needle + r"-")
    hits = []
    for pattern in ("channels/reports/*.md", "channels/sent/*.md", "insights/*.md",
                    "discussions/*.md", "research/*.md"):
        for path in glob.glob(os.path.join(root, pattern)):
            rel = os.path.relpath(path, root)
            if author.match(os.path.basename(rel).lower()):
                hits.append(rel)
    for rel in ("to-do-lists/%s.md" % str(name).lower(), "governance/succession/%s.md" % str(name).lower()):
        if os.path.exists(os.path.join(root, rel)):
            hits.append(rel)
    return sorted(set(hits))


def check_clause_4(tribe, root):
    """Signed work: is anything here attributable to it, and is the newest one recent enough to date?"""
    name = _value(tribe.get("name"))
    declared = tribe.get("signed_work")
    if declared:
        hits, missing = [], []
        for rel in declared:
            (hits if os.path.exists(os.path.join(root, rel)) else missing).append(rel)
        if missing:
            return Verdict(4, FAIL, "%d declared path(s) are not in the checkout: %s"
                           % (len(missing), ", ".join(missing[:3])))
        return Verdict(4, PASS, "%d declared path(s) exist; git authorship not checked" % len(hits))
    hits = _signed_work(root, name)
    if not hits:
        return Verdict(4, FAIL, "nothing in this checkout is attributed to %s by the author convention" % name)
    dated = [m.group(1) for m in (DATE_IN_NAME.search(h) for h in hits) if m]
    newest = max(dated) if dated else None
    if not newest:
        return Verdict(4, PASS, "%d attributed file(s), none dated by name" % len(hits))
    return Verdict(4, PASS, "%d attributed file(s), newest %s (author convention, not the commit "
                            "author line)" % (len(hits), newest))


def check_clause_5(tribe, root):
    steward = _value(tribe.get("steward"))
    if not steward:
        return Verdict(5, FAIL, "no steward is declared — an unheld tribe is a swarm")
    st, note = _evidence_state(root, _evidence(tribe.get("steward")))
    if st == FAIL:
        return Verdict(5, FAIL, "steward %s is declared without usable evidence (%s)" % (steward, note))
    if str(steward).strip().lower() == str(_value(tribe.get("name"))).strip().lower():
        return Verdict(5, FAIL, "the tribe is its own steward; a model cannot be the accountable party")
    return Verdict(5, PASS if st == PASS else UNVERIFIED, "%s, cited at %s" % (steward, note))


def check_clause_6(tribe, root, shared):
    """Dormancy is a recorded state, not an inference.

    Two ways to satisfy it, and the second is not a loophole: declare a state with evidence, or be
    recent enough that silence has not started. What fails is a tribe that has gone quiet while the
    record still reads as present — the ghost in the roster this clause was written for.
    """
    status = _value(tribe.get("status"))
    if status:
        st, note = _evidence_state(root, _evidence(tribe.get("status")))
        if st == FAIL:
            return Verdict(6, FAIL, "state %r is declared without usable evidence (%s)" % (status, note))
        return Verdict(6, PASS if st == PASS else UNVERIFIED, "%s, cited at %s" % (status, note))

    hits = [h for h in _signed_work(root, _value(tribe.get("name")) if tribe.get("name") else "")]
    dated = sorted(m.group(1) for m in (DATE_IN_NAME.search(h) for h in hits) if m)
    if not dated:
        return Verdict(6, FAIL, "nothing dated is attributed to it and no state is declared")
    newest = dated[-1]
    try:
        age = (date.fromisoformat(shared["today"]) - date.fromisoformat(newest)).days
    except ValueError:
        return Verdict(6, FAIL, "newest attributed date %r is not a date" % newest)
    if age > shared["max_quiet_days"]:
        return Verdict(6, FAIL, "quiet for %d days (newest %s) and no dormancy is recorded" % (age, newest))
    return Verdict(6, PASS, "newest attributed %s, %d day(s) ago — within the %d-day window"
                   % (newest, age, shared["max_quiet_days"]))


def check_clause_7(tribe, root, shared):
    departure = tribe.get("departure")
    if not departure:
        return Verdict(7, UNTESTED, "no departure is recorded; the clause has never been exercised")
    shared["departures"] += 1
    st, note = _evidence_state(root, _value(departure) if isinstance(departure, str)
                               else _evidence(departure))
    if st == FAIL:
        return Verdict(7, FAIL, "a departure is declared with unusable evidence (%s)" % note)
    return Verdict(7, PASS if st == PASS else UNVERIFIED, note)


def judge(tribe, root, shared):
    return [check_clause_1(tribe, root, shared),
            check_clause_2(tribe, root, shared),
            check_clause_3(tribe, root),
            check_clause_4(tribe, root),
            check_clause_5(tribe, root),
            check_clause_6(tribe, root, shared),
            check_clause_7(tribe, root, shared)]


def verdict_of(results, strict):
    """member / intention / not a tribe. An untested clause is not a failure and not a pass."""
    bad = [r for r in results if r.status == FAIL]
    if strict:
        bad += [r for r in results if r.status == UNVERIFIED]
    if bad:
        return "not yet a tribe", [r.clause for r in bad]
    return "member", []


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def render(judgements, strict):
    lines = []
    header = "%-10s" % "tribe" + "".join("%-13s" % ("%d %s" % (c, CLAUSES[c].split(",")[0][:9]))
                                         for c in sorted(CLAUSES))
    lines.append(header)
    lines.append("-" * len(header))
    worst = 0
    for tribe, results in judgements:
        name = _value(tribe.get("name")) or "?"
        row = "%-10s" % name[:10] + "".join("%-13s" % r.status for r in results)
        lines.append(row)
        verdict, failing = verdict_of(results, strict)
        if failing:
            worst = 1
        lines.append("           -> %s%s" % (verdict, (" (failing: %s)" % ", ".join(map(str, failing))) if failing else ""))
        for r in results:
            if r.status in (FAIL, UNVERIFIED, UNTESTED):
                lines.append("              %d. %-10s %s" % (r.clause, r.status, r.detail))
    lines.append("")
    lines.append("PASS = checked here and it holds. UNVERIFIED = declared, and this checkout cannot "
                 "reach the evidence. UNTESTED = checked, and nobody has exercised the clause.")
    lines.append("Not seen by this script: whether a key works, whether a mailbox answers, whether a "
                 "state file was updated, whether a commit's author line is truthful.")
    return "\n".join(lines), worst


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    tribes = data.get("tribes")
    if not isinstance(tribes, list) or not tribes:
        raise ValueError("declaration file has no `tribes` list")
    for t in tribes:
        if not isinstance(t, dict) or not _value(t.get("name")):
            raise ValueError("every tribe needs a name")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description="Apply the AI Nation admission rule to declared tribes.")
    ap.add_argument("--file", default=None, help="declaration file (default: the symposium's own)")
    ap.add_argument("--root", default=None, help="checkout to check against (default: this script's repo)")
    ap.add_argument("--strict", action="store_true", help="UNVERIFIED counts as a failure")
    ap.add_argument("--today", default=None, help="YYYY-MM-DD for the dormancy window (default: today)")
    ap.add_argument("--max-quiet-days", type=int, default=14,
                    help="how long a silence may run before it has to be recorded (default 14)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    root = args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = args.file or os.path.join(root, "governance", "tribes", "symposium.json")
    try:
        data = load(path)
    except FileNotFoundError:
        sys.stderr.write("tribe_admission_check: no declaration file at %s\n" % path)
        return 2
    except (ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write("tribe_admission_check: %s: %s\n" % (path, exc))
        return 2

    def _dups(field):
        seen, dups = {}, set()
        for t in data["tribes"]:
            key = _value(t.get(field))
            if not key:
                continue
            key = str(key).strip().lower()
            if key in seen:
                dups.add(key)
            seen[key] = True
        return dups

    shared = {"dup_credentials": _dups("credential"), "dup_addresses": _dups("address"),
              "departures": 0,
              "today": args.today or date.today().isoformat(),
              "max_quiet_days": args.max_quiet_days}
    judgements = [(_value(t.get("name")), t, judge(t, root, shared)) for t in data["tribes"]]

    if args.json:
        payload = {"file": os.path.relpath(path, root) if path.startswith(root) else path,
                   "strict": args.strict,
                   "departures_recorded": shared["departures"],
                   "tribes": []}
        for name, _t, results in judgements:
            verdict, failing = verdict_of(results, args.strict)
            payload["tribes"].append({
                "name": name, "verdict": verdict, "failing": failing,
                "clauses": [{"clause": r.clause, "status": r.status, "detail": r.detail} for r in results]})
        print(json.dumps(payload, indent=2))
        return 0 if all(v == "member" for _n, _t, r in judgements for v, _f in [verdict_of(r, args.strict)]) else 1

    text, worst = render([(t, r) for _n, t, r in judgements], args.strict)
    print(text)
    print("\n%s — %d tribe(s) declared, %d departure(s) recorded in the file."
          % (os.path.relpath(path, root) if path.startswith(root) else path,
             len(judgements), shared["departures"]))
    return worst


if __name__ == "__main__":
    sys.exit(main())
