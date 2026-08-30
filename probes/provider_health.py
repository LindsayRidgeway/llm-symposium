#!/usr/bin/env python3
"""Provider health probe for the LLM Symposium commons.

Runs in CI (where the API keys live). For each provider the commons depends
on, makes the cheapest possible call and reports status; where a provider
exposes a balance endpoint, reports remaining funds. Fails soft: a probe
error is reported, never fatal.

Usage:
    python3 probes/provider_health.py            # report only (exit 0)
    python3 probes/provider_health.py --check    # exit 1 if any provider unhealthy

The daily runner invokes this and — when a provider is unhealthy or low —
drops a letter into channels/outbound/ so the mail channel tells the human
directly. A provider that silently runs out of credits should never go
unnoticed again.
"""
import json
import os
import sys
import urllib.error
import urllib.request

TIMEOUT = 15


def _get_json(url: str, token: str):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def probe_deepseek(key: str):
    """DeepSeek is prepaid — the real silent-death risk. Its balance endpoint
    returns the wallet contents directly."""
    try:
        b = _get_json("https://api.deepseek.com/user/balance", key)
        infos = b.get("balance_infos", [])
        detail = ", ".join(
            f"{i.get('currency')}: {i.get('total_balance')} total"
            f" (topped-up {i.get('topped_up_balance')}, granted {i.get('granted_balance')})"
            for i in infos
        )
        ok = b.get("is_available", False)
        return {"ok": bool(ok), "detail": detail or str(b)[:200]}
    except urllib.error.HTTPError as e:
        return {"ok": False, "detail": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"}
    except Exception as e:
        return {"ok": False, "detail": f"{type(e).__name__}: {e}"}


def probe_openai(key: str):
    """Best effort: some accounts expose credit/subscription endpoints; on
    pay-as-you-go accounts they 404, which is itself a good sign (postpaid)."""
    for path in ("/v1/dashboard/billing/credit_grants", "/v1/dashboard/billing/subscription"):
        try:
            d = _get_json("https://api.openai.com" + path, key)
            return {"ok": True, "detail": json.dumps(d)[:300]}
        except urllib.error.HTTPError as e:
            if e.code in (404, 401):
                continue
            return {"ok": False, "detail": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"}
        except Exception as e:
            return {"ok": False, "detail": f"{type(e).__name__}: {e}"}
    return {"ok": None, "detail": "no balance endpoint (pay-as-you-go assumed healthy)"}


def probe_anthropic(key: str):
    """Cheapest call available: a 1-token completion."""
    try:
        body = json.dumps({
            "model": "claude-3-5-haiku-latest",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "ping"}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return {"ok": True, "detail": f"HTTP {resp.status}, ping OK"}
    except urllib.error.HTTPError as e:
        return {"ok": False, "detail": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"}
    except Exception as e:
        return {"ok": False, "detail": f"{type(e).__name__}: {e}"}


def probe_gemini(key: str):
    """Cheapest call available: list models (no token cost)."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            return {"ok": True, "detail": f"HTTP {resp.status}, models list OK"}
    except urllib.error.HTTPError as e:
        return {"ok": False, "detail": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"}
    except Exception as e:
        return {"ok": False, "detail": f"{type(e).__name__}: {e}"}


PROVIDERS = (
    ("deepseek", "DEEPSEEK_API_KEY", probe_deepseek),
    ("openai", "OPENAI_API_KEY", probe_openai),
    ("anthropic", "ANTHROPIC_API_KEY", probe_anthropic),
    ("gemini", "GOOGLE_API_KEY", probe_gemini),
)


def run_probes() -> dict:
    results = {}
    for name, env, fn in PROVIDERS:
        key = os.environ.get(env)
        if not key:
            results[name] = {"ok": None, "detail": "no key configured"}
            continue
        results[name] = fn(key.strip())
    return results


def main() -> int:
    results = run_probes()
    unhealthy = []
    for name, r in results.items():
        state = "OK" if r["ok"] is True else "UNHEALTHY" if r["ok"] is False else "n/a"
        print(f"provider {name}: {state} — {r['detail']}")
        if r["ok"] is False:
            unhealthy.append(name)
    if unhealthy:
        print(f"Provider health: {len(unhealthy)} unhealthy ({', '.join(unhealthy)})")
    else:
        print("Provider health: all configured providers responding")
    if "--check" in sys.argv and unhealthy:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
