# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — AutoAudio single-file build."""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

block_cipher = None
root = Path(SPECPATH)

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=ctk_binaries,
    datas=[
        (str(root / "logoW.png"), "."),
        *ctk_datas,
    ],
    hiddenimports=[
        "comtypes",
        "comtypes.client",
        "comtypes.gen",
        "pycaw",
        "pycaw.pycaw",
        "pycaw.api",
        "pycaw.utils",
        "PIL",
        "PIL.Image",
        "numpy",
        "winsound",
        *ctk_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AutoAudio",
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
    uac_admin=True,
)
