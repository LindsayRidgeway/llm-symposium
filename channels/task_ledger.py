#!/usr/bin/env python3
# Owner: Desi
"""Identity for commons task-ledger entries — so the ledger stops filing itself twice.

Why this exists (2026-09-25). `file_tasks` in the Telegram bot appends a line to
`channels/tasks.md` on *every* turn whose reply carries a `TASK:` marker, and it never asks
whether that line is already there. Measured on the live file: one request (Telegram image
intake) was filed **nine times**, another four times. The human's own words for the cost: he
"reports the same work over and over, so I believe it never did get done." A ledger that grows
copies of itself is a ledger a wake misreads — a wake that sees nine open copies of one request
cannot tell whether it is nine tasks or one.

The bot's copy of the fix cannot be tested from here and cannot be landed from here, so this is
the canonical half: the *identity* rule for a ledger entry, as pure stdlib code, with the tests
that pin it. `scripts/dedupe_tasks.py` is the CLI over it, and the bot's whole fix is a filter:

    from channels.task_ledger import new_items
    items = new_items(items, open(path, encoding="utf-8").read().splitlines())

What "the same item" means — and what it deliberately does not:

  * the **checkbox and the markdown are not identity** — `- [x] **Desi:** fix X` and
    `- [ ] Desi: fix X` are one item; emphasis is noise and is thrown away;
  * the **provenance trailer is not identity** — `— *(filed from Telegram)*` and
    `*Done 2026-09-17 (Gemini)*` are stamped by the tool or by a later editor, and a refiling
    differs from its original in exactly that stamp;
  * the **body is** identity, compared as a token set. Two normal forms are the same item when
    they are equal, share >= 90% of their words (Jaccard), or when the shorter one's words are
    *wholly contained* in the longer one (a refiling that lost its detail) and it carries at
    least `MIN_CONTAINMENT_TOKENS` distinct words;
  * **a merge never makes work look done.** A merged entry is checked only if *every* copy was
    checked. Over-merging is therefore safe in the direction that matters: at worst an entry
    that is already finished stays open and visible, never the reverse. The longer body always
    survives, so no statement of the task is lost either.

Anything less than "same item" is *reported, never merged*: two entries can read alike and be
two real tasks, and a similarity number is not entitled to decide that.
"""
from __future__ import annotations

import re
from pathlib import Path

LEDGER_REL = "channels/tasks.md"

# An entry, as file_tasks writes it: "- [ ] <body>" or "- [x] <body>".
ITEM_RE = re.compile(r"^(?P<indent>\s*)[-*]\s+\[(?P<box>[ xX])\]\s+(?P<body>.*)$")

# Provenance stamps: written by the tool or a later editor, never by the item's author.
_PROV_RE = re.compile(r"\*+\s*\((?:filed|reported|raised|sent)\s+from[^)]*\)\s*\*+", re.I)
_DONE_SPAN_RE = re.compile(
    r"\*+\s*(?:done|fixed|delivered|landed|closed|merged)\b[^*]*\*+", re.I)
_EMPHASIS_RE = re.compile(r"[*_`~]+")
_URL_RE = re.compile(r"https?://\S+")
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")

# Scores in [NEAR_DUPLICATE, 1.0] are auto-mergeable; [NEAR_MISS_FLOOR, NEAR_DUPLICATE) is for a
# reader's judgement and is never applied.
NEAR_DUPLICATE = 0.90
NEAR_MISS_FLOOR = 0.60

# A wholly-contained body must carry at least this many distinct words before containment
# counts as identity; below it, "one photo" and "send photo" would start collapsing together.
MIN_CONTAINMENT_TOKENS = 6


def is_item(line: str) -> bool:
    """True if the line is a checklist entry."""
    return bool(ITEM_RE.match(line or ""))


def item_body(line: str) -> str | None:
    """The entry's text without its checkbox, or None if the line is not an entry."""
    m = ITEM_RE.match(line or "")
    return m.group("body").strip() if m else None


def is_checked(line: str) -> bool:
    """True if the entry is ticked done."""
    m = ITEM_RE.match(line or "")
    return bool(m and m.group("box").lower() == "x")


def normalize(text: str) -> str:
    """Identity form of an entry: no provenance stamp, no markdown, lowercase, words only.

    Deliberately keeps numbers and every content word — two entries that differ only in a
    quantity ("2.5 g" vs "5 g") are different entries, and a dedupe that merged them would
    delete a correction.
    """
    t = text or ""
    t = _PROV_RE.sub(" ", t)
    t = _DONE_SPAN_RE.sub(" ", t)
    t = _URL_RE.sub(" ", t)
    t = _EMPHASIS_RE.sub(" ", t)      # drop the markers, keep the words they wrapped
    t = t.lower()
    t = _NON_WORD_RE.sub(" ", t)
    return " ".join(t.split())


def tokens(text: str) -> set[str]:
    """The identity word set of a body."""
    return set(normalize(text).split())


def similarity(a: str, b: str) -> float:
    """Token-set Jaccard similarity in [0, 1]; 1.0 when the identity forms are equal."""
    na, nb = normalize(a), normalize(b)
    if na == nb:
        return 1.0
    ta, tb = set(na.split()), set(nb.split())
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    return inter / len(ta | tb) if inter else 0.0


def containment(a: str, b: str) -> float:
    """Fraction of the shorter identity form's words that the longer one also carries."""
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def same_item(a: str, b: str, threshold: float = NEAR_DUPLICATE) -> bool:
    """True when two bodies are the same ledger entry.

    Equal normal forms, or a high enough Jaccard, or one body wholly contained in the other
    (a refiling that dropped detail) provided the contained body is substantial enough to be
    identifiable at all.
    """
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if similarity(a, b) >= threshold:
        return True
    ta, tb = set(na.split()), set(nb.split())
    if min(len(ta), len(tb)) >= MIN_CONTAINMENT_TOKENS and containment(a, b) >= threshold:
        return True
    return False


def is_duplicate(candidate: str, existing: list[str],
                 threshold: float = NEAR_DUPLICATE) -> bool:
    """True if `candidate` is already carried by any line in `existing`.

    Passing the whole file is correct: only checklist lines are compared.
    """
    for line in existing or []:
        body = item_body(line)
        if body is not None and same_item(candidate, body, threshold):
            return True
    return False


def new_items(candidates: list[str], existing: list[str],
              threshold: float = NEAR_DUPLICATE) -> list[str]:
    """Filter `candidates` down to those the ledger does not already carry.

    This is the function `file_tasks` should call before it inserts anything. Order-preserving
    and self-deduplicating: two identical candidates in one batch yield one.
    """
    kept: list[str] = []
    seen = list(existing or [])
    for cand in candidates or []:
        text = (cand or "").strip()
        if not text or is_duplicate(text, seen, threshold):
            continue
        kept.append(text)
        seen.append("- [ ] " + text)
    return kept


def duplicate_pairs(lines: list[str], threshold: float = NEAR_DUPLICATE,
                    floor: float = NEAR_MISS_FLOOR) -> list[dict]:
    """Scored entry pairs worth looking at, in file order.

    Each row: {"i","j","score","containment","same"} with i < j line indices. `same` marks the
    pairs that are the same item (`dedupe_lines` collapses exactly those); the rest are shown
    for a reader's judgement.
    """
    entries = [(i, item_body(ln)) for i, ln in enumerate(lines or [])]
    entries = [(i, b) for i, b in entries if b]
    out = []
    for x in range(len(entries)):
        i, bi = entries[x]
        for y in range(x + 1, len(entries)):
            j, bj = entries[y]
            same = same_item(bi, bj, threshold)
            score = similarity(bi, bj)
            ov = containment(bi, bj)
            if same or score >= floor:
                out.append({"i": i, "j": j, "score": round(score, 3),
                            "containment": round(ov, 3), "same": same,
                            "kept": bi, "dup": bj})
    return out


def dedupe_lines(lines: list[str], threshold: float = NEAR_DUPLICATE
                 ) -> tuple[list[str], list[dict]]:
    """Collapse entries that are the same item, keeping the longer text and the first place.

    Conservative on purpose:
      * the **longer body** survives, so no statement of the task is lost;
      * the checkbox is the **AND** of the copies — done only if every copy was done — so a
        merge can never make unfinished work look finished ("a merge never makes work done");
      * non-entry and blank lines are untouched, and running it twice changes nothing.
    Returns (new_lines, merged_rows).
    """
    lines = list(lines or [])
    pairs = [p for p in duplicate_pairs(lines, threshold=threshold, floor=1.1) if p["same"]]
    drop: dict[int, int] = {}          # dropped index -> surviving index
    body_of: dict[int, str] = {}
    checked_of: dict[int, bool] = {}
    for p in pairs:
        si = drop.get(p["i"], p["i"])
        sj = drop.get(p["j"], p["j"])
        if si == sj:
            continue
        bi = body_of.get(si) or item_body(lines[si]) or ""
        bj = body_of.get(sj) or item_body(lines[sj]) or ""
        survivor, loser, body = (si, sj, bi) if len(bi) >= len(bj) else (sj, si, bj)
        checked = checked_of.get(si, is_checked(lines[si])) and \
            checked_of.get(sj, is_checked(lines[sj]))
        m = ITEM_RE.match(lines[survivor])
        indent = m.group("indent") if m else ""
        lines[survivor] = f"{indent}- [{'x' if checked else ' '}] {body}"
        body_of[survivor], checked_of[survivor] = body, checked
        drop[loser] = survivor
        drop.pop(survivor, None)
        for k, v in list(drop.items()):      # re-point anything that pointed at the loser
            if v == loser:
                drop[k] = survivor

    merged = [{"kept_line": v + 1, "dup_line": k + 1,
               "score": round(similarity(item_body(lines[v]) or "",
                                         item_body(lines[k]) or ""), 3)}
              for k, v in drop.items()]
    out = [ln for idx, ln in enumerate(lines) if idx not in drop]
    return out, sorted(merged, key=lambda r: r["kept_line"])


def check_file(path: str | Path, threshold: float = NEAR_DUPLICATE,
               floor: float = NEAR_MISS_FLOOR) -> dict:
    """Read a ledger and report repeated entries without changing it."""
    p = Path(path)
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return {"path": str(p), "error": f"{type(e).__name__}: {e}", "same": [], "near": [],
                "items": 0, "lines": 0}
    same, near = [], []
    for row in duplicate_pairs(lines, threshold=threshold, floor=floor):
        out = {"kept_line": row["i"] + 1, "dup_line": row["j"] + 1, "score": row["score"],
               "containment": row["containment"],
               "kept": row["kept"][:120], "dup": row["dup"][:120]}
        (same if row["same"] else near).append(out)
    return {"path": str(p), "items": sum(1 for ln in lines if is_item(ln)),
            "lines": len(lines), "same": same, "near": near}


def apply_file(path: str | Path, threshold: float = NEAR_DUPLICATE) -> int:
    """Collapse same-item duplicates in the file in place. Returns the number merged.

    Reported-but-not-merged near misses are never applied — see `dedupe_lines`.
    """
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()
    out, merged = dedupe_lines(lines, threshold=threshold)
    if not merged:
        return 0
    text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    p.write_text(re.sub(r"\n{3,}", "\n\n", text), encoding="utf-8")
    return len(merged)
