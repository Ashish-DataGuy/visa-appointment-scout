#!/usr/bin/env python3
"""Install or remove this user's macOS or Windows Telegram monitor."""

from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import subprocess
import sys
import venv
from pathlib import Path

from local_security import secure_directory, secure_file

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "private"
LABEL = "org.visa-appointment-scout.monitor"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
MONITOR = ROOT / "scripts" / "monitor_telegram.py"
WINDOWS_TASK = "Visa Appointment Scout Monitor"
MAC_RUNTIME = Path.home() / "Library" / "Application Support" / "Visa Appointment Scout" / "runtime"


def service_target() -> str:
    return f"gui/{os.getuid()}/{LABEL}"


def run_launchctl(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["launchctl", *arguments], check=check, capture_output=True, text=True)


def deploy_macos_runtime() -> tuple[Path, Path]:
    runtime = ROOT.resolve()
    if runtime != MAC_RUNTIME.resolve():
        secure_directory(MAC_RUNTIME.parent)
        secure_directory(MAC_RUNTIME)

        def ignored(directory: str, names: list[str]) -> set[str]:
            excluded = {".git", ".venv", "__pycache__"} & set(names)
            if Path(directory).name == "private" and "monitor.log" in names:
                excluded.add("monitor.log")
            return excluded

        shutil.copytree(ROOT, MAC_RUNTIME, dirs_exist_ok=True, ignore=ignored)
        runtime = MAC_RUNTIME

    secure_directory(runtime)
    private = runtime / "private"
    secure_directory(private)
    for candidate in (runtime / ".env", private / "telegram_user.session", runtime / "watchlist.local.json"):
        if candidate.exists():
            secure_file(candidate)
    log_file = private / "monitor.log"
    if log_file.exists():
        secure_file(log_file)

    python = runtime / ".venv" / "bin" / "python"
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(runtime / ".venv")
    subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(runtime / "requirements.txt")],
        check=True,
        capture_output=True,
        text=True,
    )
    return runtime, python


def install() -> None:
    if sys.prefix == sys.base_prefix:
        raise SystemExit("Run this command with the project's virtual environment Python (the Windows Scripts folder or macOS bin folder).")
    if not (ROOT / "watchlist.local.json").exists():
        raise SystemExit("Copy watchlist.example.json to watchlist.local.json and select your chats first.")
    secure_directory(PRIVATE_DIR)

    if sys.platform == "win32":
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        if not pythonw.exists():
            raise SystemExit("Could not find pythonw.exe beside the virtual environment's Python.")
        command = subprocess.list2cmdline([str(pythonw), str(MONITOR)])
        result = subprocess.run(
            ["schtasks.exe", "/Create", "/F", "/SC", "ONLOGON", "/TN", WINDOWS_TASK, "/TR", command, "/IT"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise SystemExit(result.stderr.strip() or result.stdout.strip() or "Windows Task Scheduler could not start the monitor.")
        print("Installed the monitor in Windows Task Scheduler for this user at sign-in.")
        print("It runs only during this user's interactive session; the PC must be awake and online.")
        return

    if sys.platform != "darwin":
        raise SystemExit("The background monitor installer supports macOS and Windows.")
    runtime, python = deploy_macos_runtime()
    monitor = runtime / "scripts" / "monitor_telegram.py"
    PLIST_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    record = {
        "Label": LABEL,
        "ProgramArguments": [str(python), str(monitor)],
        "WorkingDirectory": str(runtime),
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 30,
        "StandardOutPath": str(runtime / "private" / "monitor.log"),
        "StandardErrorPath": str(runtime / "private" / "monitor.log"),
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
    print(f"Installed and started the monitor from the private runtime at {runtime}.")
    print("It will restart after login. Check macOS notification settings if alerts are not visible.")


def uninstall() -> None:
    if sys.platform == "win32":
        subprocess.run(
            ["schtasks.exe", "/Delete", "/F", "/TN", WINDOWS_TASK],
            check=False,
            capture_output=True,
            text=True,
        )
        print("Removed the Windows scheduled task. Telegram credentials and session remain private locally.")
        return
    if sys.platform != "darwin":
        raise SystemExit("The background monitor installer supports macOS and Windows.")
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
