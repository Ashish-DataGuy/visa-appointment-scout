#!/usr/bin/env python3
"""Save this user's Telegram API credentials in a private local .env file."""

from __future__ import annotations

import getpass
import os
from pathlib import Path

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
PRIVATE_DIR = ROOT / "private"


def main() -> None:
    os.umask(0o077)
    PRIVATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    PRIVATE_DIR.chmod(0o700)

    existing = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}
    api_id = str(existing.get("TG_API_ID") or "").strip()
    api_hash = str(existing.get("TG_API_HASH") or "").strip()

    if not api_id:
        api_id = input("Telegram API ID: ").strip()
    if not api_id.isdecimal() or int(api_id) <= 0:
        raise SystemExit("TG_API_ID must be a positive number.")

    if not api_hash:
        api_hash = getpass.getpass("Telegram API hash (hidden): ").strip()
    if not api_hash or any(character.isspace() for character in api_hash):
        raise SystemExit("TG_API_HASH must be non-empty and contain no spaces.")

    set_key(ENV_FILE, "TG_API_ID", api_id, quote_mode="never")
    set_key(ENV_FILE, "TG_API_HASH", api_hash, quote_mode="never")
    ENV_FILE.chmod(0o600)
    print("Saved Telegram API values to the Git-ignored .env with owner-only permissions.")
    print("Credential values were not displayed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit("\nStopped without saving.")
