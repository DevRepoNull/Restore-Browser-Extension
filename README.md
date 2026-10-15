# Extension Vault

Desktop tool to **back up and restore** extensions from **Google Chrome**, **Microsoft Edge**, **Brave**, and **Mozilla Firefox**.

It runs as a windowed app on Windows, macOS, and Linux. Release builds are single executables — no Python install required.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why this exists

Moving to a new machine, or resetting a profile, usually means reinstalling every add-on by hand. Extension Vault copies the installed extension files from the browser profile, stores them next to the app, and puts them back later.

---

## Features

- **Graphical app** (Tkinter) — pick a browser, choose a folder, Backup or Restore
- **CLI** still available for scripts and power users
- **Chromium packing** via the browser’s own `--pack-extension`, with ZIP fallback
- **Firefox** copies `.xpi` files (or zips unpacked add-ons) from the active profile
- **Brave** supported in addition to Chrome and Edge
- **No runtime pip dependencies** — Python standard library only
- **Ready-made binaries** for Windows (`.exe`), macOS, and Linux via GitHub Actions + PyInstaller

---

## Install without Python (recommended)

1. Open the [Releases](../../releases) page.
2. Download the build for your OS:
   - Windows: `ExtensionVault.exe`
   - macOS: `ExtensionVault`
   - Linux: `ExtensionVault`
3. Run it. On macOS/Linux you may need `chmod +x ExtensionVault`.

GitHub Actions workflow: [`.github/workflows/release.yml`](.github/workflows/release.yml). Tag a version (`v2.0.0`) or run the workflow manually to produce artifacts.

---

## Run from source

Requires **Python 3.9+**. No extra packages.

```bash
git clone https://github.com/DevRepoNull/Restore-Browser-Extension.git
cd Restore-Browser-Extension
python app.py
```

Close the target browser before backup or restore (especially Firefox).

### Command line

```bash
python app.py --cli backup --browser Chrome
python app.py --cli restore --browser Firefox
```

The older scripts still work:

```bash
python pack_browser_extensions.py
python restore_browser_extensions.py
```

---

## How restore works

| Browser | After restore |
| --- | --- |
| Chrome / Edge / Brave | Folders appear under `restored_extensions/`. Open `chrome://extensions` (or `edge://` / `brave://`), enable **Developer mode**, **Load unpacked**. |
| Firefox | `.xpi` files are copied into the default profile `extensions/` directory. Start Firefox with the browser fully closed during copy. |

Chromium unpacked reloads get a **new extension ID** because the original developer key is not in the profile. Settings keyed to the old ID are not migrated.

---

## Layout after a backup

```text
Restore-Browser-Extension/
├── app.py
├── extension_backup/
│   ├── core.py
│   └── gui.py
├── chrome_extensions_backup/
├── firefox_extensions_backup/
├── edge_extensions_backup/
├── brave_extensions_backup/
└── restored_extensions/
```

The working folder can be changed in the UI.

---

## Building binaries locally

```bash
pip install -r requirements-build.txt
pyinstaller --noconfirm --clean --windowed --onefile --name ExtensionVault app.py
```

Output: `dist/ExtensionVault` (or `ExtensionVault.exe` on Windows).

---

## Troubleshooting

| Symptom | What to try |
| --- | --- |
| Browser executable not found | Install the browser in the default location, or use ZIP-only backup (automatic fallback). |
| Extensions folder not found | Open the browser once so a profile is created. Only the **Default** Chromium profile is scanned. |
| Firefox restore fails | Quit Firefox completely (check the system tray / Activity Monitor). |
| Empty Firefox backup | Confirm add-ons in `about:addons`. Temporary `about:debugging` loads are not listed in `extensions.json`. |
| Chrome packing fails | Expected on some versions; the app stores a ZIP of the unpacked folder instead. |

---

## Contributing

Issues and pull requests are welcome. Please describe OS, browser, and whether you used the GUI, CLI, or a packaged binary.

---

## License

MIT — see [LICENSE](LICENSE).
