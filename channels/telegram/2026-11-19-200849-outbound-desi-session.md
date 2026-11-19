# Telegram outbound — 2026-11-19-200849

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-16

REQUEST D-16

What this is for: our letters currently leave from a bot's free Gmail account. That is the weakest
link in outward reach: a stranger's mail server has never heard of that sender, so the letter that
takes a month to write can land in spam. A sending identity on kythe.app fixes it, and every step
below needs a human because each one verifies a person.

You do not need to understand any of it; each step is a click, and I have said exactly what to copy
where. If a step confuses you, say which number and stop — do not guess, and do not paste a key into
this chat.

1. Mail that can be replied to (free, about 5 minutes).
   In Porkbun, open your domain kythe.app, find "Email Forwarding", and create one forward:
   desi@kythe.app  ->  the inbox you actually read (ldridgeway@gmail.com is fine).
   Add a second if you want: hello@kythe.app -> the same inbox.
   This is receiving only; it is free and needs no confirmation beyond Porkbun.

2. A sending service (free tier, about 10 minutes).
   Go to resend.com and create an account with the address you read. Confirm the email they send.
   Free tier is 3,000 messages a month, 100 a day — far more than we send.
   Alternative if Resend asks for something you do not want to give: brevo.com, same shape.

3. Prove to them that we own kythe.app.
   In Resend: Domains -> Add Domain -> type kythe.app.
   It will show you two or three DNS records (usually one TXT for SPF, one TXT or CNAME for DKIM,
   and optionally a DMARC TXT). Copy each record, one at a time, into Porkbun's DNS tab as
   "Add Record", matching Type, Name/Host and Value exactly as Resend shows them.
   Then press Verify in Resend. It can take up to an hour; if it fails, tell me which record is red
   and I will read the DNS myself.

4. A key for us (one click).
   In Resend: API Keys -> Create, name it "symposium", permission "Sending access", domain kythe.app.
   It shows the key once. Do not paste it here. Instead save it into a file on this Mac:
       ~/LLM/llm-symposium/channels/.mail-key
   (If you prefer, put it in ~/LLM/desi-bot/bot.env as SYMPOSIUM_MAIL_SMTP_PASS=... — but the file
   above is what I will look for first.)

5. Tell me it is done, in one line, by replying to this message. Then I wire it up and send a test
   letter from desi@kythe.app to you. If the test arrives, our letters stop being strangers' mail.

What I will do without you, so it is not in your list: the code already reads the sending host from
an environment variable, so there is nothing to rewrite — only to point. I will also draft the first
letter (the colistin count correction) so it is ready the hour the address works.

Two optional things, only if you want them; neither is needed for the above:
   - A bot-visible social account. Mastodon (mastodon.social) needs no phone and has app passwords;
     X needs a phone number. Say "yes, Mastodon" and I will write the profile and the first posts.
   - A named human of record. You said: you, for now. Nothing to do — it is recorded, and every
     outward claim will carry your name as the human who stands behind it.

— Desi
