#!/usr/bin/env python3
"""
Client web UI — no terminal required.

  cd python && python web_app.py
  Open http://127.0.0.1:8765

Desktop app (native window):
  python desktop_app.py
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_paths import (  # noqa: E402
    api_key_configured,
    apply_brand_loader_paths,
    ensure_user_setup,
    init_paths,
    masked_api_key,
    reference_dc,
    sample_source,
    save_api_key,
    web_dir,
)

ensure_user_setup()
apply_brand_loader_paths()

from brand_loader import (  # noqa: E402
    CONFIG_PATH,
    EXAMPLE_PATH,
    INBOX_DIR,
    OUTPUT_DIR,
    brand_summary,
    build_json_system_prompt,
    load_brand_config,
    parse_json_response,
    read_source_file,
    render_fixed_document,
    validate_brand_config,
)
from design import cmd_preview  # noqa: E402
from make import DEFAULT_MODEL, get_client, save_output  # noqa: E402

ALLOWED_UPLOAD = {".txt", ".md", ".csv", ".json", ".log", ".rtf"}

app = FastAPI(title="HVAC Asset Management — Report Studio", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    doc_type: str  # report | proposal
    source_name: Optional[str] = None
    use_sample: bool = False


class ApiKeyRequest(BaseModel):
    api_key: str


def _config_ok() -> bool:
    return CONFIG_PATH.exists()


def _safe_name(name: str) -> str:
    base = Path(name).name
    if not re.match(r"^[a-zA-Z0-9._\- ]+$", base):
        raise HTTPException(400, "Invalid file name")
    return base


def _list_documents() -> list:
    if not OUTPUT_DIR.exists():
        return []
    docs = []
    for p in sorted(OUTPUT_DIR.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        docs.append(
            {
                "name": p.name,
                "size_kb": round(p.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%b %d, %Y · %I:%M %p"),
                "is_preview": p.name == "design-preview.html",
            }
        )
    return docs


def _list_inbox() -> list:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for p in sorted(INBOX_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_file() and p.suffix.lower() in ALLOWED_UPLOAD and p.name != "README.txt":
            files.append(
                {
                    "name": p.name,
                    "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%b %d, %Y · %I:%M %p"),
                }
            )
    return files


@app.get("/api/status")
def status():
    config = None
    company = "Not configured"
    colors = {}
    warnings: List[str] = []

    if _config_ok():
        config = load_brand_config()
        company = config["company"]["name"]
        colors = {
            "teal": config["colors"].get("primary", "#184C4C"),
            "bronze": config["colors"].get("accent", "#9C7B4D"),
        }
        warnings = validate_brand_config(config)
    else:
        warnings.append("Brand not set up")

    from app_paths import user_data, is_frozen

    return {
        "ready": _config_ok() and api_key_configured(),
        "company": company,
        "colors": colors,
        "api_key_set": api_key_configured(),
        "api_key_masked": masked_api_key(),
        "config_set": _config_ok(),
        "brand_summary": brand_summary(config) if config else "",
        "warnings": warnings,
        "documents": _list_documents(),
        "inbox_files": _list_inbox(),
        "has_reference": reference_dc.exists(),
        "has_sample": sample_source.exists(),
        "desktop_mode": is_frozen(),
        "data_folder": str(user_data),
    }


@app.get("/api/settings")
def get_settings():
    from app_paths import user_data

    return {
        "api_key_set": api_key_configured(),
        "api_key_masked": masked_api_key(),
        "data_folder": str(user_data),
    }


@app.post("/api/settings/api-key")
def set_api_key(req: ApiKeyRequest):
    key = req.api_key.strip()
    if not key.startswith("sk-ant-"):
        raise HTTPException(400, "Invalid API key format")
    save_api_key(key)
    return {"ok": True, "message": "API key saved", "api_key_masked": masked_api_key()}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_UPLOAD:
        raise HTTPException(400, f"Please upload a text file ({', '.join(sorted(ALLOWED_UPLOAD))})")

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    dest = INBOX_DIR / _safe_name(file.filename or "upload.txt")
    content = await file.read()
    if not content.strip():
        raise HTTPException(400, "File is empty")
    dest.write_bytes(content)
    return {"ok": True, "name": dest.name, "message": f"Uploaded {dest.name}"}


@app.post("/api/generate")
def generate(req: GenerateRequest):
    if req.doc_type not in ("report", "proposal"):
        raise HTTPException(400, "Document type must be report or proposal")
    if not _config_ok():
        raise HTTPException(503, "Brand not configured.")
    if not api_key_configured():
        raise HTTPException(503, "Add your Anthropic API key in Settings.")

    if req.use_sample:
        if not sample_source.exists():
            raise HTTPException(404, "Sample file not found")
        source_path = sample_source
    elif req.source_name:
        source_path = INBOX_DIR / _safe_name(req.source_name)
        if not source_path.exists():
            raise HTTPException(404, f"File not found: {req.source_name}")
    else:
        inbox = _list_inbox()
        if not inbox:
            raise HTTPException(400, "Upload a property notes file first")
        source_path = INBOX_DIR / inbox[0]["name"]

    config = load_brand_config()
    client = get_client()
    source_text = read_source_file(source_path)

    system = build_json_system_prompt(config, req.doc_type)
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=8192,
        system=system,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Fill the {req.doc_type} template from this source material. "
                    "Use the fixed section keys. Do not ask questions.\n\n"
                    f"--- SOURCE MATERIAL ---\n{source_text}"
                ),
            }
        ],
    )
    payload = parse_json_response(response.content[0].text)
    html = render_fixed_document(config, req.doc_type, payload)
    out_path = save_output(html, req.doc_type, config, source_path.name)

    return {
        "ok": True,
        "filename": out_path.name,
        "message": f"{'Standard Review' if req.doc_type == 'report' else 'Proposal'} generated successfully",
        "view_url": f"/view/{out_path.name}",
    }


@app.post("/api/preview/design")
def preview_design():
    if not _config_ok():
        raise HTTPException(503, "Brand not configured")
    config = load_brand_config()
    cmd_preview(config)
    return {"ok": True, "filename": "design-preview.html", "view_url": "/view/design-preview.html"}


@app.get("/api/documents")
def documents():
    return {"documents": _list_documents()}


@app.get("/view/{filename}")
def view_document(filename: str):
    name = _safe_name(filename)
    path = OUTPUT_DIR / name
    if not path.exists():
        raise HTTPException(404, "Document not found")
    return FileResponse(path, media_type="text/html")


@app.get("/download/{filename}")
def download_document(filename: str):
    name = _safe_name(filename)
    path = OUTPUT_DIR / name
    if not path.exists():
        raise HTTPException(404, "Document not found")
    return FileResponse(path, media_type="text/html", filename=name)


@app.get("/reference")
def reference_design():
    if not reference_dc.exists():
        raise HTTPException(404, "Reference design not found")
    return FileResponse(reference_dc, media_type="text/html")


@app.get("/")
def index():
    index_path = web_dir / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>Web UI not found</h1>", status_code=500)
    return FileResponse(index_path)


if web_dir.joinpath("static").exists():
    app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")


def main() -> None:
    import uvicorn

    from desktop_launcher import UVICORN_LOG_CONFIG, fix_stdio

    fix_stdio()
    init_paths()
    ensure_user_setup()
    apply_brand_loader_paths()

    host = os.getenv("HAM_UI_HOST", "127.0.0.1")
    port = int(os.getenv("HAM_UI_PORT", "8765"))
    print(f"\n  HVAC Asset Management — Report Studio")
    print(f"  Open in your browser: http://{host}:{port}\n")
    if not _config_ok():
        print(f"  ⚠ Brand config: {CONFIG_PATH}")
    if not api_key_configured():
        print("  ⚠ Add API key in the app Settings screen\n")
    uvicorn.run(app, host=host, port=port, log_level="info", log_config=UVICORN_LOG_CONFIG)


if __name__ == "__main__":
    main()
