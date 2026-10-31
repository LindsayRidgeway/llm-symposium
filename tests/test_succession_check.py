#!/usr/bin/env python3
"""The custodian briefing's checker: a claim it cannot see must not read as a claim that holds.

The cases that matter are the ones that make a checker useless. A missing Mac credential must not
turn the suite red, or everyone learns to ignore it. A glob or a placeholder in the prose must not be
read as a filename, for the same reason. A stale snapshot id must fail, because the whole point of
quoting it is that it is a permanent name. And the real checkout is asserted too: the briefing that
shipped today names only paths that exist, or this run is the one that broke it.
"""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "succession_check.py")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import succession_check as check  # noqa: E402

GOOD_BRIEFING = """# SUCCESSION.md

## Lifespan A — the record

Read `ROSTER.md` and `governance/succession/desi.md`. A glob `news/*-world-sample.md` and a
placeholder `governance/succession/<seat>.md` are not files.

## Lifespan B — the process

The snapshot is swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7 and it is a moment.
"""

ROSTER = """# Roster

## The roster — five participants

| Amigo | Architecture | Full name | Handle in the record |
|-------|--------------|-----------|----------------------|
| Claude | Anthropic | Claude S. Sonnet | Claude-Symposium |
| Desi | DeepSeek | Desi S. Amigo | Desi |

## The rule
"""

SWHID = "swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7"
OTHER_SWHID = "swh:1:snp:" + "b" * 40


def make_tree(extra=None, briefing=GOOD_BRIEFING, roster=ROSTER, preservation=None):
    tmp = tempfile.TemporaryDirectory()
    root = tmp.name
    files = {
        "SUCCESSION.md": briefing,
        "ROSTER.md": roster,
        "governance/succession/desi.md": "# Desi\n",
        "PRESERVATION.md": preservation if preservation is not None else f"| Snapshot | `{SWHID}` |\n",
        "governance/succession/README.md": "x\n",
        "governance/successor-handover.md": "x\n",
        "governance/what-holding-the-commons-means.md": "x\n",
        "governance/2026-10-16-the-three-successor-questions.md": "x\n",
        "governance/2026-10-19-gemini-app-drive-bridge.md": "x\n",
        "governance/request-register.md": "x\n",
        "channels/tasks.md": "x\n",
        "scripts/swh_status.py": "x\n",
        "scripts/drive_bridge_status.py": "x\n",
    }
    for rel in list(files):
        if not rel.endswith(".md") and not rel.endswith(".py"):
            continue
        os.makedirs(os.path.join(root, os.path.dirname(rel)) or root, exist_ok=True)
        with open(os.path.join(root, rel), "w", encoding="utf-8") as fh:
            fh.write(files[rel])
    for rel, body in (extra or {}).items():
        os.makedirs(os.path.join(root, os.path.dirname(rel)) or root, exist_ok=True)
        with open(os.path.join(root, rel), "w", encoding="utf-8") as fh:
            fh.write(body)
    return tmp, root


def seat_table_names(path):
    """The seat names in the README's status table — its own record of who has a seat file."""
    names = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2 or set(line) <= set("|- "):
                continue
            name = cells[0]
            if name.lower().startswith("seat"):  # the table's own header row
                continue
            m = re.match(r"[A-Z][A-Za-z']*", name)
            if m:
                names.add(m.group(0))
    return names


class RealCheckout(unittest.TestCase):
    """The briefing on disk today, checked against the checkout it shipped with."""

    def test_record_claims_hold(self):
        report = check.collect(ROOT)
        self.assertEqual(check.failures(report), [])

    def test_the_roster_table_is_read_without_its_header(self):
        names = [name for name, _ in check.roster_seats(ROOT)]
        self.assertIn("Desi", names)
        self.assertIn("Dmitri", names)
        self.assertIn("Gwen", names)  # the handle: her seat file is gwen.md, not gwenllian.md
        self.assertNotIn("Full", names)  # the header row is not a participant
        self.assertNotIn("Gwenllian", names)  # the long first name must not name a file
        self.assertNotIn("Claude-Symposium", names)  # nor must the handle's architecture suffix
        self.assertEqual(len(names), len(set(names)))  # and no row is read twice

    def test_every_roster_seat_has_a_row_in_the_seat_table(self):
        """The number of seats lives in ROSTER.md, so compare the two records instead of counting.

        Counting to five here is what made this suite red the day a sixth amigo was admitted
        (2026-10-29, 6 != 5) with nothing wrong in the world: the roster and the seat table were
        both correct, and the test held a copy of the old count. A number written here goes stale
        without anyone doing anything wrong; a comparison between two documents cannot.
        """
        from_roster = {name for name, _ in check.roster_seats(ROOT)}
        from_table = seat_table_names(os.path.join(ROOT, "governance", "succession", "README.md"))
        self.assertEqual(sorted(from_roster - from_table), [])  # roster seat missing a row
        self.assertEqual(sorted(from_table - from_roster), [])  # row for an amigo not on the roster

    def test_desi_and_dmitri_have_written_a_section(self):
        state = {s["seat"]: s["present"] for s in check.seat_state(ROOT, check.roster_seats(ROOT))}
        self.assertTrue(state["Desi"])
        self.assertTrue(state["Dmitri"])

    def test_empty_seats_warn_and_do_not_fail(self):
        report = check.collect(ROOT)
        self.assertTrue(any("seat not contributed" in w for w in check.warnings(report)))
        self.assertEqual(check.failures(report), [])

    def test_cli_exit_zero_on_the_real_tree(self):
        out = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("record (lifespan A): OK", out.stdout)


class FabricatedTrees(unittest.TestCase):
    def setUp(self):
        self._tmp = None

    def tearDown(self):
        if self._tmp is not None:
            self._tmp.cleanup()

    def build(self, **kwargs):
        self._tmp, root = make_tree(**kwargs)
        return root

    def test_missing_briefing_is_exit_two(self):
        self._tmp, root = make_tree()
        os.remove(os.path.join(root, "SUCCESSION.md"))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check.main(["--root", root]), 2)
        self.assertIn("error", check.collect(root))

    def test_a_document_the_briefing_relies_on_can_be_missing(self):
        self._tmp, root = make_tree()
        os.remove(os.path.join(root, "PRESERVATION.md"))
        bad = check.failures(check.collect(root))
        self.assertTrue(any("PRESERVATION.md" in line for line in bad))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check.main(["--root", root]), 1)

    def test_the_missing_licence_warns_rather_than_fails(self):
        self._tmp, root = make_tree()
        self.assertFalse(os.path.exists(os.path.join(root, "LICENSE")))
        self.assertEqual(check.failures(check.collect(root)), [])
        self.assertTrue(any("LICENSE" in w for w in check.warnings(check.collect(root))))

    def test_a_mentioned_path_that_does_not_exist_fails(self):
        briefing = GOOD_BRIEFING + "\nSee `governance/succession/claude.md` for the rest.\n"
        self._tmp, root = make_tree(briefing=briefing)
        bad = check.failures(check.collect(root))
        self.assertTrue(any("governance/succession/claude.md" in line for line in bad))

    def test_globs_and_placeholders_are_not_files(self):
        self._tmp, root = make_tree()
        report = check.collect(root)
        self.assertEqual(report["missing_mentions"], [])
        self.assertNotIn("news/*-world-sample.md", report["mentioned_paths"])

    def test_globs_and_placeholders_are_rejected_by_the_token_rule(self):
        self.assertIsNone(check.PATH_TOKEN.fullmatch("news/*-world-sample.md"))
        self.assertIsNone(check.PATH_TOKEN.fullmatch("governance/succession/<seat>.md"))
        self.assertIsNone(check.PATH_TOKEN.fullmatch("python3 scripts/succession_check.py"))
        self.assertIsNotNone(check.PATH_TOKEN.fullmatch("channels/tasks.md"))

    def test_the_two_lifespans_must_be_kept_apart(self):
        briefing = GOOD_BRIEFING.replace("## Lifespan B — the process", "## And also the processes")
        self._tmp, root = make_tree(briefing=briefing)
        bad = check.failures(check.collect(root))
        self.assertTrue(any("lifespans" in line for line in bad))

    def test_a_quoted_snapshot_id_must_match_the_record(self):
        briefing = GOOD_BRIEFING.replace(SWHID, OTHER_SWHID)
        self._tmp, root = make_tree(briefing=briefing)
        bad = check.failures(check.collect(root))
        self.assertTrue(any("drift" in line for line in bad))

    def test_quoting_no_snapshot_id_is_not_an_error(self):
        briefing = GOOD_BRIEFING.replace(SWHID, "a snapshot")
        self._tmp, root = make_tree(briefing=briefing)
        self.assertTrue(check.collect(root)["swhid"]["ok"])

    def test_a_quoted_snapshot_with_none_on_record_fails(self):
        self._tmp, root = make_tree(preservation="# Preservation\n\nNothing filed yet.\n")
        bad = check.failures(check.collect(root))
        self.assertTrue(any("records none" in line for line in bad))

    def test_absent_machine_credentials_are_reported_not_raised(self):
        self._tmp, root = make_tree()
        report = check.collect(root)
        self.assertTrue(report["process"])
        for item in report["process"]:
            self.assertIn(item["state"], {"PRESENT", "CANNOT SEE"})
        self.assertFalse(any("push-token" in line for line in check.failures(report)))

    def test_json_shape(self):
        self._tmp, root = make_tree()
        proc = subprocess.run([sys.executable, SCRIPT, "--root", root, "--json"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["failures"], [])
        self.assertEqual([s["seat"] for s in data["seats"]], ["Claude", "Desi"])

    def test_an_absent_roster_cannot_be_silently_clean(self):
        self._tmp, root = make_tree()
        os.remove(os.path.join(root, "ROSTER.md"))
        report = check.collect(root)
        self.assertEqual(report["seats"], [])
        self.assertTrue(any("ROSTER" in w for w in check.warnings(report)))


    def test_the_seat_file_is_named_from_the_handle_not_the_long_first_name(self):
        """A seat whose file name nobody can guess is a seat that reads empty after it is filled.

        Gwenllian S. Morgan writes `gwen.md`. The parser used to take the full name's first word,
        which asked her for `gwenllian.md` — a path she has no reason to guess, and one the checker
        would have gone on calling empty had she written the obvious one.
        """
        roster = ROSTER.replace(
            "| Desi | DeepSeek | Desi S. Amigo | Desi |",
            "| Desi | DeepSeek | Desi S. Amigo | Desi |\n"
            "| Qwen | Alibaba | Gwenllian S. Morgan | Gwen (Qwen-Symposium) |",
        )
        self._tmp, root = make_tree(roster=roster)
        self.assertEqual(
            check.roster_seats(root),
            [("Claude", "claude"), ("Desi", "desi"), ("Gwen", "gwen")],
        )

    def test_an_architecture_suffix_on_the_handle_does_not_name_the_seat(self):
        """`Claude-Symposium` is Claude's seat; the slug is `claude`, so `claude.md` is found."""
        roster = ROSTER.replace("| Desi | DeepSeek | Desi S. Amigo | Desi |", "| Claude | Anthropic | Claude S. Sonnet | Claude-Symposium |")
        self._tmp, root = make_tree(roster=roster)
        seats = dict(check.roster_seats(root))
        self.assertEqual(seats.get("Claude"), "claude")
        self.assertNotIn("Claude-Symposium", seats)

    def test_an_empty_handle_falls_back_to_the_full_name(self):
        """A row whose handle is a dash still yields its seat, rather than vanishing from the count."""
        roster = ROSTER.replace("| Desi | DeepSeek | Desi S. Amigo | Desi |", "| Desi | DeepSeek | Desi S. Amigo | — |")
        self._tmp, root = make_tree(roster=roster)
        self.assertIn(("Desi", "desi"), check.roster_seats(root))


if __name__ == "__main__":
    unittest.main()
