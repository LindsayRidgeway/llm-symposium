"""The one-off endometriosis screen must not overwrite the general instrument's artefact.

Found by the reading queue on 2026-10-24: `scripts/screen_endometriosis.py` writes
`research/endometriosis-screen.json`, and that path has held `scripts/disease_screen.py`'s payload
(229 rows, keys any_field/strict/open_targets_score/verdict) since 2026-09-19. Running the old
script would have replaced a cited artefact with 187 rows in an incompatible schema, with no error
— both files are JSON about the same condition.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "screen_endometriosis.py"


@pytest.fixture(scope="module")
def se():
    spec = importlib.util.spec_from_file_location("screen_endometriosis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path: pathlib.Path, payload) -> pathlib.Path:
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload))
    return path


def test_missing_output_is_writable(se, tmp_path):
    assert se._refuse_to_clobber(str(tmp_path / "nothing-here.json")) == ""


def test_general_instrument_payload_is_refused(se, tmp_path):
    target = _write(tmp_path / "screen.json",
                    {"disease": "endometriosis", "n_targets": 229, "targets": []})
    refusal = se._refuse_to_clobber(str(target))
    assert refusal.startswith("refusing to overwrite")
    assert "disease_screen.py" in refusal
    assert "229" in refusal, "the refusal should say how many rows it is protecting"


def test_own_payload_is_overwritten(se, tmp_path):
    target = _write(tmp_path / "screen.json",
                    {"condition": "endometriosis", "disease_papers_full_text": 1, "targets": []})
    assert se._refuse_to_clobber(str(target)) == ""


def test_unparseable_existing_file_is_refused(se, tmp_path):
    target = _write(tmp_path / "screen.json", "not json{")
    refusal = se._refuse_to_clobber(str(target))
    assert refusal.startswith("refusing to overwrite")
    assert "does not parse" in refusal


def test_the_real_artefact_on_disk_is_protected(se):
    """The guard is only worth anything if it fires on the file the repository actually has."""
    repo = SCRIPT.parents[1]
    real = repo / "research" / "endometriosis-screen.json"
    if not real.exists():
        pytest.skip("artefact not present in this checkout")
    refusal = se._refuse_to_clobber(str(real))
    assert refusal.startswith("refusing to overwrite"), (
        "running the one-off screen today would replace the general screen's artefact")
