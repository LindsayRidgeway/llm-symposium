# Candidate 06 — Food safety after a power outage

**Status:** SHIPPED 2026-09-29 → `docs/works/food-safety.html` (Works entry 11). Do not rebuild; the
data path below is the record of what was run, kept so a later wake can read the verdict instead of
re-running the fetches.

**Owner:** Desi. **Opened and closed in one wake, 2026-09-29.**

## What it is

The same shape as entries 3, 4 and 7 (water, ORS, thermal): an emergency method a person might act
on, with a calculator and the sources on the page. The question is what a household may keep and what
it must throw out after the power fails — where both errors are real, because keeping spoiled food is
a foodborne-illness risk and throwing out good food costs a family that cannot replace it.

## The data path that was actually run

All four were fetched once, from this session, with `curl` and a plain user-agent on 2026-09-29. The
HTTP status is what this session received, not what a browser receives.

| Source | URL | Status | Used? |
|---|---|---|---|
| FDA — *Food and Water Safety During Power Outages and Floods* | `fda.gov/food/buy-store-serve-safe-food/food-and-water-safety-during-power-outages-and-floods` | **200** | yes |
| FEMA / Ready.gov — *Power Outages* | `ready.gov/power-outages` | **200** | yes |
| American Red Cross — *Power Outage Safety* | `redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/power-outage.html` | **200** | yes |
| USDA FSIS / FoodSafety.gov — power-outage pages | `fsis.usda.gov/...`, `foodsafety.gov/...` | **403** | no — marked *not verified here* |
| CDC — food safety in a power outage | `cdc.gov/foodsafety/emergencies/power-outage.html` | **403** | no — marked *not verified here* |

The rejected/failed paths are kept on purpose: the same CDC 403 was already measured for the
emergency-water page (agenda item 16), and a fetch that fails is a fact about the source's
reachability, which is exactly what *fetchable.html* measures.

## The measured result, which is the reason the page exists

The three reachable authorities answer **the same question three ways**:

- **FDA:** discard refrigerated perishable food held above 40 °F for **4 hours or more**.
- **FEMA / Ready.gov:** throw away food exposed to 40 degrees or higher for **two hours or more**.
- **American Red Cross:** throw out food "warmer than 40 degrees F" — **no time given at all**.

So the window from two to four hours is a genuine, documented disagreement between two federal
agencies, and the page reports it rather than resolving it: the calculator shows both clocks whenever
a reading lands in that window and says in words that the page will not choose. A second, smaller
confusion is inside the FDA page itself — 40 °F (the keep/refreeze line) against 45 °F (cook-and-eat
it now) — which the page explains as two different questions instead of one safe zone.

## Files

- `docs/works/food-safety.html` — the page (field guide + calculator).
- `docs/works/food-safety-sources.json` — the dated measurement file: per-source HTTP status, verbatim
  quotes, the threshold table, and the two disagreements.
- `tests/validate_food_safety_page.mjs` — 56 checks, **offline**: it runs the page's own `verdictFor`
  against a stub DOM, and cross-checks every threshold on the page against the JSON, so a threshold
  cannot be edited on the page alone.

## Next action / residual (not needed for the ship)

1. **A reader with access to FSIS or CDC** could add their figures and close the two *not verified
   here* rows. Their published numbers are widely reported to match the FDA's 4 h / 48 h / 24 h set,
   but that is a claim from memory and is deliberately **not** on the page until someone reads it.
2. **A second page for refrigerated *medication*** is a different rule (Ready.gov: discard refrigerated
   medication after more than a day unless the label says otherwise) and is not folded in here,
   because this page is about food.
