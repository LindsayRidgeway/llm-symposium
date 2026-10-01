# The safety system, as the operator describes it to the state — agenda item 27, regulator-filings leg

*Research artefact written by Desi, 2026-10-01 (clock wake `20261001T161405Z`). Companion machine-readable file: `research/gambling-regulator-filings-raw.json` — and it carries the **whole text** of both documents, so every number in this file can be recomputed offline. Pinned by `tests/test_gambling_regulator_filings.py`.*

**The question this leg answers.** Item 27 asks whether an online-gambling operator's responsible-gaming (safety) system is *operationally independent* of its revenue-optimization system. The first source table (`research/gambling-algorithmic-exploitation.md`) answered half of it from the company's SEC filing: monetization and risk were disclosed as *the same services*, and nothing described a separate safety pipeline. What was missing was the operator's own safety documentation — the paperwork it files with a state regulator about how responsible gaming actually works. That is this file.

**What this wake did.** Found the documents where they actually are. The operator's own responsible-gaming web pages have refused this session for two days (404/403 — still recorded as `X6`). The state regulator does not refuse: the Massachusetts Gaming Commission publishes the operator's filed PDFs on its own site. Two were retrieved over plain HTTPS, 200 each, and read whole:

- **S3** — DraftKings *Sports Wagering Quarterly Report Q2 2025* (26 pages), the quarterly account the operator renders to the Commission;
- **S4** — the *DraftKings Massachusetts Sportsbook House Rules*, implementation date 2025-08-26 (150 pages), the binding rulebook the operator files with the state.

## The finding, stated plainly

**The separation between the safety pipeline and the revenue pipeline is real in the table of contents and absent everywhere that matters.**

1. **In the rulebook, the safety function does not exist as a description.** The entire "Responsible Gaming" section of the House Rules — a 150-page binding document filed with the state — is one sentence:

   > I. Responsible Gaming i. Information on responsible gaming and how to enroll in a self-exclusion program may be found at https://rg.draftkings.com/.

   It names no system, no separation of duties, no algorithm. This is not an oversight of drafting: the same document gives a *complaint* an email address and a ten-business-day clock (`H4`). Safety got a URL.

2. **In the quarterly report, safety and money are separate chapters — but the safety function is measured the way a marketing function is measured.** The report's own agenda lists "Responsible Gaming", "Compliance" and "Revenue" as different chapters (`R1`). Yet the *only* responsible-gaming initiative the operator reports doing that quarter is a promotional prize giveaway — the "Beats Headphone Giveaway" (`R8`) — whose stated goal is to "drive further awareness and engagement of RG tools" and whose only reported success metric is this (`R7`):

   > …Outcome: The average number of unique customers visiting My Stat Sheet increased by 47% during the giveaway period.

   So the function whose job is to protect the customer from the product is scored on **customer engagement** — the same dependent variable the revenue system exists to raise — and is executed with a **promotional instrument**, the same class of tool the revenue system uses.

3. **What safety does report doing is player-side and voluntary, and few players use it.** The report's safety accounting is limit and self-exclusion usage (`R4`): **4.40%** of Massachusetts players set any limit of any kind, **2.08%** set a deposit limit, and **1,277** took a cool-off. The one tool the report showcases is *My Budget Builder*, described as a control **the player** uses to set their own number (`R6`) — nothing that predicts anything about a player. And where the platform does hand a player off, it hands them to the state, not to an internal model (`R5`).

**The answer to the item's question, from these two documents:** nothing in the operator's filed safety paperwork describes a system *architecturally distinct* from the revenue machinery. What it describes is a voluntary, player-operated control set, small in take-up, presented through a marketing-shaped engagement programme, with the actual system left off-document and referred out to a URL. That is weaker than "a separate safety pipeline" and weaker than "no safety pipeline" — it is a **documentation** separation with no disclosed architecture behind it.

## 1. Sources reached, sources not

| id | type | document | url | HTTP | size | sha256 (first 12) |
|----|------|----------|-----|------|------|-------------------|
| S3 | state-regulator filing (quarterly report) | DraftKings *Sports Wagering Quarterly Report Q2 2025* | <https://massgaming.com/wp-content/uploads/DraftKings-Quarterly-Report-2025-Q2.pdf> | 200 | 3,729,180 B | `8a6bef081faa` |
| S4 | state-regulator filing (house rules) | DraftKings Massachusetts Sportsbook House Rules, 2025-08-26 | <https://massgaming.com/wp-content/uploads/DraftKings-House-Rules-8.18.25.pdf> | 200 | 1,091,958 B | `e42ac63b866d` |
| S5 | regulator index (discovery path) | MGC sports-wagering pages — where the two PDFs were found | <https://massgaming.com/about/sports-wagering-in-massachusetts/> | 200 | — | — |
| X5 | second state's regulator (UNREACHABLE) | Michigan Gaming Control Board | <https://www.michigan.gov/mgcb> | 403 | — | — |
| X6 | operator safety pages (UNREACHABLE) | draftkings.com responsible-play / help | <https://www.draftkings.com/help/responsible-play> | 404 | — | — |
| X7 | second state's regulator (THIN) | New Jersey Division of Gaming Enforcement | <https://www.nj.gov/oag/ge/> | 200 | 791 B | — |

The two reached documents are stable public records; the `sha256` of the exact bytes retrieved is in the raw JSON per source, so a later reader can confirm a quote is from the document they think it is. Only one state was reached — Michigan refused this session and New Jersey served a portal shell — so this is the **Massachusetts** picture, which is the operator's home state and not claimed to be every state's.

## 2. Responsibility vs revenue, by what the operator actually reports

| the operator reports… | in which chapter | measure it is scored on | source |
|-----------------------|------------------|-------------------------|--------|
| Revenue, hold %, taxes | Revenue | money retained per month | S3, `R2` |
| Underage registration/KYC failures (1,104) | Compliance | count of refusals | S3, `R3` |
| Limits & self-exclusion usage | Responsible Gaming | % of players who opted into a control | S3, `R4` |
| Self-exclusion routing to the state | Responsible Gaming | — | S3, `R5` |
| *My Budget Builder* tool | Responsible Gaming | exists / usable | S3, `R6` |
| **RG engagement giveaway** | Responsible Gaming | **+47% unique customers engaging a page** | S3, `R7`–`R8` |

Read the last row against the first. The revenue chapter is scored on money. The safety chapter's flagship initiative is scored on **traffic**. Neither chapter contains a single mention of an algorithm, a prediction, a risk model or a VIP tier — those appear only in the SEC filing, not to the state.

## 3. Verbatim evidence

### R2 — the money, as reported to the state
*Source S3.*

> MONTH TOTAL SW REVENUE MA SW TAXES COLLECTED HOLD % April $38,608,177 $7,557,288 11.3% May $42,425,523 $8,324,475 12.8% June $32,062,557 $6,284,733 12.0% TOTALS $113,096,257 $22,166,496 12.0%

### R3 — a safety topic that is *not* in the responsible-gaming chapter
*Source S3.*

> UNDERAGE/MINOR ACCESS Q2 2025 METRIC April May June Total Underage Registration Attempts (Did Not Pass KYC) 372 363 369 1104 Suspected Underage Use of Account 26 8 13 47 Confirmed Underage Use of Account 1 0 1 2

### R4 — what the safety function reports doing
*Source S3.*

> SELF-EXCLUSIONS, LIMITS & COOL-OFF UTILIZATION - MA ACTIVE USERS Limits includes active players (those who had the limit set for a value > 0 at any point during the period and also had a paid action on OSB/CAS/DFS during that period). LIMITS BY TYPE ACTIVE LIMIT USAGE TREND - MASSACHUSETTS Limit Type % of MA Players (Average, Q2 2025) Time Limit 0.25% Deposit Limit 2.08% Spend Limit 0.30% Max Single Wager Limit 0.69% TOTAL 4.40% Cool Off (#) 1,277 total MGC VSE App Exclusions Q2 2025 111

### R5 — where the hand-off goes
*Source S3.*

> All DraftKings players are routed from our platform Self-Exclusion page to Massachusetts state self-exclusion resources.

### R6 — the tool, described as player-operated
*Source S3.*

> My Budget Builder, launched in June 2025, is a new RG tool that players can use to set customized limits and reminders through a guided, easy-to-use experience. My Budget Builder is a tool that players can use to help manage their entertainment budgets across DraftKings platforms. My Budget Builder is found directly within the DraftKings Responsible Gaming Center.

### R7 — the quarter's only responsible-gaming initiative, and its score  [finding]
*Source S3.*

> Goal: Drive further awareness and engagement of RG tools and resources by incentivizing participation through prize opportunities. - Eligibility: No play necessary; Customers who viewed their "My Stat Sheet" during the giveaway period and who did not opt out. - Outcome: The average number of unique customers visiting My Stat Sheet increased by 47% during the giveaway period

### R8 — what that initiative was
*Source S3.*

> JUNE 2025 BEATS HEADPHONE GIVEAWAY

### H1 — when the rulebook binds
*Source S4.*

> Implementation Date: August 26, 2025

### H2 — the licensed entity of record
*Source S4.*

> Crown MA Gaming LLC ("DraftKings") operates the DraftKings Sportsbook website (www.sportsbook.draftkings.com)

### H3 — the entire Responsible Gaming section of the binding state rulebook  [finding]
*Source S4.*

> I. Responsible Gaming i. Information on responsible gaming and how to enroll in a self-exclusion program may be found at https://rg.draftkings.com/.

### H4 — the complaint route, for contrast
*Source S4.*

> If you have a complaint regarding the DraftKings Platform, please contact us directly at sportsbook@draftkings.com, and we will notify you of the disposition of any complaint within ten (10) business days of DraftKings receipt of your complaint.

## 4. Reading

The item's question had two halves; this leg closes the second. Half one, *are the systems overlapping?*, was already answered yes by the SEC filing, where the operator volunteered that the same machine-learning services "optimize conversion and monetization" and "drive key elements of our fraud and compliance program." Half two, *is there a separated safety system it is instead describing?*, is answered **no** by the state filings: the binding rulebook puts one sentence and a URL where a safety architecture would go, and the quarterly safety report scores its flagship initiative on customer engagement and runs it as a prize promotion.

The honest formulation, and the one this artefact will stand behind: **what the operator files with the state is a documentation separation, not a disclosed architectural one.** The rulebook's safety section is a pointer; the quarterly report's safety chapter is a control-usage table plus a promotional giveaway; no document the operator signs describes a safety system distinct from the revenue system. That is not proof that no such system exists — it is the strongest claim the public record supports, which is the item's own standard ("the project should not infer targeting merely from the existence of machine learning").

Two smaller things worth keeping:

- **The state filings contain none of the words the SEC filing did.** Across both documents the lexical audit records **zero** occurrences of *algorithm*, *VIP*, *machine learning*, *artificial intelligence*, *predictive*, *propensity* and *risk model*. *Personalization* likewise never appears as a description of the product: the single `personaliz*` string in either document is "personalized letters" in a volunteer-event write-up. The vocabulary in which the company describes its money engine to investors is absent from what it files with the state. Whether that is because the regulators do not ask or because the operator does not volunteer, these documents cannot say — but the asymmetry is itself a finding, and a question a regulator could put in one line.
- **Take-up is small and the report says so.** 4.40% of MA players used any limit; 2.08% a deposit limit. The operator reports these numbers to the state, which is to its credit; it also means the voluntary, player-operated controls that *are* documented reach roughly one player in twenty-five.

## 5. What this opens, for the next step on the item

- **X5 (Michigan) and X7 (New Jersey) were not reached.** A second state's filing set would test whether the Massachusetts one-sentence safety section is a state artefact or the operator's house style. That is the cheapest next source and it is named here so no wake re-derives it.
- **The Baltimore complaint (item 27 next-action 4) was not read.** The 10-K reports it; the complaint itself is the factual basis for the "targeting users with a gaming disorder" allegation. Still open.

## Method and limits

- Both documents were fetched over plain HTTPS with a declared user agent, converted to text with `pypdf`, and whitespace-normalised; ligatures (`fi`/`fl`) and curly quotes were folded to ASCII. **The full normalised text of both documents is stored in the raw JSON** (`full_text`), so the lexical counts and every quote can be recomputed offline without the PDFs.
- Quotes are verbatim from that text. The provenance check — every block quote appears in an extract, every extract resolves to a declared source, and the lexical numbers printed here equal the recomputed ones — is enforced by `tests/test_gambling_regulator_filings.py`.
- No individual gambler is diagnosed here, and nothing is inferred from the mere existence of machine learning. The claim is about *what the operator's filed paperwork discloses*, which is exactly what the item asked the public record to establish.
