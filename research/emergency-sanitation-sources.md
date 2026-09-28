# Emergency sanitation — the sources, read off the pages on 2026-09-28

**Why this file exists.** The Arcade entry `docs/works/sanitation.html` ("The Other Bucket") is a field
method, which means a person may act on it, possibly in an emergency, possibly where being wrong hurts.
So every figure on that page has to be traceable to a page that was actually fetched, on a stated date,
and nothing here is from memory. This note is that trail. It is the same discipline the water page uses
(`docs/works/water.html`) and the ORS page uses, applied to the one leg of the survival set the commons
never wrote down: what to do about human waste when the plumbing stops.

**The family this belongs to.** Three of the four household-survival methods are already built —
far it sits beside `water.html` (drinking water), `ors.html` (rehydration after diarrhoea already
started) and `thermal.html` (staying warm). Sanitation is the missing third of the water–sanitation–
hygiene triad, and it is the leg that *prevents* the diarrhoea the ORS page treats.

## Reachability, measured 2026-09-28

Every source below was requested with `curl -A Mozilla/5.0`. A refusal is recorded as a fact about
reachability, not a gap left silent — and the consequence is stated: no figure from a page we could not
fetch appears unlabelled anywhere.

| Source | URL | HTTP | Used for |
|---|---|---|---|
| WHO — Sanitation (fact sheet) | `https://www.who.int/news-room/fact-sheets/detail/sanitation` | **200** | burden-of-disease numbers |
| WHO — Drinking-water (fact sheet) | `https://www.who.int/news-room/fact-sheets/detail/drinking-water` | **200** | diarrhoeal-death number, second figure |
| Wikipedia — Emergency sanitation | `.../api/rest_v1/page/html/Emergency_sanitation` | **200** | the emergency-phase toilet options |
| Wikipedia — Pit latrine | `.../api/rest_v1/page/html/Pit_latrine` | **200** | siting distances, vent pipe |
| Wikipedia — Bucket toilet | `.../api/rest_v1/page/html/Bucket_toilet` | **200** | cover material, liners, fly control |
| Wikipedia — Hand washing | `.../api/rest_v1/page/html/Hand_washing` | **200** | 20-second rule, ash fallback |
| CDC (two emergency-sanitation paths) | `cdc.gov/sanitation/...`, `cdc.gov/healthywater/emergency/...` | **403** | not used — refused an automated fetch |
| FEMA / ready.gov (four paths) | `ready.gov/{sanitation,hygiene,emergency-sanitation}`, FEMA PDF | **404 / 403** | not used |
| Sphere Standards (handbook PDF) | `spherestandards.org/.../Sphere-Handbook-2018-EN.pdf` | **403** | the 1-toilet-per-20-people ratio could **not** be verified live, so it is **not stated** as a number on the page |
| UNHCR Emergency Handbook | `unhcr.org/emergency-handbook` | **403** | not used |

**Consequence, stated rather than buried.** The widely-cited emergency ratio "one toilet per 20 people"
is a Sphere/Humanitarian-Charter figure. Sphere refused this session's fetch, so that number is **not**
printed on the page as fact. What the page offers instead is the *design of the choice* (which toilet,
how far from water, how covered, how washed) and the WHO numbers it could read. A number we could not
verify does not go on a page a stranger might act on.

## The burden numbers (WHO Sanitation fact sheet, fetched 2026-09-28)

Quoted exactly, with the sentence around each:

- **"1.4 million people die each year as a result of inadequate drinking-water, sanitation and hygiene."**
- **"Unsafe sanitation accounts for 564 000 of these deaths, largely from diarrhoeal disease"** — and, the
  same sentence continues, "it is a major factor in several neglected tropical diseases, including
  intestinal worms, schistosomiasis and trachoma."
- **"Over 1.5 billion people still do not have basic sanitation services, such as private toilets or
  latrines. Of these, 419 million still defecate in the open"** (street gutters, bushes, open fields).
- **"Better water, sanitation, and hygiene could prevent the deaths among children aged under 5 years,
  395 000 in the year 2019."**

## The second burden figure, and why both are printed (WHO Drinking-water fact sheet, fetched 2026-09-28)

- **"Microbiologically contaminated drinking water … is estimated to cause approximately 505 000
  diarrhoeal deaths each year."**
- **"Some 1 million people are estimated to die each year from diarrhoea as a result of unsafe
  drinking-water, sanitation and hand hygiene."**

**The discrepancy, reported rather than smoothed.** WHO's sanitation page gives **1.4 million** WASH-
attributable deaths a year; WHO's drinking-water page gives **"some 1 million"**. These are different
measures, not a contradiction — the 1.4 million counts deaths from all WASH-attributable causes, the
1 million counts diarrhoea only — but a reader who meets one number and not the other cannot tell. The
page names both and says which is which. This is the same discipline as the water page's CDC-vs-EPA boil
discrepancy.

## Siting a pit or trench (Wikipedia "Pit latrine", fetched 2026-09-28)

Wikipedia is a secondary source; the numbers it carries are cited there to WHO/IRC guidance. Because the
primary (WHO/IRC, Sphere) refused this session's fetch, the page attributes these to the fetched page and
names the disagreement rather than presenting one figure as settled:

- **"As a very general guideline it is recommended that the bottom of the pit should be at least 2 metres
  above groundwater level, and a minimum horizontal distance of 30 metres between a pit and a water
  source is normally recommended to limit exposure to microbial contamination."**
- A **weaker**, separate guideline appears in the same article: **"The distance from water wells and
  surface water should be at least 10 m (30 ft) to decrease the risk of groundwater pollution."**
  → **10 m vs 30 m is a real disagreement in the sources.** The page prints both and says the 30 m figure
  is the one to hold to when the water is a drinking source; the 10 m figure protects the *well*, the
  30 m figure protects the *drinker* from microbial load.
- The article adds a condition that overrides distance: a **well-developed clay cover layer** plus a
  well-sealed well annulus makes a shorter separation sufficient — i.e. geology, not a magic number.
- Vent pipe: **internal diameter at least 110 mm**, reaching **more than 300 mm above the highest point
  of the toilet superstructure** (a fly-and-smell control, ordinary plumbing items).
- A single pit is typically **1 to 1.5 m** wide.

## The covered bucket (Wikipedia "Bucket toilet", fetched 2026-09-28)

- **Cover after every use** with one of: **quicklime, wood ash, finely crushed charcoal, or fine
  sawdust.**
- The liner method: **"the bag could be sealed with a knot and the bucket would remain fairly clean"** —
  a bag/liner keeps the container clean where water for washing it is short.
- Where there is no liner, place dry material in the base (newspaper, sawdust, leaves, straw) to ease
  emptying.
- Disposal: **"Some municipalities accept double/triple bagged waste in the trash can, much like the
  disposing of cat litter."** → the page tells the reader to **ask their own local authority first**, and
  says local rules win.
- **Flies:** **"Flies can access the contents unless it is kept securely covered."** → the lid is not
  cosmetic; it is the disease barrier.
- Urine diversion: a separate **"urine bucket"** whose "bottom … should be covered with water and emptied
  every day."

## Hands (Wikipedia "Hand washing", fetched 2026-09-28)

- **"WHO recommends washing hands for at least 20 seconds before and after certain activities."**
- The fallback, and its limit, in the article's own words: **"When neither hand washing nor using hand
  sanitizer is possible, hands can be cleaned with uncontaminated ash and clean water, although the
  benefits and risks are uncertain for reducing the spread of viral or bacterial infections."** → the
  page prints the ash fallback *with* that uncertainty attached, not as an endorsement.

## What the emergency-phase menu is (Wikipedia "Emergency sanitation", fetched 2026-09-28)

The article's own taxonomy for the first phase: the focus is on **managing open defecation**, and the
toilets available include **"very basic trench latrines, pit latrines, bucket toilets, container-based
toilets, chemical toilets"**, with **twin** bucket toilets used where one container is emptied while the
other is in use. This is the menu the page's decision section is built from.
