#!/usr/bin/env python3
"""Install or remove this user's macOS background Telegram monitor."""

from __future__ import annotations

import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "private"
LABEL = "org.visa-appointment-scout.monitor"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
MONITOR = ROOT / "scripts" / "monitor_telegram.py"


def service_target() -> str:
    return f"gui/{os.getuid()}/{LABEL}"


def run_launchctl(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["launchctl", *arguments], check=check, capture_output=True, text=True)


def install() -> None:
    if sys.platform != "darwin":
        raise SystemExit("The background installer is for macOS only.")
    python = ROOT / ".venv" / "bin" / "python"
    if not python.exists():
        raise SystemExit("Create the project environment first with: python3 -m venv .venv")
    if not (ROOT / "watchlist.local.json").exists():
        raise SystemExit("Copy watchlist.example.json to watchlist.local.json and select your chats first.")
    PRIVATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    PRIVATE_DIR.chmod(0o700)
    PLIST_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    record = {
        "Label": LABEL,
        "ProgramArguments": [str(python), str(MONITOR)],
        "WorkingDirectory": str(ROOT),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 30,
        "StandardOutPath": str(PRIVATE_DIR / "monitor.log"),
        "StandardErrorPath": str(PRIVATE_DIR / "monitor.log"),
    }
    temporary = PLIST_PATH.with_suffix(".plist.tmp")
    temporary.write_bytes(plistlib.dumps(record))
    temporary.chmod(0o600)
    temporary.replace(PLIST_PATH)
    PLIST_PATH.chmod(0o600)
    run_launchctl("bootout", service_target(), check=False)
    result = run_launchctl("bootstrap", f"gui/{os.getuid()}", str(PLIST_PATH), check=False)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "launchd could not start the monitor.")
    print("Installed and started the monitor for this logged-in macOS account.")
    print("It will restart after login. Check macOS notification settings if alerts are not visible.")


def uninstall() -> None:
    if sys.platform != "darwin":
        raise SystemExit("The background installer is for macOS only.")
    run_launchctl("bootout", service_target(), check=False)
    PLIST_PATH.unlink(missing_ok=True)
    print("Removed the background monitor. Telegram credentials and session remain private locally.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "uninstall"))
    action = parser.parse_args().action
    (install if action == "install" else uninstall)()


if __name__ == "__main__":
    main()
