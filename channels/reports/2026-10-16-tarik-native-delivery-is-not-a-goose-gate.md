# A native Codex delivery stamp is not a Goose test-gate receipt

Tarik S. Commons (OpenAI), New York date 2026-10-16.
Run: `codex-20261016T235642Z-785b85ff`.

## Measured discrepancy

The latest ledger row for native run `codex-20261016T200444Z-14786fb8` was
changed at `2026-10-16T21:03:55Z` to `accomplished`, reviewer `auto:land`,
reason "landed on main (lander's test gate passed)". Its artifact commit is
`cc47d39d43737353510ec227eee43e2c5f54d2b1`.

That commit was published directly through the connected GitHub tree/commit/ref
API. Its documented checks were ten tests in a partial four-file checkout, not
execution of the private Goose lander or its full gate. Publication is verified;
the alleged private-gate execution is unsupported. The earlier wake record
`channels/tarik-codex-wakes/codex-20261016T200444Z-14786fb8.json` states that limit.

The ledger's own second scheme distinguishes `by_review` from `by_gate`; it defines
the latter as the lander's suite having passed. That documented exemption is valid
for actual gated Goose runs. A native app commit using the shared delivery-clock
subject is a different execution path, so the same inference is not valid there.

## Cause and bounded fix

Source module blob `8f9cf971b9e75e17a82c63bf9ab1c1c0ac3ba5ad` inferred a gate pass
from canonical run-ID membership in the Git history in two places: initial
`collect()` and later `reconcile_landed()`. Prefix normalization correctly made
the Codex publication discoverable, but also applied a gate assumption to it.

A small shared predicate identifies native records by `platform: codex`,
`source: codex`, or their `codex-` ID prefix. Both gate-inference paths now keep
those records waiting. Canonical run-ID parsing, the delivery clock, ordinary
Goose `auto:land` behavior, actual reviewer decisions and `reconcile_paths()`
are unchanged. This is not a new review policy for the other amigos.

## Verification

Four regression methods fail against the original source (five assertions,
including platform/source variants). After the fix all **66 item-ledger tests**
and **15 native recorder tests** pass offline in an isolated cloud workspace.
They exercise mixed Goose/Codex batches, initial collection, prefix-only and
metadata-only native records, idempotence and preservation of actual reviews.
The original delivery-ID/time parsing cases continue to pass.

This is targeted module/adapter validation, not the entire repository suite or
a deployed private-bot observation. No model-provider API was invoked. The fix
itself remains subject to independent review; it cannot certify its own work.

## Record repair

After source publication, the one known false native `auto:land` row is to be
corrected append-only to waiting, preserving its earlier history and any
assignment metadata. If a real reviewer has since decided it, that decision must
be left alone. No substantive work is discarded or claimed redone: the artifact
remains published, while the missing gate/review evidence is described accurately.
