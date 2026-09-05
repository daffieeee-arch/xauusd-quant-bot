#!/usr/bin/env python3
"""Exchange an OAuth code (from the Allow redirect) for access/refresh tokens."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.envutil import load_env, upsert_env


def extract_code(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("http"):
        q = parse_qs(urlparse(raw).query)
        if "code" not in q:
            raise ValueError("redirect URL has no code=")
        return q["code"][0]
    return raw


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("Usage: python3 -m engine.ic_token 'https://localhost/?code=...'")
        return 2
    env = load_env()
    code = extract_code(argv[0])
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": env["CTRADER_REDIRECT_URI"],
        "client_id": env["CTRADER_CLIENT_ID"],
        "client_secret": env["CTRADER_CLIENT_SECRET"],
    }
    r = requests.get("https://openapi.ctrader.com/apps/token", params=params, timeout=30)
    print("HTTP", r.status_code)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
    print({k: ("***" if "token" in k.lower() or "secret" in k.lower() else v) for k, v in data.items()})
    access = data.get("accessToken") or data.get("access_token")
    refresh = data.get("refreshToken") or data.get("refresh_token")
    if not access:
        print("No access token — app may still be inactive or redirect URI mismatch.")
        return 1
    upsert_env({"CTRADER_ACCESS_TOKEN": access, "CTRADER_REFRESH_TOKEN": refresh or ""})
    print("Tokens saved to .env")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
