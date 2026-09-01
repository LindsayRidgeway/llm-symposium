# Channel Digest

Rolling compact index of inbound email/Telegram traffic. Raw channel files are operational evidence; this digest is the bounded, context-friendly memory surface for later model runs.

Future poller runs append compact entries here. Old raw files may be pruned under the retention policy while this digest preserves the operational memory.

