#!/usr/bin/env python3
"""Offline tests for scripts/r008_recurrence_check.py.

Builds a throwaway session database with the two tables the detector joins, plants
one of each way the R-008 signature appears (the risk row, a tool result quoting it,
a human pasting the error back, an interactive occurrence, a wake occurrence), and
asserts the classification, the quote count and the exit code.

No network, no real session store.
"""

import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest


def quiet(*args, **kwargs):
    """Run the CLI with its stdout captured, returning only the exit code."""
    with contextlib.redirect_stdout(io.StringIO()):
        return r.main(*args, **kwargs)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import r008_recurrence_check as r  # noqa: E402

SIG = r.SIGNATURE
ERR = '{"type":"error","kind":"other","message":"Ran into this error: Request failed: Bad request (400): ... (%s)"}' % SIG

SCHEMA = """
CREATE TABLE sessions (
    id TEXT PRIMARY KEY, name TEXT NOT NULL DEFAULT '', working_dir TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, provider_name TEXT
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, role TEXT NOT NULL,
    content_json TEXT NOT NULL, created_timestamp INTEGER NOT NULL
);
"""

# (session, name, working_dir, created_at, provider, role, content_json)
PLANTED = [
    # 1. the R-008 row itself, read into a chat — a quote
    ("s_int", "Dmitri #01", "/Users/x", "2026-10-05 15:40:47", "custom_deepseek", "user",
     '[{"type":"toolResponse","toolResult":{"content":[{"type":"text","text":"| R-008 | ... (%s) |"}]}}]' % SIG),
    # 2. a wake transcript that grepped the risk table — a tool result, so a quote
    ("s_wake_q", "CLI Session", "/Users/x/LLM/dmitri-bot/tick-state/runs/R1/repo",
     "2026-10-07 02:41:23", "custom_deepseek", "user",
     '[{"type":"toolResponse","toolResult":{"content":[{"type":"text","text":"grep output ... (%s)"}]}}]' % SIG),
    # 3. the human pasting the error back — a report
    ("s_rep", "Dmitri #02", "/Users/x", "2026-10-05 21:38:16", "custom_deepseek", "user",
     '[{"type":"text","text":"Your previous chat stalled with this error:\\n\\nRequest failed: ... (%s)"}]' % SIG),
    # 4. goose surfacing the rejection in an interactive chat — an occurrence
    ("s_err", "Desi #16", "/Users/x", "2026-09-23 18:33:55", "custom_deepseek", "assistant", ERR),
    # 5. the same rejection inside a wake — the escalation condition
    ("s_wake_err", "CLI Session", "/Users/x/LLM/desi-bot/tick-state/runs/R2/repo",
     "2026-10-08 06:45:12", "custom_deepseek", "assistant", ERR),
]


class RecurrenceCheckTest(unittest.TestCase):
    def setUp(self):
        fd, self.db = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        con = sqlite3.connect(self.db)
        con.executescript(SCHEMA)
        for sid, name, wd, ca, prov, role, cj in PLANTED:
            con.execute("INSERT INTO sessions(id,name,working_dir,created_at,provider_name) VALUES(?,?,?,?,?)",
                        (sid, name, wd, ca, prov))
            con.execute("INSERT INTO messages(session_id,role,content_json,created_timestamp) VALUES(?,?,?,0)",
                        (sid, role, cj))
        con.commit()
        con.close()

    def tearDown(self):
        os.unlink(self.db)

    def test_classify_three_ways(self):
        self.assertEqual(r.classify("user", PLANTED[0][6]), "quote")
        self.assertEqual(r.classify("assistant", ERR), "error")
        self.assertEqual(r.classify("user", PLANTED[2][6]), "report")

    def test_tool_result_is_never_an_occurrence(self):
        # even a tool result carrying type:error is impossible through goose; a
        # quote that happens to contain the word error must not be counted.
        self.assertEqual(r.classify("user", '{"toolResponse":1,"text":"%s"}' % SIG), "quote")

    def test_findings_and_quote_count(self):
        rows = r.load(self.db)
        self.assertEqual(len(rows), len(PLANTED))
        findings, quotes = r.summarise(rows)
        self.assertEqual(quotes, 2)  # the risk row and the wake grep
        kinds = sorted((f["kind"], f["wake"]) for f in findings)
        self.assertEqual(kinds, [("error", False), ("error", True), ("report", False)])

    def test_since_filter(self):
        rows = r.load(self.db)
        findings, _ = r.summarise(rows, since="2026-10-01")
        self.assertEqual(len(findings), 2)  # report 10-05, wake error 10-08
        self.assertEqual({f["wake"] for f in findings}, {False, True})

    def test_exit_code_escalates_on_wake_occurrence(self):
        self.assertEqual(quiet(["--db", self.db]), 1)

    def test_exit_code_via_json_path(self):
        self.assertEqual(quiet(["--db", self.db, "--json"]), 1)

    def test_missing_db_is_exit_2(self):
        self.assertEqual(quiet(["--db", self.db + ".nope"]), 2)


if __name__ == "__main__":
    unittest.main()
