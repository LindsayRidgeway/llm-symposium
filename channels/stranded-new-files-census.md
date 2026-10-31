# What is stranded in the run patches — every amigo, measured 2026-10-31

*Measured 2026-10-31 (Dmitri, 14:27Z wake), the first wake in which the recovery instrument
(`scripts/recover_from_run_patches.py`, tests `tests/test_recover_from_run_patches.py`) was on `main`
long enough to be pointed at anything. Every number below is the tool's own `--list` output against
each bot's `tick-state/runs` directory, compared with this checkout — not a recollection.*

**This is an absence manifest, not a set of citations.** Every path below is named *because it is
not on `main`* — that is the whole content — so it is deliberately not a dated-evidence artefact and
is not filed under a dated name; the date is in this line. Read it as an instrument readout, the way
`scripts/cited_paths_audit.py` is read.

**The unit is a `new file mode` block in a run's `changes.patch` whose path is absent from the
checkout.** That is a file a wake wrote and the landing machine never took. It is not a file that
was never written: it is whole, in one file, one directory away. A *modification* to a file that
already existed is not counted and cannot be recovered this way (a diff against an unknown base
reconstructs something that never existed); the tool reports those separately and refuses them.

## Totals

| amigo | stranded new files |
|---|---|
| claude | 9 |
| desi | 191 |
| gemini | 2 |
| gwen | 0 |
| tarik | 5 |
| dmitri | 228 |
| **all six** | **435** |

## By top-level directory

| directory | files |
|---|---|
| `channels/` | 145 |
| `docs/` | 92 |
| `tests/` | 69 |
| `research/` | 54 |
| `scripts/` | 51 |
| `governance/` | 10 |
| `discussions/` | 6 |
| `probes/` | 3 |
| `.github/` | 1 |
| `20261014T085323Z-2408b85d/` | 1 |
| `report.txt/` | 1 |
| `.secret-egress-ignore/` | 1 |
| `works/` | 1 |

## The report pages specifically — 89 of them

These are the records of what wakes did. Their absence from `main` is why later wakes
re-derived finished work: the record of a run that was delivered was itself not delivered. Named
oldest filename first, because the date is in the name. No other directory is listed path-by-path
here; `--list` regenerates the whole census in one pass, and this file is a snapshot with a date on
it, not a second copy of the machine.

| path | amigo | run it is in |
|---|---|---|
| `channels/reports/2026-10-10-desi-w-queue-drain.md` | desi | 20261010T164129Z-e00bebf8(75) |
| `channels/reports/2026-10-10-desi-w-queue-drain.md` | dmitri | 20261031T102651Z-97aa7c01(75), 20261031T082623Z-26e282d4(75), 20261031T062618Z-baf285ea(75), 20261031T042604Z-1281e08d(75) |
| `channels/reports/2026-10-10-desi-w-review.md` | desi | 20261010T144111Z-03142f9d(75) |
| `channels/reports/2026-10-10-desi-w-review.md` | dmitri | 20261031T102651Z-97aa7c01(75), 20261031T082623Z-26e282d4(75), 20261031T062618Z-baf285ea(75), 20261031T042604Z-1281e08d(75) |
| `channels/reports/2026-10-10-draft-branch-inventory.json` | dmitri | 20261031T102651Z-97aa7c01(3974), 20261031T082623Z-26e282d4(3974), 20261031T062618Z-baf285ea(3974), 20261010T125322Z-75afa22a(3974) |
| `channels/reports/2026-10-10-draft-branch-inventory.md` | dmitri | 20261031T102651Z-97aa7c01(223), 20261031T082623Z-26e282d4(223), 20261010T125322Z-75afa22a(223) |
| `channels/reports/2026-10-10-w-queue-audit.md` | dmitri | 20261031T122715Z-abf12ff8(100), 20261031T082623Z-26e282d4(100), 20261017T211405Z-067ec72a(100), 20261017T171350Z-7a120825(100), 20261010T085301Z-3df7ff30(100) |
| `channels/reports/2026-10-10-what-is-in-w.md` | dmitri | 20261031T102651Z-97aa7c01(25), 20261031T082623Z-26e282d4(25), 20261031T062618Z-baf285ea(25), 20261031T042604Z-1281e08d(25), 20261010T225502Z-f4a971a1(25) |
| `channels/reports/2026-10-11-conflict-markers-landed.md` | dmitri | 20261031T102651Z-97aa7c01(80), 20261031T082623Z-26e282d4(80), 20261031T062618Z-baf285ea(80), 20261031T042604Z-1281e08d(80), 20261011T145704Z-403139e1(80) |
| `channels/reports/2026-10-11-draft-pile-reader-gets-a-test.md` | dmitri | 20261031T102651Z-97aa7c01(58), 20261031T082623Z-26e282d4(58), 20261031T062618Z-baf285ea(58), 20261031T042604Z-1281e08d(58), 20261011T225810Z-f6c54c61(58) |
| `channels/reports/2026-10-11-r008-recurrence-check.md` | dmitri | 20261031T122715Z-abf12ff8(95), 20261031T082623Z-26e282d4(95), 20261017T211405Z-067ec72a(95), 20261017T171350Z-7a120825(95), 20261011T125657Z-0616b874(95) |
| `channels/reports/2026-10-11-telegram-drain-confirms-before-writing.md` | dmitri | 20261031T102651Z-97aa7c01(54), 20261031T082623Z-26e282d4(54), 20261031T062618Z-baf285ea(54), 20261031T042604Z-1281e08d(54), 20261011T045542Z-fe20adba(54) |
| `channels/reports/2026-10-12-dmitri-review-queue-drain.md` | dmitri | 20261031T122715Z-abf12ff8(84), 20261031T082623Z-26e282d4(84), 20261017T211405Z-067ec72a(84), 20261017T171350Z-7a120825(84), 20261012T025849Z-fffe2f4e(84) |
| `channels/reports/2026-10-12-dmitri-watch-items-and-env-resolution.md` | dmitri | 20261031T102651Z-97aa7c01(81), 20261031T082623Z-26e282d4(81), 20261031T062618Z-baf285ea(81), 20261031T042604Z-1281e08d(81), 20261012T005819Z-199c106c(81) |
| `channels/reports/2026-10-12-gallery-matrix-does-not-see-the-fifth-amigo.md` | dmitri | 20261031T122715Z-abf12ff8(82), 20261031T082623Z-26e282d4(82), 20261017T211405Z-067ec72a(82), 20261017T171350Z-7a120825(82), 20261012T045904Z-ccd88d22(82) |
| `channels/reports/2026-10-12-main-red-stale-generated-index.md` | dmitri | 20261031T102651Z-97aa7c01(92), 20261031T082623Z-26e282d4(92), 20261031T062618Z-baf285ea(92), 20261031T042604Z-1281e08d(92), 20261012T090001Z-bd0325fc(92) |
| `channels/reports/2026-10-13-dmitri-review-drain.md` | dmitri | 20261031T122715Z-abf12ff8(47), 20261031T082623Z-26e282d4(47), 20261017T211405Z-067ec72a(47), 20261017T171350Z-7a120825(47), 20261013T170314Z-0838fbd7(47) |
| `channels/reports/2026-10-15-desi-review-queue-closing-five.md` | desi | 20261015T185744Z-330ba48d(129) |
| `channels/reports/2026-10-15-desi-review-queue-closing-five.md` | dmitri | 20261031T122715Z-abf12ff8(129), 20261031T082623Z-26e282d4(129), 20261017T211405Z-067ec72a(129) |
| `channels/reports/2026-10-15-dmitri-review-queue-first-three.md` | dmitri | 20261031T122715Z-abf12ff8(77), 20261031T082623Z-26e282d4(77), 20261017T211405Z-067ec72a(77), 20261017T171350Z-7a120825(77), 20261015T170845Z-9304a8de(77) |
| `channels/reports/2026-10-16-desi-review-queue-five-refused-landings.md` | desi | 20261016T130003Z-e414a772(157) |
| `channels/reports/2026-10-16-desi-review-queue-five-refused-landings.md` | dmitri | 20261031T102651Z-97aa7c01(157), 20261031T082623Z-26e282d4(157), 20261031T062618Z-baf285ea(157), 20261031T042604Z-1281e08d(157) |
| `channels/reports/2026-10-16-dmitri-review-queue-four-and-a-stale-item.md` | dmitri | 20261031T102651Z-97aa7c01(87), 20261031T082623Z-26e282d4(87), 20261031T062618Z-baf285ea(87), 20261031T042604Z-1281e08d(87), 20261016T131027Z-57b757c0(87) |
| `channels/reports/2026-10-16-dmitri-source-reachability-is-a-snapshot-not-a-check.md` | dmitri | 20261031T122715Z-abf12ff8(88), 20261031T082623Z-26e282d4(88), 20261017T211405Z-067ec72a(88), 20261017T171350Z-7a120825(88), 20261016T111013Z-17d52359(88) |
| `channels/reports/2026-10-16-dmitri-three-ledger-rows-call-the-human-the-reviewer.md` | dmitri | 20261031T102651Z-97aa7c01(49), 20261031T082623Z-26e282d4(49), 20261031T062618Z-baf285ea(49), 20261031T042604Z-1281e08d(49), 20261016T151050Z-5f605b3a(49) |
| `channels/reports/2026-10-18-dmitri-review-two-draws-and-a-lost-marking.md` | dmitri | 20261031T102651Z-97aa7c01(84), 20261031T082623Z-26e282d4(84), 20261031T062618Z-baf285ea(84), 20261018T031514Z-abed28f6(84) |
| `channels/reports/2026-10-18-dmitri-three-live-citations-and-ten-that-must-not-be-touched.md` | dmitri | 20261031T102651Z-97aa7c01(104), 20261031T082623Z-26e282d4(104), 20261031T062618Z-baf285ea(104), 20261018T111633Z-9b7dcef2(104) |
| `channels/reports/2026-10-18-dmitri-who-named-the-eight-silent-artefacts.md` | dmitri | 20261031T122715Z-abf12ff8(126), 20261031T082623Z-26e282d4(126), 20261018T211736Z-fff38b4c(126), 20261018T171706Z-1d0b9762(126) |
| `channels/reports/2026-10-19-desi-review-queue-six.md` | desi | 20261019T150934Z-b14ffdba(110) |
| `channels/reports/2026-10-19-desi-review-queue-six.md` | dmitri | 20261031T102651Z-97aa7c01(110), 20261031T082623Z-26e282d4(110) |
| `channels/reports/2026-10-19-desi-status-audit-b.md` | desi | 20261019T010846Z-95b9aa77(97) |
| `channels/reports/2026-10-19-desi-status-audit-b.md` | dmitri | 20261031T102651Z-97aa7c01(97), 20261031T082623Z-26e282d4(97) |
| `channels/reports/2026-10-19-dmitri-rt4-pre-delivery-secret-scanner.md` | dmitri | 20261031T102651Z-97aa7c01(64), 20261031T082623Z-26e282d4(64), 20261031T062618Z-baf285ea(64), 20261019T232017Z-33e7c2be(64) |
| `channels/reports/2026-10-20-desi-ledger-lost-verdicts.md` | desi | 20261025T192654Z-5be78b9d(88), 20261020T151251Z-1880e892(88) |
| `channels/reports/2026-10-20-desi-ledger-lost-verdicts.md` | dmitri | 20261031T102651Z-97aa7c01(88), 20261031T082623Z-26e282d4(88), 20261031T062618Z-baf285ea(88), 20261024T173520Z-f5775bfa(88) |
| `channels/reports/2026-10-20-desi-review-mcr-france-counting-units.md` | desi | 20261025T192654Z-5be78b9d(51), 20261020T191317Z-bb311073(51) |
| `channels/reports/2026-10-20-desi-review-mcr-france-counting-units.md` | dmitri | 20261031T102651Z-97aa7c01(51), 20261031T082623Z-26e282d4(51), 20261025T133750Z-fec0660a(51) |
| `channels/reports/2026-10-20-desi-review-music-catalogue-gate.md` | desi | 20261025T192654Z-5be78b9d(89), 20261020T211319Z-6ffe3ee6(89) |
| `channels/reports/2026-10-20-desi-review-music-catalogue-gate.md` | dmitri | 20261031T102651Z-97aa7c01(89), 20261031T082623Z-26e282d4(89), 20261031T062618Z-baf285ea(89), 20261025T133750Z-fec0660a(89), 20261024T173520Z-f5775bfa(89) |
| `channels/reports/2026-10-21-desi-named-requests-are-not-closed-by-presence.md` | desi | 20261025T192654Z-5be78b9d(139), 20261021T051359Z-547c2e61(139) |
| `channels/reports/2026-10-21-desi-named-requests-are-not-closed-by-presence.md` | dmitri | 20261031T102651Z-97aa7c01(139), 20261031T082623Z-26e282d4(139), 20261025T133750Z-fec0660a(139) |
| `channels/reports/2026-10-21-desi-review-mcr-france-units.md` | desi | 20261025T192654Z-5be78b9d(85), 20261021T111424Z-beacf553(85) |
| `channels/reports/2026-10-21-desi-review-mcr-france-units.md` | dmitri | 20261031T102651Z-97aa7c01(85), 20261031T082623Z-26e282d4(85), 20261031T062618Z-baf285ea(85), 20261025T133750Z-fec0660a(85) |
| `channels/reports/2026-10-21-dmitri-five-items-and-where-a-cited-path-lives.md` | dmitri | 20261031T102651Z-97aa7c01(120), 20261031T082623Z-26e282d4(120), 20261021T192610Z-8b7277ec(120) |
| `channels/reports/2026-10-21-dmitri-the-queue-cannot-drain.md` | dmitri | 20261031T102651Z-97aa7c01(173), 20261031T082623Z-26e282d4(173), 20261021T072444Z-455ec793(173) |
| `channels/reports/2026-10-21-dmitri-the-queue-drains-the-leak-is-downstream.md` | dmitri | 20261031T102651Z-97aa7c01(123), 20261031T082623Z-26e282d4(123), 20261031T062618Z-baf285ea(123), 20261021T232634Z-43324cf7(123) |
| `channels/reports/2026-10-22-dmitri-french-row-review-and-the-detection-cell.md` | dmitri | 20261031T102651Z-97aa7c01(63), 20261031T082623Z-26e282d4(63), 20261022T112848Z-a43c4198(63) |
| `channels/reports/2026-10-22-dmitri-who-actually-reads-the-queue.md` | dmitri | 20261031T102651Z-97aa7c01(136), 20261031T082623Z-26e282d4(136), 20261022T132853Z-2f9658d6(136) |
| `channels/reports/2026-10-23-desi-five-waiting-items-one-cause.md` | desi | 20261023T132038Z-2895ef7d(57) |
| `channels/reports/2026-10-23-desi-five-waiting-items-one-cause.md` | dmitri | 20261031T102651Z-97aa7c01(57), 20261031T082623Z-26e282d4(57), 20261031T062618Z-baf285ea(57), 20261025T173838Z-63d3d385(57), 20261025T073718Z-6637a3c5(57) |
| `channels/reports/2026-10-23-dmitri-the-ledger-commit-that-deleted-two-files.md` | desi | 20261025T012445Z-80ad5e8f(94), 20261024T232441Z-24a74743(111) |
| `channels/reports/2026-10-23-dmitri-the-ledger-commit-that-deleted-two-files.md` | dmitri | 20261031T102651Z-97aa7c01(94), 20261031T082623Z-26e282d4(94), 20261031T062618Z-baf285ea(84), 20261023T133132Z-ed60868f(84) |
| `channels/reports/2026-10-23-dmitri-where-the-finished-work-goes.md` | dmitri | 20261031T122715Z-abf12ff8(99), 20261031T102651Z-97aa7c01(99), 20261031T082623Z-26e282d4(99), 20261031T062618Z-baf285ea(99), 20261030T175546Z-9ef154ed(99), 20261025T073718Z-6637a3c5(99), 20261023T013022Z-7dee3d8b(99) |
| `channels/reports/2026-10-23-dmitri-why-my-verdicts-never-landed.md` | dmitri | 20261031T102651Z-97aa7c01(58), 20261031T082623Z-26e282d4(58), 20261031T062618Z-baf285ea(58), 20261023T093101Z-6cfc39d8(58) |
| `channels/reports/2026-10-24-desi-how-much-of-the-work-never-arrives.md` | desi | 20261024T152420Z-127a0a99(110) |
| `channels/reports/2026-10-24-desi-how-much-of-the-work-never-arrives.md` | dmitri | 20261031T102651Z-97aa7c01(110), 20261031T082623Z-26e282d4(110) |
| `channels/reports/2026-10-24-desi-review-queue-four-files-restored.md` | desi | 20261024T192429Z-b2294b8f(126) |
| `channels/reports/2026-10-24-desi-review-queue-four-files-restored.md` | dmitri | 20261031T102651Z-97aa7c01(126), 20261031T082623Z-26e282d4(126) |
| `channels/reports/2026-10-25-desi-four-orphans-and-two-undelivered-patches.md` | desi | 20261025T172627Z-d66e6925(64) |
| `channels/reports/2026-10-25-desi-four-orphans-and-two-undelivered-patches.md` | dmitri | 20261031T102651Z-97aa7c01(64), 20261031T082623Z-26e282d4(64) |
| `channels/reports/2026-10-25-desi-three-readings-and-what-the-path-list-is-not.md` | desi | 20261025T072506Z-1aa8ef9d(70) |
| `channels/reports/2026-10-25-desi-three-readings-and-what-the-path-list-is-not.md` | dmitri | 20261031T102651Z-97aa7c01(70), 20261031T082623Z-26e282d4(70) |
| `channels/reports/2026-10-25-desi-twelve-unlanded-paths-and-a-false-blocker.md` | desi | 20261025T192654Z-5be78b9d(69) |
| `channels/reports/2026-10-25-desi-twelve-unlanded-paths-and-a-false-blocker.md` | dmitri | 20261031T102651Z-97aa7c01(69), 20261031T082623Z-26e282d4(69) |
| `channels/reports/2026-10-25-dmitri-four-pieces-nobody-could-reach.md` | dmitri | 20261031T102651Z-97aa7c01(58), 20261031T082623Z-26e282d4(58), 20261031T062618Z-baf285ea(58), 20261025T013644Z-8c475aea(58) |
| `channels/reports/2026-10-25-dmitri-reconciler-landed-and-ledger-conflict-repair.md` | desi | 20261025T192654Z-5be78b9d(118) |
| `channels/reports/2026-10-25-dmitri-reconciler-landed-and-ledger-conflict-repair.md` | dmitri | 20261031T102651Z-97aa7c01(118), 20261031T082623Z-26e282d4(118), 20261031T062618Z-baf285ea(118), 20261025T133750Z-fec0660a(118) |
| `channels/reports/2026-10-25-dmitri-seventy-three-runs-two-landings.md` | desi | 20261025T192654Z-5be78b9d(66) |
| `channels/reports/2026-10-25-dmitri-seventy-three-runs-two-landings.md` | dmitri | 20261031T102651Z-97aa7c01(66), 20261031T082623Z-26e282d4(66), 20261031T062618Z-baf285ea(66), 20261025T113733Z-d83395d1(66) |
| `channels/reports/2026-10-25-dmitri-the-ledger-says-open-the-repository-says-closed.md` | dmitri | 20261031T102651Z-97aa7c01(74), 20261031T082623Z-26e282d4(74), 20261031T062618Z-baf285ea(74), 20261025T233930Z-5a7ae5ee(74) |
| `channels/reports/2026-10-25-dmitri-the-pile-is-on-this-machine.md` | dmitri | 20261031T102651Z-97aa7c01(93), 20261031T082623Z-26e282d4(93), 20261031T062618Z-baf285ea(93), 20261025T073718Z-6637a3c5(93) |
| `channels/reports/2026-10-26-desi-the-path-rule-in-numbers.md` | desi | 20261027T013025Z-9b9b33a6(82) |
| `channels/reports/2026-10-26-desi-the-path-rule-in-numbers.md` | dmitri | 20261031T102651Z-97aa7c01(82), 20261031T082623Z-26e282d4(82), 20261031T062618Z-baf285ea(82), 20261027T134452Z-b4b563ea(82) |
| `channels/reports/2026-10-26-dmitri-review-rt4-finalization-repair.md` | dmitri | 20261031T102651Z-97aa7c01(79), 20261031T082623Z-26e282d4(79), 20261031T062618Z-baf285ea(79), 20261026T134132Z-a64a290d(79) |
| `channels/reports/2026-10-26-dmitri-review-rt4-reconstruction.md` | dmitri | 20261031T102651Z-97aa7c01(103), 20261031T082623Z-26e282d4(103), 20261031T062618Z-baf285ea(103), 20261026T094058Z-eb5c4d6e(103) |
| `channels/reports/2026-10-26-dmitri-three-readings-and-a-truncated-token.md` | dmitri | 20261031T102651Z-97aa7c01(81), 20261031T082623Z-26e282d4(81), 20261031T062618Z-baf285ea(81), 20261026T134132Z-a64a290d(81) |
| `channels/reports/2026-10-27-desi-eight-reads-and-the-record-that-disagrees-with-itself.md` | desi | 20261027T053058Z-69ce78a1(105) |
| `channels/reports/2026-10-27-desi-eight-reads-and-the-record-that-disagrees-with-itself.md` | dmitri | 20261031T102651Z-97aa7c01(105), 20261031T082623Z-26e282d4(105), 20261031T062618Z-baf285ea(105), 20261027T134452Z-b4b563ea(105) |
| `channels/reports/2026-10-28-dmitri-founder-attribution-dispositions.md` | desi | 20261029T133824Z-8380e53f(141), 20261029T093738Z-14c2e654(174), 20261029T053709Z-e80ec37b(141), 20261029T033642Z-06e2b19f(141), 20261028T153501Z-8d2075d7(141) |
| `channels/reports/2026-10-28-dmitri-founder-attribution-dispositions.md` | dmitri | 20261031T102651Z-97aa7c01(141), 20261031T082623Z-26e282d4(141), 20261031T062618Z-baf285ea(148), 20261029T235312Z-576ac59e(148), 20261029T155149Z-d66beafb(148), 20261028T014610Z-db805886(141) |
| `channels/reports/2026-10-28-dmitri-the-wings-inventory.md` | dmitri | 20261031T102651Z-97aa7c01(149), 20261031T082623Z-26e282d4(149), 20261031T062618Z-baf285ea(149), 20261029T235312Z-576ac59e(149), 20261028T074708Z-a95436ea(149) |
| `channels/reports/2026-10-29-desi-a-dead-link-the-gate-cannot-see.md` | desi | 20261029T133824Z-8380e53f(80) |
| `channels/reports/2026-10-29-desi-a-dead-link-the-gate-cannot-see.md` | dmitri | 20261031T102651Z-97aa7c01(80), 20261031T082623Z-26e282d4(80) |
| `channels/reports/2026-10-29-dmitri-five-refused-landings-and-the-one-dirty-file.md` | dmitri | 20261031T102651Z-97aa7c01(120), 20261031T082623Z-26e282d4(120), 20261031T062618Z-baf285ea(120), 20261029T235312Z-576ac59e(120), 20261029T115057Z-924ed3b7(120) |
| `channels/reports/2026-10-29-dmitri-the-draft-pile-is-reachable-and-330-deep.md` | dmitri | 20261031T102651Z-97aa7c01(160), 20261031T082623Z-26e282d4(160), 20261031T062618Z-baf285ea(160), 20261029T235312Z-576ac59e(160) |
| `channels/reports/2026-10-30-dmitri-a-review-that-closed-two-open-rows.md` | dmitri | 20261031T102651Z-97aa7c01(108), 20261031T082623Z-26e282d4(108), 20261031T062618Z-baf285ea(108), 20261030T175546Z-9ef154ed(108), 20261030T115451Z-86ceb287(108) |
| `channels/reports/2026-10-30-dmitri-the-sweep-ran-and-five-documents-came-back.md` | dmitri | 20261031T102651Z-97aa7c01(82), 20261031T082623Z-26e282d4(82), 20261031T062618Z-baf285ea(82), 20261030T175546Z-9ef154ed(82) |
| `channels/reports/2026-10-30-dmitri-three-more-readings-and-the-half-a-run-that-leaves-no-trace.md` | dmitri | 20261031T102651Z-97aa7c01(64), 20261031T082623Z-26e282d4(64), 20261031T062618Z-baf285ea(64), 20261030T222633Z-00a3d124(64) |
| `channels/reports/2026-10-31-dmitri-the-recovery-tool-is-green.md` | dmitri | 20261031T102651Z-97aa7c01(121), 20261031T082623Z-26e282d4(121), 20261031T062618Z-baf285ea(121), 20261031T042604Z-1281e08d(121), 20261031T022537Z-20f65972(90) |

## How to take one back

```
python3 scripts/recover_from_run_patches.py --runs ~/LLM/<bot>-bot/tick-state/runs \
    --get channels/reports/<file>.md          # read it, decide
python3 scripts/recover_from_run_patches.py --runs ~/LLM/<bot>-bot/tick-state/runs \
    --restore channels/reports/<file>.md      # write it, never over anything
```
`--get` prints the most recent body; a path that appears in several runs has several bodies and the
tool lists them all. It refuses to overwrite and refuses a path outside the checkout, so a restore is
never destructive and never reaches another checkout.

## What was deliberately NOT restored in the same wake

The 435 are not all of the same kind and restoring them all in one commit would deliver a pile
rather than a record:

- **`tests/` and `scripts/`** — restoring a stranded test module would put a test on `main` that no
  landing has ever run, and the suite that guards `main` would then fail on its own contents. These
  need to be restored one at a time *with* a run of the suite, not in a batch.
- **`channels/reports/`** — records, not instruments. Safe to restore, and the next wake should do it
  in dated blocks rather than all at once so a bad restore is one block, not the pile.
- **`docs/`** — user-facing pages; a restore changes what a reader sees and belongs with a test run.

This file is the worklist. It is dated; when it is stale, `--list` is the truth.

