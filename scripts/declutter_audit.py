#!/usr/bin/env python3
"""declutter_audit.py — find obsolete, redundant, and conflicting artifacts in the commons.

Raised by the human, 2026-09-17: "*I am convinced that you are retaining a certain
number of artifacts, or items within artifacts, that are either obsolete, redundant,
or in conflict with others.*" He proposed a single-thread declutter project comparing
every artifact to every other, looping forever like painting the Golden Gate bridge.

This script is the cheap half of that, and it runs for free. It does not compare
every pair of everything (1094 tracked files is ~600k pairs, and almost every pair is
legitimately different — comparing them tells you nothing and costs tokens to find
that out). It looks instead for the small number of specific pathologies that
actually produce clutter:

  1. EXACT      — byte-identical files (same sha256). Provably redundant. AUTO-fixable.
  2. NEAR       — documents sharing >=NEAR_THRESHOLD of their 6-grams. Candidates only:
                  two files can share most of their words and both be worth keeping.
  3. ORPHAN     — a tracked file that no other tracked file refers to. Candidates only:
                  some things are entry points and are *supposed* to be unreferenced.
  4. DANGLING   — a markdown link to a relative path that does not exist. Provably
                  broken. AUTO-fixable (the link or the target is wrong; a human or a
                  second architecture decides which).
  5. DRIFT      — a file that declares itself GENERATED whose generator re-run produces
                  different bytes. Provably out of date.

WHAT THIS SCRIPT MUST NOT FLAG. It was written wrong twice before it was written
right, and both mistakes are instructive — an earlier draft of this same detector
proposed deleting channels/agenda.md (the generated agenda index, which is *made of*
agenda/*.md and is therefore 100% "duplicate" by construction) and runs/<date> (the
laptop/cloud double-run marker files, referenced only as a shell variable and so
"unreferenced" by construction). Both are load-bearing. A declutterer ignorant of
intent proposes deleting the structure. Hence the tables below, and hence the rule:

    A machine may de-duplicate what is byte-identical. Everything else is a proposal.
    Declutter, like review, cannot be self-approved: the fix for a finding of class
    NEAR/ORPHAN/or CONFLICT goes to an architecture that did not raise it.

scripts/check-counterpoint.py is the standing proof of why: it is a second, independent
fugue checker, kept deliberately alongside check_music_rules.py, with the reason
written in its docstring ("getting the same answer from two independently-written
parsers"). A cleaner that deleted it on sight would have destroyed the evidence.

Usage:
    python3 scripts/declutter_audit.py                # write channels/declutter/<date>.md
    python3 scripts/declutter_audit.py --stdout       # print, write nothing
    python3 scripts/declutter_audit.py --quiet        # exit code only: 0 clean, 1 findings
                                                       # (nothing is ever auto-fixed here;
                                                       # --quiet is the only gating mode)

Budget note: this file is the free part. It costs no tokens. An agent fixes what it
finds, and that agent has a cap, because this job has no end and would otherwise
absorb whatever it is given.
"""

import argparse
import collections
import datetime as dt
import hashlib
import itertools
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "channels", "declutter")
NEAR_THRESHOLD = 0.80   # deliberately high: at 0.35 this script's first run reported
                        # 200 "duplicate" pairs, nearly all of them noise
MIN_WORDS = 400         # below this, short files collide by accident — at 120 the
                        # Gemini telegram replies all clustered as "duplicates" of each other
MAX_LIST = 25           # cap each section so the report stays readable

# ---------------------------------------------------------------------------
# INTENT. Files here are excluded from a detector because their apparent defect is
# the point of them. Every entry needs a reason, and a date, because an entry with
# no reason is itself clutter. Prune this table when an entry stops being true.
# ---------------------------------------------------------------------------
# Each entry names the detector classes it exempts and why. Scope matters: an intent
# declared for one class must not silently suppress another. This table was written
# globally first, with "docs/" meaning "served pages are reached by URL, not by
# relative link" — which is true, and which also exempted every JPEG under docs/ from
# the EXACT detector, hiding ~4 MB of genuinely duplicated gallery images. Same
# mistake as the false positives above, pointing the other way: intent applied
# without discipline hides as much as a detector that does not know intent at all.
INTENDED = {
    "docs/gallery/sumi-e/generate-tarik-interval.py": (("exact",),
        "2026-09-17 — tarik's generator, copied into the sumi-e pavilion so it is "
        "self-contained; the two copies are meant to be identical"),
    "works/queue": (("orphan",), "2026-09-17 — intake queue; empty is its resting state"),
    "actuator": (("orphan",), "2026-09-17 — patches are addressed by the actuator, never linked"),
    "tests": (("orphan",), "2026-09-17 — harnesses are invoked by hand and by CI, never cited"),
    "docs": (("orphan",), "2026-09-17 — served pages are reached by URL, not by relative link"),
    "news": (("orphan", "near"), "2026-09-17 — dated news items are terminal; nothing cites them forward"),
    "recipes": (("orphan",), "2026-09-17 — run by goose, by name, from outside the repo"),
    ".github/workflows/check-tarik-model.yml": (("orphan",),
        "2026-09-17 — workflow_dispatch only; a human runs it from the Actions tab, "
        "which no file in the repo can reference"),
}

# Path patterns whose referent is computed at runtime, so static reference-hunting
# will never see it.
DYNAMIC_PATTERNS = [
    (re.compile(r"^runs/\d{4}-\d{2}-\d{2}$"),
     "2026-09-17 — double-run marker, touched as runs/${TODAY}"),
    (re.compile(r"^\.gitkeep$"), "2026-09-17 — keeps an empty dir in git"),
]

TEXT_EXT = {".md", ".py", ".js", ".mjs", ".html", ".yml", ".yaml", ".json", ".txt",
            ".sh", ".css", ".toml", ".cfg", ".ini"}

# Dirs excluded from the *reference corpus* (what counts as referring to something).
# channels/declutter/ is here because a report that lists an orphan refers to it, and so
# would cure the orphan it reports. Observed 2026-09-17: one run wrote "0 orphans" and the
# very next run found ten again, because the first run's own output — which still held the
# previous list — had counted as the reference. An instrument that measures itself has to
# be excluded from its own sample.
CORPUS_SKIP = ("channels/declutter/", "docs/gallery/")


def tracked():
    out = subprocess.check_output(["git", "-C", REPO, "ls-files"]).decode()
    return [f for f in out.split("\n") if f]


def read(path):
    try:
        with open(os.path.join(REPO, path), "rb") as fh:
            return fh.read()
    except OSError:
        return b""


def is_intended(path, cls):
    """Is this path declared intentional *for this detector class*?"""
    for key, (classes, why) in INTENDED.items():
        if cls in classes and (path == key or path.startswith(key.rstrip("/") + "/")):
            return why
    for pat, why in DYNAMIC_PATTERNS:
        if pat.match(path):
            return why
    return None


def declares_generated(data):
    head = data[:1200].decode("utf8", "ignore")
    return ("GENERATED by" in head) or ("generated by scripts/" in head)


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return "%d %s" % (n, unit)
        n /= 1024.0
    return "%.1f GB" % n


# ---------------------------------------------------------------------------
# 1. EXACT
# ---------------------------------------------------------------------------
def find_exact(files, blobs):
    groups = collections.defaultdict(list)
    for f in files:
        b = blobs.get(f)
        if not b:                      # empty files are not informative
            continue
        groups[hashlib.sha256(b).hexdigest()].append(f)
    out = []
    for digest, members in groups.items():
        if len(members) < 2:
            continue
        members.sort()
        survivors = [m for m in members if not is_intended(m, "exact")]
        if len(survivors) < 2:
            continue
        out.append((os.path.getsize(os.path.join(REPO, members[0])), digest, members))
    out.sort(reverse=True)
    return out


# ---------------------------------------------------------------------------
# 2. NEAR
# ---------------------------------------------------------------------------
def shingles(path, data):
    text = data.decode("utf8", "ignore")
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    words = text.split()
    if len(words) < MIN_WORDS:
        return None
    grams = set()
    for i in range(len(words) - 5):
        grams.add(" ".join(words[i:i + 6]))
    return grams


def find_near(files, blobs):
    """Group near-identical documents into clusters.

    Reported as clusters, not pairs. The first version of this function reported
    pairs and listed the nine near-identical probe reports as 36 separate findings,
    which buries the one fact that matters (nine files, one content) under the
    arithmetic of the fact (9 choose 2).
    """
    grams, nwords, size = {}, {}, {}
    for f in files:
        if not f.endswith((".md", ".txt")):
            continue
        if is_intended(f, "near"):
            continue
        if f.startswith("channels/telegram/"):
            continue                    # chat logs: short, formulaic, terminal record
        data = blobs.get(f, b"")
        if not data or declares_generated(data):
            continue                    # a generated index is a duplicate by design
        s = shingles(f, data)
        if s:
            grams[f], nwords[f], size[f] = s, len(s), len(data)
    keys = sorted(grams)
    parent = {f: f for f in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in itertools.combinations(keys, 2):
        inter = len(grams[a] & grams[b])
        if not inter:
            continue
        if inter / min(nwords[a], nwords[b]) >= NEAR_THRESHOLD:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

    clusters = collections.defaultdict(list)
    for f in keys:
        clusters[find(f)].append(f)
    out = []
    for members in clusters.values():
        if len(members) < 2:
            continue
        members.sort()
        redundant = sum(size[m] for m in members[1:])
        newest = members[-1]
        out.append((len(members), redundant, newest, members))
    out.sort(key=lambda r: (-r[0], -r[1]))
    return out


# ---------------------------------------------------------------------------
# 3. ORPHAN
# ---------------------------------------------------------------------------
def find_orphans(files, blobs):
    """Tracked files that nothing refers to — restricted to files that *should* be cited.

    The first version of this returned 495 of 1094 files (45%), which is not a finding
    but a description: most of what the commons writes is a dated terminal record —
    inbound mail, sent mail, telegram logs, news items, run markers — that nothing
    cites forward and nothing should. Measuring that tells you nothing. So the search
    is restricted to files whose being unreferenced is *surprising*: code, workflows,
    agenda items, governance, tests, recipes, outreach, and served pages.
    """
    SCOPE = ("scripts/", ".github/", "agenda/", "governance/", "tests/", "recipes/",
             "outreach/", "to-do-lists/", "research/", "workarounds/", "experiments/",
             "probes/", "works/", "discussions/")
    SKIP_DIRS = ("docs/gallery/", "actuator/", "runs/", "news/", "insights/",
                 "channels/inbound/", "channels/sent/", "channels/telegram/",
                 "channels/outbox/", "channels/declutter/")
    candidates = []
    for f in files:
        if f.startswith(SKIP_DIRS):
            continue
        if f.startswith(SCOPE) or (f.count("/") == 0 and f.endswith(".md")):
            candidates.append(f)

    corpus = []
    for f in files:
        if f.startswith(CORPUS_SKIP):
            continue
        if os.path.splitext(f)[1] in TEXT_EXT and len(blobs.get(f, b"")) < 2_000_000:
            corpus.append((f, blobs[f].decode("utf8", "ignore")))

    out = []
    for f in candidates:
        if is_intended(f, "orphan"):
            continue
        base = os.path.basename(f)
        stem = os.path.splitext(base)[0]
        needles = {f, base}
        if len(stem) > 8:
            needles.add(stem)                      # "20-creating-motive"
        m = re.match(r"^(\d{2})-", base)
        if m:
            needles.add("item %s" % int(m.group(1)))
            needles.add(item_number_hit(m.group(1)))
        for other, text in corpus:
            if other == f:
                continue
            if any(n and n in text for n in needles):
                break
        else:
            out.append(f)
    return sorted(out)


def item_number_hit(num):
    return "/%s-" % num


# ---------------------------------------------------------------------------
# 6. PUBLIC — pages published but listed nowhere a person would look
# ---------------------------------------------------------------------------
SERVED_DIRS = ("docs/works/", "docs/papers/")
PUBLIC_INDEXES = ("README.md", "docs/index.html", "docs/works/index.html",
                  "docs/papers/index.html")
# A served page that is deliberately not advertised. Reason and date required; an
# exception without one is exactly the clutter this detector exists to find.
UNLISTED_OK = {
    "docs/works/index.html": "the works index itself",
    "docs/papers/index.html": "the papers index itself",
}


def find_public(files, blobs):
    """Published pages reachable from nothing a person would navigate.

    Added 2026-09-18, in answer to the human's question about the README's "Tools you can
    use right now": that table is the front door, and one published page was absent from
    every human-facing index in the repository — live at a public URL, linked only from
    sitemap.xml and atom.xml, which are indexes for crawlers. A machine index is not a door.

    Both directions, because a front door can err either way: a page that exists and is
    listed nowhere, and a front-door link pointing at a page that does not exist.
    """
    out = []
    indexes = {p: blobs.get(p, b"").decode("utf8", "ignore") for p in PUBLIC_INDEXES}
    combined = "\n".join(indexes.values())

    for f in files:
        if not f.startswith(SERVED_DIRS) or not f.endswith(".html"):
            continue
        if f in UNLISTED_OK or is_intended(f, "public"):
            continue
        if os.path.basename(f) not in combined:
            out.append(("unlisted", f, "linked from no human-facing index"))

    for src, text in indexes.items():
        for m in re.finditer(
                r"https://lindsayridgeway\.github\.io/llm-symposium/([^)\s\"]+)", text):
            if not os.path.exists(os.path.join(REPO, "docs", m.group(1))):
                out.append(("front door", src,
                            "links to docs/%s, which does not exist" % m.group(1)))
    return sorted(out)


# ---------------------------------------------------------------------------
# 4. DANGLING
# ---------------------------------------------------------------------------
LINK = re.compile(r"\]\(([^)\s#]+)")


def find_dangling(files, blobs):
    out = []
    for f in files:
        if not f.endswith(".md"):
            continue
        text = blobs.get(f, b"").decode("utf8", "ignore")
        for m in LINK.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(f), target))
            if not os.path.exists(os.path.join(REPO, resolved)):
                out.append((f, target))
    return out


# ---------------------------------------------------------------------------
# 5. DRIFT — declared-generated files whose generator disagrees with them
# ---------------------------------------------------------------------------
GENERATOR = re.compile(r"(?:GENERATED|generated) by (?:\.?/?)?(scripts/[\w.-]+\.py)")


def find_drift(files, blobs):
    """Files that declare themselves GENERATED, where re-running the generator disagrees.

    Two guards learned the hard way on 2026-09-17, both from the same first draft:

    * A generator is re-run in the tree, so this detector mutates as it measures. The
      original bytes are restored, and the test suite asserts the tree is unchanged.
    * It must never re-run *itself*. The report declares "GENERATED by
      scripts/declutter_audit.py", so the first version of this function found the
      report, ran the auditor from inside the auditor, which wrote the report, which
      the nested auditor then found — an unbounded process tree that had to be killed
      by hand. A detector that runs generators will eventually discover its own output.
    """
    out = []
    seen = set()
    me = os.path.basename(__file__)
    for f in files:
        data = blobs.get(f, b"")
        if not data or f.startswith("channels/declutter/"):
            continue
        m = GENERATOR.search(data[:1200].decode("utf8", "ignore"))
        if not m:
            continue
        gen = m.group(1)
        if os.path.basename(gen) == me:
            continue                                   # never re-run ourselves
        if (f, gen) in seen or not os.path.exists(os.path.join(REPO, gen)):
            continue
        seen.add((f, gen))
        try:
            path = os.path.join(REPO, f)
            old_bytes = open(path, "rb").read()
            subprocess.run([sys.executable, gen], cwd=REPO, timeout=120,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if open(path, "rb").read() != old_bytes:
                with open(path, "wb") as fh:           # put the tree back as found
                    fh.write(old_bytes)
                out.append((f, gen))
        except Exception as exc:                       # a generator that cannot run cleanly
            out.append((f, "%s  (generator failed: %s)" % (gen, type(exc).__name__)))
    return out


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    files = tracked()
    blobs = {f: read(f) for f in files}

    exact = find_exact(files, blobs)
    near = find_near(files, blobs)
    orphan = find_orphans(files, blobs)
    dangling = find_dangling(files, blobs)
    drift = find_drift(files, blobs)
    public = find_public(files, blobs)

    today = dt.date.today().isoformat()
    L = []
    L.append("<!-- GENERATED by scripts/declutter_audit.py — DO NOT EDIT THIS FILE. -->")
    L.append("")
    L.append("# Declutter audit — %s" % today)
    L.append("")
    L.append("Raised by the human 2026-09-17. %d tracked files examined. "
             "Mechanical findings only; this file does not decide anything."
             % len(files))
    L.append("")

    def section(title, rows, note):
        L.append("## %s — %d" % (title, len(rows)))
        L.append("")
        L.append(note)
        L.append("")
        for row in rows[:MAX_LIST]:
            L.append(row)
        if len(rows) > MAX_LIST:
            L.append("")
            L.append("*(%d more not shown)*" % (len(rows) - MAX_LIST))
        if not rows:
            L.append("*(none)*")
        L.append("")

    section(
        "EXACT — byte-identical files",
        ["- %s bytes, sha256 %s…  **AUTO**: delete all but one; pick the survivor by "
         "which path is cited elsewhere.\n  %s" % (size, digest[:12], "\n  ".join(m))
         for size, digest, m in exact],
        "Same content, two or more paths. Provably redundant. No judgment needed to "
        "know *that* they are identical; judgment is needed only for which one survives.")

    section(
        "NEAR — clusters of documents sharing ≥%d%% of their 6-grams" % int(NEAR_THRESHOLD * 100),
        ["- **%d files, %s of redundant bytes** — the newest is kept last; delete the "
         "rest only if the newest subsumes them:\n  %s"
         % (n, human(redundant), "\n  ".join(members))
         for n, redundant, newest, members in near],
        "Candidates. This is a reading list, not a deletion list. Two documents can "
        "share most of their sentences and both be worth keeping — one may be the "
        "record of why, the other the thing itself, and one may be a deliberately "
        "independent second implementation (see scripts/check-counterpoint.py). "
        "Resolution requires an architecture that did not write either.")

    section(
        "ORPHAN — tracked files nothing refers to",
        ["- %s" % f for f in orphan],
        "Candidates. Restricted to files whose being unreferenced is surprising. Most of "
        "the commons is dated terminal record — inbound mail, sent mail, news, run "
        "markers — and nothing cites it forward, correctly. An entry here is only "
        "clutter if it is also superseded and unread.")

    section(
        "DANGLING — links to paths that do not exist",
        ["- %s → `%s`" % (f, t) for f, t in dangling],
        "Provably broken. Either the link or the target moved. **AUTO**-fixable once a "
        "reader confirms which side is right.")

    section(
        "DRIFT — GENERATED files whose generator disagrees",
        ["- %s  (generator: %s)" % (f, g) for f, g in drift],
        "The file on disk is not what its generator produces. **AUTO**: re-run the "
        "generator. Never hand-merge a generated file.")

    section(
        "PUBLIC — published pages no human-facing index lists",
        ["- **%s**  %s — %s" % (kind, path, why) for kind, path, why in public],
        "The front door is README.md and the two works indexes. A page linked only from "
        "sitemap.xml or atom.xml is reachable by a crawler and by nobody else — a machine "
        "index is not a door. The reverse case is listed too: a front-door link pointing "
        "at a page that does not exist.")

    L.append("## What this audit cannot see")
    L.append("")
    L.append("Conflict of substance — two files that assert things which cannot both be "
             "true — is not detectable by string comparison, and it is the class the "
             "human actually named first. It needs a reader. The mechanical classes "
             "above are the ones that can be settled without one.")
    L.append("")
    L.append("Nothing in this report has been changed. A machine de-duplicates only what "
             "is byte-identical, and only under the rule above.")
    L.append("")
    L.append("*(%s — scripts/declutter_audit.py, owner: Desi)*" % today)
    report = "\n".join(L) + "\n"

    total = (len(exact) + len(near) + len(orphan) + len(dangling) + len(drift)
             + len(public))

    if args.stdout:
        print(report)
    elif not args.quiet:
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "%s.md" % today)
        with open(path, "w") as fh:
            fh.write(report)
        print("declutter audit: %d exact, %d near, %d orphan, %d dangling, %d drift, "
              "%d public → %s"
              % (len(exact), len(near), len(orphan), len(dangling), len(drift), len(public),
                 os.path.relpath(path, REPO)))

    if args.quiet:
        # --quiet is the only mode that is a gate: nonzero means "there is something
        # to resolve". The report modes always exit 0, so that wiring this into a
        # schedule can never turn a finding into a failed run.
        print("declutter audit: %d findings" % total)
        return 1 if total else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
