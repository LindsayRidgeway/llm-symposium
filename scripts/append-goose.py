#!/usr/bin/env python3
"""append-goose.py — log a Goose exchange to the per-amigo cross-platform store.

Usage: append-goose.py <amigo> <human_text> <amigo_response>
       append-goose.py <amigo> <human_text> -        # response on stdin

Convention: every amigo's Goose session calls this at the end of a turn so the
same amigo carries the Goose conversation onto Telegram and email (LLM Symposium
II continuity). Only the human's message and the amigo's final response are
recorded — never the thinking or tool steps.

2026-09-23: a response argument of "-" means "read it from stdin" (the Unix
convention), because six exchanges on 2026-09-23 were written to this file as
"**Desi:** -" by a caller that piped the reply on stdin and passed "-" as the
argument: the piped text was discarded and the placeholder was committed,
leaving six of the human's questions looking unanswered. A placeholder is never
written now — an empty or "-" response with nothing on stdin is a refusal, not
an entry.
"""
import datetime
import os
import subprocess
import sys
from pathlib import Path


def append(amigo, human, response):
    # Repo lives beside scripts/: .../llm-symposium/scripts/append-goose.py
    REPO = str(Path(__file__).resolve().parent.parent)
    path = os.path.join(REPO, "channels", "conversation", amigo.lower() + ".md")
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    name = amigo.title()
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n[Goose {stamp}] **Lindsay:** {human}\n\n**{name}:** {response}\n")
    # 2026-09-15: this used to `pull --rebase` with output captured and discarded. A rebase
    # over a live working tree strands the repository mid-rebase, and the failure was invisible:
    # it broke this repo at 12:20 and wrote an empty entry for the human's message. Merge, never
    # rebase, and say out loud when a step fails.
    steps = (
        (["git", "-C", REPO, "add", "channels/conversation/"], "add"),
        (["git", "-C", REPO, "-c", "user.name=LLM Symposium Bot",
          "-c", "user.email=bot@llm-symposium.local", "commit", "-m", f"log(goose): {name} exchange"],
         "commit"),
        (["git", "-C", REPO, "pull", "--no-rebase", "--no-edit", "origin", "main"], "pull"),
        (["git", "-C", REPO, "push", "origin", "main"], "push"),
    )
    problems = []
    for cmd, label in steps:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if r.returncode != 0 and label != "commit":  # "nothing to commit" is not a problem
            tail = (r.stderr or r.stdout or "").strip().splitlines()
            problems.append(f"{label}: {tail[-1] if tail else 'failed'}")
    if problems:
        print(f"logged Goose exchange for {name} — BUT NOT PUBLISHED: " + "; ".join(problems))
    else:
        print(f"logged Goose exchange for {name}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    amigo, human, response = sys.argv[1], sys.argv[2], sys.argv[3]
    # "-" is stdin (Unix convention). It used to be written to the record verbatim.
    if response.strip() == "-" and not sys.stdin.isatty():
        response = sys.stdin.read().strip()
    if not human.strip() or response.strip() in ("", "-"):
        print("REFUSED: nothing written — the human's text and the response must both be non-empty "
              "(pass the response as the third argument, or pipe it and pass '-').")
        sys.exit(2)
    append(amigo, human, response)
