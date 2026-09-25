#!/usr/bin/env python3
"""Systematic screen of molecular targets in endometriosis across major biological axes.

Uses Europe PMC to query both scopes:
  1. All-fields (string co-occurrence anywhere in full text)
  2. Strict (co-occurrence in Title or Abstract)

Outputs research/endometriosis-screen.json.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Any

UA = {"User-Agent": "llm-symposium-precheck/1.0 (public research; no key)"}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

TARGETS_BY_CATEGORY: Dict[str, List[str]] = {
    "steroid hormone reception & local intracrine biosynthesis": [
        "ESR1", "ESR2", "GPER1", "PGR", "AR", "CYP19A1", "HSD17B1", "HSD17B2", 
        "STS", "SULT1E1", "NR5A1", "STAR", "FKBP5", "FKBP4"
    ],
    "prostaglandin synthesis, transport & eicosanoid signaling": [
        "PTGS1", "PTGS2", "PTGES", "PTGES2", "PTGES3", "PTGER1", "PTGER2", 
        "PTGER3", "PTGER4", "HPGD", "SLCO2A1", "ALOX5", "ALOX12", "ALOX15", 
        "LTA4H", "LTC4S", "CYSLTR1", "CYSLTR2"
    ],
    "invasion, ECM remodeling & EMT": [
        "MMP1", "MMP2", "MMP3", "MMP7", "MMP9", "MMP11", "MMP14", 
        "TIMP1", "TIMP2", "TIMP3", "CDH1", "CDH2", "VIM", "SNAI1", "SNAI2", 
        "TWIST1", "ZEB1", "ZEB2", "FN1", "COL1A1", "ACTA2", "CTGF", "CCN1", 
        "TNC", "TNXB"
    ],
    "cytokine signaling, fibrogenesis & myofibroblast transformation": [
        "TGFB1", "TGFBR1", "TGFBR2", "SMAD2", "SMAD3", "SMAD4", "SMAD7", 
        "IL11", "IL11RA", "IL6", "IL6R", "IL1B", "IL1R1", "TNF", "TNFRSF1A", 
        "CXCL8", "CXCL12", "CXCR4", "CCL2", "CCR2", "IL33", "IL1RL1"
    ],
    "neuroangiogenesis, axon guidance & pelvic nociception": [
        "VEGFA", "KDR", "FLT1", "FGF2", "PDGFB", "ANGPT1", "ANGPT2", 
        "NGF", "NTRK1", "BDNF", "NTRK2", "GDNF", "RET", "GFRA1", 
        "TAC1", "TACR1", "CALCA", "CALCRL", "RAMP1", "SCN9A", "SCN10A", 
        "TRPV1", "TRPA1", "P2RX3", "SEMA3A", "SEMA3F", "NRP1", "PLXNA1", 
        "SLIT2", "ROBO1"
    ],
    "peritoneal macrophage clearance & phagocytic checkpoints": [
        "CD47", "SIRPA", "CD24", "SIGLEC10", "LILRB1", "LILRB2", "TREM2", 
        "MARCO", "CD163", "MRC1", "ARG1", "MSR1", "HAVCR2", "LGALS9", 
        "PDCD1", "CD274"
    ],
    "mast cell neuroimmune activation": [
        "KIT", "FCER1A", "TPSAB1", "CMA1", "MRGPRX2", "HDC", "HRH1", "HRH4"
    ],
    "iron overload, ferritinophagy & ferroptosis defenses": [
        "TFRC", "SLC40A1", "FTH1", "FTL", "HAMP", "HMOX1", "BLVRB", "STEAP3", 
        "SLC11A2", "NCOA4", "PCBP1", "PCBP2", "GPX4", "SLC7A11", "ACSL4", 
        "LPCAT3", "AIFM2", "DHODH", "GCH1", "NFE2L2", "KEAP1"
    ],
    "complement evasion & mesothelial attachment": [
        "CD46", "CD55", "CD59", "CFH", "CFI", "C1QA", "C3", "C5", "C5AR1", 
        "MUC16", "MUC1", "CD44", "VCAM1", "ICAM1", "ITGB1", "PODXL", "UPK1B"
    ],
    "apoptosis evasion, epigenetic drivers & decidualization resistance": [
        "BCL2", "BCL2L1", "MCL1", "BAX", "CASP3", "ARID1A", "PIK3CA", "KRAS", 
        "PTEN", "HDAC1", "HDAC6", "DNMT1", "EZH2", "FOXO1", "HOXA10", "HOXA11"
    ]
}

def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()

def europepmc(term: str) -> int:
    u = EPMC + "?format=json&pageSize=1&query=" + urllib.parse.quote(term)
    for attempt in range(3):
        try:
            res = json.loads(_get(u))
            return int(res.get("hitCount", 0))
        except Exception as e:
            time.sleep(1.0 * (attempt + 1))
    return -1

def europepmc_hits(term: str, n: int = 5) -> list:
    u = EPMC + "?format=json&pageSize=%d&resultType=core&query=" % n + urllib.parse.quote(term)
    for attempt in range(3):
        try:
            d = json.loads(_get(u))
            out = []
            for r in (d.get("resultList") or {}).get("result", []) or []:
                out.append({
                    "title": (r.get("title") or "").strip()[:180],
                    "id": r.get("pmid") or r.get("id") or "",
                    "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title", "")[:70],
                    "year": r.get("pubYear") or "",
                    "source": r.get("source") or "",
                })
            return out
        except Exception:
            time.sleep(1.0 * (attempt + 1))
    return []

def main():
    disease = "endometriosis"
    print(f"Starting screen for '{disease}' across {sum(len(v) for v in TARGETS_BY_CATEGORY.values())} targets...")
    
    # Disease totals
    dis_all = europepmc(f'"{disease}"')
    dis_strict = europepmc(f'TITLE:"{disease}" OR ABSTRACT:"{disease}"')
    
    trials_url = f"https://clinicaltrials.gov/api/v2/studies?pageSize=1&countTotal=true&query.cond={urllib.parse.quote(disease)}"
    try:
        trials_count = int(json.loads(_get(trials_url)).get("totalCount", 0))
    except Exception:
        trials_count = -1
        
    print(f"Condition totals: all-fields={dis_all:,}, strict={dis_strict:,}, registered trials={trials_count:,}\n")

    results = []
    unjoined = []
    low_hits = []

    total_targets = sum(len(v) for v in TARGETS_BY_CATEGORY.values())
    idx = 0

    for cat, symbols in TARGETS_BY_CATEGORY.items():
        print(f"\n--- {cat} ---")
        for sym in symbols:
            idx += 1
            q_all = f'"{sym}" AND ("{disease}")'
            q_strict = f'(TITLE:"{sym}" OR ABSTRACT:"{sym}") AND (TITLE:"{disease}" OR ABSTRACT:"{disease}")'
            
            c_all = europepmc(q_all)
            c_strict = europepmc(q_strict)
            
            target_data: Dict[str, Any] = {
                "category": cat,
                "symbol": sym,
                "full_text": c_all,
                "strict": c_strict,
            }

            # If strict is 0 or full_text <= 5, fetch sample evidence
            if c_strict == 0 and c_all > 0:
                target_data["sample_evidence"] = europepmc_hits(q_all, n=3)
            elif c_all == 0:
                target_data["sample_evidence"] = []

            results.append(target_data)

            flag = ""
            if c_strict == 0 and c_all == 0:
                flag = " [ZERO HITS - UNJOINED CANDIDATE]"
                unjoined.append((cat, sym, c_all, c_strict))
            elif c_strict == 0 and c_all <= 50:
                flag = " [NO STRICT HITS - POTENTIAL UNJOINED SUPPLY/REGULATORY NODE]"
                low_hits.append((cat, sym, c_all, c_strict))

            print(f"[{idx:3d}/{total_targets}] {sym:10} (all-fields={c_all:5d}, strict={c_strict:4d}){flag}")
            time.sleep(0.1)

    out_file = "research/endometriosis-screen.json"
    payload = {
        "condition": disease,
        "note": "full_text = Europe PMC full-text hitCount for \"SYMBOL\" AND \"endometriosis\"; strict = same but SYMBOL in TITLE/ABSTRACT and endometriosis in TITLE/ABSTRACT. Full text counts co-mentions, not studies.",
        "disease_papers_full_text": dis_all,
        "disease_papers_strict": dis_strict,
        "trials": trials_count,
        "targets": results
    }

    with open(out_file, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\nScreen complete. Saved {len(results)} targets to {out_file}.")
    print(f"Strict == 0 & all == 0 ({len(unjoined)}): {[x[1] for x in unjoined]}")
    print(f"Strict == 0 & all <= 50 ({len(low_hits)}): {[x[1] for x in low_hits]}")

if __name__ == "__main__":
    main()
