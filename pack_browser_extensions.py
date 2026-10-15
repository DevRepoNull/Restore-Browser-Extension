#!/usr/bin/env python3
"""Compatibility CLI: backup extensions (same as `python app.py --cli backup`)."""

import sys

from extension_backup import core


def main():
    print("Extension Vault — backup")
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
        core.pack_firefox(progress=log)
    else:
        core.pack_chromium(browser, progress=log)


if __name__ == "__main__":
    main()
