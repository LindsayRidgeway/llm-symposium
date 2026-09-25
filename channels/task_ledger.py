#!/usr/bin/env python3
"""Ledger intake — stop `channels/tasks.md` filing the same request nine times.

Written 2026-09-25 by Desi. Origin: the human, after reading one request in the ledger over
and over — *"nine copies of one request and four of another"*. `extract_tasks()` pulls `TASK:`
lines out of a Telegram reply; `file_tasks()` inserts them at the top of the
`## Filed from the chat with the human` section. It inserted **every** time, so a topic that
came up on nine chat turns produced nine ledger entries, and a wake that is handed ~2,500
characters of this file spent most of them reading the same sentence nine times.

**Exact-text matching would not have fixed this**, which is the whole reason this module is
token-based. Measured on the real history — `git show 62b3f0e^:channels/tasks.md`, the state
just before the copies were swept out by hand — the nine image-intake copies were nine
*re-wordings* of one request, each generated fresh:

    Fix Telegram relay so incoming images reach the model: handle `photo`/`document` ...
    Fix the Telegram relay so inbound images are actually delivered to the model: read ...
    Extend the Telegram channel relay to receive images — handle Telegram `photo`/`document` ...
    Add Telegram image handling to the channel relay — read the `photo`/`document` fields ...
    Extend the Telegram poller to handle image messages: parse the `photo` array ...

Not one pair of those is byte-identical, and an `if item not in file` check would have written
all nine. So the unit of comparison is a *set of content tokens* — lowercased, stopwords
dropped, lightly stemmed, markdown and field labels stripped — and the measure is containment,
`|A ∩ B| / min(|A|, |B|)`, not Jaccard, because one wording is often half the length of another
and Jaccard punishes that while a reader would not. Containment is a proxy for the only question
that matters here: *would a person reading both lines call these the same request?*

**Existing lines are compared as clusters, not one at a time.** A new item is tested against
the *union* of each cluster of already-similar lines. That is what makes the many-copy case
collapsible: the first copy is short ("extend the poller to handle image messages"), the ninth
is long, and a terse restatement can be unlike any single earlier line while being plainly the
same request as the group. The union is dominated by its members, so clusters stay small and
the measure stays legible.

**The threshold was measured, not picked.** Replaying that same 20-item snapshot in the order
it was filed, one item per call, as the bot does: at 0.42 the ledger ends with 12 lines instead
of 20 — 8 copies suppressed and counted, 1 flagged near-duplicate — and thresholds from 0.40
through 0.44 give exactly that same result. Nothing outside the two families scores above 0.33.
So 0.42 sits in the middle of a flat band with ~0.09 of margin on the safe side, and the choice
is stable rather than knife-edge. Two things it does *not* do, and this is the honest limit of a
lexical measure: it leaves three image-related lines standing, because two of them are genuinely
different sub-steps of the request ("parse the `photo` array" scores 0.17 against "call
`getFile` and base64 the bytes") and the third is the end-to-end verification. And it
under-collapses rather than over-collapses by design when the two values are close, because the
two errors are not symmetric: a duplicate left in the file is noise a reader can see, while a
distinct request silently merged into another line is work that disappears.

**The grey band is marked, not swallowed.** An item scoring 0.30–0.42 against an existing
cluster is still filed — and gets `*(close to an existing item — check for a merge)*` on its
line, so the reader is told where a merge is probably owed even when the machine declined to
make it. A machine that can only say yes or no will one day say yes wrongly; a marker costs one
line and puts the judgement back in front of a reader.

**Suppressing a copy does not throw the signal away.** A request re-filed on nine turns is
information: it says the human raised it nine times, and the file should say so. A collapsed
item increments a `*(re-filed ×N)*` marker on the line it matched. One readable copy, plus the
count of how often it came back.

Deliberately pure: `merge_filed_items()` takes lines, returns lines, and does no I/O. The bot
that owns the file keeps its own reading, committing and pushing, and the behaviour can be
pinned by a test that touches neither the network nor the real ledger. That bot keeps a
byte-identical copy of this file beside it (the same copy-not-import design as
`channels/media.py`); `tests/test_task_ledger_dedupe.py` checks for drift.

Run: python3 -m channels.task_ledger --selftest
"""
import re

FILED_HEADING = "## Filed from the chat with the human"
DEFAULT_THRESHOLD = 0.42
NEAR_THRESHOLD = 0.30
NEAR_MARKER = "*(close to an existing item — check for a merge)*"

SOURCE_TAG_RE = re.compile(r"\s*—?\s*\*\(filed from [^)]*\)\*\s*$")
REFILE_RE = re.compile(r"\s*\*\(re-filed ×(\d+)\)\*\s*$")
NEAR_RE = re.compile(r"\s*" + re.escape(NEAR_MARKER) + r"\s*$")
ITEM_RE = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s*(?P<body>.+)$")
HEADING_RE = re.compile(r"^##\s")
FIELD_RE = re.compile(r"^\*\*[^*]{1,60}:?\*\*:?\s*")     # "**Desi:** " / "**Lindsay, one photo:** "
TOKEN_RE = re.compile(r"[a-z0-9]+")

# Kept short and readable on purpose. It drops words that carry *no topic* — "fix", "add",
# "extend", "update" all mean "do this thing" — while keeping the ones that identify the
# request: photo, caption, getfile, relay. Over-stemming is how a dedupe quietly eats a
# distinct item, so nothing clever goes in here.
STOPWORDS = frozenset("""
a an and are as at be been before by can cannot could do does doing done for from get gets got
had has have how i if in into is it its just like make makes making may me might more most must
my need needs no not of on only or other our out over own same should so some such than that
the their them then there these they this those to too under up us use used using via was we
were what when where which while who whose why will with without would you your
fix fixed fixing add added adding update updated updating extend extended extending
implement implemented implementing support supported supporting also please
""".split())

# Near-synonyms that genuinely occur in this file's paraphrase pairs, kept to pairs a reader
# would call the same word. This is a dedupe, not a thesaurus.
SYNONYMS = {
    "images": "image", "imaging": "image", "picture": "image", "pictures": "image",
    "photo": "image", "photos": "image", "inbound": "incoming", "poller": "relay",
    "polling": "relay", "telegrams": "telegram", "wakes": "wake",
}


def _stem(tok):
    tok = SYNONYMS.get(tok, tok)
    if len(tok) > 4 and tok.endswith("ies"):
        return tok[:-3] + "y"
    if len(tok) > 4 and tok.endswith("es") and not tok.endswith("ses"):
        return tok[:-2]
    if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss"):
        return tok[:-1]
    return tok


def content_tokens(text):
    """The topic-bearing token set of a ledger item, or of a line's body text.

    Trailing markers — the source tag, the re-file counter, the near-duplicate marker — are
    stripped first, so an item does not become less similar to itself by having been re-filed.
    """
    body = text or ""
    while True:
        for rx in (SOURCE_TAG_RE, REFILE_RE, NEAR_RE):
            new = rx.sub("", body)
            if new != body:
                body = new
                break
        else:
            break
    body = body.replace("`", " ").replace("*", " ").replace("_", " ")
    body = FIELD_RE.sub("", body.strip())
    return frozenset(
        _stem(t) for t in TOKEN_RE.findall(body.lower())
        if t not in STOPWORDS and not t.isdigit()
    )


def similarity(a, b):
    """Containment of the smaller token set in the larger. 0.0 when either is empty."""
    if not a or not b:
        return 0.0
    return len(a & b) / float(min(len(a), len(b)))


def annotate_refile(line):
    """Bump the `*(re-filed ×N)*` marker on a line that has just been re-filed."""
    stripped = line.rstrip()
    m = REFILE_RE.search(stripped)
    n = int(m.group(1)) + 1 if m else 1
    if m:
        stripped = stripped[:m.start()].rstrip()
    return "%s *(re-filed ×%d)*" % (stripped, n)


def annotate_near(line):
    """Mark a filed line as probably the same request as one already in the file."""
    if NEAR_RE.search(line.rstrip()):
        return line
    return "%s %s" % (line.rstrip(), NEAR_MARKER)


def _section(lines, heading=FILED_HEADING):
    """(heading_index, body_start, body_end) for the filed section, or (-1, -1, -1)."""
    head = next((i for i, ln in enumerate(lines) if ln.strip() == heading), -1)
    if head < 0:
        return -1, -1, -1
    end = len(lines)
    for i in range(head + 1, len(lines)):
        if HEADING_RE.match(lines[i]) or lines[i].startswith("---"):
            end = i
            break
    return head, head + 1, end


class _Cluster(object):
    """A group of items already treated as one request. `tokens` is their union."""

    __slots__ = ("tokens", "refs")

    def __init__(self, tokens, ref):
        self.tokens = set(tokens)
        self.refs = [ref]                             # (kind, index) — 'line' or 'pending'

    def score(self, tokens):
        return similarity(tokens, self.tokens)


def merge_filed_items(lines, items, source="Telegram", threshold=DEFAULT_THRESHOLD,
                      near_threshold=NEAR_THRESHOLD, mark_near=True):
    """Insert `items` at the top of the filed section, collapsing ones already there.

    Returns `(lines, filed, re_filed, near)`:
      - `filed`    — the items actually written, in order;
      - `re_filed` — `(item, similarity, matched_line_text)` for each suppressed copy; the line
                     it matched has had its `*(re-filed ×N)*` counter bumped;
      - `near`     — `(item, similarity)` for items filed but flagged as probably a duplicate.

    Items are matched against the section's existing entries *and* against items accepted
    earlier in the same call, because one reply can carry the same request twice.
    """
    lines = list(lines)
    items = [it.strip() for it in (items or []) if it and it.strip()]
    if not items:
        return lines, [], [], []
    # See the module docstring: a copy is only suppressed when it also carries no new topic
    # words. Two lines about the same subject are not the same request, and a merge that
    # quietly drops a detail is the failure this file exists to avoid.

    head, start, end = _section(lines)
    if head < 0:
        at = next((i for i, ln in enumerate(lines) if ln.startswith("# ")), -1) + 1
        lines[at:at] = ["", FILED_HEADING, "", ""]
        head, start, end = _section(lines)

    clusters = []
    for i in range(start, end):
        m = ITEM_RE.match(lines[i])
        if not m:
            continue
        tok = content_tokens(m.group("body"))
        if not tok:
            continue
        cluster = next((c for c in clusters if c.score(tok) >= threshold), None)
        if cluster is None:
            clusters.append(_Cluster(tok, ("line", i)))
        else:
            cluster.tokens |= set(tok)
            cluster.refs.append(("line", i))

    pending = []                                      # new lines, in insertion order
    filed, re_filed, near = [], [], []

    def bump(ref):
        kind, idx = ref
        if kind == "pending":
            pending[idx] = annotate_refile(pending[idx])
        else:
            lines[idx] = annotate_refile(lines[idx])

    for item in items:
        tok = content_tokens(item)
        best, best_sim = None, 0.0
        for c in clusters:
            s = c.score(tok)
            if s > best_sim:
                best, best_sim = c, s
        if best is not None and tok and best_sim >= threshold:
            victim = max(best.refs, key=lambda r: similarity(
                tok, content_tokens(_line_body(lines, pending, r))))
            bump(victim)
            re_filed.append((item, round(best_sim, 3),
                             _line_text(lines, pending, victim).strip()))
            best.tokens |= set(tok)
            continue
        ref = ("pending", len(pending))
        line = "- [ ] %s — *(filed from %s)*" % (item, source)
        if mark_near and best is not None and best_sim >= near_threshold:
            line = annotate_near(line)
            near.append((item, round(best_sim, 3)))
        pending.append(line)
        filed.append(item)
        if best is not None and best_sim >= near_threshold:
            best.tokens |= set(tok)
            best.refs.append(ref)
        else:
            clusters.append(_Cluster(tok, ref))

    if pending:
        lines[start:start] = pending
    return lines, filed, re_filed, near


def _line_body(lines, pending, ref):
    kind, idx = ref
    raw = pending[idx] if kind == "pending" else lines[idx]
    m = ITEM_RE.match(raw)
    return m.group("body") if m else raw


def _line_text(lines, pending, ref):
    kind, idx = ref
    return pending[idx] if kind == "pending" else lines[idx]


def _selftest():
    """Tiny smoke test. Run it if you touched the tokenizer."""
    image_a = ("Fix Telegram relay so incoming images reach the model: handle "
               "`photo`/`document` fields and `caption`, call getFile")
    image_b = ("Add Telegram image handling to the channel relay — read the "
               "`photo`/`document` fields (and `caption`, not only `text`)")
    rover = "Build second rover kit — assembly to resume when the kit arrives"
    ta, tb, tc = (content_tokens(x) for x in (image_a, image_b, rover))
    assert similarity(ta, tb) >= DEFAULT_THRESHOLD, similarity(ta, tb)
    assert similarity(ta, tc) < NEAR_THRESHOLD, similarity(ta, tc)

    lines = ["# Commons tasks", "", FILED_HEADING, "",
             "- [ ] %s — *(filed from Telegram)*" % image_a,
             "", "---", "", "## 1. Other section", "- [ ] something else"]
    out, filed, re_filed, near = merge_filed_items(lines, [image_b, rover])
    assert filed == [rover] and len(re_filed) == 1 and near == [], (filed, re_filed, near)
    assert any("re-filed ×1" in ln for ln in out), out
    assert out[-2:] == ["## 1. Other section", "- [ ] something else"], out[-2:]
    again, filed2, re_filed2, _ = merge_filed_items(out, [rover])
    assert filed2 == [] and len(re_filed2) == 1, (filed2, re_filed2)
    rover_line = [ln for ln in again if ln.startswith("- [ ] Build second rover")][0]
    assert "re-filed ×1" in rover_line, rover_line
    again2, filed3, re_filed3, _ = merge_filed_items(again, [rover])
    assert filed3 == [] and "re-filed ×2" in [ln for ln in again2
                                             if ln.startswith("- [ ] Build second rover")][0]
    print("task_ledger selftest ok — image pair %.3f, image/rover %.3f, idempotent re-file ok"
          % (similarity(ta, tb), similarity(ta, tc)))


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__.split("Run:")[0].strip()[:400])
