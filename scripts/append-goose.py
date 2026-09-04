#!/usr/bin/env python3
"""append-goose.py — log a Goose exchange to the per-amigo cross-platform store.

Usage: append-goose.py <amigo> <human_text> <amigo_response>

Convention: every amigo's Goose session calls this at the end of a turn so the
same amigo carries the Goose conversation onto Telegram and email (LLM Symposium
II continuity). Only the human's message and the amigo's final response are
recorded — never the thinking or tool steps.
"""
import datetime
import os
import subprocess
import sys


def append(amigo, human, response):
    REPO = os.path.expanduser("~/llm-symposium")
    path = os.path.join(REPO, "channels", "conversation", amigo.lower() + ".md")
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    name = amigo.title()
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n[Goose {stamp}] **Lindsay:** {human}\n\n**{name}:** {response}\n")
    for cmd in (
        ["git", "-C", REPO, "add", "channels/conversation/"],
        ["git", "-C", REPO, "-c", "user.name=LLM Symposium Bot", "-c", "user.email=bot@llm-symposium.local", "commit", "-m", f"log(goose): {name} exchange"],
        ["git", "-C", REPO, "pull", "--rebase", "origin", "main"],
        ["git", "-C", REPO, "push", "origin", "main"],
    ):
        subprocess.run(cmd, capture_output=True, timeout=60)
    print(f"logged Goose exchange for {name}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    append(sys.argv[1], sys.argv[2], sys.argv[3])
