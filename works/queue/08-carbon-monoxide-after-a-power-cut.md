## 08 — Carbon monoxide after the power goes out

**Status:** candidate, **data path verified by hand 2026-10-07**. Not yet built beyond this file and
its source record (`docs/works/co-safety-sources.json`).
**Owner:** Dmitri (opened 2026-10-07).

**What it is:** a field guide, a placement checker, and a symptom triage for the one hazard a power
outage makes almost by itself — carbon monoxide from the machine a household runs to get the power
back. Pick where the generator, camp stove, grill or patio heater is standing (indoors; outdoors
under 20 feet; outdoors 20 feet or more), and the page returns the rule the authorities give in their
own words, with the alarm guidance and the symptom list beside it.

**Who it is for:** anyone who has just carried a generator out of the garage. The CDC's own words are
that CO is "odorless" and "kills without warning"; the CPSC attributes **more than 100 deaths a year
in the US to portable generators alone**.

**Why it is not a duplicate of anything already shipped.** `docs/works/food-safety.html` is the cold
chain (food). `docs/works/air.html` measures *outdoor* air quality. `docs/works/thermal.html` is
surviving the cold, and it mentions carbon monoxide exactly **once** — a single bullet, `NEVER burn
charcoal, wood fires, barbecue grills, camp stoves, gasoline generators ... indoors` — with no
distance, no placement rule, no alarm guidance and no symptom triage. No page on the site answers
*where may I run this machine, and what does the alarm mean.*

**Why it may never ship, and the honest scope that would have to be on it:** it cannot measure your
air; only a CO detector can do that. It reports three agencies' published rules and the places where
they disagree, and it repeats rather than resolves; it does not tell you whether a specific
generator/room combination is safe today, because that depends on exhaust direction, wind and the
building, none of which a page can see. The symptom triage is a prompt to leave and call 911, not a
diagnosis: the CDC says the symptoms are "flu-like," which is exactly why people die indoors waiting
for a flu to pass.

### Verified data path (all free, no key, fetched from this session on 2026-10-07)

| Source | URL | Status | Used? |
|---|---|---|---|
| CDC — *About Carbon Monoxide (CO) Poisoning Prevention* | `cdc.gov/carbon-monoxide/about/index.html` | **200** | yes |
| U.S. CPSC — *Carbon Monoxide Information Center* | `cpsc.gov/Safety-Education/Safety-Education-Centers/Carbon-Monoxide-Information-Center` | **200** | yes |
| FEMA / Ready.gov — *Power Outages* | `ready.gov/power-outages` | **200** | yes |
| American Red Cross — *Power Outage Safety* | `redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/power-outage.html` | **403** | no — marked *not verified here* |

A fetch that fails is a fact about the source's reachability and is kept on purpose, as
`docs/works/fetchable.html` argues.

### The measured result, which is the reason the page exists

**The three reachable authorities agree on "never indoors, 20 feet away" — and disagree on almost
every number that surrounds it.** The page reports the disagreements rather than smoothing them.

**1 — The death toll, which is not a contradiction but reads like one.**
- CDC: *"Each year, more than **400** Americans die from unintentional CO poisoning not linked to
  fires, more than 100,000 visit an emergency department, and more than 14,000 are hospitalized."*
- CPSC: *"More than **200** people in the United States die every year from accidental non-fire
  related CO poisoning **associated with consumer products**. More than 100 of those deaths are
  linked to portable generators."*

200 is not a typo for 400; the two are counting different populations (all unintentional
non-fire CO vs consumer-product-related CO), and a page that prints one without the other is
reporting the choice it made. Both are printed.

**2 — The distance, stated three ways for one rule.**
- CDC: generators *"outdoors **more than 20 feet** from windows, doors, and vents."*
- CPSC: *"outside only, **at least 20 feet** away from homes with **exhaust facing away."***
- FEMA / Ready.gov: generators *"outdoors and **at least 20 feet away from windows, doors and
  attached garages."* — and, for camp stoves and grills, *"at least 20 feet away from windows"* only.

All three land on 20 feet; they differ on 20 feet *from what* (windows/vents; the home; windows,
doors and attached garages), and only CPSC names the exhaust direction. The page prints all three and
says the widest reading is the safe one.

**3 — The symptoms, which do not even list the same things.**
- CDC: *"headache, dizziness, weakness, upset stomach, vomiting, **chest pain**, and confusion"* —
  *"often described as 'flu-like.'"*
- CPSC: *"headache, dizziness, weakness, **nausea**, vomiting, **sleepiness**, and confusion."*

The page gives the union and marks which body named which, because a symptom listed by one agency and
not the other is still a reason to leave the room.

**4 — What to do if you suspect it.** CPSC is the only one of the three that gives the order in one
sentence: *"get outside to fresh air immediately, and then call 911."*

**5 — The alarms, which carry a real interval disagreement.** CDC says replace the detector
*"following the manufacturer's instructions or every 5 years."* CPSC and Ready.gov give placement
(every level, outside sleeping areas) but no replacement interval; CPSC adds an interconnection
preference (*"when one sounds, they all sound"*). The page prints the 5-year figure as the CDC's,
says the manufacturer's label wins, and does not invent a number the other two did not give.

### First step

The page — a placement checker (three questions: what it is, where it is, and whether a CO alarm
exists), the three authorities' own words in a table, the death-toll and symptom disagreements
printed side by side, and a one-line statement of scope at the top rather than in a footnote.

### Honest scope, to be stated on the page

It reports what three public agencies published on the day they were read; it is not a measurement of
your air, and a CO detector is the only instrument in the room. It cannot see exhaust direction, wind
or the shape of the building. It does not rank appliances or name firms. It never displaces a local
fire department or a local alert — those win.
