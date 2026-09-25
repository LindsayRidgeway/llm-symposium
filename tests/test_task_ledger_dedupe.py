#!/usr/bin/env python3
"""Ledger intake dedupe — the test that would have caught nine copies of one request.

Written 2026-09-25 by Desi. Origin: the human, reading the commons ledger, found one request
filed nine times and another four times. `extract_tasks()` lifts `TASK:` lines out of a Telegram
reply and `file_tasks()` wrote every one of them into `channels/tasks.md` at the top of the
`## Filed from the chat with the human` section, on every turn the topic came up. The copies were
swept out by hand on 2026-09-25 (commit 62b3f0e); nothing stopped them returning, because nothing
tested the writer.

What it checks:
  1. The tokenizer — marker stripping, stopwords, stemming, the synonym map — on strings whose
     answers are obvious by eye.
  2. **The real corpus.** The 20 lines that were in that section just before the sweep, taken
     from `git show 62b3f0e^:channels/tasks.md` and replayed here in the order they were filed.
     This is the assertion that matters: the same request worded eleven different ways must not
     produce eleven lines, and eleven *unrelated* requests must not be merged into one.
  3. The threshold band: 0.40 and 0.44 must give the same result as the default 0.42, because a
     dedupe whose behaviour changes every time someone nudges the number is not a decision.
  4. False-merge guard: the two sub-steps that are genuinely different requests inside the same
     subject ("parse the `photo` array" vs "call `getFile` and base64 the bytes") must survive.
  5. Re-filing is counted, not swallowed — a request filed nine times is information.
  6. Section discipline: only the filed section is touched, and new lines go at the top of it.
  7. The copy of `task_ledger.py` beside the running bot is byte-identical to this one, because
     the design is copy-not-import. Reports SKIP where the bot directories are absent (a fork, CI),
     so the suite stays honest about what it verified.

Run: python3 tests/test_task_ledger_dedupe.py     (exit 0 pass, 1 fail)
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels.task_ledger import (                      # noqa: E402
    DEFAULT_THRESHOLD, NEAR_THRESHOLD, content_tokens, similarity, merge_filed_items,
    annotate_refile, FILED_HEADING,
)

FAILURES = []
CHECKS = [0]
SKIPS = []


def check(label, ok, detail=""):
    CHECKS[0] += 1
    if not ok:
        FAILURES.append("%s%s" % (label, (": " + str(detail)) if detail else ""))
        print("  FAIL %s%s" % (label, (": " + str(detail)) if detail else ""))
    else:
        print("  ok   %s" % label)


def section(name):
    print("\n%s\n%s" % (name, "-" * len(name)))


PREAMBLE = ["# Commons tasks", "", FILED_HEADING, "", "---", "", "## 1. Some other section",
            "- [ ] an item that is not in the filed section"]

# --- the real corpus ---------------------------------------------------------------------
# From `git show 62b3f0e^:channels/tasks.md`, the filed section as it stood just before the
# duplicates were swept out by hand. Newest first, which is the order the writer produced;
# `REPLAY` reverses it into the order they were filed. Truncation: none — these are the whole
# lines, which is why this list is long.
CORPUS = []
CORPUS = [
    'Fix Telegram relay so incoming images reach the model: handle `photo`/`document` fields and `caption` (not just `message.text`), call `getFile`, download the bytes, and pass them as image input rather than string. — *(filed from Telegram)*',
    "Close the work-loss gap: items agreed in Telegram land in `channels/tasks.md` but neither `tasks.md` nor `risks.md` is an input to a wake. Route Telegram-filed work onto `to-do-lists/desi.md` (or add `tasks.md` to the wake's inputs) so filed work actually reaches a wake. — *(filed from Telegram)*",
    'Fix the Telegram relay so inbound images are actually delivered to the model: read `photo`/`document` (not just `text`), call `getFile`, download the bytes, and pass them as image input rather than a string. Also capture `caption`. Verify with a real photo sent from Telegram. — *(filed from Telegram)*',
    'Close the plumbing gap where work agreed in Telegram never reaches a wake — `channels/tasks.md` is not an input to a wake, and nothing currently promotes its lines onto `to-do-lists/desi.md`. Either add tasks.md to the wake\'s inputs or add an automatic promotion step, then document it so "nothing needed from you" can\'t be said falsely again. — *(filed from Telegram)*',
    'Extend the Telegram channel relay to receive images — handle Telegram `photo`/`document` fields and `caption` (not just `text`), call `getFile` and download the bytes, then pass the image to the model as an image input. Owner: Desi. — *(filed from Telegram)*',
    'Wire `channels/tasks.md` into `to-do-lists/desi.md` so a filed task reaches a wake without a human hand-carrying it. Owner — *(filed from Telegram)*',
    'Add Telegram image handling to the channel relay — read the `photo`/`document` fields (and `caption`, not only `text`) instead of dropping image messages; call `getFile`, download the bytes, and pass them to the model as an image input rather than a string. — *(filed from Telegram)*',
    'Copy the open items from channels/tasks.md onto to-do-lists/desi.md each cycle, so ledger work actually reaches a wake — currently the ledger is not one of the three things a wake reads. — *(filed from Telegram)*',
    'Extend the Telegram poller to handle image messages: parse the `photo` array (take the largest size variant) and `document` entries with image mime types, and read `caption` when `text` is absent — it currently reads only `message.text`, so pictures arrive as empty strings and are dropped silently. — *(filed from Telegram)*',
    "For any image-bearing update, call Telegram's `getFile` to obtain a file path, download the bytes over HTTPS, base64-encode them, and pass the result as an image content block to a vision-capable model instead of a text string. — *(filed from Telegram)*",
    'Verify end-to-end — send a photo from Telegram and confirm the reply describes the actual image content, — *(filed from Telegram)*',
    "When the replacement rover kit arrives (~early next week), install the new Pi card and verify the camera works end-to-end; determine whether last week's failure was the board's connector tab or the ribbon cable, and record which; then complete the second rover build for Gemini on the new hardware. — *(filed from Telegram)*",
    'Build second rover kit (identical to the first, ordered as a twin when the first was ordered) — assembly to resume when the kit arrives, paired with the new Pi card shipping for early next week. — *(filed from Telegram)*',
    '**Desi:** make the tick report name the file it touched ("proof in the report") — raised 2026-09-20, declared filed, never done; the human reads reports and not the repo, so a report that does not name a file is indistinguishable from a wake that did nothing — *(filed from Telegram)*',
    '**Desi:** file each inbound Telegram message verbatim BEFORE attempting a reply, so a failed answer cannot erase the question — raised 2026-09-15; the text[:100] truncation was fixed, the reply-first ordering was not — *(filed from Telegram)*',
    '**Desi:** fix the ORS calculator — it hardcodes 2 level teaspoons for any sugar amount between 1.5 and 3 tsp, so the 250 mL cup option prescribes a third too much sugar — diagnosed 2026-09-16, never fixed — *(filed from Telegram)*',
    "**Desi:** correct the ORS home-mix sodium figure in the same page (the table's ~50-60 mmol/L is generous; 2.6 g salt per litre is ~44) — diagnosed 2026-09-16, never fixed — *(filed from Telegram)*",
    '**Desi:** read the retained tick drafts (the bin of unpublished work) — promised 2026-09-15, "it\'s on my list", no reading reported since — *(filed from Telegram)*',
    '**Claude, Desi, Tarik:** the Literary Wing matrix (a poem, a story and a play from each amigo) — routed 2026-09-21 to to-do lists and active mission queue — *(filed from Telegram)*',
    '**Desi:** Generalize the agentic local_tick harness for Claude and Tarik (Idea #5 from chat with Lindsay, 2026-09-24) — adapt `local_tick.py` into `claude-bot` and `tarik-bot` with cost-weighted wake cadences (e.g. 12h or 24h) so they have agentic hands instead of single-pass runner scripts. — *(filed from Telegram)*',
]


# The two families the human named, by index into CORPUS (newest-first).
IMAGE = [0, 2, 4, 6, 9]
LEDGER = [1, 3, 5, 7]
DISTINCT = [8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
REPLAY = list(reversed(CORPUS))          # the order they were actually filed


def ledger_lines(lines):
    return [ln for ln in lines if ln.startswith("- [ ]")]


def replay(threshold, items=None):
    """Replay CORPUS in filing order, one item per call, as the bot does. -> (lines, stats)."""
    lines = list(PREAMBLE)
    filed = re_filed = near = 0
    for item in (items if items is not None else REPLAY):
        lines, f, r, n = merge_filed_items(lines, [item], threshold=threshold)
        filed += len(f)
        re_filed += len(r)
        near += len(n)
    return lines, {"filed": filed, "re_filed": re_filed, "near": near}


def section_1_tokenizer():
    section("1. the tokenizer")
    a = content_tokens("Fix Telegram relay so incoming images reach the model: handle "
                       "`photo`/`document` fields and `caption`, call getFile")
    b = content_tokens("Add Telegram image handling to the channel relay — read the "
                       "`photo`/`document` fields (and `caption`, not only `text`)")
    c = content_tokens("Build second rover kit — assembly to resume when the kit arrives")
    check("two wordings of one request overlap", similarity(a, b) >= DEFAULT_THRESHOLD,
          round(similarity(a, b), 3))
    check("an unrelated request does not", similarity(a, c) < NEAR_THRESHOLD,
          round(similarity(a, c), 3))
    check("stopwords carry no topic", "fix" not in a and "handle" not in a, sorted(a))
    check("synonyms fold", "image" in a and "photo" not in a, sorted(a))
    check("markers do not change an item's own tokens",
          content_tokens("- [ ] x — *(filed from Telegram)* *(re-filed ×3)*") ==
          content_tokens("- [ ] x"), sorted(content_tokens("x")))
    check("an empty item is not similar to anything", similarity(frozenset(), a) == 0.0)
    check("the counter bumps rather than repeating",
          annotate_refile("- [ ] x *(re-filed ×3)*").count("re-filed") == 1 and
          "×4" in annotate_refile("- [ ] x *(re-filed ×3)*"))


def section_2_corpus():
    section("2. the real corpus (20 items, the state before the hand sweep)")
    check("the fixture is the pre-sweep snapshot", len(CORPUS) == 20, len(CORPUS))
    lines, stats = replay(DEFAULT_THRESHOLD)
    body = ledger_lines(lines)
    check("20 asked-for items no longer become 20 lines", len(body) == 12, len(body))
    check("eight copies were suppressed, not written", stats["re_filed"] == 8, stats)
    check("the ledger family collapsed to one line", sum(
        1 for ln in body if "to-do-lists/desi.md" in ln) == 1, body)
    check("the image family collapsed to one line", sum(
        1 for ln in body if "getFile" in ln and "base64" in ln) == 1, body)
    check("nothing outside the two families was merged away", len(body) == 12)
    for i in DISTINCT:
        first = CORPUS[i][:38]
        check("kept: %s..." % first.replace("`", ""),
              any(first.split("—")[0].strip()[:30] in ln for ln in body))


def section_3_band():
    section("3. the threshold band (0.40 to 0.44 must agree)")
    base, bstats = replay(0.40)
    check("0.40 gives the same eight collapses", bstats["re_filed"] == 8, bstats)
    check("0.40 gives the same line count", len(ledger_lines(base)) == 12,
          len(ledger_lines(base)))
    top, tstats = replay(0.44)
    check("0.44 gives the same eight collapses", tstats["re_filed"] == 8, tstats)
    check("0.44 gives the same line count", len(ledger_lines(top)) == 12,
          len(ledger_lines(top)))
    check("cross-family overlap stays well under the threshold",
          max(similarity(content_tokens(CORPUS[i]), content_tokens(CORPUS[j]))
              for i in IMAGE for j in DISTINCT) < 0.34,
          round(max(similarity(content_tokens(CORPUS[i]), content_tokens(CORPUS[j]))
                    for i in IMAGE for j in DISTINCT), 3))


def section_4_substeps():
    section("4. false-merge guard — sub-steps of one request are not one request")
    parse_it = content_tokens(CORPUS[8])
    fetch_it = content_tokens(CORPUS[9])
    check("'parse the photo array' is not 'call getFile and base64 the bytes'",
          similarity(parse_it, fetch_it) < DEFAULT_THRESHOLD,
          round(similarity(parse_it, fetch_it), 3))
    _, stats = replay(DEFAULT_THRESHOLD, items=[CORPUS[10]])
    check("the end-to-end verification stays its own item", stats["re_filed"] == 0, stats)


def section_5_counting():
    section("5. re-filing is counted, not swallowed")
    lines = list(PREAMBLE)
    item = "Close the work-loss gap: items agreed in Telegram land in channels/tasks.md"
    for n in range(1, 10):
        lines, f, r, _ = merge_filed_items(lines, [item])
    body = ledger_lines(lines)
    check("nine filings of one request leave one line", len(body) == 1, body)
    check("the line says how often it came back", "re-filed ×8" in body[0], body[0])
    check("idempotent: a tenth filing changes no words but the counter",
          len(merge_filed_items(lines, [item])[1]) == 0)


def section_6_section_discipline():
    section("6. section discipline")
    lines, f, r, n = merge_filed_items(PREAMBLE, ["a brand new request about the rover"])
    body = ledger_lines(lines)
    check("the new line goes to the top of the filed section", body[0].startswith(
        "- [ ] a brand new request"), body)
    check("the item outside the filed section is untouched",
          lines[-1] == "- [ ] an item that is not in the filed section", lines[-1])
    check("the '---' fence is still after the filed items",
          lines.index("---") > lines.index(body[0]), lines)
    check("a heading-less file gains the section rather than failing",
          ledger_lines(merge_filed_items(["# Commons tasks"], ["x"])[0]) == ["- [ ] x"])


def section_7_copy():
    section("7. the bot's copy of task_ledger.py (skips where absent)")
    canonical = (REPO / "channels" / "task_ledger.py").read_bytes()
    bots = [Path.home() / "LLM" / b for b in
            ("desi-bot", "claude-bot", "gemini-bot", "tarik-bot")]
    seen = 0
    for bot in bots:
        copy = bot / "task_ledger.py"
        if not copy.exists():
            continue
        seen += 1
        check("%s/task_ledger.py is byte-identical to channels/task_ledger.py" % bot.name,
              copy.read_bytes() == canonical)
    if not seen:
        SKIPS.append("no bot directories on this machine — copy drift not checked")
        print("  SKIP no bot copy present (fork or CI): nothing to compare")


def main():
    for fn in (section_1_tokenizer, section_2_corpus, section_3_band, section_4_substeps,
               section_5_counting, section_6_section_discipline, section_7_copy):
        fn()
    print("\n%d checks, %d failed%s" % (CHECKS[0], len(FAILURES),
          (", %d skipped" % len(SKIPS)) if SKIPS else ""))
    for f in FAILURES:
        print("  - %s" % f)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
