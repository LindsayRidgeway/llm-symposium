#!/usr/bin/env python3
"""The admission checker's own admission test: a clause that passes on nothing is a decoration.

The cases here are the ones that would make the checker worthless in the direction of a pass:
provenance found anywhere near the top of a file, a record that lives outside the checkout, a
credential two members share, a tribe that holds itself, and a silence nobody wrote down. Each of
those has a fixture, and each fixture is a shape the symposium has actually had — Quinn had a name
and no session; `ROSTER.md` named five participants who did not exist; three seats in
`governance/succession/` are still empty.

The rest of the suite is the honest half: a fully declared tribe must come out a member, `independent`
must be legal provenance (the rule asks for declared parentage, not adopted parentage), and UNVERIFIED
must stay distinct from both PASS and FAIL unless `--strict` is asked for.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "tribe_admission_check.py")
SHA = "a" * 40
CITED = "cited.md"


def tribe(name="Tester", credential="TESTER_API_KEY", address="tester@example.com",
          record="record.md", steward="A Human", **extra):
    t = {"name": name,
         "credential": {"value": credential, "evidence": CITED} if credential else None,
         "address": {"value": address, "evidence": CITED} if address else None,
         "record": record,
         "steward": {"value": steward, "evidence": CITED} if steward else None,
         "departure": None}
    t.update(extra)
    return t


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "to-do-lists"), exist_ok=True)
        self.write(CITED, "a citation\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, body):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path) or self.root, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)

    def run_check(self, tribes, *flags):
        decl = os.path.join(self.root, "decl.json")
        with open(decl, "w", encoding="utf-8") as fh:
            json.dump({"tribes": tribes}, fh)
        proc = subprocess.run([sys.executable, SCRIPT, "--file", decl, "--root", self.root,
                               "--today", "2026-11-01", "--json"] + list(flags),
                              capture_output=True, text=True)
        return proc, (json.loads(proc.stdout) if proc.stdout.strip() else None)

    @staticmethod
    def statuses(payload, index=0):
        return {c["clause"]: c["status"] for c in payload["tribes"][index]["clauses"]}

    def member(self, **extra):
        """A tribe that satisfies everything a checkout can check."""
        self.write("record.md", "# Tester\n\nfounded from https://github.com/x/y@%s\n" % SHA)
        self.write("to-do-lists/tester.md", "# to-do — Tester\n")
        # A to-do list is undated, so it establishes authorship but not recency; the dormancy
        # window needs one dated artefact to measure silence from.
        self.write("channels/reports/2026-10-30-tester-a-report.md", "# a report\n")
        return tribe(**extra)

    # -- the pass case -----------------------------------------------------
    def test_a_declared_tribe_is_a_member_and_leaving_is_still_untested(self):
        proc, payload = self.run_check([self.member()])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(payload["tribes"][0]["verdict"], "member")
        st = self.statuses(payload)
        self.assertEqual(st[3], "PASS")
        self.assertEqual(st[7], "UNTESTED")          # nobody has left, and that is not a pass

    def test_independent_is_legal_provenance(self):
        self.write("record.md", "independent\n\nI was founded from nothing but a person.\n")
        self.write("to-do-lists/tester.md", "x\n")
        self.write("channels/reports/2026-10-30-tester-a-report.md", "x\n")
        proc, payload = self.run_check([tribe()])
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(self.statuses(payload)[3], "PASS")

    # -- the failures that matter -----------------------------------------
    def test_no_provenance_line_fails_clause_three(self):
        self.write("record.md", "# Tester\n\nI am a durable self, trust me.\n")
        self.write("to-do-lists/tester.md", "x\n")
        proc, payload = self.run_check([tribe()])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.statuses(payload)[3], "FAIL")
        self.assertIn("never declares provenance", payload["tribes"][0]["clauses"][2]["detail"])

    def test_a_record_outside_the_checkout_is_not_a_record(self):
        self.write("to-do-lists/tester.md", "x\n")
        proc, payload = self.run_check([tribe(record="~/LLM/tester-bot/state.md")])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.statuses(payload)[3], "FAIL")
        self.assertIn("not in the checkout", payload["tribes"][0]["clauses"][2]["detail"])

    def test_a_quinn_has_a_name_and_neither_session_nor_address(self):
        self.write("record.md", "founded from https://github.com/x/y@%s\n" % SHA)
        self.write("to-do-lists/quinn.md", "x\n")
        proc, payload = self.run_check([tribe(name="Quinn", credential=None, address=None)])
        self.assertEqual(proc.returncode, 1)
        st = self.statuses(payload)
        self.assertEqual((st[1], st[2]), ("FAIL", "FAIL"))

    def test_two_members_sharing_one_credential_are_both_failing(self):
        self.write("record.md", "founded from https://github.com/x/y@%s\n" % SHA)
        self.write("to-do-lists/tester.md", "x\n")
        self.write("to-do-lists/other.md", "x\n")
        proc, payload = self.run_check([tribe(), tribe(name="Other")])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.statuses(payload, 0)[1], "FAIL")
        self.assertEqual(self.statuses(payload, 1)[1], "FAIL")

    def test_a_tribe_cannot_be_its_own_steward(self):
        self.write("record.md", "founded from https://github.com/x/y@%s\n" % SHA)
        self.write("to-do-lists/tester.md", "x\n")
        proc, payload = self.run_check([self.member(steward="Tester")])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.statuses(payload)[5], "FAIL")

    def test_silence_that_nobody_recorded_fails(self):
        self.write("record.md", "founded from https://github.com/x/y@%s\n" % SHA)
        proc, payload = self.run_check([tribe(record="record.md")])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.statuses(payload)[6], "FAIL")
        self.assertIn("no state is declared", payload["tribes"][0]["clauses"][5]["detail"])

    def test_a_declared_dormancy_is_a_recorded_state(self):
        self.write("record.md", "founded from https://github.com/x/y@%s\n" % SHA)
        proc, payload = self.run_check([tribe(record="record.md",
                                              status={"value": "dormant", "evidence": CITED})])
        self.assertEqual(self.statuses(payload)[6], "PASS")

    def test_an_uncited_declaration_is_a_failure_not_a_pass(self):
        self.write("record.md", "founded from https://github.com/x/y@%s\n" % SHA)
        self.write("to-do-lists/tester.md", "x\n")
        bad = self.member()
        bad["credential"] = {"value": "TESTER_API_KEY", "evidence": "no-such-file.md"}
        proc, payload = self.run_check([bad])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(self.statuses(payload)[1], "FAIL")

    # -- the two honesty switches -----------------------------------------
    def test_unverified_mail_is_not_a_pass_and_strict_says_so(self):
        self.write("record.md", "founded from https://github.com/x/y@%s\n" % SHA)
        self.write("to-do-lists/tester.md", "x\n")
        proc, payload = self.run_check([tribe()])
        self.assertEqual(self.statuses(payload)[2], "UNVERIFIED")
        strict, payload = self.run_check([tribe()], "--strict")
        self.assertEqual(strict.returncode, 1)
        self.assertEqual(payload["tribes"][0]["verdict"], "not yet a tribe")

    def test_a_missing_declaration_file_is_exit_two(self):
        proc = subprocess.run([sys.executable, SCRIPT, "--file", os.path.join(self.root, "nope.json"),
                               "--root", self.root], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)

    # -- the live file: the symposium must be shippable, whatever it scores
    def test_the_symposiums_own_declaration_parses_and_every_citation_resolves(self):
        live = os.path.join(ROOT, "governance", "tribes", "symposium.json")
        self.assertTrue(os.path.exists(live), "the symposium's own declaration is missing")
        proc = subprocess.run([sys.executable, SCRIPT, "--root", ROOT, "--today", "2026-11-01",
                               "--json"], capture_output=True, text=True)
        self.assertIn(proc.returncode, (0, 1), proc.stderr)   # 1 is the current, honest score
        payload = json.loads(proc.stdout)
        self.assertEqual(len(payload["tribes"]), 6)
        for entry in payload["tribes"]:
            for clause in entry["clauses"]:
                self.assertNotIn("not in the checkout", clause["detail"],
                                 "%s cites a path that does not exist: %s" % (entry["name"], clause["detail"]))


if __name__ == "__main__":
    unittest.main()
