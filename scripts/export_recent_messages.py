#!/usr/bin/env python3
"""Print a bounded, redacted Telegram message sample as JSONL; persist nothing."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import stat
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "private" / "telegram_user"
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
CASE_ID = re.compile(r"\b[A-Z]{1,3}\d{6,12}\b", re.IGNORECASE)
HANDLE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{5,}")
PHONE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{8,}\d(?!\w)")


def redact(text: str) -> str:
    text = EMAIL.sub("[EMAIL]", text)
    text = CASE_ID.sub("[CASE/ID]", text)
    text = HANDLE.sub("[HANDLE]", text)

    def mask_number(match: re.Match[str]) -> str:
        value = match.group(0)
        return "[PHONE/ID]" if sum(character.isdigit() for character in value) >= 10 else value

    text = PHONE.sub(mask_number, text)
    return text[:1200] + (" [truncated]" if len(text) > 1200 else "")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", action="append", required=True, help="Exact dialog title; repeat for each channel")
    parser.add_argument("--limit", type=int, default=300, help="Recent messages per channel (1–1000; default: 300)")
    parser.add_argument("--offset-id", action="append", type=int, help="Older-message cursor for each channel, in the same order as --channel; use page_info.next_offset_id")
    parser.add_argument("--confirm-read", action="store_true", help="Confirm that selected message text may be shown to the calling agent")
    args = parser.parse_args()
    if not 1 <= args.limit <= 1000:
        parser.error("--limit must be from 1 to 1000")
    if args.offset_id and len(args.offset_id) != len(args.channel):
        parser.error("provide exactly one --offset-id per --channel, in matching order")
    if not args.offset_id:
        args.offset_id = [None] * len(args.channel)
    if not args.confirm_read:
        parser.error("add --confirm-read after confirming the selected messages may be analyzed")
    return args


async def main(args: argparse.Namespace) -> None:
    os.umask(0o077)
    load_dotenv(ROOT / ".env", override=False)
    api_id = os.environ.get("TG_API_ID", "").strip()
    api_hash = os.environ.get("TG_API_HASH", "").strip()
    if not api_id or not api_id.isdecimal() or not api_hash:
        raise SystemExit("Configure TG_API_ID and TG_API_HASH locally first.")
    if not SESSION.with_suffix(".session").exists():
        raise SystemExit("Run scripts/list_chats.py in a local terminal to create your private session first.")

    client = TelegramClient(str(SESSION), int(api_id), api_hash)
    rows: list[dict[str, str]] = []
    page_info: list[dict[str, object]] = []
    try:
        await client.connect()
        if not await client.is_user_authorized():
            raise SystemExit("The local session is not authorized; no login prompt was attempted.")
        dialogs = await client.get_dialogs()
        by_name: dict[str, list[object]] = {}
        for dialog in dialogs:
            by_name.setdefault(dialog.name, []).append(dialog.entity)

        for title, offset_id in zip(args.channel, args.offset_id):
            matches = by_name.get(title, [])
            if len(matches) != 1:
                raise SystemExit(f"Expected one dialog named {title!r}; found {len(matches)}. Check the title with list_chats.py.")
            entity = matches[0]
            messages: list[tuple[int, dict[str, str]]] = []
            options = {"limit": args.limit}
            if offset_id is not None:
                options["offset_id"] = offset_id
            async for message in client.iter_messages(entity, **options):
                text = redact(message.message or "")
                row = {
                    "channel": title,
                    "date_utc": message.date.isoformat(),
                    "text": text if text.strip() else "[media-only; not downloaded]",
                }
                messages.append((message.id, row))
            messages.reverse()
            rows.extend(row for _, row in messages)
            page_info.append({
                "record_type": "page_info",
                "channel": title,
                "count": len(messages),
                "oldest_date_utc": messages[0][1]["date_utc"] if messages else None,
                "newest_date_utc": messages[-1][1]["date_utc"] if messages else None,
                "next_offset_id": messages[0][0] if len(messages) == args.limit else None,
            })
    finally:
        if client.is_connected():
            await client.disconnect()
        session_file = SESSION.with_suffix(".session")
        if session_file.exists():
            session_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

    for row in page_info:
        print(json.dumps(row, ensure_ascii=False))
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    try:
        asyncio.run(main(arguments()))
    except KeyboardInterrupt:
        raise SystemExit("\nStopped.")
