# Packaging RetailPOS for a client

RetailPOS is a Kivy **desktop** app - there's no server to deploy. To hand it
to a non-technical client, you bundle it into a standalone program with
PyInstaller so they never see Python, pip, or a terminal.

**Important: build on the same OS you're shipping for.** PyInstaller does not
cross-compile - a Windows `.exe` must be built on Windows, a macOS app on
macOS, a Linux binary on Linux. Most retail till hardware is Windows, so
that's almost certainly what you want `build_windows.ps1` for.

## 1. One-time machine setup (on the target OS)

```powershell
# Windows, in PowerShell, from the repo root
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller "kivy_deps.sdl2" "kivy_deps.glew"
```

(`kivy_deps.sdl2`/`glew` are the prebuilt Kivy runtime binaries Windows
needs; they don't exist for Linux/macOS, where Kivy links the system SDL2
instead - `build_linux.sh` skips them automatically.)

On Linux, building Kivy itself from source (no prebuilt wheel for newer
Pythons) additionally needs these system packages first:

```bash
sudo apt-get install -y libgl1-mesa-dev libgles2-mesa-dev libsdl2-dev \
    libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libmtdev-dev \
    pkg-config
```

## 2. Build

```powershell
# Windows
.\packaging\build_windows.ps1
```

```bash
# Linux (mainly useful for a quick smoke-test build, not client delivery)
./packaging/build_linux.sh
```

Output: `dist/RetailPOS/` - a folder containing `RetailPOS.exe` (or
`RetailPOS` on Linux) plus every DLL/.so and data file it needs. That whole
folder is the app; it's relocatable, nothing else needs installing.

Quick sanity check before shipping it: copy `dist/RetailPOS/` to a machine
that does **not** have Python installed and double-click the exe. If it
opens straight to the shift-login screen, you're good.

## 3. Give it to the client

Three options, roughly in order of polish:

- **Zip the folder.** Simplest. They unzip it anywhere and double-click
  `RetailPOS.exe`. No Start Menu entry, no uninstaller.
- **Inno Setup installer** (`packaging/RetailPOS_installer.iss`). Produces a
  normal `RetailPOS_Setup.exe` with a Start Menu entry, optional desktop
  icon, and a proper uninstaller - this is what you want for a real
  rollout. Install [Inno Setup](https://jrsoftware.org/isinfo.php) (free),
  build `dist/RetailPOS/` first, then open/compile the `.iss` file.
- **MSIX/other enterprise installer** - only worth it if the client's IT
  department requires it for managed deployment; Inno Setup covers the
  normal small-retailer case.

## 4. What ships with every install, and what doesn't

The exe is fully self-contained (Python + Kivy + all deps bundled in). On
first launch it creates, next to the exe:

- `data/` - the SQLite databases (inventory, transactions, shifts). This is
  the client's actual business data - **back it up**, and never overwrite it
  when pushing an update.
- `logsKivy/` - Kivy's own log files.
- `variable.txt` - store info (name, address, **VAT number**), shift state,
  quick-add button config, printer settings. Also real data - don't wipe it
  on reinstall.
- `errorLog` - appended to whenever something in the app's own error
  handling catches an exception (receipt-tax calculations, DB writes, etc).
  Worth checking if the client reports odd behavior.

The Inno Setup script is already configured to leave all four alone on
uninstall, so upgrading a client's install (new `.exe` over the old one, or
uninstall-then-reinstall-same-version) does **not** lose their sales
history or shop settings.

## 5. Updating a client's install later

Rebuild `dist/RetailPOS/`, then either:
- re-run the Inno Setup installer over their existing install (it replaces
  the program files, leaves `data/`/`variable.txt` alone), or
- for a zip-only install, just overwrite every file **except** `data/`,
  `logsKivy/`, `variable.txt`, and `errorLog`.

## 6. Receipt / bill customization

Nothing in the packaging changes this - it's already live at runtime. From
the till's Main Menu -> **Store Information**, the manager can set Store
Name, Address Line 1/2, Store Phone, **VAT Number**, an Additional Heading
line, and two footer lines. Every receipt printed or re-printed after that
pulls from whatever is currently saved there - no rebuild, no code change,
takes effect on the very next sale.

The Store Information *screen* is fully generic (it builds its edit form
from `_DEFAULT_DATA`'s keys automatically - add a key there and a field for
it appears with no UI code changes). The printed *receipt layout* itself
lists each field explicitly, in `generateReceipt()` in `mainFunc.py`, so
that line order and formatting stay predictable on a narrow receipt-printer
width. To add another field to the receipt (e.g. a second tax ID), add it
to `_DEFAULT_DATA` and add one `if len(data.get("Your New Field","")) > 1:
receipt.append(...)` line in `generateReceipt()` next to the existing ones.
