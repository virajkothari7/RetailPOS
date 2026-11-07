# Override for PyInstaller's own built-in hook-kivy.py.
#
# Why this exists: PyInstaller's bundled hook for Kivy calls Kivy's
# get_deps_minimal(), which does `importlib.import_module('kivy.core.window')`
# to work out which window-provider submodules need bundling. Importing
# kivy.core.window makes Kivy actually try to create a window and probe the
# graphics driver for an OpenGL context. On a real machine with a real GPU
# that's harmless, but on a headless CI runner with only a software/GDI
# fallback (stuck at OpenGL 1.1, below Kivy's required 2.0), Kivy's window
# creation doesn't fail cleanly - it hangs indefinitely instead, which is
# exactly what stalled the Windows GitHub Actions build for 24+ minutes
# doing nothing.
#
# Fix: this file, placed earlier in the spec's hookspath, replaces
# PyInstaller's built-in hook-kivy.py entirely (PyInstaller uses the first
# hook it finds for a given module and stops looking). RetailPOS.spec
# already computes the Kivy datas/hiddenimports it needs by hand (via
# collect_submodules on the specific kivy.core.* and kivy.graphics
# submodules, with no module actually imported/executed to do so) and
# passes them straight into Analysis(), so nothing is lost by skipping the
# built-in hook - this file intentionally contributes nothing.

datas = []
hiddenimports = []
excludedimports = []
