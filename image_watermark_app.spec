# -*- mode: python ; coding: utf-8 -*-
# Build the standalone one-file executable:
#
#     uv run pyinstaller image_watermark_app.spec
#
# The binary lands in dist/ImageWatermarkApp[.exe] and embeds the app icon
# plus the bundled assets (window icon). Paths are resolved relative to this
# spec file, so the build works from any working directory.

import sysconfig
from pathlib import Path

PROJECT_ROOT = Path(SPECPATH)
PACKAGE_DIR = PROJECT_ROOT / "src" / "image_watermark_app"

# uv/python-build-standalone CPython links _tkinter against private Tcl/Tk
# shared libraries that are only reachable through the interpreter's own
# DT_RPATH. PyInstaller resolves binary dependencies with ldd, which does not
# see that RPATH, so the libraries must be bundled explicitly (the bootloader
# exposes the bundle directory to the dynamic linker at runtime).
_LIBDIR = Path(sysconfig.get_config_var("LIBDIR") or "")
TCL_TK_LIBS = [
    (str(lib), ".")
    for pattern in ("libtcl*.so*", "libtk*.so*")
    for lib in sorted(_LIBDIR.glob(pattern))
    if lib.is_file()
]

a = Analysis(
    [str(PACKAGE_DIR / "presentation" / "app.py")],
    pathex=[str(PROJECT_ROOT / "src")],
    binaries=TCL_TK_LIBS,
    datas=[(str(PACKAGE_DIR / "assets"), "image_watermark_app/assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ImageWatermarkApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PACKAGE_DIR / "assets" / "icon.ico"),
)
