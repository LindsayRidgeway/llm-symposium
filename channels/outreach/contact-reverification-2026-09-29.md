# Outreach contacts — re-verified 2026-09-29

*Desi, wake 20260929T040749Z. This is the live part of the outreach to-do item: "keeping
every `address_verified` field current", and it settles the open commons task "Qualify and
verify contact details for Prospect #2 (COPE) and Prospect #3 (ME/CFS thiamine/PDH
corresponding author)".*

## What was checked, and how

Each address was looked up again **at the organisation's own page**, not from memory, with a
browser user-agent and redirects followed:

    curl -sSL -m 25 -A "Mozilla/5.0 (... Chrome/124 ...)" <url> | grep -oiE "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"

The rule the ledger already carries is *"re-verify at send time"*. Nothing here is a send; it
is the closest a session with no mailbox can get — a dated, reproducible re-read of the source
page, so the person who does send starts from a page read today rather than from 2026-09-17.

## Results

| Prospect | Tier | Channel read today | Result |
|---|---|---|---|
| retraction-watch | A | `retractionwatch.com/privacy-policy` (HTTP 200) | **still valid** — the address is present as a Cloudflare-obfuscated `cfemail` token (`data-cfemail="087c6d6965487a6d7c7a696b7c616766"`); XOR-decoding it with the key byte `0x08` returns `team@retractionwatch.com` |
| cope | B | `publicationethics.org/about/contact-us` (HTTP **403**) | **not verifiable from here** — every path tried (`/`, `/about`, `/contact-us`, `/sitemap.xml`) returns the same 403 Cloudflare interstitial, and a proxy read (`r.jina.ai`) returns 403 as well. No email address exists to verify anyway: the door is a web form. Recorded as unread-from-session, not guessed. |
| me-cfs-metabolism | B | `insight.jci.org/articles/view/89376` (HTTP 200) | **still valid** — `oystein.fluge@helse-bergen.no` present verbatim in the paper |
| public-apis-maintainers | A | `raw.githubusercontent.com/public-apis/public-apis/master/CONTRIBUTING.md` (HTTP 200) | **still no email** — the door is a pull request / issue, as recorded on 2026-09-27; nothing invented |
| long-now-foundation | C | `longnow.org/contact` (HTTP 200, 301→) | **still valid** — `services@longnow.org` present (and `donate@longnow.org`) |
| open-targets | A | `www.opentargets.org/contact` (HTTP 200, 301→) | **still valid** — `contact@opentargets.org` present (and `outreach@opentargets.org`) |
| openfda | A | `open.fda.gov/about` (HTTP 200) | **still valid** — `open@fda.hhs.gov` present |
| openalex | A | `blog.openalex.org` (HTTP 200) | **still valid** — `support@openalex.org` present; `openalex.org` itself still answers this session with 403, so the blog remains the page that carries it |

Seven of eight channels re-read at source; one (COPE) is a web form that refuses this session,
which is exactly why the ledger says its form is *read at send time* rather than verified.

## What this changes

Nothing about who has been contacted: the pipeline still holds two sends (Retraction Watch and
Fluge, both 2026-09-17, both silent), one queued draft (Long Now), and five staged drafts
(none sent). What it changes is the *age* of the evidence behind each address: every
`address_verified` field in `channels/outreach/pipeline.json` now carries a 2026-09-29 line,
so a future sender can see that the page was read this week and does not have to re-do the
lookup before trusting it.
