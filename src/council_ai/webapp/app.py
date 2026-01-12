"""FastAPI app for Council AI web UI and API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from council_ai import Council
from council_ai.core.config import ConfigManager, get_api_key
from council_ai.core.council import ConsultationMode
from council_ai.core.history import ConsultationHistory
from council_ai.core.persona import PersonaCategory, list_personas
from council_ai.domains import list_domains
from council_ai.providers import list_providers

app = FastAPI(title="Council AI", version="1.0.0")

# Initialize history (shared instance)
_history = ConsultationHistory()

# Determine if we're in production (built assets exist) or development
WEBAPP_DIR = Path(__file__).parent
STATIC_DIR = WEBAPP_DIR / "static"
BUILT_HTML = STATIC_DIR / "index.html"
DEV_HTML = WEBAPP_DIR / "index.html"
IS_PRODUCTION = BUILT_HTML.exists()

# Mount static files - production from static/, development from assets/
if IS_PRODUCTION:
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
else:
    # Development mode: serve assets directly from source
    assets_dir = WEBAPP_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


class ConsultRequest(BaseModel):
    query: str = Field(..., min_length=1)
    context: Optional[str] = None
    domain: Optional[str] = None
    members: List[str] = Field(default_factory=list)
    mode: str = "synthesis"
    provider: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class ConsultResponse(BaseModel):
    synthesis: Optional[str]
    responses: list[dict]
    mode: str


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the main HTML page."""
    if IS_PRODUCTION:
        # Serve built HTML from static directory
        return FileResponse(str(BUILT_HTML))
    elif DEV_HTML.exists():
        # Development mode: serve HTML from source file
        return FileResponse(str(DEV_HTML))
    else:
        # Fallback: minimal error page if no HTML found
        return HTMLResponse(
            "<html><body><h1>Council AI</h1>"
            "<p>index.html not found. Run from the webapp directory.</p>"
            "</body></html>",
            status_code=500,
        )


@app.get("/manifest.json")
async def manifest() -> JSONResponse:
    """PWA manifest for mobile app installation."""
    return JSONResponse(
        {
            "name": "Council AI",
            "short_name": "Council AI",
            "description": "AI-powered advisory council system with customizable personas",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0c0f14",
            "theme_color": "#0c0f14",
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏛️</text></svg>",
                    "sizes": "any",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                }
            ],
        }
    )


@app.get("/api/info")
async def info() -> dict:
    config = ConfigManager().config
    return {
        "defaults": {
            "provider": config.api.provider,
            "model": config.api.model,
            "base_url": config.api.base_url,
            "domain": config.default_domain,
            "mode": config.default_mode,
        },
        "providers": list_providers(),
        "domains": [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "category": d.category.value,
                "default_personas": d.default_personas,
                "recommended_mode": d.recommended_mode,
            }
            for d in list_domains()
        ],
        "personas": [
            {
                "id": p.id,
                "name": p.name,
                "title": p.title,
                "emoji": p.emoji,
                "category": p.category.value,
                "focus_areas": p.focus_areas,
            }
            for p in list_personas()
        ],
        "categories": [c.value for c in PersonaCategory],
        "modes": [m.value for m in ConsultationMode],
    }


@app.post("/api/consult", response_model=ConsultResponse)
async def consult(payload: ConsultRequest) -> ConsultResponse:
    config = ConfigManager().config
    provider = payload.provider or config.api.provider
    model = payload.model or config.api.model
    base_url = payload.base_url or config.api.base_url
    api_key = payload.api_key or get_api_key(provider)
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required for consultation.")

    try:
        mode = ConsultationMode(payload.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if payload.members:
        council = Council(
            api_key=api_key,
            provider=provider,
            model=model,
            base_url=base_url,
        )
        for member_id in payload.members:
            try:
                council.add_member(member_id)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        domain = payload.domain or config.default_domain
        try:
            council = Council.for_domain(
                domain,
                api_key=api_key,
                provider=provider,
                model=model,
                base_url=base_url,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        # Enable history for auto-save
        council._history = _history
        result = await council.consult_async(payload.query, context=payload.context, mode=mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ConsultResponse(
        synthesis=result.synthesis,
        responses=[r.to_dict() for r in result.responses],
        mode=result.mode,
    )


@app.post("/api/consult/stream")
async def consult_stream(payload: ConsultRequest) -> StreamingResponse:
    """Stream consultation results as Server-Sent Events (SSE)."""
    config = ConfigManager().config
    provider = payload.provider or config.api.provider
    model = payload.model or config.api.model
    base_url = payload.base_url or config.api.base_url
    api_key = payload.api_key or get_api_key(provider)
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required for consultation.")

    try:
        mode = ConsultationMode(payload.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if payload.members:
        council = Council(
            api_key=api_key,
            provider=provider,
            model=model,
            base_url=base_url,
        )
        for member_id in payload.members:
            try:
                council.add_member(member_id)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        domain = payload.domain or config.default_domain
        try:
            council = Council.for_domain(
                domain,
                api_key=api_key,
                provider=provider,
                model=model,
                base_url=base_url,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Enable history for auto-save
    council._history = _history

    async def generate_stream():
        try:
            async for update in council.consult_stream(
                payload.query, context=payload.context, mode=mode
            ):
                # Convert update to SSE format
                if "result" in update:
                    # For the final result, convert MemberResponse objects to dicts
                    result = update["result"]
                    update["result"] = {
                        "query": result.query,
                        "context": result.context,
                        "mode": result.mode,
                        "timestamp": result.timestamp.isoformat(),
                        "responses": [r.to_dict() for r in result.responses],
                        "synthesis": result.synthesis,
                    }
                elif "response" in update:
                    # Convert MemberResponse to dict
                    update["response"] = update["response"].to_dict()

                # Format as SSE
                yield f"data: {json.dumps(update)}\n\n"
        except Exception as exc:
            error_update = {
                "type": "error",
                "error": str(exc),
            }
            yield f"data: {json.dumps(error_update)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.get("/api/history")
async def history_list(limit: Optional[int] = None, offset: int = 0) -> dict:
    """List saved consultations."""
    consultations = _history.list(limit=limit, offset=offset)
    return {"consultations": consultations, "total": len(consultations)}


@app.get("/api/history/{consultation_id}")
async def history_get(consultation_id: str) -> dict:
    """Get a specific consultation."""
    data = _history.load(consultation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return data


@app.post("/api/history/{consultation_id}/save")
async def history_save(
    consultation_id: str, tags: Optional[List[str]] = None, notes: Optional[str] = None
) -> dict:
    """Save/update a consultation (used after consultation completes)."""
    # This would typically be called after a consultation completes
    # For now, consultations are auto-saved, but this allows updating tags/notes
    if _history.update_metadata(consultation_id, tags=tags, notes=notes):
        return {"status": "saved", "id": consultation_id}
    raise HTTPException(status_code=404, detail="Consultation not found")


@app.delete("/api/history/{consultation_id}")
async def history_delete(consultation_id: str) -> dict:
    """Delete a consultation."""
    if _history.delete(consultation_id):
        return {"status": "deleted", "id": consultation_id}
    raise HTTPException(status_code=404, detail="Consultation not found")


@app.get("/api/history/search")
async def history_search(q: str, limit: Optional[int] = None) -> dict:
    """Search consultations."""
    results = _history.search(q, limit=limit)
    return {"consultations": results, "query": q, "count": len(results)}
