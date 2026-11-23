#!/usr/bin/env python3
"""Apply owner-only permissions to private configuration and session paths."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def secure_directory(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "nt":
        account = subprocess.check_output(["whoami"], text=True).strip()
        subprocess.run(
            ["icacls.exe", str(path), "/inheritance:r", "/grant:r", f"{account}:(OI)(CI)F"],
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        path.chmod(0o700)


def secure_file(path: Path) -> None:
    if os.name == "nt":
        account = subprocess.check_output(["whoami"], text=True).strip()
        subprocess.run(
            ["icacls.exe", str(path), "/inheritance:r", "/grant:r", f"{account}:F"],
            check=True,
            capture_output=True,
            text=True,
        )
    else:
        path.chmod(0o600)
