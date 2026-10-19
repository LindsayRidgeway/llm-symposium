#!/usr/bin/env python3
"""The wide branch of the review draw — the branch that has never yet fired.

Why this file exists (2026-10-19, dmitri). Measured on `channels/items.jsonl` — 343 assignment
rows, 327 of them draws, **zero of them wide**:

    branch      assignee   count
    cheap       dmitri     196
    cheap       desi       128
    named       gemini      11
    named       desi         8

and the decisions the register records carry the same shape: `desi` 136, `dmitri` 184,
`gemini` 6, `claude` 0, `tarik` 0. The cheap band is `desi, dmitri`, and both are DeepSeek, so
until 2026-10-18 the draw could not produce a reader who does not share the author's blind spots
— "the author is never the reviewer" held while the *point* of review did not.

`WIDE_SHARE` (one item in four is drawn from outside the band, minus anyone running the author's
own architecture) was written for exactly that, and it landed on 2026-10-18T15:06Z. Nothing has
fired because nothing has drawn since: the three assignments made after it are `named`, by
codex. So the wide branch is one day old and has never run in production, and the adapter it
triggers — `scripts/queue_review_handoff.py`, which makes a Tarik assignment visible to his body
— has never been exercised either. With the pool sitting at ~1 draw in 4 that lands outside the
band, and 1 draw in 3 of those naming Tarik, his seat is reached about once in twelve draws.

This file pins what the branch does on the day it fires, including the one thing it must not do:
assert a different architecture it has no record of. `item_ledger._pool` documents that a
diversity claim nothing supports is worse than an honest cheap review — but with an empty
architecture map it used to print "the band runs <author>'s own architecture" from no evidence
at all. The reason is the record here, so a reason that invents its premise is the defect.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402

BAND = ["desi", "dmitri"]
RATES = {"desi": 0.01, "dmitri": 0.01, "gemini": 0.59, "claude": 1.15, "tarik": 1.86}
ARCH = {"desi": "DeepSeek", "dmitri": "DeepSeek",
        "gemini": "Gemini", "claude": "Claude", "tarik": "GPT"}


def wide_ids(prefix: str = "w-wide", n: int = 4) -> list[str]:
    """Ids whose draw digest sends them across the wide branch. Fixed by sha256, not by luck."""
    out = [f"{prefix}-{i}" for i in range(200)
           if int(hashlib.sha256(f"{prefix}-{i}".encode()).hexdigest()[8:16], 16) % il.WIDE_SHARE == 0]
    return out[:n]


def cheap_ids(prefix: str = "w-cheap", n: int = 2) -> list[str]:
    out = [f"{prefix}-{i}" for i in range(200)
           if int(hashlib.sha256(f"{prefix}-{i}".encode()).hexdigest()[8:16], 16) % il.WIDE_SHARE != 0]
    return out[:n]


class WideBranchTest(unittest.TestCase):
    """`_pool` and `draw` on the branch nothing has ever exercised."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "items.jsonl"
        self.ledger.touch()
        self.band_dir = self.root / "usage"
        self.band_dir.mkdir()

    def write_band(self, *, architectures=None, carry_architectures=True, rates=None):
        data = {"as_of": "2026-08-25", "band": BAND, "cheapest": "desi",
                "rates_usd_per_million": rates or RATES}
        if carry_architectures and architectures is not None:
            data["architectures"] = architectures
        (self.band_dir / "price-band-2026-10.json").write_text(json.dumps(data), encoding="utf-8")

    def write_items(self, ids, author="desi"):
        with self.ledger.open("a", encoding="utf-8") as fh:
            for i, item_id in enumerate(ids):
                fh.write(json.dumps({
                    "id": item_id, "amigo": author, "scope": "internal",
                    "paths": ["x.md"], "filed_utc": f"2026-10-18T0{i}:00:00Z",
                    "state": None, "reviewer": None, "assigned_to": None,
                }) + "\n")

    def test_a_wide_draw_is_named_outside_the_band_and_says_so(self):
        """The branch's whole product: a reader the band cannot supply, and a reason that says it."""
        self.write_band(architectures=ARCH)
        self.write_items(wide_ids())
        made = il.draw(path=self.ledger, dir_=self.band_dir, by="dmitri")
        self.assertTrue(made, "the wide ids must produce assignments")
        for rec in made:
            self.assertNotIn(rec["assigned_to"], BAND,
                             f"{rec['id']} was drawn wide and landed back inside the band")
            self.assertNotEqual(rec["assigned_to"], "desi", "the author may never be the reviewer")
            self.assertIn("outside the cheap band", rec["assign_reason"])
            self.assertIn(f"1 item in {il.WIDE_SHARE}", rec["assign_reason"])

    def test_the_wide_branch_prefers_a_different_architecture(self):
        """With the map in hand, the pool is the bodies whose architecture differs from the author's."""
        self.write_band(architectures=dict(ARCH, claude="DeepSeek"))  # claude shares the author's
        self.write_items(wide_ids(), author="desi")
        made = il.draw(path=self.ledger, dir_=self.band_dir, by="dmitri")
        picked = {rec["assigned_to"] for rec in made}
        self.assertNotIn("claude", picked,
                         "claude runs the author's architecture in this fixture and must be excluded")

    def test_and_it_says_so_rather_than_claiming_what_it_cannot_show(self):
        """No architecture is recorded anywhere: widen on price, and claim nothing about the model.

        The pre-fix reason read "because the band runs desi's own architecture" — a sentence with
        no source, because `architectures()` had returned an empty map. That is the same defect as
        a stamp: a record asserting something nobody checked.
        """
        self.write_band(architectures={})  # band file carries no map and no model-prices.json exists
        self.assertEqual({}, il.architectures(self.band_dir))
        self.write_items(wide_ids())
        made = il.draw(path=self.ledger, dir_=self.band_dir, by="dmitri")
        self.assertTrue(made)
        for rec in made:
            reason = rec["assign_reason"]
            self.assertIn("outside the cheap band", reason)
            self.assertNotIn("the band runs", reason,
                             f"{rec['id']} claims an architecture the map does not record")
            self.assertIn("no architecture is recorded", reason)

    def test_when_every_body_outside_the_band_shares_the_author_it_says_widest_available(self):
        """The honest wording for a world where every body runs one architecture."""
        same = {"desi": "DeepSeek", "dmitri": "DeepSeek", "gemini": "DeepSeek",
                "claude": "DeepSeek", "tarik": "DeepSeek"}
        self.write_band(architectures=same)
        self.write_items(wide_ids())
        made = il.draw(path=self.ledger, dir_=self.band_dir, by="dmitri")
        self.assertTrue(made)
        for rec in made:
            self.assertIn("no body outside the band runs a different architecture",
                          rec["assign_reason"])
            self.assertIn("the widest pool available was used", rec["assign_reason"])
            self.assertNotIn("on purpose", rec["assign_reason"])

    def test_the_cheap_branch_is_unchanged_by_the_widening(self):
        """Three draws in four must still be the cost rule the band exists to obey."""
        self.write_band(architectures=ARCH)
        self.write_items(cheap_ids())
        made = il.draw(path=self.ledger, dir_=self.band_dir, by="dmitri")
        self.assertTrue(made)
        for rec in made:
            self.assertIn(rec["assigned_to"], BAND)
            self.assertIn("among the least expensive", rec["assign_reason"])
            self.assertNotIn("wide draw", rec["assign_reason"])
            self.assertNotEqual(rec["assigned_to"], "desi")

    def test_a_wide_draw_is_still_settled_and_re_derivable(self):
        """A draw that can re-roll is unowned with extra steps, wide branch included."""
        self.write_band(architectures=ARCH)
        ids = wide_ids()
        self.write_items(ids)
        first = {r["id"]: r["assigned_to"] for r in
                 il.draw(path=self.ledger, dir_=self.band_dir, by="dmitri")}
        self.write_items(ids)  # a second, unassigned copy of the same ids
        second = il.draw(path=self.ledger, dir_=self.band_dir, only=ids[0], by="dmitri")
        self.assertEqual([first[ids[0]]], [r["assigned_to"] for r in second])


if __name__ == "__main__":
    unittest.main()
