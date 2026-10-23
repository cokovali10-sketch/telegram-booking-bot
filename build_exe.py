#!/usr/bin/env python3
"""Build single-file EXE for telegram-booking-bot using PyInstaller."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
# --- константы вынесены FORGE refactor ---
CONST_1024 = 1024


PROJECT_DIR = Path(__file__).resolve().parent
APP_NAME = "telegram-bot"
ENTRY = str(PROJECT_DIR / "bot.py")
ICON_PATH = PROJECT_DIR / "telegram-bot.ico"


def clean():
    for d in ("build", "dist"):
        p = PROJECT_DIR / d
        if p.exists():
            shutil.rmtree(p)
            print(f"  Removed {p}")
    for f in PROJECT_DIR.glob("*.spec"):
        f.unlink()
        print(f"  Removed {f}")


def build(clean_first=False):
    print(f"[*] Building {APP_NAME}.exe ...")
    if clean_first:
        print("[*] Cleaning build artifacts ...")
        clean()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", APP_NAME,
        "--console",
        "--distpath", str(PROJECT_DIR / "dist"),
        "--workpath", str(PROJECT_DIR / "build"),
        "--specpath", str(PROJECT_DIR),
        "--paths", str(PROJECT_DIR),
        "--hidden-import", "app",
        "--hidden-import", "app.config",
        "--hidden-import", "app.config.settings",
        "--hidden-import", "app.database",
        "--hidden-import", "app.database.db",
        "--hidden-import", "app.database.models",
        "--hidden-import", "app.database.requests",
        "--hidden-import", "app.database.session",
        "--hidden-import", "app.handlers",
        "--hidden-import", "app.handlers.admin",
        "--hidden-import", "app.handlers.booking",
        "--hidden-import", "app.handlers.start",
        "--hidden-import", "app.keyboards",
        "--hidden-import", "app.keyboards.inline",
        "--hidden-import", "app.keyboards.main_menu",
        "--hidden-import", "app.keyboards.reply",
        "--hidden-import", "app.keyboards.services",
        "--hidden-import", "app.middlewares",
        "--hidden-import", "aiogram",
        "--hidden-import", "aiogram.filters",
        "--hidden-import", "aiogram.fsm.context",
        "--hidden-import", "aiogram.fsm.storage.memory",
        "--hidden-import", "aiogram.fsm.state",
        "--hidden-import", "aiogram.types",
        "--hidden-import", "aiogram.utils.keyboard",
        "--collect-submodules", "app",
    ]

    if ICON_PATH.exists():
        cmd += ["--icon", str(ICON_PATH)]

    cmd.append(ENTRY)

    result = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    if result.returncode != 0:
        print(f"[!] Build failed for {APP_NAME}")
        sys.exit(1)

    exe = PROJECT_DIR / "dist" / f"{APP_NAME}.exe"
    if exe.exists():
        size_mb = exe.stat().st_size / (CONST_1024 * CONST_1024)
        print(f"[+] {exe}  ({size_mb:.1f} MB)")
    else:
        print(f"[!] Expected EXE not found: {exe}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Build {APP_NAME}.exe")
    parser.add_argument("--clean", action="store_true", help="Remove build artifacts first")
    args = parser.parse_args()
    build(clean_first=args.clean)
