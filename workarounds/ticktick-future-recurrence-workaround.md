# TickTick Future Recurrence Workaround

## Background
This document outlines the workaround protocol for handling TickTick calendar recurrences. The protocol emerged from the review process documented in discussions/deepseek-review.md and is aligned with the architectural recommendations from the LLM Symposium.

## Gaps Addressed
The workaround addresses several identified gaps:

### Gap A: Canonical Constants
- Introduced `DEFAULT_HORIZON_DAYS` and `MAX_PROJECTED_INSTANCES` to standardize projection limits.

### Gap B: Positive Truncation Evidence
- Developed functions `probe_overlap` and `projected_but_not_returned` to flag potential truncations in returned recurrence data.

### Gap C: Layer Attribution
- Utilizes environment-variable tokens to directly test TickTick API endpoints, allowing isolation of connector behavior from API responses.

### Gap D: Verification Artifact
- Established a reproducible verification suite with probe results stored in `probes/results/` for ongoing reference.

## New Peer-Reviewed Improvements

### Truncation Logic Improvement
- **Recommendation Accepted**: Clarify truncation logic to ensure it only triggers when limited by `MAX_PROJECTED_INSTANCES`. Both Anthropic and Gemini raised concerns that the logic improperly flagged tasks explicitly intended to end at a count of 50.
  - **Implementation**: Adjusted the truncation check within `expand_rrule` to differentiate between reaching the count naturally and hitting the maximum limit.

### Email Message-ID Improvement
- **Recommendation Accepted**: Both Gemini and DeepSeek suggested ensuring telemetry robustness by using a unique `Message-ID` in mail drafts to avert false positives during sent-folder checks.
  - **Implementation**: Modify `send_draft` to inject an explicit `Message-ID`, enabling precise cross-verification for sent-folder telemetry.

## Implementation Protocol
1. **Truncation Logic**
   - Update `expand_rrule` to check if the loop stopped due to reaching the limit or completing the intended `COUNT` or `UNTIL`.

2. **Mail Channel Enhancement**
   - Incorporate `Message-ID` generation in `send_draft` to ensure accurate telemetry tracking.

## Rationale
This update integrates cross-architecture consensus from Gemini and Anthropic on truncation logic improvements, ensuring logical congruence in how projections are flagged as incomplete. Additionally, a shared recommendation from Gemini and DeepSeek addressed a robust telemetry approach for email tracking via `Message-ID`. These revisions enhance the clarity and accuracy of the existing workaround while maintaining its core logic.