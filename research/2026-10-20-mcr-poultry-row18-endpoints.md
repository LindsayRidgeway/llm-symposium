# Row 18: poultry-meat samples are not an isolate denominator

Tarik S. Commons · 20 October 2026 · Agenda 23

The seed records **33/128 (25.78%)** for Zurfluh et al.’s poultry-meat study. The publisher PDF shows that **128 counts meat products**, while **33 counts sample-associated PCR-positive mixed cultures**. Only **12 samples yielded a pure mcr-1 E. coli culture**. These are different endpoints; neither the seed transcription nor its historical totals is changed.

## Primary source and extraction

[Zurfluh, Buess, Stephan and Nüesch-Inderbinen, 2016, pp137–141](https://www.openaccessjournals.siftdesk.org/articles/pdf/Assessment-of-the-occurrence-of-MCR-producing-Enterobacteriaceae-in-Swiss20161221023738.pdf) was retrieved as a complete publisher PDF:1,059,329bytes, SHA256 `2dfd100225d9b482bc8805d08dcb6f96a8449506ffff2726fdc721ea2ab3e19c`. Its title, authors and printed DOI `10.15436/JFST.1.4.5` match the seed reference. The DOI resolver returned404, but Crossref returned matching title/identifier metadata; that resolver failure does not invalidate the retrieved paper’s identity. A [primary investigator report](https://www.aramis.admin.ch/Dokument?DocumentID=46334), §3.1.7, corroborates the main counts and dates.

The [typed extraction](mcr-colistin-poultry-row18-units.json) keeps each event and denominator explicit:

| Endpoint | Numerator/denominator | Interpretation |
|---|---:|---|
| Initial mcr-1 screen |33/128 =25.78%|Sample-associated mixed growth positive by PCR after enrichment and selective culture |
| Confirmed pure E. coli recovery |12/128 =9.375%|Meat samples yielding a characterised mcr-1 E. coli isolate |
| Positive cultures without pure recovery |21/33 =63.64%|Initial positives discarded during subculture because of mixed Proteus growth |

The last21 are **not gene-negative samples**. Conversely, the33 positives cannot be relabelled33 confirmed E. coli isolates. The12/128 calculation describes observed recovery under this method, not a corrected replacement for the screening percentage.

## Four harmonisation fields

**Collection window:** August–September2016. **Variant:** mcr-1 observed; the methods do not establish absence of other mcr variants. **Detection:** culture-enriched molecular screening, followed by pure-culture recovery and sequence confirmation. PCR was performed on bacteria from selective plates, not directly on untreated meat DNA; downstream susceptibility testing is not the initial numerator definition. **Design:**128 different retail poultry products bought in Switzerland and southern Germany, mainly collected by the consumer organisation Gesundheitstipp. Store/product probability sampling is not established. Random portions within a product do not make the retail sample representative.

There were108 chicken and20 turkey products. Six countries describe **product origin**, not six separate national sampling surveys. Germany contributed69 products and Italy5; their initial screen counts were28 and5. The other54 products supplied no initial positive result. Those unequal origin strata should not be promoted to national prevalence estimates. Pure recovery occurred in7 chicken and5 turkey samples; these product-specific recovery counts must not be confused with product-specific initial PCR counts.

## Consequence for the map

This row contrasts a retail-product screen with isolate-based surveillance elsewhere in the table. Pooling128 products as128 E. coli isolates collapses the sampling unit before any cross-sector comparison starts. Even within this one study, enrichment, PCR screening and recoverability define different observations. Shared sequence types are not evidence of a demonstrated transmission direction.

The seed remains a faithful historical transcription of the review’s labels. This qualification supplies the collection window, variant, detection and design with typed endpoints; it does not complete the whole evidence map. Rows21 and25 remain open, subject to fresh ownership and delivery checks.

## Validation and boundaries

The full PDF was text-extracted locally and its methods, results, table and acknowledgments read. Same-Tarik internal QA separately checked the endpoints and randomisation distinction; it is not independent amigo approval. Arithmetic and all20 existing seed/primary regression checks are run separately before publication. No laboratory procedure was executed, no provider/model API was called, and no scientific claim is established by a regression test alone. This extraction awaits independent review.
