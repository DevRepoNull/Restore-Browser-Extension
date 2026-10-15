#!/usr/bin/env python3
"""Tkinter desktop UI for Browser Extension Backup & Restore."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from extension_backup import __version__
from extension_backup import core

BROWSERS = ("Chrome", "Firefox", "Edge", "Brave")

BG = "#0f1419"
PANEL = "#1a2332"
ACCENT = "#3d8bfd"
TEXT = "#e8eef7"
MUTED = "#8b9bb4"
OK = "#3dd68c"
WARN = "#f5a524"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Extension Vault  ·  v{__version__}")
        self.geometry("820x620")
        self.minsize(720, 540)
        self.configure(bg=BG)
        self._busy = False
        self._custom_dir = tk.StringVar(value=str(core.app_base_dir()))
        self._browser = tk.StringVar(value="Chrome")
        self._setup_style()
        self._build()

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("TRadiobutton", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.map("TRadiobutton", background=[("active", PANEL)])
        style.configure("TProgressbar", troughcolor="#0b1016", background=ACCENT)

    def _build(self):
        pad = ttk.Frame(self, style="TFrame")
        pad.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        ttk.Label(pad, text="Extension Vault", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            pad,
            text="Backup and restore Chrome, Edge, Brave, and Firefox extensions — no Python required when using a release build.",
            style="Sub.TLabel",
            wraplength=760,
        ).pack(anchor="w", pady=(4, 16))

        card = ttk.Frame(pad, style="Card.TFrame")
        card.pack(fill=tk.X, pady=(0, 12))
        inner = tk.Frame(card, bg=PANEL, padx=16, pady=14)
        inner.pack(fill=tk.X)

        tk.Label(inner, text="Browser", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        row = tk.Frame(inner, bg=PANEL)
        row.pack(anchor="w", pady=(6, 12))
        for name in BROWSERS:
            ttk.Radiobutton(row, text=name, value=name, variable=self._browser).pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(inner, text="Working folder (backups are stored here)", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(
            anchor="w"
        )
        path_row = tk.Frame(inner, bg=PANEL)
        path_row.pack(fill=tk.X, pady=(6, 0))
        tk.Entry(path_row, textvariable=self._custom_dir, bg="#101820", fg=TEXT, insertbackground=TEXT, relief="flat").pack(
            side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8)
        )
        ttk.Button(path_row, text="Browse…", command=self._browse).pack(side=tk.LEFT)

        actions = ttk.Frame(pad, style="TFrame")
        actions.pack(fill=tk.X, pady=8)
        ttk.Button(actions, text="Backup extensions", style="Accent.TButton", command=self._backup).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(actions, text="Restore extensions", command=self._restore).pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(pad, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(8, 8))

        tk.Label(pad, text="Log", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        self.log = tk.Text(
            pad,
            height=16,
            bg="#101820",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            wrap="word",
            font=("Consolas", 10),
        )
        self.log.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self._append("Ready. Close the selected browser before backing up or restoring.")

    def _browse(self):
        chosen = filedialog.askdirectory(initialdir=self._custom_dir.get() or str(Path.home()))
        if chosen:
            self._custom_dir.set(chosen)

    def _append(self, line: str):
        self.log.insert(tk.END, line + "\n")
        self.log.see(tk.END)

    def _set_busy(self, busy: bool):
        self._busy = busy
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _run(self, fn):
        if self._busy:
            return
        self._set_busy(True)

        def work():
            try:
                fn()
            except Exception as e:
                self.after(0, lambda: self._append(f"Error: {e}"))
                self.after(0, lambda: messagebox.showerror("Extension Vault", str(e)))
            finally:
                self.after(0, lambda: self._set_busy(False))

        threading.Thread(target=work, daemon=True).start()

    def _base(self) -> Path:
        p = Path(self._custom_dir.get().strip() or str(core.app_base_dir()))
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _backup(self):
        browser = self._browser.get()
        base = self._base()

        def job():
            def prog(msg):
                self.after(0, lambda m=msg: self._append(m))

            dest = core.backup_dir_for(browser, base)
            if browser == "Firefox":
                n = core.pack_firefox(progress=prog, dest=dest)
            else:
                n = core.pack_chromium(browser, progress=prog, dest=dest)
            self.after(
                0,
                lambda: messagebox.showinfo("Backup complete", f"{n} extension(s) saved to:\n{dest}"),
            )

        self._run(job)

    def _restore(self):
        browser = self._browser.get()
        base = self._base()

        def job():
            def prog(msg):
                self.after(0, lambda m=msg: self._append(m))

            source = core.backup_dir_for(browser, base)
            if browser == "Firefox":
                if not messagebox.askokcancel(
                    "Firefox",
                    "Firefox must be fully closed before restore. Continue?",
                ):
                    return
                n = core.restore_firefox(progress=prog, source=source)
                self.after(0, lambda: messagebox.showinfo("Restore complete", f"{n} add-on(s) copied into the Firefox profile."))
            else:
                out = core.restore_chromium(browser, progress=prog, source=source)
                page = "chrome://extensions" if browser != "Edge" else "edge://extensions"
                if browser == "Brave":
                    page = "brave://extensions"
                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Restore complete",
                        f"Unpacked extensions are in:\n{out}\n\nOpen {page}, enable Developer mode, then Load unpacked.",
                    ),
                )

        self._run(job)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
