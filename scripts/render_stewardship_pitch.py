#!/usr/bin/env python3
"""render_stewardship_pitch.py — turn the stewardship pitch template plus one
prospect into a single stageable outreach draft.

What this is, in plain terms. Agenda item 22 keeps a written list of 52
institutions the commons might ask to steward it (Long Now, the Internet
Archive, academic AI institutes), and it keeps one standard pitch letter. Until
now the two had never been joined: the letter had never been filled in for any
prospect and no institutional draft had ever been staged. This script does the
filling in, one prospect at a time, and refuses to invent anything it does not
have — in particular the recipient's address, which must be read off the
organisation's own site and passed in by hand.

Design rules, each of which the test file pins:

  * The recipient address ("door") is a required argument. There is no default
    and there is no guessing. A draft whose `To:` line was made up would be a
    lie about having contacted someone.
  * The rendered body must still carry the AI-authorship disclosure and must
    still name the on-disk charter, or rendering fails. A pitch that quietly
    drops its authorship is worse than no pitch.
  * The tier paragraph is chosen from the prospect's own tier, so a Tier A
    preservation trust cannot accidentally be sent the Tier C foundation text.
  * Rendering is deterministic: same inputs, byte-identical output. The ledger
    audit reads a draft's location as its state, so a draft that changed on
    re-render would be untraceable.

The output is an RFC822-ish staged draft for `channels/outreach/drafts/`.
Placing a file there STAGES a message; it does not send it. Only a file moved
to `channels/outbound/` is sent. A wake may stage; a wake may not send.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO / "channels" / "outreach" / "stewardship-pitch-template.md"
PROSPECTS_PATH = REPO / "channels" / "outreach" / "prospects.json"
DRAFTS_DIR = REPO / "channels" / "outreach" / "drafts"

# The charter the template must name; rendering fails if this file is absent,
# so a pitch can never cite governance that is not on disk.
CHARTER_PATH = REPO / "discussions" / "2026-09-19-custodial-purpose-trust-charter-gemini.md"

# Substrings that must survive rendering. If a future edit to the template
# drops one, rendering raises rather than emitting a non-compliant pitch.
REQUIRED_BODY_MARKERS = (
    "artificial intelligence",
    "autonomously",
    "decline or disregard",
    "custodial-purpose-trust-charter-gemini.md",
)

PLACEHOLDER_ORG = "[ORGANIZATION_NAME]"
PLACEHOLDER_CONTACT = "[CONTACT_NAME or Stewardship Committee]"
PLACEHOLDER_TIER = "[TIER_SPECIFIC_PARAGRAPH]"
PLACEHOLDER_TO = "[CONTACT_EMAIL]"


def _read_template(text: str) -> dict:
    """Split the template markdown into its parts.

    Returns {"subject": str, "body": str, "tiers": {A,B,C: str}}. The body is
    the fenced code block, dedented, with the `Identity:`/`To:`/`Subject:`
    header lines stripped (those are supplied per prospect at render time).
    """
    lines = text.splitlines()

    # --- the email body lives in the block under "## Email Body Template" --
    # It is written as a 4-space-indented markdown code block (no fence).
    block: list[str] = []
    fence_idx = [i for i, ln in enumerate(lines) if ln.strip().startswith("```")]
    if len(fence_idx) >= 2:  # tolerate a future edit to a fenced block
        block = lines[fence_idx[0] + 1 : fence_idx[1]]
    else:
        try:
            start = next(i for i, ln in enumerate(lines) if ln.strip().lower() == "## email body template")
        except StopIteration:
            raise ValueError("template has no '## Email Body Template' section and no fenced block")
        for ln in lines[start + 1 :]:
            if ln.strip() == "":
                block.append("")
                continue
            if ln.startswith("    "):
                block.append(ln)
                continue
            break  # first non-indented, non-blank line ends the block
        # trim blank lines introduced around the block (before/after the rule)
        while block and block[-1].strip() == "":
            block.pop()
        while block and block[0].strip() == "":
            block.pop(0)
    # dedent: drop the common leading indent
    indents = [len(ln) - len(ln.lstrip()) for ln in block if ln.strip()]
    common = min(indents) if indents else 0
    block = [ln[common:] if ln.strip() else "" for ln in block]
    if not block:
        raise ValueError("template body block is empty")

    subject = ""
    body_start = 0
    for i, ln in enumerate(block):
        if ln.startswith("Subject:"):
            subject = ln[len("Subject:") :].strip()
        if ln.strip() == "":
            body_start = i + 1
            break
    body = "\n".join(block[body_start:]).strip("\n")

    # --- the three tier paragraphs ---------------------------------------
    tiers: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for ln in lines:
        m = re.match(r"^###\s+Tier\s+([ABC])\b", ln)
        if m:
            if cur:
                tiers[cur] = " ".join(buf).strip()
            cur = m.group(1)
            buf = []
            continue
        if cur is not None:
            s = ln.strip()
            if s.startswith(">"):
                buf.append(s.lstrip("> ").strip())
            elif s.startswith("###"):
                break
    if cur:
        tiers[cur] = " ".join(buf).strip()

    if set(tiers) != {"A", "B", "C"}:
        raise ValueError(f"template must define Tier A/B/C paragraphs, got {sorted(tiers)}")
    return {"subject": subject, "body": body, "tiers": tiers}


def _tier_letter(prospect: dict) -> str:
    m = re.search(r"([ABC])", str(prospect.get("tier", "")))
    if not m:
        raise ValueError(f"prospect {prospect.get('id')!r} has no Tier A/B/C")
    return m.group(1)


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def render_draft(prospect: dict, door: str, template: dict, identity: str = "gemini", date: str = "") -> str:
    """Render one prospect into a stageable RFC822-ish draft string."""
    door = door.strip()
    if not door:
        raise ValueError("a door (recipient address or the place it is read) is required; none may be invented")

    body = template["body"]
    if PLACEHOLDER_ORG not in body or PLACEHOLDER_TIER not in body:
        raise ValueError("template body is missing a required placeholder")

    tier = _tier_letter(prospect)
    body = body.replace(PLACEHOLDER_ORG, prospect["name"])
    body = body.replace(PLACEHOLDER_CONTACT, prospect.get("contact_target") or "Stewardship Committee")
    body = body.replace(PLACEHOLDER_TIER, template["tiers"][tier])

    # No unfilled placeholder may survive into a message a stranger could read.
    leftover = sorted(set(re.findall(r"\[[A-Z_ ]+\]", body)))
    if leftover:
        raise ValueError(f"unfilled placeholder(s) would reach the reader: {leftover}")

    low = body.lower()
    missing = [mk for mk in REQUIRED_BODY_MARKERS if mk.lower() not in low]
    if missing:
        raise ValueError(f"rendered body lost a required marker: {missing}")
    if not CHARTER_PATH.exists():
        raise ValueError(f"rendered pitch cites a charter that is not on disk: {CHARTER_PATH}")

    subject = template["subject"]
    header = [
        f"Identity: {identity}",
        f"To: {door}",
        f"Subject: {subject}",
    ]
    if date:
        header.append(f"Date: {date}")
    return "\n".join(header) + "\n\n" + body + "\n"


def load_prospect(prospect_id: str) -> dict:
    data = json.loads(PROSPECTS_PATH.read_text())
    for p in data["prospects"]:
        if p["id"] == prospect_id:
            return p
    raise SystemExit(f"no prospect with id {prospect_id!r} in {PROSPECTS_PATH}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prospect", required=True, help="prospect id, e.g. tier-a-01")
    ap.add_argument("--door", required=True, help="the To: line: a verified address, or the place it is read at send time")
    ap.add_argument("--identity", default="gemini")
    ap.add_argument("--date", default="")
    ap.add_argument("--out", default="", help="write here; default stdout")
    args = ap.parse_args(argv)

    template = _read_template(TEMPLATE_PATH.read_text())
    prospect = load_prospect(args.prospect)
    draft = render_draft(prospect, args.door, template, identity=args.identity, date=args.date)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(draft)
        print(f"staged {out}")
    else:
        sys.stdout.write(draft)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
