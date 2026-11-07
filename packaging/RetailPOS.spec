# PyInstaller spec for RetailPOS.
#
# Build (from the repo root, with the project's venv active and
# pyinstaller installed into it):
#
#   pyinstaller packaging/RetailPOS.spec --noconfirm
#
# Output lands in dist/RetailPOS/ (onedir build - see notes in
# packaging/README.md for why onedir is used instead of --onefile).
#
# This must be run ON the target OS (Windows build -> run on Windows,
# macOS build -> run on macOS, etc). PyInstaller does not cross-compile.
#
# Note: PyInstaller's own built-in hook-kivy.py is NOT used here - see
# packaging/pyinstaller_hooks/hook-kivy.py for why (short version: it
# imports kivy.core.window to work out what to bundle, which tries to
# create a real window/OpenGL context, and hangs indefinitely instead of
# failing cleanly on a headless CI runner with no GPU). This spec computes
# the same information by hand instead and overrides hookspath so
# PyInstaller never reaches the built-in hook.

import os
import kivy
import escpos
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Repo root = the directory this spec file's parent sits in
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(SPEC)), ".."))

# kivy_deps (sdl2/glew) ships prebuilt SDL2/GLEW binaries and is only
# published for Windows (pip install "kivy_deps.sdl2" "kivy_deps.glew" there).
# On Linux/macOS, Kivy links the system's own SDL2 and PyInstaller's binary
# dependency walker already picks those .so/.dylib files up, so this block
# is Windows-only and safe to skip elsewhere.
kivy_dep_binaries = []
if os.name == "nt":
    from kivy_deps import sdl2, glew
    kivy_dep_binaries = [Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]

# Kivy's own data/module dirs (fonts, default images, providers) need to
# ship alongside the exe or windows/widgets render with missing assets.
kivy_datas = [
    (kivy.kivy_data_dir, os.path.join("kivy_install", os.path.basename(kivy.kivy_data_dir))),
    (kivy.kivy_modules_dir, os.path.join("kivy_install", os.path.basename(kivy.kivy_modules_dir))),
]

# Core providers (window/text/image backends etc.) are picked with
# __import__ at runtime, so PyInstaller's static import scan won't find them
# on its own - this app has no audio/video/camera, so those providers are
# deliberately left out to keep the build smaller.
kivy_hiddenimports = sorted(set(
    [
        "xml.etree.cElementTree",
        "kivy.core.gl",
        "kivy.weakmethod",
        "kivy.core.window.window_info",
    ]
    + collect_submodules("kivy.graphics")
    + collect_submodules("kivy.core.window")
    + collect_submodules("kivy.core.text")
    + collect_submodules("kivy.core.image")
    + collect_submodules("kivy.core.clipboard")
))

a = Analysis(
    [os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=kivy_datas + collect_data_files("escpos") + collect_data_files("kivymd") + [
        (os.path.join(PROJECT_ROOT, "posapp.kv"), "."),
        (os.path.join(PROJECT_ROOT, "images"), "images"),
    ],
    # KivyMD widgets are loaded on demand by Kivy's Factory from KivyMD's own
    # internal .kv files (e.g. the first time a screen uses an MDSpinner).
    # PyInstaller's static import scan can't see those - it only sees what
    # main.py/kivyScripts/*.py literally `import`, so without pulling in
    # every kivymd.uix.* submodule up front, the app crashes the first time
    # it touches a widget type that happened not to be explicitly imported
    # anywhere in this project's own source (this is exactly how the
    # ModuleNotFoundError: kivymd.uix.spinner failure during packaging
    # testing showed up).
    hiddenimports=kivy_hiddenimports + collect_submodules("kivymd") + [
        "databaseScripts.inventory",
        "databaseScripts.allTransactions",
        "databaseScripts.transactions",
        "databaseScripts.shifts",
        "kivyScripts.screenManager",
        "kivyScripts.inventoryScreen",
        "kivyScripts.storeScreen",
        "kivyScripts.reportsScreen",
        "kivyScripts.retailAdditonalScreens",
        "kivyScripts.retailScreen",
        "kivyScripts.settingsScreen",
        "usb.backend.libusb1",
        "escpos.printer",
        "openpyxl",
    ],
    hookspath=[os.path.join(PROJECT_ROOT, "packaging", "pyinstaller_hooks")],
    runtime_hooks=[],
    excludes=["tkinter", "_tkinter", "twisted"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RetailPOS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    # The app's own source uses plain relative paths - "./images/...",
    # "./data", "./logsKivy", "./posapp.kv" - resolved against the current
    # working directory. PyInstaller 6+ defaults to nesting bundled data
    # under dist/RetailPOS/_internal/, which breaks those lookups (the app
    # starts but every image load fails). contents_directory="." keeps the
    # classic flat layout instead, so bundled data sits directly next to
    # RetailPOS.exe, matching what the source expects.
    contents_directory=".",
    # Windows needs a real .ico file here (PNG won't work reliably).
    # Generate one (e.g. via an online PNG->ICO converter or Pillow) from
    # images/cash-register-g87e120a86_640.png, drop it in packaging/ as
    # app_icon.ico, and uncomment the next line:
    # icon=os.path.join(PROJECT_ROOT, "packaging", "app_icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *kivy_dep_binaries,
    strip=False,
    upx=False,
    name="RetailPOS",
)
