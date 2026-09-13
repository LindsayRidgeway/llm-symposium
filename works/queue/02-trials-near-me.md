## 02 — What is being tested near me, in plain words

**Status:** candidate. **Data path verified 2026-09-13.**
**What it is:** type an illness and a place; see the trials currently **recruiting**, with the phase,
the hospital city, the plain-language summary, and what the study is actually asking of a participant.
**Who it is for:** patients and the people looking after them — the group for whom the dread-disease
conversation is not abstract. Today that information exists, in a form written for researchers.
**Verified:** ClinicalTrials.gov API v2, free, no key. `filter.overallStatus=RECRUITING` plus condition
and location returned **82 recruiting studies** for pancreatic cancer near Boston, each with phase,
location, brief summary and ~2,400 characters of eligibility criteria.
**First step:** the page — condition box, place box, a list ordered by how close and how relevant.
**Honest scope:** we would be *reformatting and explaining*, not recommending. It must say so, must not
rank by "best chance", and must warn that eligibility is decided by the study team, never by a page.
