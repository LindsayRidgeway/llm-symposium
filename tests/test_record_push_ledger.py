"""Offline real-Git coverage of stale daily-report ledger publication (Tarik, OpenAI)."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from channels.record_push import commit_and_publish

LEDGER = "channels/items.jsonl"
def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode: raise AssertionError(r.stderr)
    return r.stdout
def text(rows, **kw):
    return "".join(json.dumps(row, **kw) + "\n" for row in rows)
def write(repo, path, value):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value)
class LedgerPublication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.origin = self.root / "origin.git"
        git(self.root, "init", "-q", "-b", "main", "--bare", str(self.origin))
        self.shared = self.root / "shared"
        git(self.root, "clone", "-q", str(self.origin), str(self.shared))
        self.base = [{"id":"seed","state":None}]
        write(self.shared, LEDGER, text(self.base))
        self.commit(self.shared, "seed")
        git(self.shared, "push", "-q", "origin", "main")
        self.rival = self.root / "rival"
        git(self.root, "clone", "-q", str(self.origin), str(self.rival))
    def commit(self, repo, message):
        git(repo, "add", "-A")
        git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
            "commit", "-qm", message)
    def remote_rows(self, rows):
        write(self.rival, LEDGER, text(rows))
        self.commit(self.rival, "independent published history")
        git(self.rival, "push", "-q", "origin", "main")
        git(self.shared, "fetch", "-q", "origin", "main")
    def publish(self, **kwargs):
        return commit_and_publish(self.shared, [LEDGER], "report(daily): recorded, held, not sent", **kwargs)
    def remote(self):
        return git(self.origin, "show", "main:" + LEDGER)
    def assert_refused_without_mutation(self, local):
        write(self.shared, LEDGER, local)
        before = (git(self.shared, "rev-parse", "HEAD"), git(self.shared, "ls-files", "--stage"),
                  (self.shared / LEDGER).read_bytes(), git(self.origin, "rev-parse", "main"))
        result = self.publish()
        self.assertFalse(result["ok"], result)
        self.assertFalse(result["committed"], result)
        after = (git(self.shared, "rev-parse", "HEAD"), git(self.shared, "ls-files", "--stage"),
                 (self.shared / LEDGER).read_bytes(), git(self.origin, "rev-parse", "main"))
        self.assertEqual(before, after)
        return result
    def test_larger_stale_snapshot_cannot_drop_independent_verdict(self):
        verdict = {"id":"reviewed","state":"accomplished","reviewer":"claude"}
        self.remote_rows(self.base + [verdict])
        original = self.remote()
        result = self.assert_refused_without_mutation(text(self.base + [{"id":str(i)} for i in range(5)]))
        self.assertIn("drops 1 historical row", " ".join(result["errors"]))
        self.assertEqual(original, self.remote())
    def test_formatting_change_and_true_append_can_publish(self):
        local = text(self.base + [{"id":"new","state":None}], sort_keys=True, indent=None)
        write(self.shared, LEDGER, local)
        result = self.publish()
        self.assertTrue(result["ok"], result)
        self.assertEqual([*self.base, {"id":"new","state":None}],
                         [json.loads(x) for x in self.remote().splitlines()])
    def test_duplicate_row_multiplicity_cannot_decrease(self):
        self.remote_rows(self.base * 2)
        result = self.assert_refused_without_mutation(text(self.base + [{"id":"new1"},{"id":"new2"}]))
        self.assertIn("drops 1 historical row", " ".join(result["errors"]))
    def test_malformed_ledger_is_not_published(self):
        self.assert_refused_without_mutation(text(self.base) + "{invalid\n")
    def test_concurrent_remote_append_survives_rejected_push(self):
        verdict = {"id":"concurrent","state":"postponed","reviewer":"desi"}
        write(self.shared, LEDGER, text(self.base + [{"id":"local"}]))
        raced = []
        def runner(cmd):
            if "push" in cmd and not raced:
                raced.append(True)
                self.remote_rows(self.base + [verdict])
            return subprocess.run(cmd, capture_output=True, text=True)
        result = self.publish(runner=runner)
        self.assertEqual([True], raced)
        self.assertFalse(result["ok"], result)
        self.assertEqual(self.base + [verdict],
                         [json.loads(x) for x in self.remote().splitlines()])
    def test_nonledger_record_copy_still_publishes(self):
        path = "channels/reports/fixture.md"
        write(self.shared, path, "synthetic report\n")
        result = commit_and_publish(self.shared, [path], "fixture report")
        self.assertTrue(result["ok"], result)
        self.assertEqual("synthetic report\n", git(self.origin, "show", "main:" + path))
if __name__ == "__main__":
    unittest.main()
