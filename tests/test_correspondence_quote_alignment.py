#!/usr/bin/env python3
"""Synthetic source-alignment regressions; no correspondence corpus is read."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import correspondence_audit as ca


class SourceWitness(unittest.TestCase):
    LETTER = ("alpha bravo charlie delta echo foxtrot. Interruption sentence inserted here. "
              "bravo charlie delta echo foxtrot golf.")
    REPLY = "alpha bravo charlie delta echo foxtrot golf"

    def assert_witnesses(self, letter, reply, quotes):
        source = ca.words(ca.strip_markup(letter))
        target = ca.words(ca.strip_markup(reply))
        for quote in quotes:
            self.assertEqual(target[quote["start"]:quote["end"]],
                             source[quote["source_start"]:quote["source_end"]])

    def test_adjacent_reply_hits_cannot_bridge_different_source_locations(self):
        quotes = ca.find_quotes(self.LETTER, self.REPLY)
        self.assertEqual([q["words"] for q in quotes], [6, 6])
        self.assert_witnesses(self.LETTER, self.REPLY, quotes)

    def test_overlapping_valid_quotes_count_covered_words_once(self):
        quotes = ca.find_quotes(self.LETTER, self.REPLY)
        self.assertEqual(ca.quoted_word_count(quotes), 7)
        self.assertEqual(ca.echo_share(self.LETTER, self.REPLY, quotes)["copied_share"], 1.0)
        result = ca.audit(self.LETTER, self.REPLY)
        self.assertEqual(result["echo"]["longest_run"], 6)

    def test_alternate_source_occurrence_can_extend_the_whole_quote(self):
        reply = "alpha bravo charlie delta echo foxtrot golf hotel"
        letter = self.LETTER + " Different passage. " + reply
        quotes = ca.find_quotes(letter, reply)
        self.assertEqual([q["words"] for q in quotes], [8])
        self.assert_witnesses(letter, reply, quotes)

    def test_repeated_source_does_not_duplicate_reply_evidence(self):
        reply = "alpha bravo charlie delta echo foxtrot golf hotel"
        quotes = ca.find_quotes(reply + " separator " + reply, reply)
        self.assertEqual(len(quotes), 1)
        self.assertEqual(quotes[0]["words"], 8)

    def test_excluded_window_breaks_a_source_alignment(self):
        reply = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima"
        excluded = frozenset({tuple(reply.split()[2:8])})
        quotes = ca.find_quotes(reply, reply, boilerplate=excluded)
        self.assertEqual([q["words"] for q in quotes], [7, 9])
        self.assert_witnesses(reply, reply, quotes)
        self.assertEqual(ca.quoted_word_count(quotes), 12)


if __name__ == "__main__":
    unittest.main()
