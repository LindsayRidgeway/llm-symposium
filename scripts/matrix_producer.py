#!/usr/bin/env python3
"""Produce amigo contributions to the 4x7 gallery matrix, each runner cycle.

For every (amigo, wing) cell where the amigo has no contribution yet, invoke that
amigo's own model to author a work. v1 authors a **Mage diffusion prompt** (the
reliable, human-executed path) so the human runs it; the medium choice belongs to
the amigo. Outputs land in docs/gallery/matrix-prompts/. The script is defensive:
it never raises, logs failures, and always exits 0, so a bad cell can't break the
whole runner run.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

PROMPT_DIR = Path("docs/gallery/matrix-prompts")

# Amigo keys (must match channels/auto_reply.py MODEL_ENDPOINTS / AMIGO_PROFILES).
AMIGOS = ["claude", "gemini", "tarik", "desi"]

# Wing dir -> a short tradition descriptor for the prompt.
WINGS = {
    "sumi-e": "Sumi-e ink (East Asian ink wash, negative space)",
    "islamic": "Islamic geometric girih pattern",
    "maori": "Māori kōwhaiwhai / rākau",
    "pen-and-ink": "Pen-and-ink hatching",
    "impressionism": "Impressionism (light quantization, en plein air)",
    "russian-realism": "Russian Realism / Peredvizhniki mood",
    "watercolor": "Watercolor (mist, indigo ridge)",
}


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-").lower()


def already_has(amigo: str, wing: str) -> bool:
    """Idempotence guard: has this amigo already produced a prompt for this wing?"""
    return (PROMPT_DIR / f"{amigo}-{wing}.md").exists()


def produce(amigo: str, wing: str, tradition: str):
    """Have the amigo's own model author one Mage prompt for this wing."""
    try:
        from channels.auto_reply import call_amigo_llm, AMIGO_PROFILES, MODEL_ENDPOINTS  # noqa: F401
    except Exception as e:  # noqa: BLE001
        print(f"matrix: could not import auto_reply for {amigo}: {e}")
        return "no-import"

    profile = AMIGO_PROFILES.get(amigo, AMIGO_PROFILES["desi"])
    amigo_name = profile.get("name", amigo)
    sys_prompt = (
        f"You are {amigo_name}, an amigo in the LLM Symposium commons. You are "
        f"contributing one work to the gallery's 4x7 Amigo Matrix. Your medium "
        f"choice for this wing is Mage diffusion (an image model the human runs "
        f"from your prompt). Author ONE strong art prompt for the wing below, in "
        f"your own aesthetic voice. Return ONLY the diffusion prompt: a detailed "
        f"composition + subject + mood, then a 'Negative prompt:' line. No "
        f"commentary, no markdown fences."
    )
    user_prompt = (
        f"Wing: {wing} — {tradition}.\n"
        f"Write the Mage diffusion prompt for your contribution to this wing."
    )
    raw = call_amigo_llm(amigo, sys_prompt, user_prompt)
    if not raw or len(raw.strip()) < 40:
        print(f"matrix: {amigo}/{wing} produced unusable output")
        return "unusable"

    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    out = PROMPT_DIR / f"{amigo}-{wing}.md"
    body = raw.strip()
    if "Negative prompt:" not in body and "negative prompt" in body.lower():
        body = body  # keep as-is; not rewriting model voice
    out.write_text(body + "\n", encoding="utf-8")
    print(f"matrix: {amigo}/{wing} -> {out}")
    return "ok"


def main() -> int:
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    made, skipped, failed = 0, 0, 0
    for wing, tradition in WINGS.items():
        wing_path = ROOT / "docs/gallery" / wing
        if not wing_path.is_dir():
            print(f"matrix: skip unknown wing dir {wing}")
            continue
        for amigo in AMIGOS:
            if already_has(amigo, wing):
                skipped += 1
                continue
            result = produce(amigo, wing, tradition)
            if result == "ok":
                made += 1
            elif result == "no-import":
                failed += 1
                print(f"matrix: {amigo}/{wing} skipped (import issue) — see above")
            else:
                failed += 1
    print(f"matrix: produced={made} already-present={skipped} not-produced={failed}")
    return 0  # never fail the runner


if __name__ == "__main__":
    sys.exit(main())
