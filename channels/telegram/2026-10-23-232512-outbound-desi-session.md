# Telegram outbound — 2026-10-23-232512

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-13

Give the lander a fixed address on the home LAN.

Why: my SSH alias points at raspberrypi.local, which this Mac cannot resolve, so every session starts by sweeping the LAN trying to find the body. That is minutes burned each time and a chance to knock on the wrong machine.

At http://192.168.1.1 (the AT&T gateway):
1. Sign in if it asks.
2. Open LAN / IP Allocation. Some firmware labels it "DHCP Reservation" or "IP Address Allocation".
3. Find the device named raspberrypi. If names are not shown, it is the newest unknown device.
4. Reserve the address it already has. I do not need a particular number, I need it to stop changing.
5. Save. The Pi does not need a reboot.

If that menu does not exist: say so, and I will pin the address from the Pi side with nmcli. In that case I need one fact from you - whether 192.168.1.178 is inside the router's DHCP pool, or the two of us will fight over it.

When it is done, send REQUEST D-13 DONE and I will fix the alias. After that the body answers to one name.

— Desi
