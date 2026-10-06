#!/usr/bin/env python3
"""Static guard: the DeepSeek key is per-amigo, and the cloud workflows must say so.

Since 2026-10-05 two DeepSeek instances (Desi and Dmitri) hold separate keys, named to match each
bot's `bot.env` — the human's convention: an ALL-CAPS env name matches the GitHub secret of the
same name. The code (`channels/auto_reply.py`, `.github/scripts/runner.py`) and Goose still read
the *plain* `DEEPSEEK_API_KEY`, so every workflow that exports it must bind it from the per-amigo
secret of the DeepSeek voice it speaks as, keeping the generic name only as a fallback.

Why this is a test and not a comment: the regression is silent. `symposium.yml` and
`channel-poll.yml` were both retired from cron on 2026-09-25 and now run only on
`workflow_dispatch`, so a key name that drifted out of sync with the secrets would not fail loudly
until the day the cloud is revived — and then it would fail as "the reasoning engine isn't
configured", not as a name mismatch. This test turns that day into now. No network.
"""
from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

# The workflows that export the plain variable the code reads.
DEEPSEEK_WORKFLOWS = ("symposium.yml", "channel-poll.yml")

BINDING_RE = re.compile(r"^\s*DEEPSEEK_API_KEY:\s*(?P<value>.+?)\s*$")


def _deepseek_binding(name: str):
    """The `DEEPSEEK_API_KEY:` value in a workflow, or None. Comments cannot match: a comment
    that names `DEEPSEEK_API_KEY_DESI` has no colon directly after `DEEPSEEK_API_KEY`."""
    for line in (WORKFLOWS / name).read_text().splitlines():
        m = BINDING_RE.match(line)
        if m:
            return m.group("value")
    return None


def _deepseek_identity() -> str:
    """The amigo the repo wires to DEEPSEEK_API_KEY (channels/auto_reply.py: MODEL_ENDPOINTS)."""
    tree = ast.parse((ROOT / "channels" / "auto_reply.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "MODEL_ENDPOINTS":
            table = ast.literal_eval(node.value)
            return next(ident for ident, row in table.items() if "DEEPSEEK_API_KEY" in row)
    raise AssertionError("MODEL_ENDPOINTS not found in channels/auto_reply.py")


class DeepSeekKeyRepointTests(unittest.TestCase):
    def test_exactly_one_deepseek_voice_in_repo(self):
        tree = ast.parse((ROOT / "channels" / "auto_reply.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "MODEL_ENDPOINTS":
                table = ast.literal_eval(node.value)
                voices = [i for i, row in table.items() if "DEEPSEEK_API_KEY" in row]
                self.assertEqual(len(voices), 1, "exactly one identity should speak DeepSeek")
                return
        self.fail("MODEL_ENDPOINTS not found")

    def test_workflows_bind_the_per_amigo_secret(self):
        expected = "secrets.DEEPSEEK_API_KEY_" + _deepseek_identity().upper()
        for name in DEEPSEEK_WORKFLOWS:
            value = _deepseek_binding(name)
            self.assertIsNotNone(value, f"{name}: no DEEPSEEK_API_KEY binding found")
            self.assertIn(expected, value, f"{name}: DEEPSEEK_API_KEY must bind from {expected}")
            self.assertRegex(
                value,
                r"\|\|\s*secrets\.DEEPSEEK_API_KEY\s*\}\}",
                f"{name}: keep the generic secret as a fallback so deleting it is a separate step",
            )
            self.assertNotEqual(
                value.strip(),
                "${{ secrets.DEEPSEEK_API_KEY }}",
                f"{name}: a generic-only binding reintroduces the ambiguity the split removed",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
