#!/usr/bin/env python3
"""The reject-queue sweep must actually run, and it must count what the file says.

Written 2026-10-04 with `scripts/reject_queue_sweep.py`'s first test in `tests/`. Two defects
motivate it, and both are the kind the repository has already found elsewhere.

1. **Nothing ran it.** The sweep was the only instrument in `scripts/` with no test here and no
   line in `.github/workflows/test-and-report.yml`, so the `--selftest` it offers instead of a
   test was never executed on a landing. This repository has found that class of defect four
   times already: `.mjs` validators that were never executed (2026-09-30), `compile_agenda.py
   --check`, which nothing ran (2026-09-30), evidence-table pins named by an artefact but never
   run, and a pin named for a file that did not exist. A guard on the clock is not a guard.

2. **A silently dropped review is the failure that matters.** The sweep counts a `reviewed:` line
   only when it names one of the amigos, an ISO date and a parenthesised reason; everything
   else is skipped without a word. That is the right rule for a rubber stamp — "cannot" with no
   reason is not a verdict, and the queue must not treat it as one. It is the wrong behaviour for
   a typo: a review filed to `tarik` mis-spelled, or dated `2026-10-4`, disappears from the count,
   the item never matures, and the queue goes quiet — which is the single thing this queue exists
   to prevent. So the real file is asserted to contain **no** review line the sweep declines to
   count.

**Amended 2026-10-08 (Dmitri).** The sweep's `AMIGOS` tuple was four names, written before the
founder's amendment of 2026-10-05 admitted a fifth amigo. The effect was live, not cosmetic: a
review by the fifth amigo was reported as a stray/malformed line and left out of the count, and
`ready()` asked the human once four of us had looked — with the fifth never counted at all. The
roster is five (ROSTER.md); the sweep and its fixtures now say so, and this file pins both halves
of the fix: a fifth-amigo review counts, and four-of-five is not ready.

Offline. Reads the real `channels/reject-queue.md`; writes only to a temp copy.
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reject_queue_sweep as sweep  # noqa: E402

QUEUE = ROOT / "channels" / "reject-queue.md"
ISO_DAY = re.compile(r"^\d{4}-\d\d-\d\d$")


def unfenced(text):
    """The file's own lines, minus anything inside a fence (the format description lives there)."""
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return out


def declared_blocks(text):
    """What the file says is an item, derived here independently of the sweep's parser.

    A heading is an item only if a `- raised:` line follows it before the next heading — the
    file's own rule, and the one that stops its section headings counting as queue items.
    """
    lines = unfenced(text)
    heads = [i for i, ln in enumerate(lines) if sweep.HEAD_RE.match(ln)]
    blocks = []
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        body = lines[i + 1:end]
        if any(sweep.RAISED_RE.match(ln) for ln in body):
            blocks.append({"title": sweep.HEAD_RE.match(lines[i]).group("title"),
                           "body": body})
    return blocks


class SweepSelftest(unittest.TestCase):
    """The script's own fixtures, run the way CI will run them: as a subprocess."""

    def test_selftest_passes(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "reject_queue_sweep.py"),
                               "--selftest"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("all checks passed", proc.stdout)

    def test_check_mode_writes_nothing(self):
        before = QUEUE.read_bytes()
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "reject_queue_sweep.py"),
                               "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(QUEUE.read_bytes(), before, "--check must not touch the queue")


class RealQueueInvariants(unittest.TestCase):
    """What the real queue must satisfy for the sweep's arithmetic to mean anything."""

    @classmethod
    def setUpClass(cls):
        cls.text = QUEUE.read_text(encoding="utf-8")
        cls.lines = unfenced(cls.text)
        cls.blocks = declared_blocks(cls.text)
        cls.items = sweep.parse(cls.text)

    def test_the_file_has_items_at_all(self):
        self.assertTrue(self.blocks, "no queue item parses — the sweep is counting nothing")

    def test_parser_sees_exactly_the_declared_items(self):
        self.assertEqual([b["title"] for b in self.blocks], [i["title"] for i in self.items])

    def test_the_fenced_format_example_is_not_an_item(self):
        for title in (i["title"] for i in self.items):
            self.assertNotIn("<", title, "a placeholder heading was counted as a queue item")

    def test_every_item_says_who_raised_it_and_what_blocks_it(self):
        for b in self.blocks:
            raised = [ln for ln in b["body"] if sweep.RAISED_RE.match(ln)]
            self.assertEqual(len(raised), 1, "%s: expected one `- raised:` line" % b["title"])
            m = re.match(r"^-\s*raised:\s*(?P<day>\d{4}-\d\d-\d\d)\s+by\s+(?P<amigo>[A-Za-z]+)\s*$",
                         raised[0], re.I)
            self.assertIsNotNone(m, "%s: malformed `- raised:` line: %r" % (b["title"], raised[0]))
            self.assertTrue(ISO_DAY.match(m.group("day")), raised[0])
            self.assertIn(m.group("amigo").lower(), sweep.AMIGOS, raised[0])
            self.assertTrue(any(ln.lower().startswith("- blocked because:") and ln.split(":", 1)[1].strip()
                                for ln in b["body"]),
                            "%s: no `- blocked because:` reason" % b["title"])

    def test_no_review_line_is_silently_dropped(self):
        """The guard that matters: every `reviewed:` line in the file must be counted.

        A line that looks like a review and is not counted is worse than no line — it reads as a
        verdict in the file and is absent from the arithmetic. The queue file currently carries
        no shrugs; if one is ever wanted, it must not be written in the review format.
        """
        raw = [ln for ln in self.lines if re.match(r"^-\s*reviewed:", ln, re.I)]
        self.assertTrue(raw, "no review lines in the file — has the format changed?")
        # Every line that is written as a review must be one: a well-formed verdict by one of the
        # amigos. The sweep keeps only the latest per amigo per item (a re-review is a later
        # verdict), so the count it holds is the number of distinct (item, amigo) pairs, not the
        # line count.
        pairs = set()
        for b in self.blocks:
            for n, ln in enumerate(b["body"]):
                if not re.match(r"^-\s*reviewed:", ln, re.I):
                    continue
                m = sweep.REVIEW_RE.match(ln)
                self.assertIsNotNone(m, "unparsable review line: %r" % ln)
                self.assertIn(m.group("amigo").lower(), sweep.AMIGOS,
                              "review by someone who is not one of the amigos: %r" % ln)
                self.assertTrue(ISO_DAY.match(m.group("day")), ln)
                self.assertTrue(m.group("reason").strip(), ln)
                pairs.add((b["title"], m.group("amigo").lower()))
        counted = sum(len(i["reviews"]) for i in self.items)
        self.assertEqual(counted, len(pairs),
                         "the sweep holds %d verdicts; the file declares %d" % (counted, len(pairs)))
        self.assertEqual(sweep.stray_reviews(self.text), [],
                         "the sweep reports uncounted review lines in the real file")

    def test_a_wrapped_or_misspelled_verdict_is_reported(self):
        """The negative test for the guard: a verdict the count cannot see must not be silent."""
        wrapped = "- reviewed: tarik 2026-10-04 cannot (wrapped across two\n  lines, text continues)"
        bad_date = "- reviewed: tarik 2026-10-4 cannot (the date is not ISO)"
        stranger = "- reviewed: dawn 2026-10-04 cannot (not one of the amigos)"
        for text in (wrapped, bad_date, stranger):
            self.assertEqual(len(sweep.stray_reviews(text)), 1, "not reported: %r" % text)
        self.assertEqual(sweep.stray_reviews("- reviewed: tarik 2026-10-04 cannot (fine)"), [])
        # A review by any amigo on the roster — including the fifth — is not stray.
        for amigo in sweep.AMIGOS:
            self.assertEqual(sweep.stray_reviews(
                "- reviewed: %s 2026-10-08 cannot (looked, cannot)" % amigo), [],
                "review by %s is treated as a typo" % amigo)

    def test_nothing_is_asked_of_the_human_before_all_amigos_have_looked(self):
        for i in self.items:
            if i["requested"]:
                self.assertEqual(len(i["reviews"]), len(sweep.AMIGOS),
                                 "%s was asked before all the amigos had looked" % i["title"])

    def test_ready_means_every_amigos_verdict_and_no_request_yet(self):
        for i in sweep.ready(self.items):
            self.assertEqual(sorted(i["reviews"]), sorted(sweep.AMIGOS))
            self.assertIsNone(i["requested"])

    def test_four_of_five_is_not_ready_and_a_full_item_is_marked_once(self):
        """Round-trip through the real file's structure: a short count is not ready; a full one is,
        and stamping it stops a second sweep asking twice."""
        nearly = ("\n## Synthetic four-verdict item\n"
                  "- raised: 2026-10-04 by desi\n"
                  "- blocked because: a fixture with one amigo's verdict missing\n"
                  + "".join("- reviewed: %s 2026-10-04 cannot (fixture)\n" % a
                            for a in sweep.AMIGOS if a != "dmitri"))
        extra = ("\n## Synthetic full-verdict item\n"
                 "- raised: 2026-10-04 by desi\n"
                 "- blocked because: a temporary fixture, written only to a temp copy\n"
                 + "".join("- reviewed: %s 2026-10-04 cannot (fixture)\n" % a for a in sweep.AMIGOS)
                 + "\n## Synthetic one-verdict item\n"
                   "- raised: 2026-10-04 by desi\n"
                   "- blocked because: a fixture that must not be marked\n"
                   "- reviewed: desi 2026-10-04 cannot (fixture)\n")
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "reject-queue.md"
            copy.write_text(self.text + nearly + extra, encoding="utf-8")
            items = sweep.parse(copy.read_text(encoding="utf-8"))
            self.assertEqual([i["title"] for i in sweep.ready(items)],
                             ["Synthetic full-verdict item"],
                             "an item missing the fifth amigo's verdict was declared ready")
            sweep.stamp(copy, [i["title"] for i in sweep.ready(items)], "2026-10-04")
            after = sweep.parse(copy.read_text(encoding="utf-8"))
            self.assertEqual(sweep.ready(after), [], "the marked item is ready again — it would be asked twice")
            marked = [i for i in after if i["title"].startswith("Synthetic") and i["requested"]]
            self.assertEqual([i["title"] for i in marked], ["Synthetic full-verdict item"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
