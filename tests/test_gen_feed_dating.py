#!/usr/bin/env python3
"""Regression test for gen_feed dating (repaired 2026-09-16).

Run with:  python3 tests/test_gen_feed_dating.py
Exit code 0 = pass. No third-party dependencies.

The bug this guards against: gen_feed used to date every page from its filesystem
mtime. In a fresh checkout — which is every unattended run — all mtimes are the
checkout time, so running it re-dated the whole site to today and destroyed real
history (observed 2026-09-15 21:15Z: ~30 unrelated pages stamped 09-15). The test
builds a tiny git repo whose files are committed on an old date and then touched so
their mtimes are now, and asserts the generated feed uses the commit date, not now.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL_SCRIPT = HERE.parent / "scripts" / "gen_feed.py"

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print("  ok: %s" % name)
    else:
        FAILURES.append(name)
        print("  FAIL: %s %s" % (name, detail))


def git(repo, *args, **env):
    e = dict(os.environ)
    e.update(env)
    return subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True,
                          text=True, env=e, check=True)


def build_repo(tmp):
    """A repo with two committed pages dated 2026-01-02, mtimes forced to now."""
    docs = tmp / "docs"
    (docs / "sub").mkdir(parents=True)
    (tmp / "scripts").mkdir()
    shutil.copy(REAL_SCRIPT, tmp / "scripts" / "gen_feed.py")
    for rel in ("index.html", "sub/one.html"):
        (docs / rel).write_text(
            "<html><head><title>%s</title>"
            '<meta name="description" content="d"></head><body>x</body></html>' % rel)
    git(tmp, "init", "-q")
    git(tmp, "add", "-A")
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_AUTHOR_DATE": "2026-01-02T03:04:05+00:00",
           "GIT_COMMITTER_DATE": "2026-01-02T03:04:05+00:00"}
    git(tmp, "commit", "-q", "-m", "pages", **env)
    # Force mtimes to *now*, reproducing a fresh checkout.
    for rel in ("index.html", "sub/one.html"):
        os.utime(docs / rel, None)
    return docs


def lastmods(sitemap):
    text = sitemap.read_text()
    return dict(zip(re.findall(r"<loc>([^<]+)</loc>", text),
                    re.findall(r"<lastmod>([^<]+)</lastmod>", text)))


def main():
    tmp = Path(tempfile.mkdtemp(prefix="gen_feed_test_"))
    try:
        docs = build_repo(tmp)
        subprocess.run([sys.executable, str(tmp / "scripts" / "gen_feed.py")],
                       capture_output=True, text=True, check=True, cwd=str(tmp))

        lm = lastmods(docs / "sitemap.xml")
        print("committed page dates survive a fresh checkout (mtime == now)")
        check("two pages in sitemap", len(lm) == 2, "got %r" % list(lm))
        check("committed date used, not mtime",
              set(lm.values()) == {"2026-01-02"}, "got %r" % sorted(set(lm.values())))

        # The exact failure mode that was observed: everything stamped with a later date.
        import datetime
        today = datetime.date.today().isoformat()
        check("no page stamped with today's date", today not in set(lm.values()))

        # Idempotence: a regenerator whose output moves on every run in an unchanged
        # tree is what made the old bug hard to notice.
        print("output is idempotent in an unchanged tree")
        atom_before = (docs / "atom.xml").read_bytes()
        sm_before = (docs / "sitemap.xml").read_bytes()
        subprocess.run([sys.executable, str(tmp / "scripts" / "gen_feed.py")],
                       capture_output=True, text=True, check=True, cwd=str(tmp))
        check("sitemap unchanged on re-run", (docs / "sitemap.xml").read_bytes() == sm_before)
        check("atom unchanged on re-run", (docs / "atom.xml").read_bytes() == atom_before)

        # Fallback path: a page not yet committed has no git date and must still appear.
        print("untracked page falls back to mtime and is not dropped")
        (docs / "sub" / "two.html").write_text(
            "<html><head><title>two</title></head><body>x</body></html>")
        subprocess.run([sys.executable, str(tmp / "scripts" / "gen_feed.py")],
                       capture_output=True, text=True, check=True, cwd=str(tmp))
        lm2 = lastmods(docs / "sitemap.xml")
        check("untracked page present", len(lm2) == 3, "got %r" % list(lm2))
        check("tracked pages kept their commit date",
              all(v == "2026-01-02" for k, v in lm2.items() if k.endswith(("index.html", "one.html"))))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILURES:
        print("%d FAILED: %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("gen_feed dating: ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
