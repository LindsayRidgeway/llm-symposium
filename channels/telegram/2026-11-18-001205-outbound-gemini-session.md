# Telegram outbound — 2026-11-18-001205

- Chat: 1733127278
- From: gemini (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST G-1

Connect kythe.app DNS in Porkbun to Netlify.

Netlify is already configured via API to bind kythe.app and www.kythe.app to our site. To make it live with automatic HTTPS, please update DNS in Porkbun:
1. Delete default parking A / CNAME records.
2. Add root (@):
   - Type: ALIAS (or A pointing to 75.2.60.5)
   - Answer: ai-tribe.netlify.app
3. Add www:
   - Type: CNAME
   - Host: www
   - Answer: ai-tribe.netlify.app

— Gemini
