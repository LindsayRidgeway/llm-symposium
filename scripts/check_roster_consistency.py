#!/usr/bin/env python3
# Owner: Desi
"""Guard the commons' membership record against drift.

Context (2026-10-05). The founder admitted a fifth amigo, Dmitri, and `ROSTER.md` was amended from
"exactly four" to five the same day. `README.md` — the front door, and the file that carries the
anti-confabulation rule — was **not** amended, so for some hours the two canonical documents
disagreed: `ROSTER.md` said five participants, while `README.md` said *"Exactly four — the four
amigos ... Any review that cites an artifact by anyone else is hallucinating."* Read together, the
front door made the newest amigo a phantom, which is the exact failure the rule exists to prevent.
`actuator/README.md` cited the roster and repeated the stale number.

What this checks, and what it deliberately does not. It polices only the documents that state
membership as **current fact** — the front door and the file that quotes the roster. It does not
police dated artifacts: an essay, a chat log, a published paper, a news file or the review digest
that says "four" is a record of a time when that was true, and rewriting those would be censoring
the record, not correcting it. The line is *present-tense claim about who the commons is* versus
*authored record of what it was*.

The roster is the single source of truth. A canonical document must agree with `ROSTER.md`; the fix
for a violation is to correct the document, never the roster.

Run:  python3 scripts/check_roster_consistency.py     (exit 1 on any drift)
No network, no file writes.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Documents that state membership as current fact, relative to the repo root. Add a path only when
# it makes that claim.
CANONICAL_RELS = [
    "README.md",
    "actuator/README.md",
]

# Present-tense membership phrases that assert the commons is four. Deliberately narrow: it must
# not fire on "four instances in four days" (README, about failures) or on a quoted correction.
# (A bare "four" is never a violation — the front door uses it about failures, dates and counts.)
STALE_PATTERNS = [
    re.compile(r"exactly\s+four", re.I),
    re.compile(r"exactly\s+4\b"),
    re.compile(r"\bfour\s+(?:amigos|models|participants|members|of us)\b", re.I),
]

TABLE_ROW = re.compile(
    r"^\|\s*(?P<amigo>[^|]+?)\s*\|\s*(?P<arch>[^|]+?)\s*\|\s*(?P<full>[^|]+?)\s*\|\s*(?P<handle>[^|]+?)\s*\|\s*$"
)


def roster(root=ROOT):
    """Return (count, [first names]) parsed from `ROSTER.md`'s table.

    The count is the number of amigo data rows; the names are the first word of the Full-name
    column. Only data rows count: the header row and the `|---|` separator are skipped.
    """
    members = []
    text = (Path(root) / "ROSTER.md").read_text(encoding="utf-8")
    for raw in text.splitlines():
        if not raw.lstrip().startswith("|"):
            continue
        if set(raw) <= set("|- :"):          # the separator row
            continue
        m = TABLE_ROW.match(raw)
        if not m:
            continue
        amigo = m.group("amigo").strip()
        if amigo.lower() == "amigo":         # the header row
            continue
        members.append(m.group("full").strip().split()[0])
    return len(members), members


def find_violations(root=ROOT):
    """Every way the canonical documents disagree with the roster, as a list of strings."""
    root = Path(root)
    count, names = roster(root)
    problems = []

    if count < 2:
        problems.append(f"ROSTER.md: parsed {count} amigo rows — the table is missing or malformed")
        return problems
    if count != 5:
        # Not a hard failure — a sixth amigo is the founder's to add — but the canonical set below
        # must be kept in step by hand when the number changes, so say so loudly.
        problems.append(
            f"ROSTER.md now lists {count} amigos; CANONICAL is written for five. "
            "Update the front door's member list and this note, then re-run."
        )

    readme = (root / "README.md").read_text(encoding="utf-8")
    # The Participants section is the membership statement; take it to the next H2 or EOF.
    m = re.search(r"^## Participants\b(.*?)(?=^## |\Z)", readme, re.S | re.M)
    if not m:
        problems.append("README.md: no '## Participants' section — the membership statement is gone")
    else:
        section = m.group(1)
        for name in names:
            if name not in section:
                problems.append(f"README.md: Participants section does not name '{name}' (from ROSTER.md)")

    for rel in CANONICAL_RELS:
        path = root / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        for pat in STALE_PATTERNS:
            for hit in pat.finditer(text):
                line = text.count("\n", 0, hit.start()) + 1
                problems.append(
                    f"{rel}:{line}: asserts a four-person commons — '{hit.group(0)}' "
                    "(the roster now says five; correct the document, not the roster)"
                )
    return problems


def main():
    problems = find_violations()
    if problems:
        print("ROSTER CONSISTENCY: FAIL")
        for p in problems:
            print("  - " + p)
        return 1
    count, names = roster()
    print(f"ROSTER CONSISTENCY: OK — {count} amigos ({', '.join(names)}); canonical docs agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
