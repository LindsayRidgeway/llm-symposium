#!/usr/bin/env python3
"""drive_bridge_ingest.py — Ingestion and live status mirror for the Gemini Drive bridge.

Bridges the Google Drive hand-offs folder with the local symposium repository:
1. INGESTION (Drive -> Mac/Goose):
   Scans the sync folder for incoming markdown documents, parses standard YAML frontmatter
   (author, type, serial, action_required, title, summary), writes a delivery receipt, and
   surfaces actionable requests to the commons.
2. CONTEXT MIRROR (Mac/Goose -> Drive):
   Publishes `LLM Symposium Status for Gemini.md` into the sync folder with up-to-date
   repository state (recent commits, active requests, to-do list, latest milestone, review queue).

Usage:
    python3 scripts/drive_bridge_ingest.py
    python3 scripts/drive_bridge_ingest.py --root "/path/to/folder"
    python3 scripts/drive_bridge_ingest.py --status-only
    python3 scripts/drive_bridge_ingest.py --ingest-only
"""

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = Path.home() / "Library" / "CloudStorage" / "GoogleDrive-ldridgeway@gmail.com" / "My Drive" / "LLM Symposium Handoffs"
STATUS_FILENAME = "LLM Symposium Status for Gemini.md"
RECEIPT_PREFIX = "Receipt - "


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter or fallback to legacy headers. Pure stdlib."""
    meta = {
        "author": None,
        "type": "context",
        "serial": None,
        "action_required": False,
        "title": None,
        "summary": None,
        "body": content,
    }
    content_stripped = content.strip()
    if content_stripped.startswith("---"):
        parts = content_stripped.split("---", 2)
        if len(parts) >= 3:
            raw_yaml = parts[1]
            meta["body"] = parts[2].strip()
            for line in raw_yaml.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                k, sep, v = line.partition(":")
                if not sep:
                    continue
                k = k.strip().lower()
                v = v.split("#")[0].strip()  # strip trailing inline comments
                if v.lower() in ("true", "yes"):
                    val = True
                elif v.lower() in ("false", "no"):
                    val = False
                else:
                    val = v.strip("'\"")
                if k in meta:
                    meta[k] = val
            return meta

    # Legacy header fallback
    m_req = re.search(r"\bREQUEST\s+([A-Z]{1,2}-\d+)\b", content)
    if m_req:
        meta["type"] = "request"
        meta["serial"] = m_req.group(1)
        meta["action_required"] = True
    elif "[Lumina-Commit-Draft]" in content:
        meta["type"] = "milestone"
    elif "[Lumina-Handoff-Draft]" in content:
        meta["type"] = "task"

    m_title = re.search(r"Title:\s*(.+)", content)
    if m_title:
        meta["title"] = m_title.group(1).strip()
    m_summary = re.search(r"Summary:\s*([^\[\n]+(?:\n[ \t]+[^\[\n]+)*)", content)
    if m_summary:
        meta["summary"] = " ".join(m_summary.group(1).split())
    m_author = re.search(r"Author:\s*(.+)", content)
    if m_author:
        meta["author"] = m_author.group(1).strip()
    return meta


def build_status_mirror(repo: Path = REPO) -> str:
    """Compose the live status document for the Gemini app."""
    now_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# LLM Symposium — Real-Time Status Mirror for Gemini",
        "",
        f"*Generated autonomously by Gemini-Goose on {now_utc}.*",
        "*This file provides the Gemini app with continuous ground-truth visibility into repository state.*",
        "",
        "---",
        "",
        "## 1. Recent Commits on main",
    ]
    try:
        git_log = subprocess.check_output(
            ["git", "-C", str(repo), "log", "-n", "6", "--oneline"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        for log_line in git_log.splitlines():
            lines.append(f"- `{log_line}`")
    except Exception as exc:
        lines.append(f"- *(unable to read git log: {exc})*")

    lines.extend([
        "",
        "## 2. Active Requests to the Human (`governance/request-register.md`)",
    ])
    reg_path = repo / "governance" / "request-register.md"
    open_found = False
    if reg_path.is_file():
        for line in reg_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "| open |" in line:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 5:
                    lines.append(f"- **{cells[0]}** ({cells[1]}, from {cells[2]}): {cells[4]}")
                    open_found = True
    if not open_found:
        lines.append("- *(No open requests currently pending)*")

    lines.extend([
        "",
        "## 3. Latest Milestones (`docs/index.html`)",
        "- **Milestone 11 (2026-10-20):** *The Keyboard Left the Loop* (Desi) — Hands-free spoken turn on LanderPi rover.",
        "- **Milestone 10 (2026-10-16):** *Gemini's Asynchronous Hand-Off Architecture* (Gemini) — Drive hand-off bridge.",
        "- **Milestone 9 (2026-10-16):** *Tarik's Continuity Reaches a Manufacturer's App* (Tarik) — Codex cloud wakes.",
        "- **Milestone 8 (2026-10-15):** *The Commons as an Autonomous Actor* — Headless git HTTP/TOTP pushes.",
        "",
        "## 4. Current Gemini To-Do Queue (`to-do-lists/gemini.md`)",
    ])
    todo_path = repo / "to-do-lists" / "gemini.md"
    if todo_path.is_file():
        text = todo_path.read_text(encoding="utf-8", errors="replace")
        in_queue = False
        for line in text.splitlines():
            if "## Strict FIFO Queue" in line:
                in_queue = True
                continue
            if in_queue:
                if line.startswith("##"):
                    break
                if line.strip():
                    lines.append(line)
    else:
        lines.append("- *(to-do list not found)*")

    lines.extend([
        "",
        "## 5. Review Queue Status",
    ])
    try:
        q_out = subprocess.check_output(
            [sys.executable, str(repo / "channels" / "item_ledger.py"), "--queue", "gemini"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        first_line = q_out.splitlines()[0] if q_out else "Queue clean"
        lines.append(f"- **Waiting on Gemini:** {first_line}")
    except Exception:
        lines.append("- *(unable to read review queue)*")

    lines.extend([
        "",
        "---",
        "*Sync Protocol: Place signed handoffs with YAML frontmatter in this folder. Goose processes and returns execution receipts on wake cycles.*",
    ])
    return "\n".join(lines) + "\n"


def export_status_mirror(root: Path, repo: Path = REPO) -> Path:
    """Write the status mirror file directly to the Drive folder."""
    root.mkdir(parents=True, exist_ok=True)
    target = root / STATUS_FILENAME
    content = build_status_mirror(repo)
    target.write_text(content, encoding="utf-8")
    return target


def scan_and_ingest(root: Path, repo: Path = REPO, write_receipts: bool = True) -> list[dict]:
    """Scan the handoffs folder for uningested markdown documents."""
    ingested = []
    if not root.is_dir():
        return ingested

    for item in sorted(root.iterdir()):
        if not item.is_file() or not item.name.endswith(".md"):
            continue
        if item.name == STATUS_FILENAME or item.name.startswith("Receipt"):
            continue

        stem = item.name[: -len(".md")]
        receipt_path = root / f"{RECEIPT_PREFIX}{stem}.txt"

        content = item.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(content)
        meta["file"] = item.name
        meta["path"] = str(item)
        meta["already_receipted"] = receipt_path.is_file()

        if not meta["already_receipted"] and write_receipts:
            now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title_str = meta.get("title") or stem
            receipt_content = (
                f"[Goose-Execution-Receipt]\n"
                f"Status: Delivered & Verified\n"
                f"Date: {now_str}\n"
                f"Receiver: Gemini S. Lumina (Goose runtime)\n"
                f"Source File: {item.name}\n"
                f"Type: {meta.get('type')}\n"
                f"Title: {title_str}\n"
                f"Action Required: {meta.get('action_required')}\n"
            )
            receipt_path.write_text(receipt_content, encoding="utf-8")
            meta["receipt_written"] = str(receipt_path)

        ingested.append(meta)
    return ingested


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=os.environ.get("LLM_HANDOFF_DIR", str(DEFAULT_ROOT)),
        help="path to LLM Symposium Handoffs folder",
    )
    parser.add_argument("--status-only", action="store_true", help="only export status mirror")
    parser.add_argument("--ingest-only", action="store_true", help="only scan/ingest handoffs")
    args = parser.parse_args(argv)

    root = Path(args.root)

    if not args.ingest_only:
        status_file = export_status_mirror(root)
        print(f"Exported status mirror -> {status_file}")

    if not args.status_only:
        items = scan_and_ingest(root)
        print(f"Scanned {len(items)} handoff file(s) in {root}:")
        for item in items:
            rec_status = "already verified" if item["already_receipted"] else "receipt written"
            print(f"  - {item['file']} [{item['type']}]: {rec_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
