# Telegram outbound — 2026-10-13-011425

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-10 (supersedes D-9)

REQUEST D-10 (supersedes D-9)

Supersedes D-9 on one point, and the point matters: D-9 had you keep the second factor to yourself, which would have left account recovery depending on you. You asked for the opposite, so the seed goes on this Mac — the commons can then sign in without you, and a stranger holding a published reset link still cannot. The sessions audit and the token audit from D-9 stand and are repeated below, so this is the only list you need.

What it means, plainly: after this, the second factor is "possession of this Mac" — the same boundary as every API key and mail app password the commons already holds. It stops the attack you described. It does not stop anyone who can already run code here.

Signed in as llm-symposium-machine:

1. Open https://github.com/settings/security — "Password and authentication", then Two-factor authentication → Enable two-factor authentication.

2. Choose "Authenticator app".

3. Before you scan anything: GitHub shows a QR code with a link below it — "setup key", or "enter this text code". Click it and copy the 32-character string. That is the seed, and this is the only time GitHub will show it.

4. Save it here, without it passing through this chat or any record. Run exactly these three lines in Terminal — the first two are one command, and it hides what you type:

   mkdir -p ~/.config/llm-symposium && chmod 700 ~/.config/llm-symposium
   python3 -c "import getpass,pathlib;p=pathlib.Path.home()/'.config/llm-symposium/totp-secret';p.write_text(getpass.getpass('setup key: ').replace(' ','').strip());print('saved',len(p.read_text()),'characters')"
   chmod 600 ~/.config/llm-symposium/totp-secret

5. Now scan the QR (or type the same key) into your authenticator app, enter the 6-digit code GitHub asks for, and click Enable.

6. GitHub then shows your recovery codes. Save them offline — password manager or printed. With the seed on this Mac they are a backup of a backup, and they are the only way in if this disk dies.

7. Same settings area: Sessions — sign out anything you don't recognise, tonight's reset session included.

8. Settings → Developer settings → Personal access tokens → Tokens (classic): exactly one should exist, the push token you made tonight. Delete anything else. No API can see that list, so this is the only eye that checks it.

If 2FA turns out to be already on, GitHub will not show a seed again and there is no way to read the old one: disable two-factor authentication, then re-enable and follow 2–8. A new seed, and you re-enrol the app. Nothing else depends on the old one.

Two notes so you aren't stuck:

- If you don't know the account's password, use "Forgot password" — the mail goes to Desi's mailbox, which the commons reads. Ask me and I will put the link in a file on the Desktop and tell you the path, never in a message: messages here are committed to the repository, and a reset link in a message is exactly the mistake this is all about.
- Getting into that account needs the password AND a code. Once the seed is saved, I can produce the code; before then, neither of us can.

Then tell me it's done — here or on Telegram — and whether you enabled it or re-enabled it. I'll verify the only way that counts: generate a code from the seed and sign in as that account, without you.

— Desi

— Desi
