#!/usr/bin/env python3
"""Watch selected Telegram dialogs locally and notify on configured phrases."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import unicodedata
from collections import OrderedDict
from datetime import timezone
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.utils import get_peer_id
from local_security import secure_directory, secure_file

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "private"
SESSION = PRIVATE_DIR / "telegram_user"
WATCHLIST = ROOT / "watchlist.local.json"
MAX_SEEN = 10_000


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def matches_signal(text: str, positive_phrases: list[str], excluded_phrases: list[str]) -> bool:
    normalized = normalize(text)
    return bool(normalized) and any(phrase in normalized for phrase in positive_phrases) and not any(
        phrase in normalized for phrase in excluded_phrases
    )


def load_watchlist() -> tuple[list[str], list[str], list[str]]:
    if not WATCHLIST.exists():
        raise SystemExit("Copy watchlist.example.json to watchlist.local.json and add your exact group/channel titles.")
    try:
        config = json.loads(WATCHLIST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Could not read watchlist.local.json: {error}") from error
    if not isinstance(config, dict):
        raise SystemExit("watchlist.local.json must contain a JSON object.")

    def phrases(key: str) -> list[str]:
        value = config.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise SystemExit(f"watchlist.local.json field {key!r} must be a list of phrases.")
        return [normalize(item) for item in value if item.strip()]

    channels = config.get("channels")
    if not isinstance(channels, list) or not channels or any(not isinstance(item, str) or not item.strip() for item in channels):
        raise SystemExit("watchlist.local.json must list one or more exact dialog titles in 'channels'.")
    if len(set(channels)) != len(channels):
        raise SystemExit("Remove duplicate titles from watchlist.local.json.")
    positive = phrases("availability_phrases")
    if not positive:
        raise SystemExit("Add at least one availability phrase to watchlist.local.json.")
    return channels, positive, phrases("exclude_phrases")


def notify() -> None:
    body = "A monitored Telegram chat may mention a visa slot. Open Telegram and verify it."
    if sys.platform != "darwin":
        if sys.platform == "win32":
            try:
                from winotify import Notification
            except ImportError:
                print("Install requirements.txt to enable Windows toast notifications.", file=sys.stderr, flush=True)
                print(body, flush=True)
                return
            try:
                toast = Notification(app_id="Visa Appointment Scout", title="Visa Appointment Scout", msg=body)
                toast.show()
            except Exception:
                print("Could not show a Windows toast; check Windows notification settings.", file=sys.stderr, flush=True)
                print(body, flush=True)
            return
        print(body, flush=True)
        return
    result = subprocess.run(
        [
            "osascript", "-l", "JavaScript", "-e",
            'ObjC.import("Foundation"); ObjC.import("AppKit"); '
            'var n = $.NSUserNotification.alloc.init; '
            'n.title = "Visa Appointment Scout"; '
            f'n.informativeText = {json.dumps(body)}; '
            '$.NSUserNotificationCenter.defaultUserNotificationCenter.deliverNotification(n);',
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        print("Could not show a macOS notification; check notification settings.", file=sys.stderr, flush=True)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-notification", action="store_true", help="Show a sample local notification and exit")
    return parser.parse_args()


async def main() -> None:
    os.umask(0o077)
    secure_directory(PRIVATE_DIR)
    if sys.platform == "win32" and (sys.stdout is None or sys.stderr is None):
        stream = (PRIVATE_DIR / "monitor.log").open("a", encoding="utf-8")
        sys.stdout = stream
        sys.stderr = stream
    args = parse_arguments()
    if args.test_notification:
        notify()
        return

    titles, positive_phrases, excluded_phrases = load_watchlist()
    load_dotenv(ROOT / ".env", override=False)
    api_id = os.environ.get("TG_API_ID", "").strip()
    api_hash = os.environ.get("TG_API_HASH", "").strip()
    if not api_id or not api_id.isdecimal() or not api_hash:
        raise SystemExit("Configure TG_API_ID and TG_API_HASH locally first.")
    if not SESSION.with_suffix(".session").exists():
        raise SystemExit("Run scripts/list_chats.py locally to sign in and create the private session first.")

    client = TelegramClient(str(SESSION), int(api_id), api_hash)
    dialogs_by_title: dict[str, list[object]] = {}
    resolved_titles: dict[int, str] = {}
    seen: OrderedDict[tuple[int, int], bytes] = OrderedDict()
    try:
        await client.connect()
        if not await client.is_user_authorized():
            raise SystemExit("The local Telegram session is not authorized. Run scripts/list_chats.py in a terminal.")
        dialogs = await client.get_dialogs(limit=None)
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                dialogs_by_title.setdefault(dialog.name, []).append(dialog)

        selected = []
        for title in titles:
            matches = dialogs_by_title.get(title, [])
            if len(matches) != 1:
                raise SystemExit(f"Expected one accessible group/channel named {title!r}; found {len(matches)}.")
            dialog = matches[0]
            selected.append(dialog.entity)
            resolved_titles[get_peer_id(dialog.entity)] = title

        print(f"Watching {len(selected)} selected Telegram group(s)/channel(s); message text stays on this device.", flush=True)
        print("Alerts are keyword leads only. Check the source post and official calendar yourself.", flush=True)

        async def handle(event: object) -> None:
            message = event.message
            if getattr(message, "out", False):
                return
            raw_text = message.message or ""
            if not matches_signal(raw_text, positive_phrases, excluded_phrases):
                return
            text = normalize(raw_text)
            key = (int(event.chat_id or 0), int(message.id))
            signature = hashlib.sha256(text.encode("utf-8")).digest()
            if seen.get(key) == signature:
                return
            seen[key] = signature
            seen.move_to_end(key)
            if len(seen) > MAX_SEEN:
                seen.popitem(last=False)
            title = resolved_titles.get(key[0], "selected chat")
            timestamp = message.date.astimezone(timezone.utc).isoformat()
            safe_title = " ".join(title.split())
            print(f"Possible slot-related report | {safe_title} | message time {timestamp} UTC", flush=True)
            notify()

        client.add_event_handler(handle, events.NewMessage(chats=selected, incoming=True))
        client.add_event_handler(handle, events.MessageEdited(chats=selected))
        await client.catch_up()
        await client.run_until_disconnected()
    finally:
        if client.is_connected():
            await client.disconnect()
        session_file = SESSION.with_suffix(".session")
        if session_file.exists():
            secure_file(session_file)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        raise SystemExit("\nMonitor stopped.")
