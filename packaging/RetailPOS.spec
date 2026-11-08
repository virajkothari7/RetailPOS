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
# Note on a subtle Kivy/CI interaction, read before changing anything below:
#
# Several things during this spec's OWN execution (not the packaged app's -
# THIS FILE's, while PyInstaller is analyzing it) end up importing
# kivy.core.window - PyInstaller's own built-in hook-kivy.py does it via
# get_deps_minimal(), and collect_submodules("kivy.graphics") /
# collect_submodules("kivy.core.text") do it too, transitively, since those
# packages import Window themselves. Importing kivy.core.window makes Kivy
# actually try to create a window and probe the graphics driver for a real
# OpenGL context. On a machine with a real GPU that's harmless. On a
# headless CI runner with only a software/GDI fallback (stuck at OpenGL
# 1.1, below Kivy's required 2.0), Kivy's window creation doesn't fail
# cleanly - it hangs indefinitely instead, with no further output. That
# hang is what stalled the Windows GitHub Actions build for 24+ minutes
# doing nothing, twice, before this was tracked down (a sys.modules stub
# to short-circuit the import was tried first and did NOT work - Kivy
# still reached real window creation some other way, so it's not used
# here). What actually works is KIVY_GL_BACKEND=mock, set as an
# environment variable in .github/workflows/build-windows.yml before this
# spec runs (also set here for anyone invoking pyinstaller directly, e.g.
# packaging/build_windows.ps1) - it makes Kivy use its own built-in mock
# graphics backend instead of touching any real driver, confirmed by
# direct test to create a Window with no hang and no crash. This has zero
# effect on the packaged app's own runtime behavior on the client's
# machine: it's only read while analyzing/building, not by the shipped
# exe, which still uses a real window/GL backend when the client runs it.
#
# kivy.core.window's own submodules are still listed by hand further down
# instead of via collect_submodules() - harmless now that the hang itself
# is fixed, but avoids the import happening at all for that one case,
# which keeps this spec's own behavior easy to reason about.

import os
os.environ.setdefault("KIVY_GL_BACKEND", "mock")

import kivy
import escpos
import libusb
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

# libusb-1.0: pyusb/escpos can't talk to any USB device (printer or the
# Settings screen's device list) without this shared library, and Windows
# doesn't provide it - confirmed on a real Windows install via the error
# dialog this app now shows instead of silently doing nothing:
# "Could not list USB devices: No backend available".
#
# Earlier attempt used collect_data_files("libusb") plus reading
# libusb._platform.DLL_PATH at *runtime* to point pyusb at it - that's
# exactly what produced the error above: DLL_PATH is computed from
# os.path.dirname(os.path.abspath(__file__)) inside the libusb package's
# own module, and PyInstaller does not give every bundled package's
# modules a real on-disk __file__ that lines up with where
# collect_data_files placed their data (pure-Python modules normally live
# inside the frozen PYZ archive, not as loose files) - so at runtime, in
# the shipped exe, that path resolution silently failed and the except
# Exception in mainFunc.py fell back to usb_backend = None, same as if
# libusb had never been bundled at all.
#
# Fixed by sidestepping the package's own path logic entirely: resolve
# the real DLL's location here, at *spec-build time* (this file runs as
# an ordinary, non-frozen Python process on the build machine, so
# DLL_PATH is reliable here), and place that one file directly at the
# bundle root via `binaries` - next to RetailPOS.exe, same as every other
# top-level file, since contents_directory="." below keeps everything
# flat. mainFunc.py then builds the path itself from sys.executable's
# own directory when frozen, instead of importing libusb or trusting its
# DLL_PATH at runtime at all.
libusb_binaries = [(libusb._platform.DLL_PATH, ".")] if os.path.isfile(libusb._platform.DLL_PATH) else []

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
#
# kivy.core.window's own submodules are listed by hand rather than via
# collect_submodules() - that function imports the package it's collecting
# from in order to list it, and importing kivy.core.window is exactly the
# thing this whole file is written to avoid (see the note up top). This is
# the complete provider list Kivy 2.0.0 ships for that package (confirmed
# from a successful build's own hidden-import log), so nothing is lost.
kivy_hiddenimports = sorted(set(
    [
        "xml.etree.cElementTree",
        "kivy.core.gl",
        "kivy.weakmethod",
        "kivy.core.window.window_sdl2",
        "kivy.core.window.window_pygame",
        "kivy.core.window.window_egl_rpi",
        "kivy.core.window.window_info",
        # Kivy's own kivy/factory_registers.py registers RecycleView /
        # RecycleViewBehavior under the literal dotted name
        # "kivy.uix.recycleview.__init__", not "kivy.uix.recycleview" - a
        # quirk specific to this one widget (its classes live directly in
        # the package's __init__.py, and Kivy's Factory does an explicit
        # import of that exact string at the moment something requests the
        # widget by name from .kv). collect_submodules("kivy.uix") below
        # bundles "kivy.uix.recycleview" just fine, but PyInstaller's
        # frozen import table has no entry for the separate
        # "...__init__" name Factory actually asks for, so it has to be
        # listed explicitly - this exact gap is what crashed Settings on a
        # real Windows install with "No module named
        # 'kivy.uix.recycleview.__init__'" the moment MDFileManager
        # (which uses RecycleView) was constructed.
        "kivy.uix.recycleview.__init__",
    ]
    + collect_submodules("kivy.graphics")
    + collect_submodules("kivy.core.text")
    + collect_submodules("kivy.core.image")
    + collect_submodules("kivy.core.clipboard")
    # Same reasoning as the kivymd.uix.* collection below: Kivy's own
    # widgets (e.g. kivy.uix.recycleview, used internally by KivyMD's file
    # manager) are loaded on demand via Kivy's Factory, not through a plain
    # `import` anywhere in this project's source, so PyInstaller's static
    # scan misses them too unless the whole kivy.uix package is included up
    # front.
    + collect_submodules("kivy.uix")
))

a = Analysis(
    [os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=libusb_binaries,
    datas=kivy_datas + collect_data_files("escpos") + collect_data_files("kivymd") + [
        (os.path.join(PROJECT_ROOT, "posapp.kv"), "."),
        (os.path.join(PROJECT_ROOT, "images"), "images"),
        (os.path.join(PROJECT_ROOT, "fonts"), "fonts"),
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
