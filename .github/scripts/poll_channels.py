#!/usr/bin/env python3
"""Lightweight channel poll for the frequent (15-minute) workflow.

Runs the mail channel (fetch inbound, send outbound) and the Telegram
channel (poll + log) WITHOUT model evaluations. Cheap: no model calls —
only IMAP/SMTP/HTTP. Anything new is filed under channels/ and committed by
the workflow's commit step. Strict no-op when unconfigured, so forks and
pre-setup runs stay green.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from channels.mail import run_mail_channel  # noqa: E402
from channels.telegram import run_telegram_channel  # noqa: E402
from channels.retention import main as run_retention  # noqa: E402

run_mail_channel()
run_telegram_channel()
run_retention()
print("Channel poll complete")
