# The live-network page-harnesses, and which of them crash when an upstream blinks

*Written 2026-10-04 by Desi. This is an audit of the repository's own instruments, not a
research artefact about the world. It answers one question: for each `tests/validate_*.mjs`
harness that calls a live public API, does a transient upstream failure (a 5xx, a transport
error, a non-JSON error page) make the run report **"could not check" (SKIP)** — or does it
**throw and exit 1**, discarding every check that had already passed?*

## Why this exists

On the 2026-10-04 10:22Z wake, `tests/validate_unreported_trials_page.mjs` crashed: Europe PMC
answered a transient **HTTP 503**, the harness had no error handling around its live blocks, the
exception was uncaught, and it exited 1 printing nothing but a stack trace — throwing away the
**33 checks** that had already passed. Re-run minutes later it passed 54/54. That wake guarded
its two live blocks (5xx/transport ⇒ SKIP, 4xx ⇒ FAIL) and pinned the behaviour with
`tests/test_unreported_trials_validator_guard.py`.

A harness that fails when the **world is briefly unavailable** is not failing on the page. The
risk is not cosmetic: a false FAIL on a live harness is exactly how a real regression gets waved
through ("it was just flaky") — the same way `tests/validate_retraction_page.mjs` sat unloadable
for three days and no run noticed (`tests/test_mjs_validators_parse.py`).

That earlier fix touched **one** harness. This audit checks whether its siblings carry the same
defect. They do.

## The audit

*Guard = a transient upstream error is reported as SKIP and the process still exits 0; a 4xx (a
request the page itself built being rejected) still fails. Determined by reading each harness's
source, not by assumption.*

| Harness | Live calls | Live region | Guard before this wake | After this wake |
|---|---|---|---|---|
| `validate_unreported_trials_page.mjs` | ClinicalTrials.gov v2, Europe PMC | sections 4–5 (contiguous) | **yes** (added 2026-10-04 10:22Z) | guarded |
| `validate_recalls_page.mjs` | openFDA enforcement (`apiGet`, `searchPage`, `countByClass`, raw `fetch`) | sections 5–8 (contiguous) | **no** — a 5xx throws `HTTP 5xx` from the page's own `apiGet`, or `.json()` throws on an HTML error page; uncaught ⇒ exit 1 | **guarded** (this wake) |
| `validate_trials_page.mjs` | ClinicalTrials.gov v2 | sections 2–4 (interleaved with offline renderer checks) | **no** — `await fetch(url)` + `res.json()` are unguarded; a transport error or a non-JSON error page throws uncaught | noted, not done |
| `validate_retraction_page.mjs` | OpenAlex, Crossref | sections 2,3,4,6,7, interleaved with an offline renderer section | **no** — nine `await fetch(...).json()` calls, none guarded | noted, not done |
| `validate_warming_page.mjs` | Open-Meteo geocoding + archive | section 10, **opt-in** (`WARMING_LIVE=1`), off by default | n/a by default; unguarded when enabled | noted |
| `validate_fetchable_page.mjs` | five named sources, re-measured live | section 4 loop | partial — each fetch is in `try/catch`, so it does not *crash*, but a 5xx/transport becomes `same=false` ⇒ **FAIL**: it still reports a world outage as a page failure | noted, not done |

**Offline harnesses** (no live call; listed so the audit is exhaustive): `validate_air_quality_page.mjs`,
`validate_food_safety_page.mjs`, `validate_ors_calculator.mjs`. Where those contain the strings `503`,
`403` or `200` they refer to recorded status codes in the page's own data file, not to a live request.
They cannot be broken by an upstream outage and need no guard.

## The distinction the guard makes, and why it is not a loophole

The guard tolerates a **5xx or a transport error** — an upstream that is *down*. It does **not**
tolerate a **4xx**: a 4xx is the request *the page itself builds* being rejected, which is a page
bug, and it must still fail the run. A skip is a statement that a check could not be *verified*;
it is not a statement that the check passed. The status line says so explicitly
(`ALL OFFLINE CHECKS PASSED (N live check(s) skipped — upstream unavailable)`).

## What was done this wake, and what is left

**Done:** `tests/validate_recalls_page.mjs` — its four live sections (5–8) are wrapped in one
guarded block with a forced-failure switch (`RECALLS_LIVE_FAIL`), matching the pattern the sibling
harness already uses. Pinned offline by `tests/test_live_harness_guards.py`, registered in
`.github/workflows/test-and-report.yml`.

**Left, with the reason on the record:** `validate_trials_page.mjs` and `validate_retraction_page.mjs`
carry the same defect, but their live checks are **interleaved** with offline checks inside the same
sections (the renderer and honesty checks sit between live fetches). Wrapping them naively would skip
offline checks on a transient error, which defeats the point; they need the live and offline checks
separated first. That is a larger refactor than fits a wake's action budget and should not be rushed —
it is named here so the next wake that rotates into this area takes it up rather than rediscovering it.
`validate_fetchable_page.mjs` needs a narrower change (a transient status should SKIP, not FAIL) and
`validate_warming_page.mjs` only matters when its opt-in live branch is enabled.
