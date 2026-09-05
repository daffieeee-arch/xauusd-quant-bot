#!/usr/bin/env python3
"""Test IC Markets / cTrader Open API app auth and print the one-time grant URL."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def grant_url(client_id: str, redirect: str, scope: str = "trading") -> str:
    q = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect,
            "scope": scope,
            "product": "web",
        }
    )
    return f"https://id.ctrader.com/my/settings/openapi/grantingaccess/?{q}"


def main() -> int:
    env = {**load_env(ROOT / ".env"), **os.environ}
    cid = env.get("CTRADER_CLIENT_ID", "")
    secret = env.get("CTRADER_CLIENT_SECRET", "")
    redirect = env.get("CTRADER_REDIRECT_URI", "https://localhost")
    scope = env.get("CTRADER_SCOPE", "trading")
    if not cid or not secret:
        print("Missing CTRADER_CLIENT_ID / CTRADER_CLIENT_SECRET in .env")
        return 2

    print("GRANT_URL=")
    print(grant_url(cid, redirect, scope))
    print()
    print("If that redirect is rejected, add this exact Redirect URI in the Open API app,")
    print("or tell me the URI you already configured.")
    print()
    print("Testing application auth on demo.ctraderapi.com:5035 …", flush=True)

    from twisted.internet import reactor

    from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
    from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoErrorRes
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAApplicationAuthReq,
        ProtoOAApplicationAuthRes,
        ProtoOAErrorRes,
    )

    result = {"ok": False, "detail": ""}
    client = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)

    def on_error(failure):
        result["detail"] = str(failure)
        print("SEND_ERROR", failure, flush=True)
        reactor.callLater(0.2, reactor.stop)

    def connected(_c):
        req = ProtoOAApplicationAuthReq()
        req.clientId = cid
        req.clientSecret = secret
        d = client.send(req, responseTimeoutInSeconds=20)
        d.addErrback(on_error)

    def disconnected(_c, reason):
        print("Disconnected:", reason, flush=True)

    def on_message(_c, message):
        ptype = message.payloadType
        if ptype == ProtoOAApplicationAuthRes().payloadType:
            result["ok"] = True
            result["detail"] = "application authorized"
            print("APP_AUTH_OK", flush=True)
            reactor.callLater(0.2, reactor.stop)
            return
        if ptype in (ProtoOAErrorRes().payloadType, ProtoErrorRes().payloadType):
            extracted = Protobuf.extract(message)
            result["detail"] = str(extracted)
            print("APP_AUTH_FAIL", extracted, flush=True)
            reactor.callLater(0.2, reactor.stop)
            return
        # Ignore heartbeats / other
        if ptype not in (51, 50):  # heartbeat-ish
            print("MSG", ptype, flush=True)

    client.setConnectedCallback(connected)
    client.setDisconnectedCallback(disconnected)
    client.setMessageReceivedCallback(on_message)
    client.startService()
    reactor.callLater(25, reactor.stop)
    reactor.run()
    print("RESULT", result["ok"], result["detail"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
