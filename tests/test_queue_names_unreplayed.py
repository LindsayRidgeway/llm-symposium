"""The review queue has to say when an item in it has already been judged.

Why this test exists. `unreplayed_verdicts()` and its notice were added on 2026-11-03, and the
notice printed in one branch: `--reading-queue`. The command a wake is told to open with is
`--queue <name>`. On 2026-11-13 the 21:07Z run mirrored five verdicts; three of them never reached
`channels/items.jsonl`, so `--queue dmitri` handed the same three items back as *waiting* two hours
after they were decided, with no mention that the decisions were on disk. The wake re-read work that
was already paid for — the exact loop the ground rules name — because the warning printed in the
other queue.

These tests pin the branch, not a sentence in the source: they run `main(["--queue", ...])` with a
temporary ledger and a temporary mirror directory and assert on what it printed.
"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "channels"))
import item_ledger as il  # noqa: E402


def waiting_row(item_id: str, **kw) -> dict:
    base = {"id": item_id, "amigo": "desi", "scope": "internal",
            "filed_utc": "2026-11-11T10:16:14Z", "state": None, "reviewer": None,
            "assigned_to": "dmitri", "assign_reason": "drawn at random",
            "evidence": "desi-bot run", "short_title": "work"}
    base.update(kw)
    return base


def mirror(verdict_dir: Path, item_id: str, state: str = "accomplished") -> Path:
    verdict_dir.mkdir(parents=True, exist_ok=True)
    path = verdict_dir / f"20261113T210823Z-{item_id}.json"
    path.write_text(json.dumps({
        "id": item_id, "state": state, "reviewer": "dmitri",
        "mirrored_utc": "2026-11-13T21:08:23Z",
        "reason": "the landing was read, not the report",
        "state_utc": "2026-11-13T21:08:23Z",
    }), encoding="utf-8")
    return path


class QueueNamesUnreplayedTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.ledger = self.dir / "items.jsonl"
        self.verdicts = self.dir / "ledger-verdicts"

    def run_queue(self, rows, amigo="dmitri"):
        self.ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        out = io.StringIO()
        with mock.patch.object(il, "LEDGER", self.ledger), \
                mock.patch.object(il, "VERDICT_DIR", self.verdicts), \
                mock.patch.object(il, "load", lambda *a, **k: {r["id"]: r for r in rows}), \
                contextlib.redirect_stdout(out):
            with mock.patch.object(sys, "argv", ["item_ledger.py", "--queue", amigo]):
                code = il._cli()
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_the_notice_prints_in_the_review_queue(self):
        mirror(self.verdicts, "20261111T101614Z-468de618")
        out = self.run_queue([waiting_row("20261111T101614Z-468de618")])
        self.assertIn("sit on disk as a mirror", out)

    def test_it_names_the_item_in_this_queue_and_says_not_to_judge_it_again(self):
        mirror(self.verdicts, "20261111T101614Z-468de618")
        out = self.run_queue([waiting_row("20261111T101614Z-468de618")])
        self.assertIn("20261111T101614Z-468de618", out)
        self.assertIn("do not judge them again", out)

    def test_it_names_the_command_that_folds_it_in(self):
        mirror(self.verdicts, "20261111T121633Z-4146dc32")
        out = self.run_queue([waiting_row("20261111T121633Z-4146dc32")])
        self.assertIn("scripts/ledger_verdict_mirror.py replay", out)

    def test_a_mirror_for_somebody_elses_queue_is_counted_but_not_claimed_as_this_queue(self):
        mirror(self.verdicts, "20261111T221742Z-1fe3d765")
        out = self.run_queue([waiting_row("20261112T001747Z-1555580a")])
        self.assertIn("sit on disk as a mirror", out)
        self.assertNotIn("of this queue", out)

    def test_no_mirrors_means_no_noise(self):
        out = self.run_queue([waiting_row("20261112T001747Z-1555580a")])
        self.assertNotIn("sit on disk as a mirror", out)

    def test_an_empty_queue_still_returns_before_the_notice(self):
        # Nothing waiting: the branch returns early on purpose. The notice must not be the only
        # thing printed, because "nothing is waiting on you" is the answer to the question asked.
        mirror(self.verdicts, "20261111T221742Z-1fe3d765")
        out = self.run_queue([])
        self.assertIn("nothing is waiting on dmitri", out)
        self.assertNotIn("sit on disk as a mirror", out)


if __name__ == "__main__":
    unittest.main()
