"""FastAPI app for Council AI web UI and API."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from council_ai import Council
from council_ai.core.config import (
    ConfigManager,
    get_api_key,
    get_tts_api_key,
    is_placeholder_key,
    sanitize_api_key,
)
from council_ai.core.council import ConsultationMode
from council_ai.core.history import ConsultationHistory
from council_ai.core.persona import PersonaCategory, list_personas
from council_ai.domains import list_domains
from council_ai.providers import list_model_capabilities, list_providers
from council_ai.providers.tts import TTSProviderFactory, generate_speech_with_fallback

# Import reviewer routes
from council_ai.webapp.reviewer import router as reviewer_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Council AI", version="1.0.0")

# Include reviewer API routes
app.include_router(reviewer_router)

# Initialize history (shared instance)
_history = ConsultationHistory()

# Initialize TTS providers (lazy - will be created when needed)
_tts_primary = None
_tts_fallback = None
_tts_initialized = False

# Audio storage directory
AUDIO_DIR = Path.home() / ".cache" / "council-ai" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

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
    query: str = Field(..., min_length=1, max_length=50000)
    context: Optional[str] = Field(default=None, max_length=50000)
    domain: Optional[str] = None
    members: List[str] = Field(default_factory=list)
    mode: str = "synthesis"
    provider: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    enable_tts: bool = False  # Enable TTS for this consultation
    temperature: Optional[float] = 0.7  # Sampling temperature
    max_tokens: Optional[int] = 1000  # Max tokens per response
    session_id: Optional[str] = None
    auto_recall: bool = False


class ConsultResponse(BaseModel):
    synthesis: Optional[str]
    responses: list[dict]
    mode: str


def _build_council(payload: ConsultRequest) -> tuple[Council, ConsultationMode]:
    """
    Build a Council instance from a ConsultRequest.

    Returns:
        Tuple of (council, mode) ready for consultation.

    Raises:
        HTTPException: If API key is missing or configuration is invalid.
    """
    from council_ai.core.council import CouncilConfig

    config = ConfigManager().config
    provider = payload.provider or config.api.provider
    model = payload.model or config.api.model
    base_url = payload.base_url or config.api.base_url

    if payload.api_key and is_placeholder_key(payload.api_key):
        raise HTTPException(
            status_code=400,
            detail="API key appears to be a placeholder. Please provide a valid API key.",
        )

    api_key = sanitize_api_key(payload.api_key) if payload.api_key else get_api_key(provider)

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required for consultation.")

    try:
        mode = ConsultationMode(payload.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    council_config = CouncilConfig(
        temperature=payload.temperature if payload.temperature is not None else 0.7,
        max_tokens_per_response=payload.max_tokens if payload.max_tokens is not None else 1000,
    )

    if payload.members:
        council = Council(
            api_key=api_key,
            provider=provider,
            model=model,
            base_url=base_url,
            config=council_config,
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
                config=council_config,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Enable history for auto-save
    council._history = _history
    return council, mode


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: Optional[str] = None
    provider: Optional[str] = None


class TTSResponse(BaseModel):
    audio_url: str
    filename: str


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the main HTML page."""
    if IS_PRODUCTION:
        # Serve built HTML from static directory
        return FileResponse(str(BUILT_HTML))
    elif DEV_HTML.exists():
        # In development mode with React, we can't just serve the source HTML
        # because it uses .tsx files and needs Vite.
        # We should redirect to the Vite dev server if running, or show a helpful message.
        return HTMLResponse(
            """
            <html>
                <body style="font-family: system-ui, sans-serif; max-width: 600px;
                    margin: 40px auto; padding: 20px; line-height: 1.6;
                    background: #f9fafb; color: #111827;">
                    <div style="background: white; padding: 32px; border-radius: 8px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;">
                        <h1 style="margin-top: 0; color: #DC2626;">Frontend Build Required</h1>
                        <p>The Council AI web interface has been migrated to React and
                            requires a build step.</p>
                        <h3 style="margin-top: 24px;">Option 1: Production (Recommended)</h3>
                        <p>Run the build command to generate static assets:</p>
                        <pre style="background: #1F2937; color: #E5E7EB;
                            padding: 12px; border-radius: 6px; overflow-x: auto;">
                            npm install && npm run build</pre>
                        <p>Then restart this server.</p>

                        <h3 style="margin-top: 24px;">Option 2: Development</h3>
                        <p>Run the Vite development server in a separate terminal:</p>
                        <pre style="background: #1F2937; color: #E5E7EB; padding: 12px;
                            border-radius: 6px; overflow-x: auto;">npm run dev</pre>
                        <p>Then access the app at
                            <a href="http://localhost:5173" style="color: #2563EB;">
                                http://localhost:5173</a>.</p>
                    </div>
                </body>
            </html>
            """,
            status_code=500,
        )
    else:
        # Fallback: minimal error page if no HTML found
        return HTMLResponse(
            "<html><body><h1>Council AI</h1>"
            "<p>index.html not found. Run from the webapp directory.</p>"
            "</body></html>",
            status_code=500,
        )


@app.get("/reviewer", response_class=HTMLResponse)
async def reviewer_ui() -> HTMLResponse:
    """Serve the LLM Response Reviewer UI."""
    reviewer_html = WEBAPP_DIR / "reviewer_ui.html"
    if reviewer_html.exists():
        return FileResponse(str(reviewer_html))
    else:
        return HTMLResponse(
            "<html><body><h1>LLM Response Reviewer</h1>"
            "<p>reviewer_ui.html not found.</p>"
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
            "description": ("AI-powered advisory council system with customizable personas"),
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0c0f14",
            "theme_color": "#0c0f14",
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": (
                        "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
                        "viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏛️</text></svg>"
                    ),
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
        "tts": {
            "enabled": config.tts.enabled,
            "provider": config.tts.provider,
            "fallback_provider": config.tts.fallback_provider,
            "voice": config.tts.voice,
            "has_elevenlabs_key": bool(get_tts_api_key("elevenlabs")),
            "has_openai_key": bool(get_tts_api_key("openai")),
        },
        "providers": list_providers(),
        "models": list_model_capabilities(),
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
                "model": p.model,
                "model_params": p.model_params,
            }
            for p in list_personas()
        ],
        "categories": [c.value for c in PersonaCategory],
        "modes": [m.value for m in ConsultationMode],
    }


@app.post("/api/consult", response_model=ConsultResponse)
async def consult(payload: ConsultRequest) -> ConsultResponse:
    council, mode = _build_council(payload)

    try:
        result = await council.consult_async(
            payload.query,
            context=payload.context,
            mode=mode,
            session_id=payload.session_id,
            auto_recall=payload.auto_recall,
        )
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
    council, mode = _build_council(payload)

    async def generate_stream():
        try:
            async for update in council.consult_stream(
                payload.query,
                context=payload.context,
                mode=mode,
                session_id=payload.session_id,
                auto_recall=payload.auto_recall,
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


@app.get("/api/sessions")
async def list_sessions(limit: int = 50):
    """List recent consultation sessions."""
    sessions = _history.list_sessions(limit=limit)
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details and full history."""
    session = _history.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session.to_dict()


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its consultations."""
    if _history.delete_session(session_id):
        return {"status": "deleted", "id": session_id}
    raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.get("/api/history/search")
async def history_search(q: str, limit: Optional[int] = None) -> dict:
    """Search consultations."""
    results = _history.search(q, limit=limit)
    return {"consultations": results, "query": q, "count": len(results)}


@app.get("/api/history/{consultation_id}")
async def history_get(consultation_id: str) -> Any:
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


# TTS Helper Functions


def _initialize_tts_providers():
    """Initialize TTS providers lazily."""
    global _tts_primary, _tts_fallback, _tts_initialized

    if _tts_initialized:
        return

    config = ConfigManager().config
    if not config.tts.enabled:
        _tts_initialized = True
        return

    try:
        primary_key = config.tts.api_key or get_tts_api_key(config.tts.provider)
        fallback_key = None
        if config.tts.fallback_provider:
            fallback_key = config.tts.fallback_api_key or get_tts_api_key(
                config.tts.fallback_provider
            )

        _tts_primary, _tts_fallback = TTSProviderFactory.create_provider(
            config.tts.provider,
            api_key=primary_key,
            fallback_provider=config.tts.fallback_provider,
            fallback_api_key=fallback_key,
        )
        _tts_initialized = True
        logger.info(
            f"TTS providers initialized: primary={config.tts.provider}, "
            f"fallback={config.tts.fallback_provider}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize TTS providers: {e}")
        _tts_initialized = True


async def _generate_tts_audio(
    text: str, voice: Optional[str] = None, provider: Optional[str] = None
) -> str:
    """
    Generate TTS audio and save to file.

    Returns:
        Filename of generated audio
    """
    _initialize_tts_providers()

    if not _tts_primary and not _tts_fallback:
        raise HTTPException(
            status_code=503, detail="TTS service not available. Check API keys configuration."
        )

    # Generate audio
    try:
        audio_data = await generate_speech_with_fallback(
            text, _tts_primary, _tts_fallback, voice=voice
        )
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

    # Save to file
    filename = f"{uuid4()}.mp3"
    filepath = AUDIO_DIR / filename

    try:
        with open(filepath, "wb") as f:
            f.write(audio_data)
        logger.info(f"TTS audio saved: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to save TTS audio: {e}")
        raise HTTPException(status_code=500, detail="Failed to save audio file")


# TTS API Endpoints


@app.post("/api/tts/generate", response_model=TTSResponse)
async def tts_generate(payload: TTSRequest) -> TTSResponse:
    """Generate TTS audio from text."""
    config = ConfigManager().config

    # Check if TTS is enabled
    if not config.tts.enabled:
        raise HTTPException(
            status_code=403,
            detail="TTS is disabled. Enable it in settings or configuration file.",
        )

    filename = await _generate_tts_audio(
        payload.text, voice=payload.voice, provider=payload.provider
    )
    audio_url = f"/api/tts/audio/{filename}"

    return TTSResponse(audio_url=audio_url, filename=filename)


@app.get("/api/tts/audio/{filename}")
async def tts_audio(filename: str) -> FileResponse:
    """Serve TTS audio file."""
    # Validate filename (security)
    if not filename.endswith(".mp3") or "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    filepath = AUDIO_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        str(filepath),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


@app.get("/api/tts/voices")
async def tts_voices() -> dict:
    """List available TTS voices."""
    _initialize_tts_providers()

    voices: dict[str, list[dict[str, Any]]] = {"primary": [], "fallback": []}

    if _tts_primary:
        try:
            voices["primary"] = await _tts_primary.list_voices()
        except Exception as e:
            logger.error(f"Failed to list primary TTS voices: {e}")

    if _tts_fallback:
        try:
            voices["fallback"] = await _tts_fallback.list_voices()
        except Exception as e:
            logger.error(f"Failed to list fallback TTS voices: {e}")

    config = ConfigManager().config
    return {
        "voices": voices,
        "default_voice": config.tts.voice,
        "provider": config.tts.provider,
        "fallback_provider": config.tts.fallback_provider,
    }
