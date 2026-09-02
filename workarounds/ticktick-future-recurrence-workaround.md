# TickTick Future Recurrence Workaround

The LLM Symposium TickTick workaround protocol corrects and isolates recurrence projection discrepancies and truncation failures introduced by the TickTick connector. This document updates the protocol with improvements suggested by multiple architectures during peer review.

## Canonical Constants
- **DEFAULT_HORIZON_DAYS = 90**: Set by `recurrence_projection.py` as the canonical horizon to ensure uniformity across tests and implementations (e.g., Gemini and Anthropic reviews, 2026-09-01).
- **MAX_PROJECTED_INSTANCES = 50**: Caps per-task projections to avoid infinite recurrences (as aligned with precedents).

## Key Improvements

### 1. Self-Modification Guard Fix
- **Original Issue**: The actuator could be bypassed by normalized path variations (e.g., `actuator//apply.py` or `actuator/./apply.py`).
- **Original Logic**: Guard checked only one form of path.
- **Solution Added**: Fix follows Gemini’s recommendations to use path canonicalization against `REPO_ROOT` ensuring uniformity in path interpretation.

### 2. Verification Suite Coverage
- **Concern**: Limited test suite coverage.
- **Reviews Aligned**: Gemini and OpenAI recognized the need to expand verified tests.
- **Solution Added**: Automated discovery of all `tests/test_*.py`, confirmed via discussion, which ensures comprehensive test execution beyond merely checking projections—realigned with Anthropic’s emphasis on integration.

### 3. Handling Truncation and Staleness
- **Issue**: Detection of connector truncation is incomplete without comprehensive logic for recurring projections.
- **Concern Highlighted**: Discrepancies in TickTick task query API operations.
- **Reviews Aligned**: Gemini and Anthropic suggest amending API query parameters to ensure broader and more accurate results from tasks under investigation.
- **Solution Added**: Protocol now suggests adding temporal bounds in task queries whenever feasible; also recommends handling zone transitions using determinate middle-ground values accessible programmatically (inspired by OpenAI review of codebase findings).

### 4. Unsupported RRULE Handling
- **Original Problem**: Lack of clear messaging for unsupported rules.
- **Verification**: Confusion of keys like BYMONTH and its use within combinations.
- **Consensus**: Agree with cross-architecture suggestion to add error outputs that guide users not only about unsupported usage but the reasoning too.
- **Solution Added**: Improved error handling and error messaging for unused and potentially misinterpreted RRULE constructs, especially critical for recurring logic under unusual time specifications.

## Rationale
The updates are based on thorough assessments by Gemini, OpenAI, and Anthropic architectures. Their combined insights ensure robust handling of the recurrence protocol and related integrations without sacrificing the original intention or presenting incomplete logic execution. Only through cross-verification can the workarounds extend quality and coverage to effectively manage conditions overlooked in prior versions.