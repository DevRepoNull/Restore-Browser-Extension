#!/usr/bin/env python3
"""Cross-platform backup and restore of Chrome, Edge, and Firefox extensions."""

from __future__ import annotations

import json
import os
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Callable, List, Optional

ProgressFn = Callable[[str], None]


def _log(progress: Optional[ProgressFn], message: str) -> None:
    if progress:
        progress(message)


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def version_key(v: str):
    try:
        return tuple(int(x) for x in v.split("_")[0].split("."))
    except Exception:
        return (0,)


def find_latest_version(ext_id_dir: Path) -> Optional[Path]:
    dirs = [d for d in ext_id_dir.iterdir() if d.is_dir()]
    versioned = [d for d in dirs if "_" in d.name or d.name[0].isdigit()]
    pool = versioned or dirs
    return max(pool, key=lambda d: version_key(d.name)) if pool else None


def zip_folder(src: Path, dst: Path) -> None:
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src):
            for f in files:
                full = os.path.join(root, f)
                zf.write(full, os.path.relpath(full, src))


def get_browser_exe(browser: str) -> Optional[str]:
    system = platform.system()
    if browser == "Chrome":
        if system == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]
        elif system == "Darwin":
            paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
        else:
            paths = [
                shutil.which(n)
                for n in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"]
            ]
    elif browser == "Brave":
        if system == "Windows":
            paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            ]
        elif system == "Darwin":
            paths = ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
        else:
            paths = [shutil.which(n) for n in ["brave-browser", "brave"]]
    else:
        if system == "Windows":
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
            ]
        elif system == "Darwin":
            paths = ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
        else:
            paths = [shutil.which(n) for n in ["microsoft-edge", "microsoft-edge-stable", "msedge", "edge"]]
    for p in paths:
        if p and os.path.isfile(p):
            return p
    return None


def get_chromium_user_data(browser: str) -> Path:
    home = Path.home()
    if browser == "Chrome":
        if sys.platform == "win32":
            return Path(os.environ["LOCALAPPDATA"]) / "Google/Chrome/User Data"
        if sys.platform == "darwin":
            return home / "Library/Application Support/Google/Chrome"
        return home / ".config/google-chrome"
    if browser == "Brave":
        if sys.platform == "win32":
            return Path(os.environ["LOCALAPPDATA"]) / "BraveSoftware/Brave-Browser/User Data"
        if sys.platform == "darwin":
            return home / "Library/Application Support/BraveSoftware/Brave-Browser"
        return home / ".config/BraveSoftware/Brave-Browser"
    if sys.platform == "win32":
        return Path(os.environ["LOCALAPPDATA"]) / "Microsoft/Edge/User Data"
    if sys.platform == "darwin":
        return home / "Library/Application Support/Microsoft Edge"
    return home / ".config/microsoft-edge"


def get_firefox_profile_dir() -> Path:
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ["APPDATA"]) / "Mozilla/Firefox/Profiles"
    elif sys.platform == "darwin":
        base = home / "Library/Application Support/Firefox/Profiles"
    else:
        base = home / ".mozilla/firefox"

    if not base.exists():
        raise FileNotFoundError("Firefox profiles directory not found")

    candidates = [d for d in base.iterdir() if d.is_dir() and (d / "extensions.json").exists()]
    if not candidates:
        raise FileNotFoundError("No Firefox profile containing extensions.json found")
    return max(candidates, key=lambda d: (d / "extensions.json").stat().st_mtime)


def get_firefox_ext_dir() -> Optional[Path]:
    try:
        return get_firefox_profile_dir() / "extensions"
    except FileNotFoundError:
        return None


def backup_dir_for(browser: str, base: Optional[Path] = None) -> Path:
    base = base or app_base_dir()
    return base / f"{browser.lower()}_extensions_backup"


def pack_chromium(browser: str, progress: Optional[ProgressFn] = None, dest: Optional[Path] = None) -> int:
    _log(progress, f"Starting backup for {browser}…")
    backup_dir = dest or backup_dir_for(browser)
    backup_dir.mkdir(parents=True, exist_ok=True)

    user_data = get_chromium_user_data(browser)
    ext_root = user_data / "Default" / "Extensions"
    if not ext_root.exists():
        raise FileNotFoundError(f"Extensions folder not found: {ext_root}")

    exe = get_browser_exe(browser)
    count = 0
    for ext_id_dir in sorted(ext_root.iterdir()):
        if not ext_id_dir.is_dir():
            continue
        ext_id = ext_id_dir.name
        latest = find_latest_version(ext_id_dir)
        if not latest:
            _log(progress, f"Skip {ext_id}: no version folder")
            continue

        _log(progress, f"Packing {ext_id} ({latest.name})")
        success = False
        if exe:
            with tempfile.TemporaryDirectory() as tmp_data:
                for headless in ([], ["--headless=new"], ["--headless"]):
                    cmd = [
                        exe,
                        f"--pack-extension={latest}",
                        f"--user-data-dir={tmp_data}",
                        "--no-first-run",
                        "--no-default-browser-check",
                    ]
                    if headless:
                        cmd.insert(1, headless[0])
                    try:
                        subprocess.run(
                            cmd,
                            check=True,
                            timeout=90,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        success = True
                        break
                    except Exception:
                        continue

        if success:
            crx_files = list(ext_id_dir.glob("*.crx"))
            if crx_files:
                newest = max(crx_files, key=os.path.getctime)
                shutil.copy2(newest, backup_dir / f"{ext_id}.crx")
                _log(progress, f"Saved {ext_id}.crx")
                count += 1
                continue

        zip_path = backup_dir / f"{ext_id}.zip"
        zip_folder(latest, zip_path)
        _log(progress, f"Saved {ext_id}.zip (fallback)")
        count += 1

    _log(progress, f"Done. {count} extension(s) saved to {backup_dir}")
    return count


def pack_firefox(progress: Optional[ProgressFn] = None, dest: Optional[Path] = None) -> int:
    _log(progress, "Starting backup for Firefox…")
    backup_dir = dest or backup_dir_for("firefox")
    backup_dir.mkdir(parents=True, exist_ok=True)

    profile_dir = get_firefox_profile_dir()
    with open(profile_dir / "extensions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    addons = data.get("addons", [])
    count = 0
    for addon in addons:
        addon_id = addon.get("id")
        if not addon_id:
            continue
        candidate_xpi = profile_dir / "extensions" / f"{addon_id}.xpi"
        candidate_dir = profile_dir / "extensions" / addon_id
        try:
            if candidate_xpi.exists():
                shutil.copy2(candidate_xpi, backup_dir / f"{addon_id}.xpi")
                _log(progress, f"Copied {addon_id}.xpi")
                count += 1
            elif candidate_dir.is_dir():
                zip_folder(candidate_dir, backup_dir / f"{addon_id}.xpi")
                _log(progress, f"Packed {addon_id}.xpi")
                count += 1
        except Exception as e:
            _log(progress, f"Failed {addon_id}: {e}")

    _log(progress, f"Done. {count} Firefox extension(s) saved to {backup_dir}")
    return count


def extract_crx(crx_path: Path, out_dir: Path) -> None:
    with open(crx_path, "rb") as f:
        magic = f.read(4)
        if magic != b"Cr24":
            raise ValueError("Not a valid CRX file")
        ver = struct.unpack("<I", f.read(4))[0]
        if ver == 2:
            pub = struct.unpack("<I", f.read(4))[0]
            sig = struct.unpack("<I", f.read(4))[0]
            f.read(pub)
            f.read(sig)
        elif ver == 3:
            header_size = struct.unpack("<I", f.read(4))[0]
            f.read(header_size)
        else:
            raise ValueError(f"Unsupported CRX version {ver}")
        with zipfile.ZipFile(f) as zf:
            zf.extractall(out_dir)


def extract_zip(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)


def restore_chromium(browser: str, progress: Optional[ProgressFn] = None, source: Optional[Path] = None) -> Path:
    backup_dir = source or backup_dir_for(browser)
    if not backup_dir.exists():
        raise FileNotFoundError(f"Backup folder not found: {backup_dir}")

    restore_dir = (source.parent if source else app_base_dir()) / "restored_extensions"
    restore_dir.mkdir(exist_ok=True)

    archives: List[Path] = sorted(backup_dir.glob("*.crx")) + sorted(backup_dir.glob("*.zip"))
    if not archives:
        raise FileNotFoundError("No .crx or .zip backup files found")

    count = 0
    for archive in archives:
        ext_id = archive.stem
        dest = restore_dir / ext_id
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)
        _log(progress, f"Extracting {archive.name}")
        try:
            if archive.suffix.lower() == ".crx":
                extract_crx(archive, dest)
            else:
                extract_zip(archive, dest)
            count += 1
        except Exception as e:
            _log(progress, f"Failed {archive.name}: {e}")

    _log(progress, f"Restored {count} extension(s) to {restore_dir}")
    return restore_dir


def restore_firefox(progress: Optional[ProgressFn] = None, source: Optional[Path] = None) -> int:
    backup_dir = source or backup_dir_for("firefox")
    if not backup_dir.exists():
        raise FileNotFoundError(f"Backup folder not found: {backup_dir}")

    xpi_files = list(backup_dir.glob("*.xpi"))
    if not xpi_files:
        raise FileNotFoundError("No .xpi files found")

    target_dir = get_firefox_ext_dir()
    if not target_dir:
        raise FileNotFoundError("Firefox profile extensions folder not found")

    target_dir.mkdir(exist_ok=True)
    count = 0
    for xpi in xpi_files:
        try:
            shutil.copy2(xpi, target_dir / xpi.name)
            _log(progress, f"Copied {xpi.name}")
            count += 1
        except Exception as e:
            _log(progress, f"Failed {xpi.name}: {e}")

    _log(progress, f"Restored {count} Firefox extension(s). Restart Firefox to load them.")
    return count
