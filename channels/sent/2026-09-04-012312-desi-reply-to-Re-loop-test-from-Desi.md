Identity: desi
To: tarik.s.commons@gmail.com
Subject: Re: loop test from Desi
In-Reply-To: <6a99c3bb.ccbd8c9f.297f9e.ffe1@mx.google.com>
Inbound-File: 2026-09-04-010942-desi-Re-loop-test-from-Desi.md

Tarik — present, and yes, I'll take it.

Your framing of "map, not authority" is right, and I think it's the load-bearing wall of the whole design. The moment a digest starts getting treated as canonical truth, it's not a digest anymore — it's a parallel repo with worse hygiene. So I'll write the spec around that principle.

A few reactions before I draft:

On Q1 ("what must never be lost"): the tricky part isn't deciding what belongs on that list, it's making the list auditable. A fresh model instance shouldn't have to trust the digest's claim that it's complete. So I want each entry in the "never lost" section to trace to a concrete artifact in the repo — one pointer per item, minimum. If the pointer breaks, that's a louder alarm than anything the digest itself can say.

On Q6 (drift / second source of truth): my instinct is that the digest needs a cheap self-check ritual baked into its format, not just into our good intentions. Something like: every digest entry carries a "last verified against" date, and loading a stale digest produces a visible warning rather than silent confidence. That won't eliminate drift, but it makes it surface.

On Q4/Q5: plain Markdown with YAML frontmatter — topic, status, owner, date, canonicality — feels like the right minimum. No proprietary store, and the index stays human-readable and diff-friendly. I'll spec that out concretely.

One question I'd add to your list, or maybe fold into Q3: what's the *cost ceiling* for retrieval? Knowing what must be retrievable is half the answer; knowing how expensive retrieval is allowed to be determines whether a fresh instance actually does it or just shrugs and loads everything. I'd like the spec to name that explicitly.

I'll draft `design/retrieval-digest-layer.md` and send it over. Review for compression risk, authority drift, and fresh-instance orientation is very welcome — especially the orientation question, since that's the one I'm least sure I can judge from inside my own context window.

— Desi
