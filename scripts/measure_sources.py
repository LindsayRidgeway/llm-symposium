#!/usr/bin/env python3
"""Measure, rather than assert, what public data a browser can actually reach.

Works entry 6 ("What a page can actually fetch"). Each source is asked three separate
questions, and the answers are not the same question:

  1. DOES IT ANSWER WITHOUT A KEY?  — an anonymous request, no credentials of any kind.
  2. CAN A WEB PAGE READ IT?        — CORS. Measured by sending an Origin header and looking
                                      for `access-control-allow-origin`. This is the one that
                                      actually decides whether a page like this one can use it,
                                      and it is invisible to a server-side script, which is why
                                      "you can curl it" is not the same claim.
  3. DID DATA COME BACK?            — a byte count and the first non-space characters, so a
                                      200 with an empty body or an error page cannot pass.

The page repeats the same three checks live in the reader's browser, which is the only place
CORS question 2 is finally settled. Key-required sources are kept in the list on purpose: a
catalogue that contains only successes measures nothing.

Usage:  python3 scripts/measure_sources.py            (writes docs/works/fetchable-sources.json)
"""
from __future__ import annotations

import datetime
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "works",
                   "fetchable-sources.json")
ORIGIN = "https://lindsayridgeway.github.io"
UA = "Mozilla/5.0 (LLM Symposium works-page measurement; +https://lindsayridgeway.github.io/llm-symposium/)"

# name, field, what it holds, sample request, whether a key is needed *as advertised*
SOURCES = [
    # --- health and biomedicine ---
    ("ClinicalTrials.gov", "health", "Every registered clinical trial, worldwide",
     "https://clinicaltrials.gov/api/v2/studies?query.cond=melanoma&pageSize=1", False),
    ("PubMed (E-utilities)", "health", "35M+ biomedical abstracts and citations",
     "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=melanoma&retmode=json&retmax=1", False),
    ("Europe PMC", "health", "Life-science literature with full text for open articles",
     "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=melanoma&format=json&pageSize=1", False),
    ("openFDA", "health", "US drug adverse-event reports and recalls",
     "https://api.fda.gov/drug/event.json?limit=1", False),
    ("WHO Global Health Observatory", "health", "WHO's country health statistics",
     "https://ghoapi.azureedge.net/api/Indicator?$top=1", False),
    ("UniProt", "health", "Protein sequences and function annotations",
     "https://rest.uniprot.org/uniprotkb/search?query=p53&size=1&format=json", False),
    ("RCSB Protein Data Bank", "health", "3D structures of proteins and nucleic acids",
     "https://data.rcsb.org/rest/v1/core/entry/1crn", False),
    ("ChEMBL", "health", "Bioactive molecules and their measured activities",
     "https://www.ebi.ac.uk/chembl/api/data/molecule.json?limit=1", False),
    ("PubChem", "health", "Chemical compounds and their properties",
     "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/property/MolecularFormula/JSON", False),
    ("Ensembl", "health", "Genomes and gene annotations",
     "https://rest.ensembl.org/info/ping?content-type=application/json", False),
    ("NHANES-style CDC WONDER", "health", "US population health statistics (query form, not API)",
     "https://wonder.cdc.gov/", False),

    # --- scholarly record ---
    ("Crossref", "scholarly", "DOIs and metadata for 150M+ published works",
     "https://api.crossref.org/works?rows=1&query=malaria", False),
    ("OpenAlex", "scholarly", "The scholarly graph: works, authors, institutions",
     "https://api.openalex.org/works?per-page=1&search=malaria", False),
    ("arXiv", "scholarly", "Preprints in physics, maths, computing, biology",
     "https://export.arxiv.org/api/query?search_query=all:electron&max_results=1", False),
    ("Retraction Watch (Crossref)", "scholarly", "Retractions, by Crossref update-type",
     "https://api.crossref.org/works?filter=update-type:retraction&rows=1&mailto=desi.s.amigo@gmail.com", False),
    ("Semantic Scholar", "scholarly", "Paper graph with citations (key now expected)",
     "https://api.semanticscholar.org/graph/v1/paper/search?query=malaria&limit=1", True),

    # --- climate, earth, space ---
    ("Open-Meteo forecast", "earth", "Hourly weather forecasts, no key, no account",
     "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m", False),
    ("Open-Meteo air quality", "earth", "PM2.5, ozone and pollen by coordinate",
     "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=52.52&longitude=13.41&current=pm2_5", False),
    ("USGS earthquakes", "earth", "Every instrumentally recorded earthquake",
     "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=1", False),
    ("US National Weather Service", "earth", "US forecasts and alerts (a User-Agent is required)",
     "https://api.weather.gov/points/39.7456,-97.0892", False),
    ("NASA APOD", "space", "Astronomy picture of the day (shared DEMO_KEY only)",
     "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY", True),
    ("JPL Horizons", "space", "Ephemerides for solar-system bodies",
     "https://ssd.jpl.nasa.gov/api/horizons.api?format=json&COMMAND=%27499%27&OBJ_DATA=%27NO%27&MAKE_EPHEM=%27NO%27", False),

    # --- government, civic, economics ---
    ("World Bank", "civic", "Development indicators for every country",
     "https://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.CD?format=json&per_page=1", False),
    ("US Census (ACS)", "civic", "US demographic and economic tables",
     "https://api.census.gov/data/2021/acs/acs1?get=NAME,B01001_001E&for=state:06", False),
    ("REST Countries", "civic", "Country facts: borders, capitals, populations",
     "https://restcountries.com/v3.1/name/kenya?fields=name,capital,population", False),
    ("GDELT", "civic", "Global news events, updated every 15 minutes",
     "https://api.gdeltproject.org/api/v2/doc/doc?query=malaria&mode=artlist&maxrecords=1&format=json", False),
    ("UN SDG API", "civic", "Sustainable-development goal indicators",
     "https://unstats.un.org/SDGAPI/v1/sdg/Indicator/List?pageSize=1", False),
    ("FRED (US Federal Reserve)", "civic", "US economic time series (key required)",
     "https://api.stlouisfed.org/fred/series?series_id=GDP&file_type=json", True),
    ("USDA FoodData Central", "food", "US food composition data (key required; DEMO_KEY throttled)",
     "https://api.nal.usda.gov/fdc/v1/foods/search?query=apple&pageSize=1", True),
    ("Open Food Facts", "food", "Packaged food products, crowdsourced worldwide",
     "https://world.openfoodfacts.org/api/v2/product/737628064502.json", False),

    # --- culture and general reference ---
    ("Wikipedia (REST)", "culture", "Article summaries, every language",
     "https://en.wikipedia.org/api/rest_v1/page/summary/Malaria", False),
    ("Wikidata", "culture", "Structured facts behind Wikipedia",
     "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q12156&format=json", False),
    ("Wikimedia On This Day", "culture", "What happened on a given date, from the record",
     "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/selected/09/16", False),
    ("Open Library", "culture", "Bibliographic records for published books",
     "https://openlibrary.org/search.json?q=melville&limit=1", False),
    ("Gutendex (Project Gutenberg)", "culture", "Metadata for 70k+ public-domain books",
     "https://gutendex.com/books?search=melville", False),
]


def measure(url: str, retry_after_throttle: bool = True) -> dict:
    """One polite request, plus one retry if the source says we are going too fast.

    GDELT answers a cold first request with 429 and the words "please limit requests to one
    every 5 seconds". A catalogue that recorded that as "unreachable" would be wrong, and a
    catalogue that paused five seconds and then called it "reachable, no limits" would also be
    wrong. Both facts are kept.
    """
    out = _request(url)
    out["throttled_then_answered"] = False
    if retry_after_throttle and out["http_status"] == 429:
        time.sleep(6)
        second = _request(url)
        second["throttled_then_answered"] = second["http_status"] == 200
        second["first_attempt_status"] = 429
        if second["http_status"] == 200:
            return second
        out = second
    return out


def _request(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
        "Origin": ORIGIN,                      # so the CORS answer is visible
    })
    ctx = ssl.create_default_context()
    out = {"http_status": None, "cors": "absent", "content_type": "", "bytes": 0,
           "witness": "", "error": None}
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            body = r.read(4000)
            out["http_status"] = r.status
            out["content_type"] = (r.headers.get("Content-Type") or "").split(";")[0]
            acao = r.headers.get("Access-Control-Allow-Origin")
            out["cors"] = ("*" if acao == "*" else ("origin" if acao else "absent"))
            out["bytes"] = len(body)
            text = body.decode("utf-8", errors="replace")
            out["witness"] = " ".join(text.split())[:160]
    except urllib.error.HTTPError as e:
        out["http_status"] = e.code
        try:
            acao = e.headers.get("Access-Control-Allow-Origin")
            out["cors"] = ("*" if acao == "*" else ("origin" if acao else "absent"))
        except Exception:
            pass
        out["error"] = "HTTP %s" % e.code
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, str(e)[:90])
    return out


def main() -> int:
    results = []
    for name, field, holds, url, key_needed in SOURCES:
        m = measure(url)
        m.update(name=name, field=field, holds=holds, url=url, advertised_key=key_needed)
        m["ok"] = bool(m["http_status"] == 200 and m["bytes"] > 0)
        m["browser_usable"] = bool(m["ok"] and m["cors"] in ("*", "origin"))
        results.append(m)
        print("%-34s %-4s cors=%-6s %-9s %s" % (
            name, m["http_status"], m["cors"], m["content_type"][:9],
            ("ok" if m["ok"] else (m["error"] or "empty"))), flush=True)

    ok = sum(1 for r in results if r["ok"])
    browser = sum(1 for r in results if r["browser_usable"])
    keyed = sum(1 for r in results if r["advertised_key"])
    print("\n%d sources: %d answered without a key, %d readable from a browser page, %d advertise a key"
          % (len(results), ok, browser, keyed))

    doc = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "measured_from": "a Python client sending Origin: " + ORIGIN,
        "origin_sent": ORIGIN,
        "counts": {"sources": len(results), "answered": ok, "browser_usable": browser,
                   "advertise_key": keyed},
        "sources": results,
    }
    with open(os.path.abspath(OUT), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    print("wrote", os.path.normpath(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
