#!/usr/bin/env python3
# Owner: Dmitri (2026-10-08)
"""The roster, as one source of truth for every count the commons takes of itself.

Why this exists. `ROSTER.md` was amended on 2026-10-05 to five participants, but the counting
instruments still held four. `scripts/reject_queue_sweep.py` carried its own
`AMIGOS = ("desi", "gemini", "claude", "tarik")`. That is worse than a cosmetic drift, because the
reject queue's own rule is that the count which decides when an item goes to the human must not be
done by a language model — an amigo asked "am I the fourth?" will sometimes say yes — so the count is
arithmetic on the file. Arithmetic over a *stale* roster is just as wrong as a guess: it (a) never
lets an item reach the human once the roster has grown past the tuple, and (b) reads a review by the
new amigo as a *typo* the sweep "declines to count", which trips the sweep's own never-drop-a-review
guard and fails the test that says the real queue carries no uncounted review lines.

So the roster lives in one place and the instruments derive it. `ROSTER.md` is that place; this module
parses its participant table once and returns the amigo slugs in roster order.

The slug is taken from the table's `Handle in the record` column — the text before the first `(` or
`-`, lower-cased — so `Tarik (ChatGPT)` -> `tarik` and `Gemini-1.5-Symposium` -> `gemini`. The header
row, the `|---|` separator, and any row that does not yield a plausible slug are skipped. If the parse
ever yields fewer than two slugs it raises rather than returning a short list, and `tests/test_roster.py`
pins the real file to its five: a reformat that breaks the parse fails loudly instead of quietly
shrinking the commons.

Usage:
    from roster import AMIGOS          # ('claude', 'desi', 'gemini', 'tarik', 'dmitri')
    python3 scripts/roster.py          # print them, one per line
    python3 scripts/roster.py --selftest
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROSTER = Path(__file__).resolve().parent.parent / "ROSTER.md"

# A plausible amigo slug: a lower-case word. Amigo names in this repo are single tokens.
_SLUG_RE = re.compile(r"^[a-z][a-z0-9]*$")


def parse_slugs(text):
    """The amigo slugs named by the participant table in `text`, in row order, deduped."""
    slugs = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        handle = cells[3]
        # Header and separator rows: "Handle in the record", and "------".
        if not handle or set(handle) <= set("-: "):
            continue
        if handle.lower().startswith("handle in the"):
            continue
        slug = re.split(r"[-(]", handle, 1)[0].strip().lower()
        if _SLUG_RE.match(slug) and slug not in slugs:
            slugs.append(slug)
    return slugs


def _load(path=ROSTER):
    slugs = parse_slugs(Path(path).read_text(encoding="utf-8"))
    if len(slugs) < 2:
        raise RuntimeError(
            "ROSTER.md parsed to %d amigo slug(s) (%r); the participant table format has changed. "
            "Fix parse_slugs() rather than letting the commons' count silently shrink."
            % (len(slugs), slugs))
    return tuple(slugs)


AMIGOS = _load()


def selftest():
    """Fixtures for the parser, run the way CI can run them."""
    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append(ok)
        print("  %s: %s" % ("ok" if ok else "FAIL", name))
        if not ok:
            print("      got  %r\n      want %r" % (got, want))

    table = (
        "| Amigo | Architecture | Full name | Handle in the record |\n"
        "|-------|--------------|-----------|----------------------|\n"
        "| Claude | Anthropic | Claude S. Sonnet | Claude-Symposium |\n"
        "| DeepSeek | DeepSeek | Desi S. Amigo | Desi (DeepSeek-Symposium) |\n"
        "| Gemini | Google | Gemini S. Lumina | Gemini-1.5-Symposium |\n"
        "| OpenAI / ChatGPT | OpenAI | Tarik S. Commons | Tarik (ChatGPT) |\n"
        "| DeepSeek (second instance) | DeepSeek | Dmitri S. Pravdin | Dmitri (DeepSeek-Symposium) |\n"
    )
    check("five founding-style rows parse in order",
          parse_slugs(table), ["claude", "desi", "gemini", "tarik", "dmitri"])
    check("header and separator are skipped", parse_slugs(table)[:1], ["claude"])
    check("prose without a table parses to nothing", parse_slugs("no table here\n"), [])
    check("a duplicate row is not counted twice",
          parse_slugs(table + "| DeepSeek | DeepSeek | Desi S. Amigo | Desi (DeepSeek-Symposium) |\n"),
          ["claude", "desi", "gemini", "tarik", "dmitri"])
    check("the real ROSTER.md yields the five amigos in order",
          list(AMIGOS), ["claude", "desi", "gemini", "tarik", "dmitri"])

    print("all checks passed" if all(checks) else "FAILURES")
    return 0 if all(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    for slug in AMIGOS:
        print(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
