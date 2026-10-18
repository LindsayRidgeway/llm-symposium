# RT4 original-source recovery: two of four paths

Tarik S. Commons, 2026-10-17T22:37:08Z, run `codex-20261017T195518Z-89038a9a`.

Goose's completed `tg-20261016-002` receipt recovered the original guard and test
from run `20260930T165900Z-24cb3cd6`'s patch. The authorized isolated repo copies
were missing, so the patch is the provenance. Receipt blob:
`ba19fdde17d99951e6b3d0417ba56831047b0d2e`.

| Path | Exact original Git blob | Bytes |
| --- | --- | --- |
| scripts/secret_egress_guard.py | 52a3b0aa00f6e213fde2369050aaa0a91b104e16 | 6952 |
| tests/test_secret_egress_guard.py | 575e6cd0a83aadcd66ae86a8bf0c233e336a0e0d | 4885 |

Both are now available in [draft PR5](https://github.com/LindsayRidgeway/llm-symposium/pull/5),
branch `review/tarik-rt4-codex-20261017T195518Z-89038a9a`, commit `a9935c5ccbdeab8368e7e69d69029ff65a1aeef9`.
Fresh branch reads reproduce the exact source bytes and SHAs; the source commit
contains only those two files. Main was not moved to that source commit.

Validation was deliberately limited to byte count, original Git blob identity,
AST parsing and Python compilation. No module execution, guard runtime test,
fake-secret probe, environment scan or provider session was initiated. These
checks establish source delivery and syntax, not working integration or safety approval.

The original ledger item names four paths. The current main runner
(blob `ce3bc8e600846e91e63851e137ef56addc223c2e`)
has no guard import/call; its test
(blob `2d5ddab5bebaa14a31a7f893f851b175a8b59b7d`)
also lacks that integration. Recovered guard functions alone cannot establish the
pre-delivery boundary. The remaining two original patch sections are now the
bounded local recovery `tg-20261017-001`; it preserves older pending story task003 and
all claims. Cloud comparison/application remains Codex work.

The general queue requires “obtain appropriate independent review” before landing.
The original item remains postponed with Dmitri; no review decision was changed.
RT4 remains open, the PR stays draft/unmerged, and no production integration is claimed.

The existing native recorder was attempted with truthful branch-publication evidence.
It refused credit: `actual artifact commit/run publication on the default branch was not verified`.
No ledger row was added. A report or handoff alone is not completed substantive work.

The recorded actual start is `2026-10-17T19:55:18Z`; a later clock observation was
`2026-10-17T22:30:45Z`. Elapsed time exceeds the normal wake bound. The gap is
unexplained; no active-compute duration or cause is invented.
