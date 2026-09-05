"""Load local .env without committing secrets."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env(path: Path | None = None) -> dict[str, str]:
    env_path = path or (ROOT / ".env")
    out: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    out.update({k: v for k, v in os.environ.items() if v})
    return out


def upsert_env(updates: dict[str, str], path: Path | None = None) -> None:
    env_path = path or (ROOT / ".env")
    current: dict[str, str] = {}
    lines: list[str] = []
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, _ = line.split("=", 1)
                current[k.strip()] = line
            else:
                lines.append(line)
    current_keys = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                current_keys[k.strip()] = v
    for k, v in updates.items():
        current_keys[k] = v
    body = []
    if env_path.exists():
        seen = set()
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, _ = line.split("=", 1)
                k = k.strip()
                body.append(f"{k}={current_keys[k]}")
                seen.add(k)
            else:
                body.append(line)
        for k, v in updates.items():
            if k not in seen:
                body.append(f"{k}={v}")
    else:
        body = [f"{k}={v}" for k, v in current_keys.items()]
    env_path.write_text("\n".join(body).rstrip() + "\n")
    env_path.chmod(0o600)
