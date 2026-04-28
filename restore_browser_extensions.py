#!/usr/bin/env python3
"""
🔄 Browser Extension Restore – Fun Edition
Cross‑Platform (Chrome / Firefox / Edge)
Restore your extensions with joy!
"""

import os
import sys
import subprocess
import shutil
import zipfile
import struct
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# ---- Colors and animations ----
C = {
    'R': '\033[91m', 'G': '\033[92m', 'Y': '\033[93m', 'B': '\033[94m',
    'M': '\033[95m', 'C': '\033[96m', 'W': '\033[0m', 'bold': '\033[1m'
}
ANIM = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

def print_banner():
    print(f"{C['C']}{'='*60}{C['W']}")
    print(f"{C['bold']}{C['M']}🔄  BROWSER EXTENSION RESTORE  🔄{C['W']}")
    print(f"{C['C']}Bring back your beloved extensions!{C['W']}")
    print(f"{C['C']}{'='*60}{C['W']}\n")

def menu():
    print("Select the browser to restore extensions for:")
    browsers = [
        (f"  [{C['Y']}1{C['W']}] {C['G']}🌐 Google Chrome{C['W']}"),
        (f"  [{C['Y']}2{C['W']}] {C['R']}🦊 Mozilla Firefox{C['W']}"),
        (f"  [{C['Y']}3{C['W']}] {C['B']}🧭 Microsoft Edge{C['W']}"),
    ]
    for line in browsers:
        print(line)
    try:
        choice = int(input(f"\n{C['Y']}👉 Enter number (1-3): {C['W']}").strip())
        if choice in (1,2,3): return choice
    except:
        pass
    print(f"{C['R']}❌ Invalid choice!{C['W']}")
    sys.exit(1)

def spinning_animation(stop_event, message):
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{C['C']}{ANIM[i%len(ANIM)]} {message}{C['W']}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " "*60 + "\r")

# ---- Core extractors ----
def extract_crx(crx_path, out_dir):
    with open(crx_path, 'rb') as f:
        if f.read(4) != b'Cr24': raise ValueError("Bad CRX")
        ver = struct.unpack('<I', f.read(4))[0]
        pub = struct.unpack('<I', f.read(4))[0]
        sig = struct.unpack('<I', f.read(4))[0]
        f.read(pub); f.read(sig)
        with zipfile.ZipFile(f) as zf:
            zf.extractall(out_dir)

def extract_zip(zip_path, out_dir):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(out_dir)

def get_firefox_ext_dir():
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"]) / "Mozilla/Firefox/Profiles"
    elif sys.platform == "darwin":
        base = home / "Library/Application Support/Firefox/Profiles"
    else:
        base = home / ".mozilla/firefox"
    if not base.exists(): return None
    for d in base.iterdir():
        if d.is_dir() and (d.name.endswith(".default-release") or d.name.endswith(".default")):
            return d / "extensions"
    for d in base.iterdir():
        if (d / "extensions").exists(): return d / "extensions"
    return None

# ---- Restore functions ----
def restore_chromium(browser):
    backup_dir = SCRIPT_DIR / f"{browser.lower()}_extensions_backup"
    if not backup_dir.exists():
        print(f"{C['R']}❌ Backup folder not found: {backup_dir}{C['W']}")
        return
    restore_dir = SCRIPT_DIR / "restored_extensions"
    restore_dir.mkdir(exist_ok=True)

    archives = sorted(backup_dir.glob("*.crx")) + sorted(backup_dir.glob("*.zip"))
    if not archives:
        print(f"{C['Y']}ℹ️  No backup files found.{C['W']}")
        return

    count = 0
    for archive in archives:
        ext_id = archive.stem
        dest = restore_dir / ext_id
        if dest.exists(): shutil.rmtree(dest)
        print(f"{C['Y']}📦 {ext_id}{C['W']} ", end="", flush=True)

        import threading
        stop_event = threading.Event()
        t = threading.Thread(target=spinning_animation, args=(stop_event, "Extracting..."))
        t.start()

        try:
            if archive.suffix == '.crx':
                extract_crx(archive, dest)
            else:
                extract_zip(archive, dest)
            stop_event.set()
            t.join()
            print(f"{C['G']}✅{C['W']}")
            count += 1
        except Exception as e:
            stop_event.set()
            t.join()
            print(f"{C['R']}❌ {e}{C['W']}")

    print(f"\n{C['bold']}{C['G']}🎉 {count} extensions restored!{C['W']}")
    print(f"   📁 {restore_dir}")
    print(f"\n{C['C']}Next steps:{C['W']}")
    print(f"  1. Open {browser} and go to {C['Y']}extensions page{C['W']}")
    print(f"  2. Enable {C['bold']}Developer mode{C['W']}")
    print(f"  3. For each folder in {restore_dir.name}, click {C['G']}Load unpacked{C['W']}")

def restore_firefox():
    backup_dir = SCRIPT_DIR / "firefox_extensions_backup"
    if not backup_dir.exists():
        print(f"{C['R']}❌ Backup folder not found: {backup_dir}{C['W']}")
        return

    xpi_files = list(backup_dir.glob("*.xpi"))
    if not xpi_files:
        print(f"{C['Y']}ℹ️  No .xpi files found.{C['W']}")
        return

    target_dir = get_firefox_ext_dir()
    if not target_dir:
        print(f"{C['R']}❌ Firefox profile extensions folder not found.{C['W']}")
        return

    print(f"\n{C['bold']}{C['R']}⚠️  Make sure Firefox is CLOSED before restoring.{C['W']}")
    input(f"{C['Y']}Press Enter to continue...{C['W']}")

    target_dir.mkdir(exist_ok=True)
    count = 0
    for xpi in xpi_files:
        try:
            shutil.copy2(xpi, target_dir / xpi.name)
            print(f"  {C['G']}📋 {xpi.name}{C['W']}")
            count += 1
        except Exception as e:
            print(f"  {C['R']}❌ {xpi.name}: {e}{C['W']}")

    print(f"\n{C['bold']}{C['G']}🎉 {count} Firefox extensions restored!{C['W']}")
    print(f"   They will load automatically next time you start Firefox.")

if __name__ == "__main__":
    print_banner()
    choice = menu()
    if choice == 1:
        restore_chromium("Chrome")
    elif choice == 2:
        restore_firefox()
    elif choice == 3:
        restore_chromium("Edge")