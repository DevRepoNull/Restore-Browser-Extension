#!/usr/bin/env python3
"""Compatibility CLI: restore extensions (same as `python app.py --cli restore`)."""

import sys

from extension_backup import core


def main():
    print("Extension Vault — restore")
    print("  [1] Google Chrome")
    print("  [2] Mozilla Firefox")
    print("  [3] Microsoft Edge")
    print("  [4] Brave")
    try:
        choice = int(input("Enter number (1-4): ").strip())
    except Exception:
        print("Invalid choice")
        sys.exit(1)
    mapping = {1: "Chrome", 2: "Firefox", 3: "Edge", 4: "Brave"}
    browser = mapping.get(choice)
    if not browser:
        print("Invalid choice")
        sys.exit(1)

    def log(m):
        print(m)

    if browser == "Firefox":
        input("Close Firefox completely, then press Enter…")
        core.restore_firefox(progress=log)
    else:
        core.restore_chromium(browser, progress=log)


if __name__ == "__main__":
    main()
