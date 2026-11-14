"""Two windows with the same title on the same day must not overwrite each other.

Found 2026-11-14 while landing one window: `--mine` landed sixty-odd old windows, most of them named
`cli-session`, and every second one wrote on top of the one before it. The INDEX kept a row per window,
so the record said all of them were kept while one file held one of them. This is the test that would
have caught it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


def _load():
    spec = importlib.util.spec_from_file_location(
        "window_land", Path(__file__).resolve().parent.parent / "scripts" / "window_land.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _row(sid, name="cli-session", day="2026-11-11"):
    return {
        "id": sid,
        "name": name,
        "created_at": f"{day} 09:00:00",
        "updated_at": f"{day} 10:00:00",
        "provider_name": "custom_deepseek",
        "accumulated_total_tokens": 1000,
        "working_dir": "/Users/x",
        "description": None,
    }


def _write(path: Path, sid: str) -> None:
    path.write_text(f"# Window\n\n| | |\n|---|---|\n| session | `{sid}` |\n", encoding="utf-8")


def test_same_title_same_day_gets_its_own_file(tmp_path):
    wl = _load()
    a = tmp_path / wl.window_path(tmp_path, _row("20261111_1")).name
    assert a.name == "2026-11-11-cli-session.md"

    _write(a, "20261111_1")
    b = wl.window_path(tmp_path, _row("20261111_2"))
    assert b != a and b.name == "2026-11-11-cli-session-2.md"

    _write(b, "20261111_2")
    c = wl.window_path(tmp_path, _row("20261111_3"))
    assert c.name == "2026-11-11-cli-session-3.md"


def test_relanding_a_window_still_overwrites_its_own_file(tmp_path):
    wl = _load()
    a = wl.window_path(tmp_path, _row("20261111_1"))
    _write(a, "20261111_1")
    assert wl.window_path(tmp_path, _row("20261111_1")) == a

    # and a later window of the same name does not adopt it
    assert wl.window_path(tmp_path, _row("20261111_9")) != a


def test_different_titles_do_not_share(tmp_path):
    wl = _load()
    p1 = wl.window_path(tmp_path, _row("20261111_1", name="AITRobot #01"))
    p2 = wl.window_path(tmp_path, _row("20261111_2", name="Something else"))
    assert p1 != p2
    assert p1.name == "2026-11-11-aitrobot-01.md"
