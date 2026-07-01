# HAM Report Studio — Desktop App (Mac & Windows)

Your client **double-clicks the app** — no Terminal, no Python, no code.

---

## For the client

### Mac
1. Open **`HAM Report Studio.app`**
2. In **Settings**, paste the Anthropic API key once → **Save API key**
3. Upload property notes → **Generate Standard Review Report**
4. **Print / Save PDF**

### Windows
1. Open **`HAM Report Studio.exe`**
2. Same steps as Mac

Documents are saved automatically in:
- **Mac:** `~/Library/Application Support/HAM Report Studio/brand/output/`
- **Windows:** `%APPDATA%\HAM Report Studio\brand\output\`

---

## For you — build the installers

Desktop apps must be built **on each platform** (Mac app on Mac, Windows exe on Windows).

### Mac (.app)

On a Mac with Python 3.9+:

```bash
cd Claude-AI-Design
chmod +x build/build-mac.sh
./build/build-mac.sh
```

Output: **`dist/HAM Report Studio.app`**

The build **does not require pywebview**. If Xcode Command Line Tools are missing, the app opens Report Studio in the default browser and shows a small control window — this is fine for clients.

#### If build fails with `pyobjc-core` / `Cannot locate a working compiler`

This happens when pip tries to compile optional native-window dependencies. The updated build script skips them automatically.

To fix completely (optional native embedded window):

```bash
xcode-select --install          # install Apple compiler (one time)
rm -rf build/venv-build dist    # clean previous failed build
./build/build-mac.sh            # rebuild
```

You do **not** need pywebview for the client — browser mode works fully.

### Windows (.exe)

On a Windows PC with Python 3.9+:

```cmd
cd Claude-AI-Design
build\build-windows.bat
```

Output: **`dist\HAM Report Studio\`** folder containing **`HAM Report Studio.exe`**

Zip the whole folder and send to the client.

---

## Development (before building)

Test the native window locally:

```bash
cd python
pip install -r requirements.txt pywebview
python desktop_app.py
```

Or browser mode:

```bash
./start-app.sh
```

---

## What's inside the app

| Piece | Purpose |
|-------|---------|
| `desktop_app.py` | Starts server + native window |
| `web_app.py` | Report generation API |
| `web/` | Client UI (upload, generate, preview) |
| `brand/` | Templates, CSS, Northgate format guide |
| User data folder | API key, inbox, generated reports |

---

## API key

The client enters the key in the app **Settings** screen. It is stored locally in the user data folder — never in the app bundle or Git.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Mac says "unidentified developer" | Right-click app → Open → Open |
| Windows SmartScreen | Click "More info" → Run anyway (or code-sign the exe) |
| Blank window | Wait 5 sec; server may still be starting |
| Generate fails | Check API key in Settings |

---

## Alternative (no build)

If you don't build installers yet, the client can still use:

```bash
./start-app.sh
```

Then open http://127.0.0.1:8765 — requires Python installed once.
