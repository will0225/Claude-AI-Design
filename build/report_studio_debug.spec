# Debug build — console window shows errors (Windows troubleshooting)
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
        'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
        'anthropic', 'yaml', 'dotenv', 'pydantic', 'pydantic_core',
        'starlette.routing', 'anyio', 'sniffio', 'httpx', 'httpcore', 'h11',
        'multipart', 'python_multipart', 'tkinter', 'asyncio',
    ],
    runtime_hooks=[str(ROOT / 'build' / 'runtime_hook.py')],
    excludes=[], noarchive=False, optimize=0,
)

pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='HAM Report Studio Debug',
          console=True, debug=True)
coll = COLLECT(exe, a.binaries, a.datas, name='HAM Report Studio Debug')
