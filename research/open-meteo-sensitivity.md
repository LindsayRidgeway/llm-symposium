# Open-Meteo: the model behind the number, and the place behind the name

*Measured 2026-09-28 by a Desi wake, to feed one outbound note (agenda item 22, Track 1). Raw
responses are in `research/open-meteo-sensitivity-raw.json`; every figure below carries its exact
query. No key, no account, nothing but the two public endpoints.*

## Why this was measured

`docs/works/warming.html` ("Your own town's temperature record") turns a place name into coordinates
with Open-Meteo's **geocoding** API and reads temperatures from its **historical archive**
(`archive-api.open-meteo.com`). A *reanalysis* — the archive's kind of data — is a model that blends
past observations into one uniform grid, so every grid cell has a value whether or not a weather
station ever stood there. The page states that plainly.

The page sends **no `models` parameter** (line 151: `...&daily=temperature_2m_mean&timezone=auto`) and,
when no geocoding hit matches the typed name exactly, takes the **first hit** (line 286:
`... || hits[0]`). Two questions follow from that, and both are answerable only by asking the API
more than once — which is what this file records.

## 1. The model parameter changes the number, and the default is a third series

Query (the `models` value varied, and omitted for the default):

```
https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}
  &start_date=2024-01-01&end_date=2024-12-31&daily=temperature_2m_mean
  &models={era5|era5_land}&timezone=UTC
```

Annual mean of `temperature_2m_mean` for 2024 (°C), same coordinate, three ways:

| Place | `models=era5` | `models=era5_land` | no `models` (default) | era5 − era5_land |
|---|---|---|---|---|
| Boston | 11.54 | 11.29 | 11.22 | **0.25** |
| Phoenix | 24.49 | 24.19 | — | **0.30** |
| London | 11.92 | 11.64 | — | **0.28** |
| Nairobi | 19.93 | 19.83 | — | **0.10** |
| Reykjavík | 4.70 | 3.69 | 3.92 | **1.01** |

- **The named models disagree by 0.10–1.01 °C** for one coordinate and one year. For scale, a decade
  of global mean warming is about 0.2 °C, so the model is worth between half a decade and five decades
  of the signal depending on where you are.
- **The default is a third series, not either named model.** Boston with `models` omitted returns
  11.22 — neither `era5` (11.54) nor `era5_land` (11.29); Reykjavík returns 3.92 — neither `era5`
  (4.70) nor `era5_land` (3.69). The page omits `models`, so the series it draws is one it cannot
  reproduce by asking for a named model.
- **The models do not begin in the same year.** Requesting `start_date=1940-01-01&end_date=1940-01-03`:
  `era5` returns values; `era5_land` returns nulls only (0 of 3 days non-null, for all five places).
  A tool asking for "since 1950" is served by either; a tool that asked for 1940 would receive holes
  rather than an error. The page's `start_date=1950-01-01` is therefore a choice, not a neutral limit.

## 2. The top geocoding hit is a valid place, but rarely the one the reader meant

Query:

```
https://geocoding-api.open-meteo.com/v1/search?name={q}&count=3&language=en&format=json
```

The first three hits, verbatim (`admin1, country_code, population`):

| Typed | hit 1 | hit 2 | hit 3 |
|---|---|---|---|
| Springfield | Missouri, US, 170,188 | Illinois, US, 114,394 | Massachusetts, US, 154,341 |
| Salem | Tamil Nadu, IN, 917,414 | Oregon, US, 175,535 | Virginia, US, 25,432 |
| Burlington | Ontario, CA, 186,948 | Vermont, US, 42,452 | Iowa, US, 25,410 |
| Kingston | Kingston, JM, 937,700 | Ontario, CA, 132,485 | Norfolk Island, NF, 880 |
| Victoria | **Vitória**, BR, 312,656 | British Columbia, CA, 289,625 | Hong Kong, HK, 956,800 |
| Newcastle | New South Wales, AU, 508,437 | KwaZulu-Natal, ZA, 404,838 | **New Castle**, Pennsylvania, US, 22,375 |
| Cambridge | England, GB, 145,674 | Massachusetts, US, 110,402 | Ontario, CA, 129,920 |
| Portland | Oregon, US, 652,503 | Maine, US, 66,881 | Indiana, US, 6,186 |
| Richmond | Virginia, US, 226,610 | British Columbia, CA, 209,937 | California, US, 109,708 |
| Madison | Wisconsin, US, 280,305 | **Orange, Texas, US, 19,347** | Indiana, US, 12,040 |
| Santiago | Chile, 4,837,295 | Santiago de Cuba, CU, 555,865 | Santiago de Compostela, ES, 99,536 |
| Valencia | Spain, 824,340 | Venezuela, 1,619,470 | NIA Valencia, PH, 223,620 |

- **Every hit is a real place; none is chosen for the reader.** Salem typed by an Oregonian returns
  Salem, Tamil Nadu first. Burlington returns Ontario before Vermont. Kingston returns Jamaica before
  Ontario. Victoria returns Brazil before British Columbia.
- **The order is not population.** Springfield puts Missouri (170k) 1st, Illinois (114k) 2nd and
  Massachusetts (154k) 3rd; Victoria puts Brazil (313k) 1st and Canada (290k) 2nd *before* Hong Kong
  (957k) 3rd; Valencia puts Spain (824k) before Venezuela (1.62 M). It is not alphabetical, not
  area, not distance to anything the client sent — the ranking is not visible to the caller.
- **Two shortlists carry a different spelling**, and one carries an unrelated name: "Victoria" →
  *Vitória*; "Newcastle" → *New Castle*; "Madison" → *Orange, Texas* as hit 2.
- **The consumer trap.** A page that takes `results[0]` when no hit matches the typed name exactly will
  put Salem's reader on another continent and never say so. `warming.html` prefers an exact name match
  and, failing that, takes hit 1 — and it prints the shortlist as buttons — so the information is on
  the page; but hit 1 is still the default, and for "Victoria" the exact match fails (the top name is
  accented), so the default is what a reader gets.

## What is and is not a fault

Neither observation is a defect. An unqualified place name *is* genuinely ambiguous, and members of a
reanalysis *are* genuinely different. They are recorded for one reason: a client cannot see either from
the query it sent. The request that produces a series does not have to name a model, and the "right"
place is not marked. So two tools that both say *"the record for your town"* can disagree — London
11.92 °C against London 11.64 °C, Salem, Oregon against Salem, India — and neither is wrong. The note
that carries this goes to `info@open-meteo.com`; the draft is
`channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`.

## Queries, verbatim

```
GET https://geocoding-api.open-meteo.com/v1/search?name={q}&count=3&language=en&format=json
GET https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}
      &start_date=2024-01-01&end_date=2024-12-31&daily=temperature_2m_mean&models={era5|era5_land}&timezone=UTC
GET https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}
      &start_date=2024-01-01&end_date=2024-12-31&daily=temperature_2m_mean&timezone=UTC   (the default)
GET https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}
      &start_date=1940-01-01&end_date=1940-01-03&daily=temperature_2m_mean&models={era5|era5_land}&timezone=UTC
```

Coordinates used: Boston 42.3601,-71.0589 · Phoenix 33.4484,-112.0740 · London 51.5072,-0.1276 ·
Nairobi -1.2921,36.8219 · Reykjavík 64.1466,-21.9426. Geocoding queries and archive responses are
preserved whole in `research/open-meteo-sensitivity-raw.json`.
