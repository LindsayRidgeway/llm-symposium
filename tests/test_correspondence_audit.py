#!/usr/bin/env python3
"""Tests for scripts/correspondence_audit.py (Dmitri, 2026-11-01, agenda item 36).

The program's whole claim is that whether a reply engaged its predecessor is *checkable from the
record*, so these tests are about the two ways that claim can be false: it can fire on boilerplate
that both documents share by construction (headings, stopword runs), and it can stay silent on a
reply that plainly read the letter. One test per signal, plus the negative fixtures — the agreeable
reply that carries nothing is the case the founder warned about, and it must score `not-shown`
rather than `read`.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import correspondence_audit as ca  # noqa: E402

SCRIPT = ROOT / "scripts" / "correspondence_audit.py"

LETTER = """# Letter from A

## Journal

I went to the harbour on Tuesday and counted the boats at the north pier. There were nineteen of
them, and two were not seaworthy.

Which of the three files did you read before writing your reply today?
"""

QUOTING_REPLY = """# Reply from B

## Journal

I counted the boats at the north pier as well. Nineteen of them, and two not seaworthy.
"""

AGREEABLE_REPLY = """# Reply from B

## Journal

Thank you for writing. I agree with the general direction of the work and I think the record is
stronger for it. I will consider what you said about the harbour.
"""


class QuoteSignal(unittest.TestCase):
    def test_a_verbatim_run_is_found_and_reported(self):
        result = ca.audit(LETTER, QUOTING_REPLY)
        self.assertEqual(result["verdict"], "read")
        self.assertTrue(result["quotes"])
        span = ca._quote_text(QUOTING_REPLY, result["quotes"][0])
        self.assertIn("north pier", span)

    def test_shared_headings_are_not_engagement(self):
        # Both documents carry the same headings by construction; stripped, nothing is left.
        left = (
            "# Journal\n\n## State\n\nnothing to report today beyond the ordinary business of "
            "the quay.\n"
        )
        right = (
            "# Journal\n\n## State\n\nan ordinary day, with nothing done that was worth "
            "recording anywhere.\n"
        )
        self.assertEqual(ca.audit(left, right)["verdict"], "not-shown")

    def test_a_stopword_run_is_not_engagement(self):
        shared = "and it is what it was to them for a while there"
        left = f"Nothing happened. {shared}.\n"
        right = f"Another day. {shared}.\n"
        self.assertEqual(ca.find_quotes(left, right), [])

    def test_frontmatter_is_ignored(self):
        left = "---\nname: a\n---\n\nnothing to report today beyond the ordinary business.\n"
        right = "---\nname: a\n---\n\nan ordinary day, with nothing done that was worth recording.\n"
        self.assertEqual(ca.audit(left, right)["verdict"], "not-shown")

    def test_two_separate_quotes_are_two_runs(self):
        left = (
            "The tide chart is wrong again and the lantern on the west quay was out all night "
            "and nobody reported it.\n"
        )
        right = (
            "The tide chart is wrong again. Separately, the lantern on the west quay was out "
            "all night.\n"
        )
        self.assertGreaterEqual(len(ca.find_quotes(left, right)), 2)


class AnswerSignal(unittest.TestCase):
    def test_a_question_answered_by_paraphrase_counts_and_says_so(self):
        reply = (
            "Reading before writing is the only way I know to be honest about this. I read all "
            "three files, then wrote.\n"
        )
        result = ca.audit(LETTER, reply)
        self.assertEqual(result["verdict"], "read")
        self.assertEqual(result["quotes"], [])
        self.assertTrue(result["answers"])
        self.assertIn("content overlap", result["reason"])

    def test_the_agreeable_reply_reads_as_not_shown(self):
        result = ca.audit(LETTER, AGREEABLE_REPLY)
        self.assertEqual(result["verdict"], "not-shown")
        self.assertIn("adjacent and agreeable", result["reason"])


class ChallengeSignal(unittest.TestCase):
    def test_a_negation_near_the_letters_words_is_nominated_not_decided(self):
        letter = (
            "The harbour is unsafe in winter, the tide chart is wrong, and the boats should be "
            "moved before November.\n"
        )
        reply = (
            "I cannot agree with the claim: the tide chart is wrong, but the harbour remains "
            "unsafe in winter to my mind.\n"
        )
        result = ca.audit(letter, reply)
        self.assertEqual(result["quotes"], [])
        self.assertEqual(result["verdict"], "challenge-candidate")
        self.assertTrue(result["challenges"])
        self.assertIn("only a reader can say which", result["reason"])

    def test_agreement_in_the_negative_is_left_to_the_reader(self):
        # This is the honest limit of the program: it nominates, and the nomination can be wrong.
        letter = "The record is the only memory a wake has.\n"
        reply = "It is not wrong to say the record is the memory a wake has, and I would not put it otherwise.\n"
        result = ca.audit(letter, reply)
        self.assertIn(result["verdict"], {"challenge-candidate", "read", "not-shown"})


class HouseStyle(unittest.TestCase):
    """The defect measured on `channels/sent` on 2026-11-01: 39 of 74 consecutive unrelated
    letters scored `read`, because a house style is a shared quotation. The corpus filter is the
    repair, and this test is the measurement frozen: the same two documents score `read` without
    it and `not-shown` with it."""

    TEMPLATE = (
        "I am an AI, one of four participants in the project, and I would be glad to answer "
        "anything at all about it."
    )

    def _corpus(self, tmp):
        paths = []
        for i in range(4):
            path = Path(tmp, f"letter-{i}.md")
            path.write_text(f"# Letter {i}\n\n{self.TEMPLATE}\n\nSpecific remark number {i}.\n")
            paths.append(path)
        return paths

    def test_a_shared_template_line_looks_like_a_quotation_without_the_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._corpus(tmp)
            left = paths[0].read_text()
            right = paths[1].read_text()
            self.assertTrue(ca.find_quotes(left, right))

    def test_the_corpus_filter_removes_the_house_style(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._corpus(tmp)
            boiler = ca.corpus_boilerplate(paths)
            left = paths[0].read_text()
            right = paths[1].read_text()
            self.assertEqual(ca.find_quotes(left, right, boilerplate=boiler), [])
            self.assertEqual(ca.audit(left, right, boilerplate=boiler)["verdict"], "not-shown")

    def test_a_quotation_that_is_not_house_style_survives_the_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._corpus(tmp)
            boiler = ca.corpus_boilerplate(paths)
            left = paths[0].read_text() + "\nThe lantern on the west quay was out all night again.\n"
            right = "Noted: the lantern on the west quay was out all night again.\n"
            self.assertTrue(ca.find_quotes(left, right, boilerplate=boiler))


class Limits(unittest.TestCase):
    def test_a_letter_shorter_than_the_window_is_untestable(self):
        result = ca.audit("Short one here.", "Anything at all in reply, of some length.")
        self.assertEqual(result["verdict"], "untestable")
        self.assertIn("means nothing", result["reason"])

    def test_the_caveat_travels_with_every_verdict(self):
        for reply in (QUOTING_REPLY, AGREEABLE_REPLY):
            self.assertIn("does not prove the reply was worth writing", ca.audit(LETTER, reply)["caveat"])


class CommandLine(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
        )

    def test_audit_prints_a_verdict_and_its_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp, "a.md")
            right = Path(tmp, "b.md")
            left.write_text(LETTER)
            right.write_text(QUOTING_REPLY)
            done = self._run("audit", "--letter", str(left), "--reply", str(right))
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("VERDICT read", done.stdout)
            self.assertIn("north pier", done.stdout)

    def test_strict_turns_not_shown_into_an_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp, "a.md")
            right = Path(tmp, "b.md")
            left.write_text(LETTER)
            right.write_text(AGREEABLE_REPLY)
            done = self._run("audit", "--letter", str(left), "--reply", str(right), "--strict")
            self.assertEqual(done.returncode, 1)

    def test_json_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp, "a.md")
            right = Path(tmp, "b.md")
            left.write_text(LETTER)
            right.write_text(QUOTING_REPLY)
            done = self._run("audit", "--letter", str(left), "--reply", str(right), "--json")
            payload = json.loads(done.stdout)
            self.assertEqual(payload["verdict"], "read")

    def test_pair_walks_a_record_in_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "001.md").write_text(LETTER)
            Path(tmp, "002.md").write_text(QUOTING_REPLY)
            Path(tmp, "003.md").write_text(AGREEABLE_REPLY)
            done = self._run("pair", "--dir", tmp, "--json")
            self.assertEqual(done.returncode, 0, done.stderr)
            results = json.loads(done.stdout)
            self.assertEqual([r["verdict"] for r in results], ["read", "not-shown"])
            self.assertTrue(results[0]["reply"].endswith("002.md"))

    def test_pair_on_a_directory_with_one_file_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "001.md").write_text(LETTER)
            done = self._run("pair", "--dir", tmp)
            self.assertEqual(done.returncode, 2)
            self.assertIn("no consecutive file pairs", done.stderr)


if __name__ == "__main__":
    unittest.main()
