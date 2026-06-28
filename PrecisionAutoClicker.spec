# -*- mode: python ; coding: utf-8 -*-

import os

# Build mode is selected by the PAC_ONEFILE environment variable so that both
# the folder bundle and the single-file executable share one source of truth
# for analysis settings (hidden imports, datas, icon, metadata, etc.).
ONEFILE = os.environ.get("PAC_ONEFILE") == "1"

# App icon shared by the window (loaded at runtime from datas) and the EXE.
ICON_PATH = os.path.join(SPECPATH, "assets", "app_icon.ico")

a = Analysis(
    ["auto_clicker.py"],
    pathex=[],
    binaries=[],
    datas=[(os.path.join("assets", "app_icon.ico"), "assets"),
           (os.path.join("assets", "app_icon.png"), "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

if ONEFILE:
    # Single self-contained executable: binaries and datas are embedded in the
    # EXE rather than collected into a folder.
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name="Precision Auto Clicker",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON_PATH,
    )
else:
    # Folder bundle: a lightweight EXE next to its collected dependencies.
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="Precision Auto Clicker",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON_PATH,
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="Precision Auto Clicker",
    )
