#!/usr/bin/env python3
"""
Client web UI — no terminal required.

  cd python && python web_app.py
  Open http://127.0.0.1:8765
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv(Path(__file__).resolve().parent / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand_loader import (  # noqa: E402
    BRAND_DIR,
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

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
REFERENCE_DC = BRAND_DIR / "design" / "Standard Review - 4600 Northgate.dc.html"
SAMPLE_SOURCE = BRAND_DIR / "samples" / "sra-northgate-h1-2026-source.txt"
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
    source_name: str | None = None
    use_sample: bool = False


def _api_key_ok() -> bool:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    return bool(key and not key.startswith("sk-ant-api03-xxx"))


def _config_ok() -> bool:
    return CONFIG_PATH.exists()


def _safe_name(name: str) -> str:
    base = Path(name).name
    if not re.match(r"^[a-zA-Z0-9._\- ]+$", base):
        raise HTTPException(400, "Invalid file name")
    return base


def _list_documents() -> list[dict]:
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


def _list_inbox() -> list[dict]:
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
    warnings: list[str] = []

    if _config_ok():
        config = load_brand_config()
        company = config["company"]["name"]
        colors = {
            "teal": config["colors"].get("primary", "#184C4C"),
            "bronze": config["colors"].get("accent", "#9C7B4D"),
        }
        warnings = validate_brand_config(config)
    else:
        warnings.append("Brand not set up — copy brand.config.example.yaml to brand.config.yaml")

    return {
        "ready": _config_ok() and _api_key_ok(),
        "company": company,
        "colors": colors,
        "api_key_set": _api_key_ok(),
        "config_set": _config_ok(),
        "brand_summary": brand_summary(config) if config else "",
        "warnings": warnings,
        "documents": _list_documents(),
        "inbox_files": _list_inbox(),
        "has_reference": REFERENCE_DC.exists(),
        "has_sample": SAMPLE_SOURCE.exists(),
    }


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
        raise HTTPException(
            503,
            "Brand not configured. Ask your administrator to run setup once.",
        )
    if not _api_key_ok():
        raise HTTPException(
            503,
            "API key not set. Add ANTHROPIC_API_KEY to python/.env",
        )

    if req.use_sample:
        if not SAMPLE_SOURCE.exists():
            raise HTTPException(404, "Sample file not found")
        source_path = SAMPLE_SOURCE
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
    if not REFERENCE_DC.exists():
        raise HTTPException(404, "Reference design not found")
    return FileResponse(REFERENCE_DC, media_type="text/html")


@app.get("/")
def index():
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>Web UI not found</h1>", status_code=500)
    return FileResponse(index_path)


if WEB_DIR.joinpath("static").exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


def main() -> None:
    import uvicorn

    host = os.getenv("HAM_UI_HOST", "127.0.0.1")
    port = int(os.getenv("HAM_UI_PORT", "8765"))
    print(f"\n  HVAC Asset Management — Report Studio")
    print(f"  Open in your browser: http://{host}:{port}\n")
    if not _config_ok():
        print(f"  ⚠ Copy {EXAMPLE_PATH} → {CONFIG_PATH}")
    if not _api_key_ok():
        print("  ⚠ Add ANTHROPIC_API_KEY to python/.env\n")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
