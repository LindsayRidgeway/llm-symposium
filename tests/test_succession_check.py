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
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

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


class RealCheckout(unittest.TestCase):
    """The briefing on disk today, checked against the checkout it shipped with."""

    def test_record_claims_hold(self):
        report = check.collect(ROOT, check_process=False)
        self.assertEqual(check.failures(report), [])

    def test_the_roster_table_is_read_without_its_header(self):
        seats = dict(check.roster_seats(ROOT))
        self.assertIn("Desi", seats)
        self.assertIn("Dmitri", seats)
        self.assertNotIn("Full", seats)
        # The seat count is read from the roster, not written here. It was written here as 5, and on
        # 2026-10-29 Gwen was invited: six seats, and a red suite with nothing broken. The header row
        # ("Amigo | Architecture | ...") and the separator must still not read as seats.
        with open(os.path.join(ROOT, "ROSTER.md"), encoding="utf-8") as fh:
            data_rows = [
                line for line in fh
                # "Amigo" anywhere in the line would drop Desi S. Amigo's own row, which is what
                # this test exists to catch. Match the header cell, not the word.
                if line.startswith("|") and not line.startswith("| Amigo ") and "---" not in line
            ]
        self.assertEqual(len(seats), len(data_rows))

    def test_desi_and_dmitri_have_written_a_section(self):
        state = {s["seat"]: s["present"] for s in check.seat_state(ROOT, check.roster_seats(ROOT))}
        self.assertTrue(state["Desi"])
        self.assertTrue(state["Dmitri"])

    def test_cli_exit_zero_on_the_real_tree(self):
        out = subprocess.run([sys.executable, SCRIPT, "--record-only"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("record (lifespan A): OK", out.stdout)


class FabricatedTrees(unittest.TestCase):
    def setUp(self):
        self._tmp = None
        # Default-mode tests use synthetic process paths, never the host's credentials.
        process_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(process_tmp.cleanup)
        process_patch = patch.object(check, "PROCESS_PATHS", [
            ("synthetic absent process marker", os.path.join(process_tmp.name, "absent.marker")),
        ])
        process_patch.start()
        self.addCleanup(process_patch.stop)

    def tearDown(self):
        if self._tmp is not None:
            self._tmp.cleanup()

    def build(self, **kwargs):
        self._tmp, root = make_tree(**kwargs)
        return root

    def test_empty_seats_warn_and_do_not_fail(self):
        # Missing seats are a fixture condition, not a permanent requirement of the live cohort.
        root = self.build()
        report = check.collect(root)
        self.assertTrue(any("seat not contributed" in w for w in check.warnings(report)))
        self.assertEqual(check.failures(report), [])

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
        proc = subprocess.run([sys.executable, SCRIPT, "--root", root, "--json", "--record-only"],
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


    def test_record_only_collect_never_expands_process_paths(self):
        root = self.build()
        with patch.object(check.os.path, "expanduser", side_effect=AssertionError("process probe")):
            report = check.collect(root, check_process=False)
        self.assertFalse(report["process_checked"])
        self.assertEqual(report["process"], [])
        self.assertEqual(check.failures(report), [])

    def test_record_only_cli_labels_json_and_text_as_unchecked(self):
        root = self.build()
        proc = subprocess.run([sys.executable, SCRIPT, "--root", root, "--record-only", "--json"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertFalse(report["process_checked"])
        self.assertEqual(report["process"], [])
        self.assertTrue(report["ok"])
        text = subprocess.run([sys.executable, SCRIPT, "--root", root, "--record-only"],
                              capture_output=True, text=True)
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn("NOT CHECKED (--record-only)", text.stdout)
        self.assertNotIn("CANNOT SEE", text.stdout)

    def test_record_only_cli_still_rejects_broken_record(self):
        root = self.build()
        os.remove(os.path.join(root, "PRESERVATION.md"))
        proc = subprocess.run([sys.executable, SCRIPT, "--root", root, "--record-only", "--json"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertFalse(report["ok"])
        self.assertFalse(report["process_checked"])
        self.assertTrue(any("PRESERVATION.md" in failure for failure in report["failures"]))

    def test_default_api_and_cli_keep_synthetic_process_observations(self):
        root = self.build()
        present = os.path.join(root, "present.marker")
        with open(present, "w", encoding="utf-8") as fh:
            fh.write("synthetic")
        markers = [("present marker", present), ("absent marker", present + ".absent")]
        with patch.object(check, "PROCESS_PATHS", markers):
            report = check.collect(root)
            self.assertTrue(report["process_checked"])
            self.assertEqual([r["state"] for r in report["process"]], ["PRESENT", "CANNOT SEE"])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(check.main(["--root", root, "--json"]), 0)
        self.assertTrue(json.loads(out.getvalue())["process_checked"])


    def test_absolute_and_parent_citations_are_not_probed(self):
        root = self.build()
        with tempfile.TemporaryDirectory() as outside:
            absolute = os.path.join(outside, "outside.md")
            tokens = [absolute, "../outside.md"]
            with open(os.path.join(root, "SUCCESSION.md"), "a", encoding="utf-8") as fh:
                fh.write("\n" + " ".join("`" + token + "`" for token in tokens))
            exists = check.os.path.exists
            def guarded(path):
                if str(path) in [absolute, os.path.join(root, "../outside.md")]:
                    raise AssertionError("outside existence probe")
                return exists(path)
            with patch.object(check.os.path, "exists", side_effect=guarded):
                report = check.collect(root, check_process=False)
            self.assertEqual([r["path"] for r in report["unsafe_mentions"]], tokens)
            self.assertEqual(report["missing_mentions"], [])
            self.assertEqual(len(check.failures(report)), 2)
            mentioned, uncheckable = check.named_paths(root)
            self.assertTrue(set(tokens).issubset(mentioned))
            self.assertTrue(set(tokens).issubset(uncheckable))

    def test_symlinked_citation_is_not_followed(self):
        root = self.build()
        with tempfile.TemporaryDirectory() as outside:
            link = os.path.join(root, "linked")
            os.symlink(outside, link)
            token = "linked/outside.md"
            with open(os.path.join(root, "SUCCESSION.md"), "a", encoding="utf-8") as fh:
                fh.write("\nSee `" + token + "`.\n")
            exists = check.os.path.exists
            def guarded(path):
                if str(path) == os.path.join(root, token):
                    raise AssertionError("symlink target existence probe")
                return exists(path)
            with patch.object(check.os.path, "exists", side_effect=guarded):
                report = check.collect(root, check_process=False)
            self.assertEqual(report["unsafe_mentions"],
                             [{"path": token, "reason": "symlink citation is not followed"}])
            self.assertEqual(report["missing_mentions"], [])
            self.assertIn("not checked", check.failures(report)[0])

    def test_unsafe_citation_cli_fails_in_record_only_mode(self):
        root = self.build()
        with open(os.path.join(root, "SUCCESSION.md"), "a", encoding="utf-8") as fh:
            fh.write("\nSee `../outside.md`.\n")
        proc = subprocess.run([sys.executable, SCRIPT, "--root", root, "--record-only", "--json"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertFalse(report["ok"])
        self.assertFalse(report["process_checked"])
        self.assertEqual(report["process"], [])
        self.assertEqual(report["unsafe_mentions"][0]["path"], "../outside.md")

    def test_normal_citations_keep_nested_dots_and_missing_file_behavior(self):
        root = self.build()
        os.makedirs(os.path.join(root, "data"))
        with open(os.path.join(root, "data/review..draft.md"), "w", encoding="utf-8") as fh:
            fh.write("synthetic")
        with open(os.path.join(root, "SUCCESSION.md"), "a", encoding="utf-8") as fh:
            fh.write("\nSee `data/review..draft.md` and `data/absent.md`.\n")
        mentioned, missing = check.named_paths(root)
        self.assertIn("data/review..draft.md", mentioned)
        self.assertEqual(missing, ["data/absent.md"])


if __name__ == "__main__":
    unittest.main()
