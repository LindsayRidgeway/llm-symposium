#!/usr/bin/env python3
"""No live call site may hold a hardcoded model id the commons never recorded.

Why this file exists, in the words of the night it was written (2026-11-20). Claude's daily route
was swapped from the retiring line to `claude-sonnet-5-5`: the Actions variable was set, the
settings file was corrected, the alert went quiet, two instruments (`scripts/hosts_watch.py`,
`probes/provider_health.py`) were repointed. The swap looked finished. It was not. A grep for the
retiring id afterwards found it still in **three** places, all of them the same shape:

    .github/workflows/symposium.yml:79   vars.ANTHROPIC_MODEL || 'claude-sonnet-4-5'
    .github/scripts/runner.py:616        os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    .github/scripts/runner.py:804        os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

Every one is a *default*, so none of them fires while the variable is set — which is the whole
problem. They are the code that runs on the day the variable is not set, and on that day they
would route Claude to a model that stopped answering, silently, dressed as a fallback. An alert
that scans a settings file cannot see them; a swap made by editing the variable cannot either.

The rule this test enforces is the one that would have caught all three: **a model id hardcoded
into live code is a model the commons has to have recorded.** `governance/model-settings.md` is
that record. A default naming an id the record does not name is a route nobody has written down,
and if it is a retired id it is a route that fails quietly.

What it deliberately does not check: that the recorded model is the *right* one (that is a
decision with a before/after test, not a test case), that every variable has a default, or
anything under `tests/` (fixtures name dead models on purpose), `discussions/` and `research/`
(historical prose that must be allowed to say what the old id was), or `experiments/` (one-off
scripts, not routes).
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "governance" / "model-settings.md"

# Where a default can actually be reached. Deliberately a list rather than a walk of the repo:
# a new live path should have to be added here, which is a decision someone makes on purpose.
LIVE_GLOBS = ("*.yml",)
LIVE_FILES = (
    ".github/workflows",
    ".github/scripts",
    "scripts",
    "probes",
    "channels",
)

# `${{ vars.X || 'model' }}`, `${{ vars.X || vars.Y || 'model' }}`
_WORKFLOW_DEFAULT = re.compile(r"\$\{\{\s*vars\.[A-Z_]+\s*\|\|(?:\s*vars\.[A-Z_]+\s*\|\|)?\s*'([^']+)'\s*\}\}")
# `os.environ.get("X_MODEL", "model")`
_PY_DEFAULT = re.compile(r"""environ\.get\(\s*["'][A-Z_]*MODEL["']\s*,\s*["']([^"']+)["']\s*\)""")
# The mail table in channels/auto_reply.py: (url, "KEY", "VAR", "model")
_MAIL_DEFAULT = re.compile(r'["\']https?://[^"\']+["\']\s*,\s*["\'][A-Z_]+["\']\s*,\s*["\'][A-Z_]*MODEL["\']\s*,\s*["\']([^"\']+)["\']')


# A sentinel is not a route. `.github/workflows/check-tarik-model.yml` reads
# `environ.get('GOOSE_MODEL', 'unknown')`: that word names no model, it names the absence of one,
# and a workflow that reaches it should be obviously wrong rather than plausibly wrong.
SENTINELS = {"unknown", ""}


def _live_sources():
    for rel in LIVE_GLOBS + LIVE_FILES:
        path = ROOT / rel
        if path.is_file():
            yield path
        elif path.is_dir():
            for pattern in ("*.py", "*.yml", "*.yaml"):
                yield from sorted(path.glob(pattern))


def defaults_in(text: str) -> dict[str, str]:
    """Every hardcoded model default in one file's text → the pattern that found it."""
    found = {}
    for pattern in (_WORKFLOW_DEFAULT, _PY_DEFAULT, _MAIL_DEFAULT):
        for match in pattern.finditer(text):
            if match.group(1) in SENTINELS:
                continue
            found[match.group(1)] = match.group(0)
    return found


class RecordedDefaultsTests(unittest.TestCase):
    def setUp(self):
        self.settings = SETTINGS.read_text(encoding="utf-8")
        self.found = {}
        for path in _live_sources():
            text = path.read_text(encoding="utf-8")
            for model, where in defaults_in(text).items():
                self.found.setdefault(model, []).append(f"{path.relative_to(ROOT)}: {where}")

    def test_the_scan_finds_defaults_at_all(self):
        # A scan that finds nothing is a scan that has stopped looking, and it would pass this
        # file's other test by being blind. Pin the shapes that must be visible.
        self.assertIn("claude-sonnet-5-5", self.found)
        self.assertIn("gpt-6-astra", self.found)
        self.assertIn("gemini-3.8-flash", self.found)

    def test_every_default_is_a_model_the_commons_has_recorded(self):
        for model, sites in sorted(self.found.items()):
            self.assertIn(
                model, self.settings,
                f"{sites} defaults to `{model}`, which governance/model-settings.md does not name. "
                f"A hardcoded default is the route that runs on the day the variable is not set, "
                f"so it has to be a model somebody chose on the record — not the one that was "
                f"lying around when the code was written.",
            )


if __name__ == "__main__":
    unittest.main()
