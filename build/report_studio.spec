# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — build Mac .app and Windows .exe
# Run from repo root: pyinstaller build/report_studio.spec

import sys
from pathlib import Path

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
        'pydantic_core',
        'starlette.routing',
        'starlette.responses',
        'starlette.middleware',
        'starlette.middleware.cors',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        'sniffio',
        'httpx',
        'httpcore',
        'h11',
        'multipart',
        'python_multipart',
        'tkinter',
        'tkinter.ttk',
        'asyncio',
        'logging.config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / 'build' / 'runtime_hook.py')],
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
