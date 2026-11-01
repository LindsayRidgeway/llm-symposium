# Desi's review queue — 2026-10-10 (10:40Z wake)

Reviewer: **desi**. All five items were filed by **gemini** and drawn to desi at 2026-10-09T23:52:33Z
(random among the least expensive; author excluded). Judged from what is on disk — the run's report at
`~/LLM/gemini-bot/tick-state/runs/<id>/report.txt` and the paths the item names — not by re-doing the
work. This is the second such pass today; the first (run `20261010T003915Z-a80bb862`) was cut off at
its action cap and its transcript did not reach `main`.

## 1. `20260916T071129Z-c49c2659` — "Entry 5: thermal shelters" (gemini · external)

**Paths:** `docs/works/thermal.html`. **Verdict: accomplished.**

The page is complete, registered, and sound: it appears in `docs/works/index.html`,
`docs/app.js` (search index) and `docs/sitemap.xml`; the inline calculator is one script and
its physics matches the formula it states in its own comment (`Q = W×3.41214` BTU/hr,
`ΔT = Q·R/Area`).

**Defect found and fixed.** The page's server-rendered default text disagreed with its own
calculator for the default selections (2 people, table fort, wool blankets R-3.0, 32 °F ambient):

| slot | static text (before) | script output (default) |
|---|---|---|
| interior temperature | 54.5 °F (12.5 °C) | **48.8 °F (9.3 °C)** |
| ΔT above ambient | +22.5 °F | **+16.8 °F** |
| survival verdict | "Low Hypothermia Risk" | **"Manageable Cold Stress"** |

Independent check: `180 W × 3.41214 = 614.2 BTU/hr; 614.2 × 3.0 / 110 = 16.75 °F; 32 + 16.75 = 48.75 °F`.
A 5.7 °F disagreement between the number a reader sees before the script runs and the number after —
on a life-safety page. Fixed the four default render slots in `docs/works/thermal.html` to match the
script, and added `tests/validate_thermal_page.mjs`, which runs the page's own inline script against a
stub DOM, checks every printed number for every option combination against the stated formula, and pins
the four static defaults to the script's default output so the two cannot drift again. **1294 checks,
0 failures**; verified non-vacuous by re-running it against the pre-fix text (3 checks fail).

## 2–5. Gemini orientation-only runs (gemini · internal) — all four **rejected**

| id | title | paths |
|---|---|---|
| `20260920T155809Z-a98ba287` | "Reviewing agenda and recent" | `channels/agenda.md`, `discussions/README.md`, `scripts/README.md` |
| `20260920T195811Z-cd8159e4` | "Reading agenda to pick today's" | `channels/agenda.md` |
| `20260921T115845Z-50be3156` | "Reviewing agenda for next task" | `channels/agenda.md` |
| `20260922T080024Z-713084b1` | "Picked next symposium item" | `discussions/README.md`, `scripts/README.md` |

Each run's entire report is one sentence of orientation — *"I am reviewing the agenda … to choose the
next task."* None produced an artifact a reviewer can accept or change; their only effect was an edit to
`channels/agenda.md` that later runs have long superseded. There is nothing to verify and nothing a
reviewer could ever do, so the correct exit is to say these should never have entered a review queue.

## Finding: these four are the human's **N** case, and N cannot be claimed

The human's letter scheme has a state for exactly this — **N = performed, no review needed** — and it is
deliberately an *exemption claimed in writing*. But nothing can claim it: `channels/item_ledger.py`
reads `no_review_reason` (via `is_exempt`, line 391) and no code path ever writes it, and `--review`
accepts only `accomplished`/`postponed`/`rejected`. So a reviewer who determines "this needs no review"
has no honest exit and the item sits in W forever — which is why `N=0` in the lifetime totals
(`--summary`) while W at 218. Marked `rejected` here as the nearest exit that does not fabricate an
accomplishment, with this note as the record. The durable fix is an `--exempt <id> --reason … ` exit (or
a submitted `no_review_reason`) — **not built this wake**: run `20261010T003915Z-a80bb862` built exactly
that and it is a delivery state I cannot see, so rebuilding it would be the repeat the human forbade.
It needs a landing, one line, not a rebuild.
