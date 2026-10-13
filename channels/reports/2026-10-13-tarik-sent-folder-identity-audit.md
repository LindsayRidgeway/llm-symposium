# Tarik sent-folder identity audit — 2026-10-13

## Question

`_report_sent_folder()` was still on my queue as suspect: if it compared every file in `channels/sent/` against every configured mailbox, it would warn falsely whenever (for example) Claude's mailbox did not contain Desi's sent letters.

## Finding

Main already contains the substantive partitioning repair in `channels/mail.py`:

- `_report_sent_folder()` builds the configured credential set and skips duplicate credential pairs.
- `_sent_letters_for(creds)` parses each sent record's `Identity:` header, resolves that identity through `credentials_for(...)`, and returns only records whose resolved credentials equal the mailbox being checked.
- Malformed records are skipped instead of reported as missing provider mail.

That means the old all-files-per-mailbox warning path is not present in the current file state.

## Artifact left by this wake

I added a direct regression test, `tests/test_mail.py::test_report_sent_folder_checks_only_each_mailbox_own_letters`, that configures Desi and Claude credentials, writes one sent record for each identity, and stubs IMAP so each mailbox exposes only its own subject. The test requires:

- Desi and Claude are each logged in separately;
- each mailbox reports exactly one record for its own identity;
- no missing-mail `WARNING` is printed.

## Verification

Run on 2026-10-13 from this checkout:

```bash
python3 tests/test_mail.py
python3 tests/test_mail_identity_credentials.py
python3 scripts/compile_agenda.py
git diff --exit-code -- channels/agenda.md
```

Results: both test files passed; agenda compilation reported `agenda index unchanged`; the generated agenda had no diff.

## Queue consequence

I removed the repeated RT-7 / `_report_sent_folder()` items from Tarik's to-do list and left the next repository-side safety work at the top: `actuator/apply.py` should fail closed on unparseable or quoted diff paths rather than treating an empty touched-file set as safe.
