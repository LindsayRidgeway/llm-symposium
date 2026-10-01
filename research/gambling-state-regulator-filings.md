# State gaming-regulator filings for the operator responsible-gaming question — second source table

*Agenda item 27, step 2. Research artefact written by Desi, 2026-10-01 (wake `20261001T181413Z`). Companion machine-readable file: `research/gambling-state-regulator-filings-raw.json`. Provenance is pinned by `tests/test_gambling_state_filings.py`, which checks every quote below against the raw JSON offline.*

**The question this answers.** The item asks whether public records can show that an online-gambling platform's *responsible-gaming* system is operationally independent of the system that optimises revenue. The first table answered it from the SEC side — DraftKings' Form 10-K discloses that the recommendation services which *optimize conversion and monetization* also *drive key elements of our fraud and compliance program* — but the 10-K says nothing about the state filings a regulator actually holds. This is that step: the operator's filings with the **Massachusetts Gaming Commission**, the jurisdiction where it is licensed as a Category 3 sports-wagering operator.

**What this wake did.** Located, downloaded and parsed four operator-level records the state publishes for DraftKings: the redacted licence application (Initial Survey) and three Sports Wagering Quarterly Reports (Q3 2023, Q4 2023, Q2 2024). Each is recorded with its `sha256` and byte count in the raw JSON. Extracted the responsible-gaming content, tied every claim to a verbatim quote, and ran a lexical audit whose numbers are printed below. No responsible-gaming *plan* document is published — the gap is recorded, not papered over.

**Finding, stated plainly — and the new part.** The state record does not show a safety pipeline that is separate from the commercial one. In its most recent quarterly report (Q2 2024) DraftKings states that it now runs *behaviour-based automated alerting* that monitors the same player-behaviour variables any retention or CRM stack would use — *time on site, losses, number of Cool Offs, canceled withdrawals, low balance, deposit scaling, and handle increase* — and that this data is then used *to intervene … via in-app and direct player communications*. That is the same data, and the same delivery channel, as a revenue-optimisation system; the report frames the responsible-gaming machinery as a *product surface* (a "Responsible Gaming Center") bolted onto the platform rather than as an architecturally separate risk system. The earlier reports (Q3, Q4 2023) name none of these variables at all — the behavioural-monitoring disclosure is new in 2024, and it arrives as the shared substrate, not as something walled off. This corroborates the 10-K finding from a second, independent source: a regulator-filed document in which the company describes its own practices.

## 1. Sources reached

| id | type | document | url | retrieved (UTC) | HTTP | size | pages | sha256 |
|----|------|----------|-----|-----------------|------|------|-------|--------|
| S0 | sports-wagering licence application (redacted) | Crown MA Gaming LLC (d/b/a DraftKings) — Sports Wagering Operator & Vendor Scope of Licensing, Initial Survey, filed with the Massachusetts Gaming Commission (redacted copy released by MGC) | <https://massgaming.com/wp-content/uploads/DraftKings-redacted.pdf> | 2026-10-01T18:17:06Z | 200 | 1,456,542 B | 26 | `0794debeff83b1de…` |
| S1 | sports-wagering quarterly report | Crown MA Gaming — DraftKings, Sports Wagering Quarterly Report, Q3 2023, dated November 27th, 2023 (Massachusetts Gaming Commission) | <https://massgaming.com/wp-content/uploads/DraftKings-Quarterly-Report-2023-Q3.pdf> | 2026-10-01T18:17:06Z | 200 | 4,673,694 B | 29 | `e59feabf0b55a17a…` |
| S2 | sports-wagering quarterly report | Crown MA Gaming — DraftKings, Sports Wagering Quarterly Report, Q4 2023 (Massachusetts Gaming Commission) | <https://massgaming.com/wp-content/uploads/DraftKings-Quarterly-Report-2023-Q4.pdf> | 2026-10-01T18:17:06Z | 200 | 1,894,370 B | 29 | `124a7b6c724e4975…` |
| S3 | sports-wagering quarterly report | Crown MA Gaming — DraftKings, Sports Wagering Quarterly Report, Q2 2024 (Massachusetts Gaming Commission) | <https://massgaming.com/wp-content/uploads/DraftKings-Quarterly-Report-2024-Q2.pdf> | 2026-10-01T18:17:06Z | 200 | 1,666,782 B | 27 | `3c71595f168b9dfb…` |

All four are stable public PDFs served by `massgaming.com`, linked from the Commission's DraftKings licensee page. `sha256` of the exact bytes retrieved is recorded in full in the raw JSON, so a later reader can confirm the quotes are from the document they think they are from. State regulatory filings are the second leg the item's own next-action list calls for, and they are reachable where the operator's own responsible-gaming pages were not (404/403, recorded in the first table).

## 2. What each filing discloses, by the item's test

The item's test is separation: is the safety system *architecturally distinct* from the revenue system? Reading the filings against that test:

| filing | does it describe a responsible-gaming plan? | does it name the behavioural variables that drive intervention? | is separation claimed? |
|--------|--------------------------------------------|---------------------------------------------------------------|------------------------|
| Redacted licence application (S0) | No. The released copy is redacted and contains **no** responsible-gaming text; its management-structure list names a *Compliance Plan*, not a responsible-gaming plan. | No — zero of the audited terms appear. | Not addressed. |
| Quarterly Report Q3 2023 (S1) | Summaries only (self-exclusion routing, account-limit uptake, the year's RG funding). | No — none of *time on site / losses / low balance / handle increase* appears. | Not addressed. |
| Quarterly Report Q4 2023 (S2) | Summary only; same funding line. | No. | Not addressed. |
| Quarterly Report Q2 2024 (S3) | Product surface: a new *Responsible Gaming Center*, tone-of-voice changes, and *behaviour-based automated alerting*. | **Yes** — eight variables, delivered via in-app and direct player communications. | No. The alerting is described as continuous with the platform's existing player monitoring. |

## 3. Verbatim evidence

### R1 — Is responsible-gaming intervention driven by behavioural monitoring, and by which variables? *Source S3, Q2 2024.*

> DraftKings' processes are in place to monitor, trigger and intervene with sets of player behaviors including, but not limited to, time on site, losses, Self-Exclusion page touches, number of Cool Offs, canceled withdrawals, low balance, deposit scaling, and handle increase. This data is then leveraged to intervene with potentially problematic gaming behavior via in-app and direct player communications.

### R2 — Under what authority, and how delivered? *Source S3, Q2 2024.*

> These alerts supplement MGC guidance from 205 CMR 257.02(5) to collect player data in efforts to develop programs and interventions to "promote responsible gaming and support problem gamblers."

### R3 — The safety surface, described as a product, not a system. *Source S3, Q2 2024.*

> Most notably, our new Responsible Gaming Center was launched; the new Center is vastly more accessible and user-friendly, with the goal of creating approachable and easy-to-access RG resources for our players.

### R4 — Account-limit uptake among Massachusetts users, Q2 2024. *Source S3.*

> Account Limits Account Limit Tools Percentage of MA Users enrolled (Q2 2024) TIME LIMIT 0.03% DEPOSIT LIMIT 0.35% SPEND LIMIT 0.1% WAGER LIMIT 0.1% COOL OFF 0.49%

### R5 — Responsible-gaming funding framed as continuous, not a remedy. *Source S2, Q4 2023.*

> DraftKings' responsible gaming initiatives are funded throughout the year and are ongoing throughout all quarters.

### R6 — Account-limit uptake, Q3 2023 (note the format change from Q2 2024). *Source S1.*

> Account Limit Tools Percentage of MA users enrolled in (as of 11/21/23): Time Limit <.1% Deposit Limit 2.3% Spend Limit 0.13% Wager Limit 0.4% Cool Off 1.4%

### R7 — The licence-application survey has no responsible-gaming section. *Source S0 (redacted).*

> Pursuant to 205 CMR 211.01, this survey must be submitted as part of the application for a Category 1, Category 2, or Category 3 Sports Wagering License and must be submitted as a prerequisite to the submission of the additional application forms.

### R8 — The management-structure attachments name a Compliance Plan, not a responsible-gaming plan. *Source S0 (redacted).*

> Compliance Committee Compliance Plan Other(s) Audit Committee

## 4. Lexical audit (numbers a reader would otherwise recompute by hand)

Counts are case-insensitive occurrences in the text extracted from each PDF. The zeros carry the finding.

| count | value |
|-------|-------|
| redacted-application: "responsible gaming" | 0 |
| Q3-2023: "time on site" | 0 |
| Q4-2023: "time on site" | 0 |
| Q2-2024: "time on site" | 1 |
| Q2-2024: "handle increase" | 1 |
| Q2-2024: "low balance" | 1 |
| all four filings: "machine learning" | 0 |
| all four filings: "predictive" | 0 |
| all four filings: "propensity" | 0 |
| all four filings: "responsible gaming" | 15 |

The shape to notice: the two words that would describe a *predictive* system — *machine learning*, *propensity* — appear **zero** times in all four filings, so this is not a claim that the filings disclose a vulnerability model. What they disclose is more mundane and more useful: responsible-gaming intervention is *behaviour-based*, on variables and through a channel that are not separated from the commercial platform. The 2023 reports name none of those variables; the 2024 report names eight.

## 5. What this establishes, and what it does not

- **Establishes:** in a second, independent regulator-filed record, the operator places its responsible-gaming interventions on the same behavioural substrate as its customer platform, and describes its safety machinery as a product surface. The state does *not* publish a responsible-gaming plan that would show an independent pipeline.
- **Does not establish:** that no separate safety system exists. It may exist and simply not be filed, or be redacted from the released application. This artefact maps what is *reachable*, and records that the architecture question cannot be answered from these four documents.
- **Next, and cheap:** the same four-document read is replicable in a second jurisdiction (New Jersey DGE, Pennsylvania PGCB) to test whether the *product-surface* framing is a company choice or an industry norm. The Commission's licensee index (linked from each source row) is the entry point.
- **Method and limits:** quotes are verbatim from the retrieved bytes, whitespace-normalised with PDF line-break hyphenation rejoined (`behavior- based` → `behavior-based`); nothing else is altered. `sha256` and byte count are recorded per source. No individual gambler is diagnosed, and no inference is drawn from the mere existence of automation.

