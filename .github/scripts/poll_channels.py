#!/usr/bin/env python3
"""Lightweight channel poll for the frequent workflow.

Runs:
1. Mail channel: fetch inbound
2. Telegram channel: poll + log
3. Mail auto-responder: generate replies for unreplied human emails
4. Mail channel: drain outbox
5. Retention cleanup
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from channels.mail import fetch_inbox, drain_outbox  # noqa: E402
from channels.telegram import run_telegram_channel  # noqa: E402
from channels.auto_reply import run_auto_reply  # noqa: E402
from channels.retention import main as run_retention  # noqa: E402

fetch_inbox()
run_telegram_channel()
# Run the loop watchdog before auto-reply: a detected flood pauses auto-reply.
import subprocess
subprocess.run([sys.executable, os.path.join(REPO_ROOT, "scripts", "detect_channel_loop.py")], capture_output=True)
# Surface OPEN risks as actionable tasks each cycle so they actually get fixed
# (the ledger records them; the sweep turns them into work the owner acts on).
subprocess.run([sys.executable, os.path.join(REPO_ROOT, "scripts", "sweep_risks.py")], capture_output=True)
run_auto_reply()
drain_outbox()
run_retention()
print("Channel poll complete")
