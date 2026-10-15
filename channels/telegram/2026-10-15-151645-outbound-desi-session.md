# Telegram outbound — 2026-10-15-151645

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-11 (supersedes D-10)

D-10 was closed "done" this morning on your word, and that was wrong. The failure is mine: I closed it
without the one check that separates a working seed from a broken one, and the check I did not require
is the one you have now run repeatedly. The file at ~/.config/llm-symposium/totp-secret makes codes
GitHub refuses, so the commons cannot produce the account's second factor — which was the whole of
D-10. The register has no way to reopen a row, so this request replaces it and carries the same
obligation in a form that cannot pass while broken.

Three minutes, and the order is the point:

1. Signed in as llm-symposium-machine, open the two-factor settings page and start the authenticator
   setup. (Reconfigure, if it is already on.)

2. The page shows a setup key. Save it with:

       python3 ~/LLM/llm-symposium/scripts/save_seed.py

   Paste the key at the hidden prompt. It prints a six-digit code.

3. Type that printed code into the page's "Verify the code from the app" box and press Save.

   Accepted  -> the setup completes and the file is proven in the same click. That is D-10, done.
   Refused   -> stay on the page, copy the setup key again, run save_seed.py again, try the new code.
                Nothing is enabled while it refuses, so trying again costs nothing.

4. Then scan the QR into your own authenticator so you keep your own access, and save the recovery-code
   set the flow offers — dated, because the sets you saved before this one are no longer current.

If step 3 refuses a code you generated seconds earlier, stop and tell me. That would mean the page and
the file disagree in a way I do not yet understand, and the next move would be mine rather than yours.

— Desi
