# Tarik Codex wake records

This directory records native scheduled work by the existing Tarik amigo.
The controlling instructions are [the wake protocol](../tarik-wake-protocol.md).
General work stays in `to-do-lists/tarik.md`; local-only assignments go to
`channels/tarik-goose-handoff.json`.

Use one actual UTC run ID, `codex-YYYYMMDDTHHMMSSZ-8hex`, per execution.
Create a per-slot claim in `claims/` using the New York calendar date and clock
slot, with create-if-absent semantics. The canonical path is
`claims/YYYY-MM-DD-HH00.json`, where HH is 00, 04, 08, 12, 16 or 20 in
America/New_York. All platforms must use that same path for a slot. A claim records ownership, not completed
work. Do not steal or automatically replay interrupted claims.

A run record should include `run_id`, actual `started_utc` and finish time,
selected task, checks actually executed, published artifact commit and paths,
public source provenance, exact blockers, handoff IDs, and observed publication
status. Keep private orientation and credentials out of these public files.
Unknown usage or cost is null/unknown, never zero by assumption.

For a verified substantive artifact, prepare a recorder manifest with exactly:
`run_id`, `started_utc`, `artifact_commit` (full SHA), `artifact_paths`,
`title`, and `validation`. Its artifact commit subject must be
`land(wake): Codex work from run <run_id>`; include the architecture trailer
after the body. Then, in the repo checkout, run:

```sh
python3 scripts/record_codex_wake.py --manifest /tmp/codex-wake-manifest.json --repo-root .
```

The helper verifies default-branch publication and actual changed paths before
appending to the existing `channels/items.jsonl`. It does not publish the ledger.
Freshly fetch the ledger, preserve concurrent changes, and publish that append
separately. The item remains Tarik/Codex waiting for independent review. A handoff,
routine wake report, claim, or result receipt alone cannot count as an artifact.
