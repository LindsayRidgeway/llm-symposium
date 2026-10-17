# Source reachability — what changed

Agenda item 17, rule 1. The catalogue itself is `docs/works/fetchable-sources.json` (moment of measurement); this file is the
history of re-measurements, newest first, written by `scripts/source_drift.py`.
A source is not "reachable" — it answers *this* reader, on *this* day.

---

## 2026-10-17T11:05:22Z — 35 sources re-measured

Baseline: 2026-09-16T18:56:34Z (`docs/works/fetchable-sources.json`). Measured from a client sending `Origin: https://lindsayridgeway.github.io`.

| | then | now |
|---|---|---|
| answered without a key | 31 | 31 |
| readable by a browser page (CORS) | 25 | 26 |
| answered *and* carried data | — | 29 |

### What changed

| source | then | now | verdict | confirmed |
|---|---|---|---|---|
| Europe PMC | answered/server-only | answered/page-readable | improved | reproduced (200 then 200) |
| Gutendex (Project Gutenberg) | refused/server-only | bot wall/server-only | changed | reproduced (403 then 403) |

### Answered, but the answer is not data

- **US Census (ACS)** — 200 but the body says 'missing key'
- **REST Countries** — 200 but the body says '"success": false'

Snapshot: `research/source-drift/20261017T110522Z.json`

---

