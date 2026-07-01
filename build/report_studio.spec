# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — build Mac .app and Windows .exe
# Run from repo root: pyinstaller build/report_studio.spec

import sys
from pathlib import Path

# SPECPATH = .../Claude-AI-Design/build  →  repo root is one level up
ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / 'python' / 'desktop_app.py')],
    pathex=[str(ROOT / 'python')],
    binaries=[],
    datas=[
        (str(ROOT / 'web'), 'web'),
        (str(ROOT / 'brand' / 'styles'), 'brand/styles'),
        (str(ROOT / 'brand' / 'templates'), 'brand/templates'),
        (str(ROOT / 'brand' / 'design'), 'brand/design'),
        (str(ROOT / 'brand' / 'samples'), 'brand/samples'),
        (str(ROOT / 'brand' / 'brand.config.example.yaml'), 'brand'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'anthropic',
        'yaml',
        'dotenv',
        'pydantic',
        'starlette.routing',
        'anyio',
        'sniffio',
        'httpx',
        'httpcore',
        'h11',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HAM Report Studio',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='HAM Report Studio',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='HAM Report Studio.app',
        icon=None,
        bundle_identifier='com.hvacasset.reportstudio',
        info_plist={
            'CFBundleName': 'HAM Report Studio',
            'CFBundleDisplayName': 'HAM Report Studio',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
