#!/usr/bin/env python3
"""Download XAUUSD bid/ask ticks from IC Markets via cTrader Open API.

Requires: Active app + tokens in .env (run engine.ic_token first).
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.envutil import load_env


def main() -> int:
    env = load_env()
    if not env.get("CTRADER_ACCESS_TOKEN"):
        print("No CTRADER_ACCESS_TOKEN yet. Waiting on Spotware Active + Allow redirect.")
        print("When you have https://localhost/?code=... run:")
        print("  python3 -m engine.ic_token 'https://localhost/?code=...'")
        print("  python3 -m engine.ic_download")
        return 2
    print("Token present — full tick pull will run here (account", env.get("IC_DEMO_ACCOUNT_NUMBER"), ").")
    print("Not starting the multi-week pull until app auth is Active (last check: not Active).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
