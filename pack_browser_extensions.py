#!/usr/bin/env python3
"""
🎒 Browser Extension Packer – Fun Edition
Cross‑Platform (Chrome / Firefox / Edge)
Backup your browser extensions with style!
"""

import os
import sys
import subprocess
import platform
import shutil
import tempfile
import zipfile
import time
import json as json_module
import threading
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# ---- Color/Emoji helpers (ANSI) ----
C = {
    'R': '\033[91m', 'G': '\033[92m', 'Y': '\033[93m', 'B': '\033[94m',
    'M': '\033[95m', 'C': '\033[96m', 'W': '\033[0m', 'bold': '\033[1m'
}
ANIM = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

def print_banner():
    print(f"{C['C']}{'='*60}{C['W']}")
    print(f"{C['bold']}{C['M']}🎒  BROWSER EXTENSION PACKER  🎒{C['W']}")
    print(f"{C['C']}Backup your extensions with a touch of fun!{C['W']}")
    print(f"{C['C']}{'='*60}{C['W']}\n")

def menu():
    print("Select the browser to backup:")
    browsers = [
        (f"{C['G']}Chrome{C['W']}",   f"  [{C['Y']}1{C['W']}] {C['G']}🌐 Google Chrome{C['W']}"),
        (f"{C['R']}Firefox{C['W']}",  f"  [{C['Y']}2{C['W']}] {C['R']}🦊 Mozilla Firefox{C['W']}"),
        (f"{C['B']}Edge{C['W']}",     f"  [{C['Y']}3{C['W']}] {C['B']}🧭 Microsoft Edge{C['W']}"),
    ]
    for _, line in browsers:
        print(line)
    try:
        choice = int(input(f"\n{C['Y']}👉 Enter number (1-3): {C['W']}").strip())
        if choice in (1,2,3):
            return choice
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

# ---- Utility functions (same robust logic) ----
def get_desktop_dir():
    home = Path.home()
    if sys.platform == "win32":
        desktop = Path(os.environ.get("USERPROFILE", home)) / "Desktop"
    elif sys.platform == "darwin":
        desktop = home / "Desktop"
    else:
        try:
            xdg = subprocess.check_output(["xdg-user-dir", "DESKTOP"], text=True).strip()
            if xdg and os.path.isdir(xdg): return Path(xdg)
        except: pass
        desktop = home / "Desktop"
    return desktop if desktop.exists() else home

def version_key(v):
    try: return tuple(int(x) for x in v.split('_')[0].split('.'))
    except: return (0,)

def find_latest_version(ext_id_dir):
    dirs = [d for d in ext_id_dir.iterdir() if d.is_dir() and '_' in d.name]
    return max(dirs, key=lambda d: version_key(d.name)) if dirs else None

def zip_folder(src, dst):
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src):
            for f in files:
                full = os.path.join(root, f)
                zf.write(full, os.path.relpath(full, src))

def get_browser_exe(browser):
    system = platform.system()
    if browser == "Chrome":
        if system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
        elif system == "Darwin":
            paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
        else:
            paths = [shutil.which(n) for n in ["google-chrome","google-chrome-stable","chrome"] if shutil.which(n)]
    else:  # Edge
        if system == "Windows":
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe")
            ]
        elif system == "Darwin":
            paths = ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
        else:
            paths = [shutil.which(n) for n in ["microsoft-edge","microsoft-edge-stable","edge"] if shutil.which(n)]
    for p in paths:
        if p and os.path.isfile(p): return p
    return None

def get_chromium_user_data(browser):
    home = Path.home()
    if browser == "Chrome":
        if sys.platform == "win32":
            return Path(os.environ["LOCALAPPDATA"]) / "Google/Chrome/User Data"
        elif sys.platform == "darwin":
            return home / "Library/Application Support/Google/Chrome"
        else:
            return home / ".config/google-chrome"
    else:  # Edge
        if sys.platform == "win32":
            return Path(os.environ["LOCALAPPDATA"]) / "Microsoft/Edge/User Data"
        elif sys.platform == "darwin":
            return home / "Library/Application Support/Microsoft Edge"
        else:
            return home / ".config/microsoft-edge"

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

def pack_chromium(browser):
    print(f"\n{C['bold']}{C['G']}🚀 Starting pack for {browser}...{C['W']}")
    backup_dir = SCRIPT_DIR / f"{browser.lower()}_extensions_backup"
    backup_dir.mkdir(exist_ok=True)

    user_data = get_chromium_user_data(browser)
    ext_root = user_data / "Default" / "Extensions"
    if not ext_root.exists():
        print(f"{C['R']}❌ Extensions folder not found.{C['W']}")
        return

    exe = get_browser_exe(browser)
    if not exe:
        print(f"{C['R']}❌ {browser} executable not found.{C['W']}")
        return

    count = 0
    for ext_id_dir in ext_root.iterdir():
        if not ext_id_dir.is_dir(): continue
        ext_id = ext_id_dir.name
        print(f"\n{C['Y']}📦 {ext_id}{C['W']}")

        latest = find_latest_version(ext_id_dir)
        if not latest:
            print(f"  {C['M']}⏩ No version folder, skipping{C['W']}")
            continue

        # Try native packing with a fun spinner
        import threading
        stop_event = threading.Event()
        t = threading.Thread(target=spinning_animation, args=(stop_event, f"Packing {latest.name} via {browser}"))
        t.start()

        success = False
        with tempfile.TemporaryDirectory() as tmp_data:
            for headless in ([], ['--headless=new'], ['--headless']):
                cmd = [
                    exe,
                    f"--pack-extension={latest}",
                    f"--user-data-dir={tmp_data}",
                    "--no-first-run", "--no-default-browser-check"
                ]
                if headless: cmd.insert(1, headless[0])
                try:
                    subprocess.run(cmd, check=True, timeout=90,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    success = True
                    break
                except:
                    continue
        stop_event.set()
        t.join()

        if success:
            crx_files = list(ext_id_dir.glob("*.crx"))
            if crx_files:
                newest = max(crx_files, key=os.path.getctime)
                shutil.copy2(newest, backup_dir / f"{ext_id}.crx")
                print(f"  {C['G']}✅ Packed as .crx{C['W']}")
                count += 1
                continue

        # Fallback to ZIP
        print(f"  {C['Y']}⚠️  Chrome packing failed, falling back to ZIP...{C['W']}")
        zip_path = backup_dir / f"{ext_id}.zip"
        try:
            zip_folder(latest, zip_path)
            print(f"  {C['G']}✅ Saved as .zip{C['W']}")
            count += 1
        except Exception as e:
            print(f"  {C['R']}❌ {e}{C['W']}")

    print(f"\n{C['bold']}{C['G']}🎉 {count} extensions backed up from {browser}!{C['W']}")
    print(f"   📁 {backup_dir}")

def get_firefox_profile_dir():
    """
    Return the path to the default Firefox profile folder
    (the one that contains extensions.json).
    """
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"]) / "Mozilla/Firefox/Profiles"
    elif sys.platform == "darwin":
        base = home / "Library/Application Support/Firefox/Profiles"
    else:
        base = home / ".mozilla/firefox"

    if not base.exists():
        raise FileNotFoundError("Firefox profiles directory not found")

    # Look for the profile with the most recent activity (or first with extensions.json)
    candidates = []
    for d in base.iterdir():
        if d.is_dir() and (d / "extensions.json").exists():
            candidates.append(d)

    if not candidates:
        raise FileNotFoundError("No Firefox profile containing extensions.json found")
    # pick the profile with the newest extensions.json
    latest = max(candidates, key=lambda d: (d / "extensions.json").stat().st_mtime)
    return latest

def pack_firefox():
    print(f"\n{C['bold']}{C['R']}🦊 Starting pack for Firefox...{C['W']}")
    backup_dir = SCRIPT_DIR / "firefox_extensions_backup"
    backup_dir.mkdir(exist_ok=True)

    try:
        profile_dir = get_firefox_profile_dir()
    except FileNotFoundError as e:
        print(f"{C['R']}❌ {e}{C['W']}")
        return

    # Read installed extensions from extensions.json
    import json as json_module
    ext_json_path = profile_dir / "extensions.json"
    with open(ext_json_path, "r", encoding="utf-8") as f:
        data = json_module.load(f)

    addons = data.get("addons", [])
    if not addons:
        print(f"{C['Y']}ℹ️  No extensions listed in extensions.json{C['W']}")
        return

    count = 0
    for addon in addons:
        addon_id = addon.get("id")
        if not addon_id:
            continue

        # Determine the source location of this addon
        # It could be an .xpi file in the "extensions" folder, or an unpacked directory,
        # or located in a different path (like built-in system addons).
        extension_dir = None
        xpi_path = None

        # Check for a regular .xpi in the profile's extensions/ folder
        candidate_xpi = profile_dir / "extensions" / f"{addon_id}.xpi"
        if candidate_xpi.exists():
            xpi_path = candidate_xpi
        else:
            # Check if it's an unpacked directory (often with the same name)
            candidate_dir = profile_dir / "extensions" / addon_id
            if candidate_dir.is_dir():
                extension_dir = candidate_dir
            else:
                # For system addons or others, they might be in the Firefox installation directory
                # We skip those as they are not portable.
                continue

        print(f"  {C['Y']}📦 {addon_id}{C['W']} ", end="", flush=True)

        try:
            if xpi_path:
                shutil.copy2(xpi_path, backup_dir / f"{addon_id}.xpi")
                print(f"{C['G']}✅ (xpi){C['W']}")
                count += 1
            elif extension_dir:
                # Create an .xpi by zipping the unpacked directory
                dest_xpi = backup_dir / f"{addon_id}.xpi"
                import threading
                stop_event = threading.Event()
                t = threading.Thread(target=spinning_animation, args=(stop_event, "Zipping..."))
                t.start()
                zip_folder(extension_dir, dest_xpi)
                stop_event.set()
                t.join()
                print(f"\r  {C['Y']}📦 {addon_id}{C['W']} {C['G']}✅ (zip -> xpi){C['W']}")
                count += 1
        except Exception as e:
            print(f"{C['R']}❌ {e}{C['W']}")

    print(f"\n{C['bold']}{C['G']}🎉 {count} Firefox extensions backed up!{C['W']}")
    print(f"   📁 {backup_dir}")
    print(f"\n{C['bold']}{C['R']}🦊 Starting pack for Firefox...{C['W']}")
    backup_dir = SCRIPT_DIR / "firefox_extensions_backup"
    backup_dir.mkdir(exist_ok=True)

    ext_dir = get_firefox_ext_dir()
    if not ext_dir or not ext_dir.exists():
        print(f"{C['R']}❌ No Firefox extensions folder found.{C['W']}")
        return

    xpi_files = list(ext_dir.glob("*.xpi"))
    if not xpi_files:
        print(f"{C['Y']}ℹ️  No .xpi files found.{C['W']}")
        return

    count = 0
    for xpi in xpi_files:
        shutil.copy2(xpi, backup_dir / xpi.name)
        print(f"  {C['G']}📋 {xpi.name}{C['W']}")
        count += 1
    print(f"\n{C['bold']}{C['G']}🎉 {count} Firefox extensions backed up!{C['W']}")
    print(f"   📁 {backup_dir}")

if __name__ == "__main__":
    print_banner()
    choice = menu()
    if choice == 1:
        pack_chromium("Chrome")
    elif choice == 2:
        pack_firefox()
    elif choice == 3:
        pack_chromium("Edge")