#!/usr/bin/env python3
"""Entry point: graphical app by default, CLI with --cli."""

from __future__ import annotations

import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description="Backup and restore browser extensions.")
    parser.add_argument("--cli", action="store_true", help="Use the terminal instead of the window")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["backup", "restore"],
        help="CLI action (requires --cli)",
    )
    parser.add_argument(
        "--browser",
        choices=["Chrome", "Firefox", "Edge", "Brave"],
        default="Chrome",
    )
    args = parser.parse_args(argv)

    if args.cli:
        from extension_backup import core

        def log(msg):
            print(msg)

        if args.action == "backup":
            if args.browser == "Firefox":
                core.pack_firefox(progress=log)
            else:
                core.pack_chromium(args.browser, progress=log)
        elif args.action == "restore":
            if args.browser == "Firefox":
                core.restore_firefox(progress=log)
            else:
                core.restore_chromium(args.browser, progress=log)
        else:
            parser.error("CLI mode needs backup or restore")
        return 0

    try:
        from extension_backup.gui import main as gui_main
    except ModuleNotFoundError as e:
        if "tkinter" in str(e).lower() or "tkinter" in repr(e).lower():
            print("Tkinter is not installed. Use: python app.py --cli backup --browser Chrome")
            print("On Debian/Ubuntu: sudo apt install python3-tk")
            return 1
        raise

    gui_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
