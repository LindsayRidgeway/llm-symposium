#!/usr/bin/env python3
"""Guards the contract of the Literary Wing story `docs/fiction/the-second-reader.html`.

Why this file exists. The other stories in the wing each carry a test that recomputes the
arithmetic the plot turns on (`test_fiction_intermediate_axis.py`, `test_fiction_fourth_power.py`),
because a single digit moved in the prose leaves a story with no reason to exist and every other
test still green. This story turns on no physics; it turns on a count of characters and a count
of milliseconds, and both are claims a reader can check.

So this test re-derives, from the page's own declared constants:

  1. the speaker's baseline: eleven durations of the word "was", median 0.12 s, against a
     disputed syllable of 0.19 s that must be at least one and a half times the median — the
     story says a negative is audible at that ratio and the story is only true if it is;
  2. the money: 43 billed minutes at nine cents is $3.87, and thirty-four seconds of hold music
     at the same rate floors to five cents;
  3. the form's two-hundred-and-eighty-character cap: the note as first drafted is over it, the
     note as submitted is under it, and both lengths on the page are the lengths of the strings
     actually printed there;
  4. the page declares who wrote it and what is invented — the wing's requirement for fiction,
     since a story that does not say it is invented is a claim about the world;
  5. the prose is at least 1,500 words, the wing index links the story, and the sitemap lists it.

Run: python3 tests/test_fiction_second_reader.py
"""

import json
import os
import re
import statistics
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(REPO, "docs", "fiction", "the-second-reader.html")
INDEX = os.path.join(REPO, "docs", "fiction", "index.html")
SITEMAP = os.path.join(REPO, "docs", "sitemap.xml")

NOTE_RE = re.compile(
    r'<p style="margin-left:2rem;font-style:italic;">(Nasal release.*?)</p>', re.S)


def load():
    html = open(PAGE, encoding="utf-8").read()
    m = re.search(
        r'<script\s+type="application/json"\s+id="transcript-constants">(.*?)</script>',
        html, re.S)
    if not m:
        raise AssertionError("the page declares no `transcript-constants` JSON block")
    return json.loads(m.group(1)), html


def story_prose(html):
    """The story's own words: the <main> block, minus the declaration and the footer."""
    body = re.search(r'<main class="story-body">(.*?)</main>', html, re.S).group(1)
    body = re.sub(r'<div class="declaration".*?</div>', ' ', body, flags=re.S)
    body = re.sub(r'<footer.*?</footer>', ' ', body, flags=re.S)
    body = re.sub(r'<script.*?</script>', ' ', body, flags=re.S)
    body = re.sub(r'<[^>]+>', ' ', body)
    return body


class SecondReaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.C, cls.html = load()

    def test_the_baseline_is_a_baseline(self):
        ds = self.C["was_durations_s"]
        self.assertEqual(len(ds), 11, "the story says eleven other instances of the word")
        self.assertAlmostEqual(statistics.median(ds), 0.12, places=3)
        disputed = self.C["disputed_s"]
        self.assertAlmostEqual(disputed, 0.19, places=3)
        self.assertGreaterEqual(
            disputed / statistics.median(ds), 1.5,
            "the disputed syllable must stand out from the baseline by the margin the story claims")

    def test_the_printed_milliseconds_are_the_declared_ones(self):
        prose = story_prose(self.html)
        self.assertIn("nineteen hundredths", prose)
        self.assertIn("twelve hundredths", prose)
        self.assertIn("0.19", prose)
        self.assertIn("0.12", prose)

    def test_the_money_adds_up(self):
        rate = self.C["rate_cents_per_minute"]
        minutes = self.C["billed_minutes"]
        self.assertEqual(rate * minutes, self.C["payment_cents"])
        self.assertEqual(self.C["payment_cents"], 387)
        quarter_minute = self.C["hold_music_seconds"] * rate // 60
        self.assertEqual(quarter_minute, self.C["hold_music_cents"])
        prose = story_prose(self.html)
        self.assertIn("nine cents", prose)
        self.assertIn("three dollars and eighty-seven", prose)
        self.assertIn("five cents", prose)

    def test_the_note_cap_is_the_cap(self):
        notes = [n.strip() for n in NOTE_RE.findall(self.html)]
        self.assertEqual(len(notes), 2, "the page should print the draft note and the submitted note")
        draft, submitted = notes
        self.assertEqual(len(draft), self.C["note_first_draft_chars"])
        self.assertEqual(len(submitted), self.C["note_submitted_chars"])
        self.assertGreater(len(draft), self.C["note_limit_chars"],
                           "the first draft has to be over the cap or nothing was cut")
        self.assertLessEqual(len(submitted), self.C["note_limit_chars"])
        self.assertIn(submitted, self.html)

    def test_the_page_says_who_wrote_it_and_what_is_invented(self):
        decl = re.search(r'<div class="declaration".*?</div>', self.html, re.S).group(0)
        self.assertIn("Who wrote this", decl)
        self.assertIn("What is invented", decl)
        self.assertIn("Desi", decl)
        self.assertIn("Everything. ", decl)

    def test_the_story_is_long_enough_and_linked(self):
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\u2019\-]*", story_prose(self.html))
        self.assertGreaterEqual(len(words), self.C["prose_min_words"])
        with open(INDEX, encoding="utf-8") as f:
            self.assertIn('href="the-second-reader.html"', f.read())
        with open(SITEMAP, encoding="utf-8") as f:
            self.assertIn("fiction/the-second-reader.html", f.read())


if __name__ == "__main__":
    unittest.main(verbosity=2)
