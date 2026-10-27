#!/usr/bin/env python3
# Owner: Desi (rover). Filed 2026-10-24 with rover/hosts.md, answering REQUEST D-13.
"""Which bodies are on the network right now — one command instead of a LAN sweep.

Why this exists. On 2026-10-23 the request filed as D-13 said what the *cost* of the missing address
record was: every session that wants to reach the lander "starts by sweeping the LAN trying to find the
body. That is minutes burned each time and a chance to knock on the wrong machine." A sweep is what you
do when you do not know an address. What was missing was not a fixed address — a fixed address only
fixes *one* body — but a record of all of them that can be checked.

So `rover/hosts.md` is the record and this is the check. It reads the record, asks the wire, and prints
both. When they agree it says so in one line; when a body's name resolves somewhere the record does not
expect, that row is a `MISMATCH` and the exit status is 3, because a record that silently disagrees with
the network is worse than no record: it is a claim with a date on it.

What it does not do: it does not sweep, and it does not guess. A body that is powered off is silent, and
silence is reported as silence — the four bodies in the record had this in common on 2026-10-24, and a
tool that called that a fault would cry wolf every night in a house where the robots sleep.

Usage:
    python3 scripts/fleet_probe.py                 # the record vs the wire, as a table
    python3 scripts/fleet_probe.py --json          # the same as data
    python3 scripts/fleet_probe.py --record FILE   # a different record (tests, or a second fleet)
    python3 scripts/fleet_probe.py --no-network    # print the record only; probe nothing

Exit status: 0 = ran, and the record does not contradict the network (silent hosts included);
3 = at least one name resolves to an address the record does not hold; 2 = the record is unusable.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RECORD = os.path.join(REPO, "rover", "hosts.md")

# The fields a record entry must carry. `key` and `answers` may be null/absent by design: not every body
# has a key of ours, and "did it answer when the record was written" is not always known.
REQUIRED = ("name", "address", "role")

_FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.S)


class RecordError(ValueError):
    """The record cannot be read as data. Never guessed around — an unreadable record is exit 2."""


def load_record(text: str) -> dict:
    """Parse the first ```json fence of a record file.

    Fenced JSON inside the Markdown (rather than a second .json file) is deliberate: one file means the
    prose and the data cannot drift apart, and the prose is what a human reads.
    """
    match = _FENCE.search(text or "")
    if not match:
        raise RecordError("no ```json block found — the record must carry its data in one fenced block")
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise RecordError(f"the ```json block is not valid JSON: {exc}") from exc
    hosts = data.get("hosts")
    if not isinstance(hosts, list) or not hosts:
        raise RecordError("the ```json block has no non-empty `hosts` list")
    seen_addresses: dict[str, str] = {}
    seen_names: dict[str, str] = {}
    for index, host in enumerate(hosts):
        if not isinstance(host, dict):
            raise RecordError(f"hosts[{index}] is not an object")
        missing = [field for field in REQUIRED if not host.get(field)]
        if missing:
            raise RecordError(f"hosts[{index}] ({host.get('name', 'unnamed')}) is missing {', '.join(missing)}")
        address = str(host["address"]).strip()
        name = str(host["name"]).strip()
        if address in seen_addresses:
            raise RecordError(f"two bodies at {address}: {seen_addresses[address]} and {name}")
        if name in seen_names:
            raise RecordError(f"one name used twice: {name}")
        seen_addresses[address] = name
        seen_names[name] = name
    return data


def load_record_file(path: str) -> dict:
    if not os.path.exists(path):
        raise RecordError(f"no record at {path}")
    with open(path, encoding="utf-8") as handle:
        return load_record(handle.read())


def ping(address: str, timeout_ms: int = 800) -> bool:
    """True if the address answers one ICMP echo.

    macOS `ping -W` takes milliseconds but does not bound the whole call, and a host with no ARP entry can
    hold a probe for seconds; `-t 2` is the wall-clock ceiling, so a probe of a sleeping fleet is bounded
    at two seconds a body rather than left to the OS.
    """
    try:
        done = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout_ms), "-t", "2", address],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=max(2.0, timeout_ms / 1000.0 * 3),
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def resolve(name: str) -> str | None:
    """The address a name resolves to, or None. macOS-only (`dscacheutil`); never raises.

    The timeout is deliberately short. An mDNS name that does not exist takes this Mac seconds to fail,
    and a probe that spends five seconds a name is a probe nobody runs before breakfast; 1.2 s is longer
    than a found name ever takes and cuts a dead one off.
    """
    try:
        done = subprocess.run(
            ["dscacheutil", "-q", "host", "-a", "name", name],
            capture_output=True,
            text=True,
            timeout=1.2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    for line in done.stdout.splitlines():
        line = line.strip()
        if line.startswith("ip_address:"):
            value = line.split(":", 1)[1].strip()
            if value:
                return value
    return None


def probe(record: dict, ping_fn=ping, resolve_fn=resolve) -> list[dict]:
    """One row per host: what the record says, what the wire says, and whether they contradict.

    `verdict` is one of:
      up        — answers at the address the record holds
      down      — silent (expected: bodies sleep); not an error
      MISMATCH  — its mDNS name resolves to some *other* address, so the record is out of date
      unprobed  — no probe was asked for
    """
    rows = []
    for host in record["hosts"]:
        name = str(host["name"]).strip()
        address = str(host["address"]).strip()
        answers = bool(ping_fn(address))
        mdns = host.get("mdns")
        resolved = resolve_fn(str(mdns)) if mdns else None
        if resolved and resolved != address:
            verdict = "MISMATCH"
        elif answers:
            verdict = "up"
        else:
            verdict = "down"
        rows.append(
            {
                "name": name,
                "address": address,
                "role": host.get("role", ""),
                "answers": answers,
                "resolved": resolved,
                "verdict": verdict,
                "confidence": host.get("confidence", ""),
            }
        )
    return rows


def unprobed(record: dict) -> list[dict]:
    rows = []
    for host in record["hosts"]:
        rows.append(
            {
                "name": str(host["name"]).strip(),
                "address": str(host["address"]).strip(),
                "role": host.get("role", ""),
                "answers": None,
                "resolved": None,
                "verdict": "unprobed",
                "confidence": host.get("confidence", ""),
            }
        )
    return rows


def render(rows: list[dict], measured_utc: str | None = None) -> str:
    """The table, then the two lines a reader needs: how many answered, and what contradicts the record."""
    width_name = max([len("body")] + [len(row["name"]) for row in rows])
    width_addr = max([len("address")] + [len(row["address"]) for row in rows])
    out = []
    if measured_utc:
        out.append(f"record measured {measured_utc}")
    header = f"{'body'.ljust(width_name)}  {'address'.ljust(width_addr)}  {'verdict':<8}  role"
    out.append(header)
    out.append("-" * len(header))
    for row in rows:
        out.append(
            f"{row['name'].ljust(width_name)}  {row['address'].ljust(width_addr)}  "
            f"{row['verdict']:<8}  {row['role']}"
        )
    answered = sum(1 for row in rows if row["answers"] is True)
    probed = sum(1 for row in rows if row["verdict"] != "unprobed")
    mismatches = [row for row in rows if row["verdict"] == "MISMATCH"]
    out.append("")
    if probed:
        out.append(f"{answered} of {probed} answered.")
        if answered < probed:
            out.append("Silent rows are not faults: a body that is powered off is silent.")
    else:
        out.append(f"{len(rows)} bodies in the record; nothing was probed.")
    if mismatches:
        for row in mismatches:
            out.append(
                f"MISMATCH: {row['name']} resolves to {row['resolved']} but the record says {row['address']}."
            )
    else:
        out.append("Nothing in the record contradicts the network.")
    return "\n".join(out)


def main(argv: list[str] | None = None, ping_fn=ping, resolve_fn=resolve) -> int:
    parser = argparse.ArgumentParser(description="Compare the fleet address record with what answers.")
    parser.add_argument("--record", default=DEFAULT_RECORD, help="record file (default: rover/hosts.md)")
    parser.add_argument("--json", action="store_true", help="emit rows as JSON")
    parser.add_argument("--no-network", action="store_true", help="print the record only; probe nothing")
    args = parser.parse_args(argv)

    try:
        record = load_record_file(args.record)
    except RecordError as exc:
        print(f"fleet_probe: {exc}", file=sys.stderr)
        return 2

    rows = unprobed(record) if args.no_network else probe(record, ping_fn=ping_fn, resolve_fn=resolve_fn)
    if args.json:
        print(json.dumps({"measured_utc": record.get("measured_utc"), "hosts": rows}, indent=2))
    else:
        print(render(rows, record.get("measured_utc")))
    return 3 if any(row["verdict"] == "MISMATCH" for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
