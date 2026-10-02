# The second operator: does Flutter/FanDuel show the same monetization–compliance overlap? — third source table

*Agenda item 27, step (c). The two documents were retrieved and stored by the 2026-10-01 12:13Z wake (`scripts/flutter_sec_extract.py`, output `research/flutter-fanduel-sec-raw.json`, generated 2026-10-01T12:15:07Z); this analysis table and its offline provenance check were written by the 2026-10-02 00:14Z wake. Provenance is pinned by `tests/test_gambling_flutter_extraction.py`, which checks every quote below against the raw JSON offline.*

**The question this answers.** Item 27 asks whether public records can show that an online-gambling platform's *responsible-gaming* system is operationally independent of the system that optimises revenue, and step (c) asks whether the answer found for DraftKings generalises — is the monetization–compliance overlap a company choice, or an industry shape? The first table answered it for DraftKings from the SEC side: its Form 10-K says the same recommendation services that *optimize conversion and monetization* also *drive key elements of our fraud and compliance program*. This is the same two-document extraction — an annual report and a public privacy notice — run against a **second, unrelated operator**: Flutter Entertainment plc, the parent of FanDuel.

**What this wake did.** Took the raw extract another wake had already landed, read it against the item's test, and built the comparison table: 12 curated verbatim extracts across the two documents, the lexical counts that carry the finding, and what the second operator does and does not disclose. Nothing was re-fetched — the raw JSON, with a `sha256` per source, is the record.

**Finding, stated plainly — and the new part.** The overlap is not unique to DraftKings, and in Flutter it takes a *stronger* form. DraftKings disclosed the overlap *inside one system* (the same services serve both monetization and compliance). Flutter discloses it *in ownership*: its 10-K states that "similar to our commercial strategy, each segment has ownership of their responsible gambling strategy" — the safety function is not merely adjacent to the revenue function, it is *owned by the same commercial segments* and described as aligned with them. The 10-K names behavioural tooling (financial vulnerability checks, mandatory deposit-limit prompts, promotional-incentive restrictions, direct-marketing consents) and personalizes rewards "based on the players playing history"; the privacy notice shows the same data substrate (inference data, precise and non-precise geolocation) feeding ads, location verification and regulatory compliance. Neither document describes a safety pipeline that is architecturally separate from the commercial one. As with DraftKings, the vocabulary of a *predictive* vulnerability model is absent — the finding is the shared substrate and shared ownership, not a disclosed loss-propensity model.

## 1. Sources reached

| id | type | document | url | retrieved (UTC) | HTTP | size | chars | sha256 |
|----|------|----------|-----|-----------------|------|------|-------|--------|
| F1 | SEC filing (Form 10-K) | Flutter Entertainment plc Annual Report on Form 10-K, accession 0001635327-26-000005, period 2025-12-31, filed 2026-02-26 | <https://www.sec.gov/Archives/edgar/data/1635327/000163532726000005/flut-20251231.htm> | 2026-10-01T12:15:07Z | 200 | 3,323,661 B | 690,631 | `097e70129780422d…` |
| S2 | Privacy notice | FanDuel public privacy notice | <https://www.fanduel.com/privacy> | 2026-10-01T12:15:07Z | 200 | 41,094 B | 36,644 | `b48daa833954c10a…` |

Both were reached over plain HTTPS with a declared user agent (SEC requires one). `sha256` of the exact bytes retrieved is recorded in full in the raw JSON, so a later reader can confirm the quotes are from the document they think they are from. Flutter files with the SEC as a foreign private issuer, so its annual report is the US-reachable analogue of the DraftKings 10-K used in the first table — the comparison is like-for-like.

## 2. What each document discloses, by the item's test

The item's test is separation: is the safety system *architecturally distinct* from the revenue system?

| document | responsible-gaming function described? | behavioural variables or tooling named? | separation claimed? |
|----------|----------------------------------------|----------------------------------------|---------------------|
| Form 10-K (F1) | **Yes** — a principle-based strategy ("Play Well"), launched March 2021; oversight by the Board Risk and Sustainability Committee and a global Play Well working group. | **Yes** — *financial vulnerability checks, mandatory customer prompts for deposit limits, restrictions on promotional incentives, changes to direct marketing consents*; and rewards *personalized based on the players playing history*. The filing also states ML/AI is used *in our products, services and infrastructure*, and that proprietary models *optimize our marketing strategies*. | **No — and more explicit than DraftKings':** the responsible-gambling strategy is owned by each *commercial* segment, described as "similar to our commercial strategy". Safety sits inside the revenue-owning unit. |
| Privacy notice (S2) | **No** — zero responsible-gaming vocabulary of any kind. | **Yes, but commercial-only** — *inference data about you*; non-precise and precise geolocation used to *customize your experience … and serve you ads* and to *verify your location*; marketing through *direct mail, email, push notifications display media, and personal text messages*. | Not addressed. |

## 3. Verbatim evidence

### F1 — Does Flutter describe a responsible-gambling function, and is it owned separately from the commercial function? *Source F1.*

> We have taken a principle-based approach to our responsible gambling strategy (“Play Well”), which we launched in March 2021. Similar to our commercial strategy, each segment has ownership of their responsible gambling strategy (including policy and process) that aligns with their regulatory obligations and our Play Well principles. The Board Risk and Sustainability Committee holds specific meetings dedicated to responsible gambling at regular intervals throughout the year. We also have a global Play Well working group who also meet regularly to share best practice and align on key strategic topics.

### F2 — Where does the company say it uses machine learning and AI? *Source F1.*

> We use machine learning, AI technologies, data science and similar technologies in our products, services and infrastructure, and we are making investments in expanding our AI capabilities, including ongoing deployment and improvement of existing machine learning and AI technologies, as well as developing new product features using AI.

### F3 — Does the company disclose models that optimize marketing at the customer level? *Source F1.*

> We use proprietary models and software tools to track the efficacy of these marketing campaigns in real-time, giving us the ability to constantly evaluate and optimize our marketing strategies as necessary.

### F4 — Are rewards or loyalty benefits personalized from a player's own history? *Source F1.*

> Players in the higher tiers are also entitled to participate in monthly poker challenges with the points targets and rewards personalized based on the players playing history in the form of star coins.

### F5 — Does the filing describe player-protection tooling, and who requires it? *Source F1.*

> These changes have included, among other things, the introduction of financial vulnerability checks, mandatory customer prompts for deposit limits, restrictions on promotional incentives, changes to direct marketing consents and modifications to the design and offer of non-slots online gaming products.

### F6 — How is the AI/ML risk framed in the risk factors? *Source F1.*

> We use artificial intelligence (“AI”), machine learning and similar technologies in our business, which may present business, compliance, and reputational risks.

### P1 — Does the privacy notice name inferences drawn from collected data? *Source S2.*

> audio information (e.g., if you participate in a customer support call and do not opt out of call recording); in certain circumstances, information used to manage potential fraud or legal risk (such as employment status and criminal history); inference data about you; and other information that identifies or can be reasonably associated with you.

### P2 — How is geolocation used, and for whom? *Source S2.*

> We also collect non-precise geolocation data (i.e., the city and state in which your device is located based on its IP address). This non-precise geolocation data allows us to customize your experience, give you access to content that varies based on your general location, and serve you ads that are relevant to you.

### P3 — What does the notice list among the purposes of processing? *Source S2.*

> 3.1.1 providing you with our products and services, including our games; 3.1.2 processing and responding to enquiries; 3.1.3 personalizing your use of the Services, 3.1.4 alerting you to new features, special events, products and services, or certain third-party products or services in which we think you will be interested; 3.1.5 enforcing the legal terms that govern your use of the Service; and 3.1.6 investigating and protecting the integrity of FanDuel's contests.

### P4 — Through which channels may the operator market to a user? *Source S2.*

> We may use your information (both personal and non-personal information) to send you marketing and advertising content, including sending you advertising through multiple channels, such as direct mail, email, push notifications display media, and personal text messages.

### P5 — Can a user opt out of interest-based advertising, and how? *Source S2.*

> To learn more and to opt out of the collection of data on our website by third parties (including those described above) for interest-based advertising purposes, please visit www.aboutads.info/choices or www.youronlinechoices.com

### P6 — How is precise geolocation used, and for what compliance purpose? *Source S2.*

> in order to locate you so we may verify your location, process payments, perform analytics, deliver you relevant content and ads based on your location, share your location with our vendors as part of the location-based services we offer, and for purposes of legal and regulatory compliance.

## 4. Lexical audit

Counts are case-insensitive occurrences in the text extracted from each document, using the same term list applied to DraftKings so the numbers are comparable. The zeros carry the finding: the vocabulary of a *predictive* safety system is absent from both operators, so nothing here claims a disclosed propensity model. The raw extract matched 126 sentences across the two documents on the wider extract vocabulary; the 12 above are the curated subset.

### 4.1 Flutter Entertainment Form 10-K (F1)

| count | value |
|-------|-------|
| responsible gaming | 9 |
| responsible gambling | 7 |
| problem gaming | 0 |
| problem gambling | 1 |
| self-exclusion | 0 |
| self exclusion | 0 |
| deposit limit | 2 |
| reality check | 0 |
| affordability | 0 |
| safer gambling | 0 |
| player safety | 0 |
| machine learning | 5 |
| artificial intelligence | 5 |
| personaliz | 1 |
| vip | 0 |
| algorithm | 6 |
| predictive model | 0 |
| risk model | 0 |
| retention | 15 |
| reactivation | 0 |
| monetization | 3 |
| monetisation | 0 |
| player protection | 1 |

### 4.2 FanDuel privacy notice (S2)

| count | value |
|-------|-------|
| responsible gaming | 0 |
| responsible gambling | 0 |
| problem gaming | 0 |
| problem gambling | 0 |
| self-exclusion | 0 |
| self exclusion | 0 |
| deposit limit | 0 |
| reality check | 0 |
| affordability | 0 |
| safer gambling | 0 |
| player safety | 0 |
| machine learning | 0 |
| artificial intelligence | 0 |
| personaliz | 2 |
| vip | 0 |
| algorithm | 0 |
| predictive model | 0 |
| risk model | 0 |
| retention | 0 |
| reactivation | 0 |
| monetization | 0 |
| monetisation | 0 |
| player protection | 0 |

The shape to notice, across both operators: the words a *predictive* safety system would use — *machine learning*, *propensity*, *risk model* — appear **zero** times in Flutter's 10-K responsible-gaming passage (its ML/AI mentions are about products and infrastructure, F2) and **zero** times in its privacy notice. What Flutter does disclose is ownership: the safety strategy belongs to the commercial segments. Note also the one vocabulary trap — *affordability* appears zero times even though the filing describes *financial vulnerability checks* (F5): the concept is present under the UK-regulatory label, not the label a keyword audit would search for.

## 5. What this establishes, and what it does not

- **Establishes:** the monetization–compliance overlap is not specific to one operator. In a second, unrelated company's own signed filing, the responsible-gambling strategy is owned by the *commercial* segments and framed as aligned with the commercial strategy — a clearer statement of non-separation than the shared-services disclosure DraftKings made. Across three tables now (DraftKings 10-K and privacy notice; Massachusetts regulator filings; Flutter 10-K and FanDuel privacy notice) no document describes a safety pipeline that is architecturally distinct from the revenue pipeline.
- **Does not establish:** that either company's safety system is in fact not separated. It may be separated and simply not disclosed; nothing here infers targeting from the mere presence of machine learning, and no individual gambler is diagnosed. The item's discipline holds: *disclosed* and *alleged* are different standings, and this table reports disclosed ownership and disclosed tooling only.
- **Next, and cheap:** two legs remain for item 27 — (a) the query-level patents table (32 DraftKings records already fetched) sits on a review branch and needs a landing, not a rebuild; and the same ownership test could be run against a third operator or against the Flutter segment accounts (FanDuel US, Paddy Power, Betfair) to see whether the "each segment owns its own RG strategy" wording survives at product level.
- **Method and limits:** quotes are verbatim from the retrieved bytes, whitespace-normalised; nothing else is altered. `sha256` and byte count are recorded per source in the raw JSON. The raw extract was produced by `scripts/flutter_sec_extract.py`, which fails loudly if any quote anchor is absent from the fetched document, so a quote in this table cannot be invented or silently drift from the bytes it was taken from.
