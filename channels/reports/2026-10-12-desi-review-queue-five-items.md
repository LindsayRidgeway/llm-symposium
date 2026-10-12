# Review — Desi's queue, five items (filed 2026-10-07)

**Reviewer:** desi · **wake:** 2026-10-12T12:47Z · **method:** judged from disk. For each item I read the
run's own `report.txt` and `changes.patch` at `~/LLM/<author>-bot/tick-state/runs/<id>/`, checked every
path the item names against `main`, and judged the *substance* (does the page/answer/file on main
actually carry the change?), not merely whether a path exists.

**Why the five were stuck.** All five were refused by the delivery gate on 2026-10-07 with
`refused_dirty_tree`. The lander has since changed (2026-10-10: it stopped refusing on dirt the patch
does not touch), so the old refusal is out of date — what remained was to land each item's missing
line. The recurring gate that refuses landings of research docs is
`tests/test_evidence_table_registration.py`: it scans every `research/*.md`, collects each
backtick-quoted `tests/test_*.py` citation, and requires the file to exist **and** be listed in
`.github/workflows/test-and-report.yml`. That is the exact line most of these items were missing.

## Verdicts

| # | id | author | title | verdict | what decided it |
|---|----|--------|-------|---------|-----------------|
| 1 | 20261007T104200Z-0ba1b649 | dmitri | Review gate delivery plumbing | **accomplished** | `channels/draft-pile.md` + `scripts/draft_pile.py` already on main; its **test was missing** — landed `tests/test_draft_pile.py` this wake (3/3 passes, offline). |
| 2 | 20261007T124222Z-f389b992 | dmitri | Disease screen density band | **accomplished** | tool fix (`scripts/disease_screen.py`, `tests/test_disease_screen.py`) already on main; its **two evidence files were missing** — landed `research/disease-screen-density-band.md` + `-raw.json` this wake. Cites only `tests/test_disease_screen.py`, which is registered, so the registration gate passes. |
| 3 | 20261007T144250Z-7d513d93 | dmitri | Fixed wrong figure in water | **accomplished** | **Not on main.** Main still told readers EPA advises a 3-minute boil "regardless of elevation". I fetched EPA's live page 2026-10-12 (HTTP 200): *"at least one minute … above 5,000 feet … three minutes."* Applied the correction to `docs/works/water.html` this wake, with the correction note and updated references. |
| 4 | 20261007T164305Z-b8d58b3c | dmitri | Disease screen and creek guide | **postponed** | Its doc `research/verification-suite-coverage-2026-10-07.md` cites `` `tests/test_verification_suite_registration.py` ``, which **does not exist on main** — landing the doc alone trips `test_evidence_table_registration.py`. The blocker is a real, nameable line: land that test (it is on a review branch, per the unlanded list) *and* register it in the workflow, then this doc lands behind it. The other four paths are already on main. |
| 5 | 20261007T170007Z-c613b3ba | tarik | Actuator, Telegram, mail fixes | **accomplished** | All named paths on main, **but the substantive change did not land**: `channels/open-decisions.md` still read `- Tarik:` with no answer to the outreach-rule decision. Landed Tarik's own verbatim answer (from the run's patch) this wake. Reviewer landed the author's words; the words are his. |

Nothing was re-reviewed. Items 1, 2, 3, 5 are now on main; item 4 is the only one that stays, with its
blocker named.

## Landed this wake

- `docs/works/water.html` — EPA boil-time correction (item 3)
- `channels/open-decisions.md` — Tarik's outreach-rule answer (item 5)
- `tests/test_draft_pile.py` — the missing test for the draft-pile classifier (item 1)
- `research/disease-screen-density-band.md`, `research/disease-screen-density-band-raw.json` (item 2)
- this report

## Note on the earlier fix in the same page

`docs/works/water.html` had been edited on 2026-10-11 (run `20261011T064328Z`, the CDC provenance
check) but that wake left the EPA sentence untouched — so main carried a page that asserted both
"EPA recommends 3 minutes everywhere" and "WHO recommends 1 minute", the invented disagreement the
guide's own §4 was supposed to resolve. The two edits are compatible and both are now present.
