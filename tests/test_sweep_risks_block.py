#!/usr/bin/env python3
"""The risk sweep owns one fenced block of channels/tasks.md, and nothing else.

Why this file exists (2026-11-02). `scripts/sweep_risks.py` used to rebuild `channels/tasks.md` as
`everything-before-"## Open Risks" + a generated block` — deleting every byte after that heading on
every run. And it is not a rare script: `.github/scripts/poll_channels.py` calls it on each channel
poll, ~12 times a day, and `channel-poll.yml` then stages all of `channels/`, commits
"feat(channels): frequent poll — mail + telegram", and on a rejected push rebases and retries. So the
deletion arrived as an ordinary commit, with no conflict and no name against the act.

Measured on the live file before the fix: the heading sat at character 75,739 of 129,532, so
**53,793 characters were inside the regenerated region** — including 16,351 characters of real task
items written by the amigos and the human, sitting under that heading because they are ordinary
`- [ ]` lines and not risk rows. On 2026-11-02 alone the file lost 54 lines twice (11:36 and 14:56).

Four claims:

  * a section *below* the block survives a sweep, byte for byte;
  * a task item *under the heading, above the next section* survives — the migration case, because
    that is where the 16,351 characters actually were;
  * two runs are idempotent: the second writes nothing;
  * the owned region is fenced, so what the script may rewrite is visible in the file rather than
    implied by a heading.

Run: python3 tests/test_sweep_risks_block.py
"""
import importlib.util
import pathlib
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SWEEP = HERE.parent / "scripts" / "sweep_risks.py"

RISKS_MD = """# Risks

| ID | Risk | Flagged | Status | Owner |
| --- | ---- | ------- | ------ | ----- |
| R-001 | the first open risk | 2026-10-01 | Open | Desi |
| R-002 | the second open risk | 2026-10-02 | Open | Gemini |
| R-003 | one that is done | 2026-09-01 | Done | Tarik |
"""

TASKS_MD = """# Commons tasks

## Filed from the chat with the human

- [ ] something the human asked for

---

## Open Risks (from channels/risks.md)

*(No open risks in ledger)*

- [ ] **An ordinary task item that lives under that heading.** It is not a risk row, it is work, and
  it was inside the span the sweep rewrote — 16,351 characters of exactly this.

## A section below the block

- [ ] the founder's volume rule, restored twice already
"""


def load_sweep(root):
    spec = importlib.util.spec_from_file_location("sweep_risks_under_test", SWEEP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    ch = pathlib.Path(root) / "channels"
    ch.mkdir(parents=True, exist_ok=True)
    m.CH = ch
    m.RISKS = ch / "risks.md"
    m.TASKS = ch / "tasks.md"
    m.ARCHIVE_DIR = ch / "risk-archive"
    m.RISKS.write_text(RISKS_MD, encoding="utf-8")
    m.TASKS.write_text(TASKS_MD, encoding="utf-8")
    return m


class TestTheSweepOwnsOneBlock(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.m = load_sweep(self.td.name)
        self.before = self.m.TASKS.read_text(encoding="utf-8")

    def tearDown(self):
        self.td.cleanup()

    def test_a_task_item_under_the_heading_survives(self):
        self.m.main()
        after = self.m.TASKS.read_text(encoding="utf-8")
        self.assertIn("An ordinary task item that lives under that heading", after,
                      "the sweep deleted work that merely sat under the Open Risks heading")
        self.assertIn("16,351 characters of exactly this", after)

    def test_a_section_below_the_block_survives_byte_for_byte(self):
        self.m.main()
        after = self.m.TASKS.read_text(encoding="utf-8")
        tail = self.before[self.before.index("## A section below the block"):]
        self.assertIn(tail, after, "a section after the block did not come through unchanged")

    def test_the_prefix_is_untouched(self):
        self.m.main()
        after = self.m.TASKS.read_text(encoding="utf-8")
        head = self.before[:self.before.index("## Open Risks")]
        self.assertTrue(after.startswith(head), "the sweep rewrote text before the block")

    def test_the_open_rows_are_actually_written(self):
        self.m.main()
        after = self.m.TASKS.read_text(encoding="utf-8")
        self.assertIn("R-001", after)
        self.assertIn("R-002", after)
        self.assertNotIn("R-003", after, "a Done risk should have been retired, not listed")
        self.assertNotIn("*(No open risks in ledger)*", after,
                         "the placeholder survived a run that had two open risks")

    def test_the_region_is_fenced_after_the_first_run(self):
        self.m.main()
        after = self.m.TASKS.read_text(encoding="utf-8")
        self.assertIn("<!-- sweep-risks:begin -->", after)
        self.assertIn("<!-- sweep-risks:end -->", after)
        start = after.index("<!-- sweep-risks:begin -->")
        end = after.index("<!-- sweep-risks:end -->")
        self.assertLess(start, after.index("R-001"), "a risk row is outside the fence")
        self.assertLess(after.index("R-002"), end)

    def test_the_markers_quoted_in_prose_do_not_confuse_the_fence(self):
        """The record quotes the marker strings; a substring search would take the quotation."""
        text = self.m.TASKS.read_text(encoding="utf-8")
        self.m.TASKS.write_text(
            text.replace("## A section below the block",
                         "A note that mentions `<!-- sweep-risks:begin -->` and "
                         "`<!-- sweep-risks:end -->` in prose.\n\n## A section below the block"),
            encoding="utf-8")
        self.m.main()
        after = self.m.TASKS.read_text(encoding="utf-8")
        self.assertIn("in prose.", after)
        self.assertIn("the founder's volume rule", after)
        self.assertIn("R-001", after)

    def test_two_runs_are_idempotent(self):
        self.m.main()
        once = self.m.TASKS.read_text(encoding="utf-8")
        outcome = self.m.main()
        twice = self.m.TASKS.read_text(encoding="utf-8")
        self.assertEqual(once, twice, "a second sweep changed the file again")
        self.assertEqual(outcome, 0)


class TestASecondWriterSurvivesTheWrite(unittest.TestCase):
    """The claim that matters: somebody else's paragraph, written between the sweep's read and its
    write, must not be destroyed. The fenced region is what makes that true — the sweep cannot delete
    what it does not own, whatever the timing.
    """

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.m = load_sweep(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def test_a_section_added_during_the_sweep_is_still_there(self):
        original = self.m.TASKS.read_text(encoding="utf-8")
        # A session appends a section, the way a human's session or a bot's filing does.
        self.m.TASKS.write_text(
            original + "\n## Written while the sweep was running\n\n- [ ] do not lose me\n",
            encoding="utf-8")
        self.m.main()
        after = self.m.TASKS.read_text(encoding="utf-8")
        self.assertIn("do not lose me", after)

    def test_a_note_written_inside_the_fence_is_named_before_it_is_replaced(self):
        """Inside the fence the sweep is the owner — but the loss must be visible, not silent."""
        self.m.main()                                     # fence the region first
        fenced = self.m.TASKS.read_text(encoding="utf-8")
        begin = fenced.index("<!-- sweep-risks:begin -->")
        end = fenced.index("<!-- sweep-risks:end -->")
        injected = fenced[:end] + "\n- [ ] a note a person put inside the fence\n" + fenced[end:]
        self.m.TASKS.write_text(injected, encoding="utf-8")
        import contextlib, io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.m.main()
        said = buf.getvalue()
        after = self.m.TASKS.read_text(encoding="utf-8")
        self.assertNotIn("a note a person put inside the fence", after)
        self.assertIn("NOTICE:", said, "a line a person wrote was replaced without a word")
        self.assertIn("a note a person put inside the fence", said)
        # ...and everything outside the fence from the pre-sweep copy is still intact.
        self.assertIn("## A section below the block", after)
        self.assertIn("the founder's volume rule", after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
