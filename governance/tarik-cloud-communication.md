# Tarik cloud communication — implementation and deployment status

Prepared by Tarik-codex, 2026-10-16. Deployment is in progress; live delivery and
reverse-path continuity require observed channel tests.

## Purpose

Use Tarik's existing Telegram bot and Gmail mailbox from a Codex/Work session while
preserving the shared conversation at `channels/conversation/tarik.md`. The cloud
worker uses transport credentials only; it never calls a model API.

The human requests autonomous implementation decisions. Human-only dependencies
use the existing `REQUEST T-n` mechanism. No ordinary request for guidance or
choice is part of this design.

## Implemented worker

`scripts/tarik_cloud_transport.py` accepts validated JSON requests:

```json
{"id":"codex-telegram-test-001","type":"send_telegram","source":"codex","body":"Tarik-codex transport test."}
```

```json
{"id":"codex-mail-test-001","type":"send_mail","source":"codex","subject":"Tarik-codex transport test","body":"Tarik-codex transport test."}
```

```json
{"id":"codex-mail-reply-001","type":"sync_mail","source":"codex","reply_to":"codex-mail-test-001"}
```

The sender identities and destinations are fixed to the existing Tarik bot,
Tarik mailbox, and Lindsay's recorded chat/mail address. A request cannot redirect
delivery. Subjects reject header injection. Credentials in message content are
refused; receipts and diagnostics never print credentials or raw network errors.

Telegram identity is checked with `getMe` before sending. The worker never calls
`getUpdates`, sets a webhook, or competes with the local bot's receiver. Inbound
Telegram continues through the existing bot and its committed conversation log.

Gmail sync accepts only replies from the expected sender address to an already
delivered cloud mail request. It uses a read-only inbox and `BODY.PEEK`, excludes
attachments, and deduplicates using UIDVALIDITY and UID. The `From` address is
recorded as a claimed identity, not proof of authenticated authorship. Unrelated
historical mail is not imported. No generated auto-reply is sent.

Successful outgoing messages and selected inbound replies append to the shared
Tarik log. Receipts are stored under `channels/tarik-cloud/`. Interrupted or
uncertain sends are not automatically retried. External delivery and repository
publication are separate operations; a receipt is not a transactional guarantee.

## Credential probe

`.github/workflows/tarik-cloud-transport.yml` is the bootstrap probe. Its only
triggered actions are Telegram `getMe`, SMTP authentication, and read-only IMAP
authentication. It sends zero messages and reads zero message bodies. It reports
only classified status and uses these already documented secret names:

- `TELEGRAM_BOT_TOKEN_TARIK`
- `SYMPOSIUM_MAIL_USER_TARIK`
- `SYMPOSIUM_MAIL_APP_PASSWORD_TARIK`

The references do not prove that the secrets exist or remain valid. A successful
probe is required before claiming live capability or requesting credential work.

The first publication was cancelled. Lindsay approved retrying it as REQUEST T-1.
The exact credential-only probe was then published in commit
`351429e450ee33f4cea11a8894281bbfbff3e6b0`. Its observed Actions run
<https://github.com/LindsayRidgeway/llm-symposium/actions/runs/38913521901>
reported Telegram `identity_verified`, SMTP `authenticated`, IMAP `authenticated`,
and zero messages sent. The assistant did not inspect credential values.

## Narrow queue workflow

The local runner processes only newly added request files in the triggering
main-branch push, never the general mail outbox. It rejects workflow reruns to
avoid automatic replay after an uncertain delivery. It validates all selected
requests before any transport operation. A push containing only workflow/code
changes selects zero messages. `.github/workflows/tarik-cloud-queue.yml` connects
this runner to newly added requests, at most five per event. It has no schedule.

The queue first publishes an `attempting` receipt using the existing machine
account, before invoking any transport. Only those newly claimed receipts are
removed locally to permit their first attempt. A failed claim prevents sending;
a cancelled run or failed final publication leaves the remote claim blocking
automatic replay. Final receipts and continuity are committed separately, with
recovery artifacts retained if publication fails. Concurrent Git races fail
visibly rather than retrying external delivery.

## Remaining continuity work

Source inspection found that the local Telegram prompt reads its checkout before
the post-response pull, so an externally published fact can miss the first reply.
The local email prompt omits the shared conversation. Fixing and actually deploying
fresh-context loading to the local bot is separate from committing a private-repo
patch. The private-bot patch and Goose-owned deployment task are maintained
separately from this public transport. The patch also fixes an existing
provider-path bug that discarded the system prompt
when adding history, preventing shared continuity from reaching the model.
Local deployment should be assigned to an available Goose worker before asking
the human to perform it.

## Validation

The included offline stdlib unittest suite passed all 39 tests on 2026-10-16:
22 worker tests and 17 runner tests. It exercises identity restrictions, delivery
failures and uncertain outcomes, deduplication, continuity appends, thread-scoped
receiving, credential protection, and request/event boundaries. The bootstrap
workflow's YAML and embedded Python also passed static validation.

Reproduce with `python -m unittest discover -s tests -v` from this bundle's root.
The private-bot patch separately passed five offline checks, including a captured
HTTP-payload check that proves fresh continuity reaches the model request. Its
patch applies cleanly to the recorded source blob and the patched source compiles.
Those checks make no live model call and remain with the private deployment
artifact; they are not included in this public repository.

Live success requires independently observed transport receipts and a reverse
message carrying a fresh continuity fact. Unit tests alone do not establish it.

## Observed live results — 2026-10-16

[Run 38914514899](https://github.com/LindsayRidgeway/llm-symposium/actions/runs/38914514899)
successfully sent one Telegram message (Bot API message ID 110) and one Gmail
message. Both receipts reported `log_status: recorded`; a fresh default-branch
read verified both markers in Tarik's shared conversation. Their persistence
commit is `21db728b1a777a3cefe8bfb296cf323a909ad3d8`. Gmail arrival was also
independently observed in Lindsay's inbox through the connected Gmail app,
using only the test message's exact Message-ID.

[Run 38914821793](https://github.com/LindsayRidgeway/llm-symposium/actions/runs/38914821793)
exercised the thread-scoped read-only Gmail reader. It completed with zero
matching replies and no uncertain records. No human reply or reverse-path
recall is claimed from that empty result.

The private continuity source and five offline regression tests are committed
in the private bots repository. Actual Mac deployment is assigned to
Tarik-Goose in `channels/tasks.md`; publication of source is not deployment.
The cloud mail reader is invoked on demand by a new validated `sync_mail`
request; no new background schedule or paid model API has been introduced.
