#!/usr/bin/env python3
"""Sign in locally if needed and list accessible group/channel titles only."""

from __future__ import annotations

import asyncio
import getpass
import os
import stat
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "private"
SESSION = PRIVATE_DIR / "telegram_user"


def get_credentials() -> tuple[int, str]:
    load_dotenv(ROOT / ".env", override=False)
    api_id = os.environ.get("TG_API_ID", "").strip()
    api_hash = os.environ.get("TG_API_HASH", "").strip()
    if not api_id or not api_hash:
        raise SystemExit("Run scripts/configure_credentials.py first.")
    if not api_id.isdecimal():
        raise SystemExit("TG_API_ID must be numeric.")
    return int(api_id), api_hash


async def main() -> None:
    os.umask(0o077)
    PRIVATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    PRIVATE_DIR.chmod(0o700)
    api_id, api_hash = get_credentials()
    client = TelegramClient(str(SESSION), api_id, api_hash)
    try:
        await client.start(
            phone=lambda: input("Telegram phone number (with country code): ").strip(),
            code_callback=lambda: getpass.getpass("Telegram login code (hidden): ").strip(),
            password=lambda: getpass.getpass("Telegram 2FA password (hidden): "),
        )
        print("Accessible Telegram groups and channels:")
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                print(f"- [group] {dialog.name}")
            elif dialog.is_channel:
                print(f"- [channel] {dialog.name}")
        print("Listed titles only; no message history was read.")
    finally:
        if client.is_connected():
            await client.disconnect()
        session_file = SESSION.with_suffix(".session")
        if session_file.exists():
            session_file.chmod(stat.S_IRUSR | stat.S_IWUSR)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        raise SystemExit("\nStopped.")
