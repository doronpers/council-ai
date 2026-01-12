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
IS_PRODUCTION = BUILT_HTML.exists()

# Mount static files if in production
if IS_PRODUCTION:
    # Mount assets directory
    assets_dir = STATIC_DIR / "assets"
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
    else:
        # Development mode: serve inline HTML (fallback)
        return HTMLResponse(_INDEX_HTML)


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


_INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Council AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes" />
    <meta name="description" content="AI-powered advisory council system with customizable personas" />
    <meta name="theme-color" content="#0c0f14" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
    <meta name="apple-mobile-web-app-title" content="Council AI" />
    <link rel="manifest" href="/manifest.json" />
    <style>
      :root { 
        color-scheme: light dark; 
        --primary: #3b82f6;
        --primary-hover: #2563eb;
        --bg-primary: #0c0f14;
        --bg-secondary: #141824;
        --bg-tertiary: #0e1118;
        --border: #1f2430;
        --text-primary: #f6f7fb;
        --text-secondary: #d4d7dd;
        --text-muted: #9aa3b2;
      }
      
      * { box-sizing: border-box; }
      
      body { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; 
        margin: 0; 
        background: var(--bg-primary); 
        color: var(--text-primary);
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }
      
      header { 
        padding: 20px 16px; 
        border-bottom: 1px solid var(--border); 
        background: #0f1219;
        position: sticky;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(10px);
      }
      
      header h1 { 
        margin: 0 0 4px; 
        font-size: 24px; 
        font-weight: 700;
      }
      
      header p { 
        margin: 0; 
        color: var(--text-muted); 
        font-size: 14px;
      }
      
      main { 
        display: grid; 
        gap: 20px; 
        padding: 20px 16px; 
        max-width: 1100px; 
        margin: 0 auto;
        padding-bottom: 40px;
      }
      
      .panel { 
        background: var(--bg-secondary); 
        border: 1px solid var(--border); 
        border-radius: 12px; 
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .panel h2 {
        margin: 0 0 16px;
        font-size: 20px;
        font-weight: 600;
      }
      
      label { 
        display: block; 
        margin-bottom: 8px; 
        color: var(--text-secondary); 
        font-weight: 600;
        font-size: 14px;
      }
      
      input, select, textarea { 
        width: 100%; 
        margin-bottom: 16px; 
        padding: 12px; 
        border-radius: 8px; 
        border: 1px solid #2a3140; 
        background: var(--bg-tertiary); 
        color: var(--text-primary);
        font-size: 16px; /* Prevents zoom on iOS */
        font-family: inherit;
        transition: border-color 0.2s, box-shadow 0.2s;
      }
      
      input:focus, select:focus, textarea:focus {
        outline: none;
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
      
      textarea { 
        min-height: 100px; 
        resize: vertical; 
        line-height: 1.5;
      }
      
      button { 
        background: var(--primary); 
        color: white; 
        border: none; 
        padding: 14px 24px; 
        border-radius: 8px; 
        font-weight: 600; 
        cursor: pointer;
        font-size: 16px;
        width: 100%;
        transition: background 0.2s, transform 0.1s;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
      }
      
      button:active {
        transform: scale(0.98);
      }
      
      button:hover:not(:disabled) { 
        background: var(--primary-hover);
      }
      
      button:disabled { 
        opacity: 0.6; 
        cursor: not-allowed;
        transform: none;
      }
      
      .grid { 
        display: grid; 
        gap: 16px; 
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
      }
      
      .responses { 
        display: grid; 
        gap: 12px; 
      }
      
      .response { 
        background: var(--bg-tertiary); 
        border: 1px solid #23293a; 
        padding: 16px; 
        border-radius: 8px;
        word-wrap: break-word;
        overflow-wrap: break-word;
      }
      
      .response p {
        margin: 8px 0 0;
        white-space: pre-wrap;
      }
      
      .muted { 
        color: var(--text-muted); 
        font-size: 14px; 
      }
      
      .badge { 
        background: #1f2937; 
        padding: 4px 10px; 
        border-radius: 999px; 
        font-size: 12px;
        display: inline-block;
        font-weight: 600;
        margin-bottom: 8px;
      }
      
      .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.8s linear infinite;
        margin-right: 8px;
        vertical-align: middle;
      }
      
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
      
      .error {
        color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin-top: 12px;
      }
      
      .synthesis {
        background: var(--bg-tertiary);
        padding: 16px;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
        margin-bottom: 16px;
      }
      
      .synthesis h3 {
        margin: 0 0 8px;
        font-size: 18px;
        color: var(--text-secondary);
      }
      
      .synthesis p {
        margin: 0;
        white-space: pre-wrap;
      }
      
      /* Mobile optimizations */
      @media (max-width: 768px) {
        header {
          padding: 16px;
        }
        
        header h1 {
          font-size: 22px;
        }
        
        header p {
          font-size: 13px;
        }
        
        main {
          padding: 16px 12px;
          gap: 16px;
        }
        
        .panel {
          padding: 16px;
        }
        
        .panel h2 {
          font-size: 18px;
          margin-bottom: 12px;
        }
        
        .grid {
          grid-template-columns: 1fr;
          gap: 12px;
        }
        
        input, select, textarea {
          margin-bottom: 12px;
          padding: 14px;
        }
        
        button {
          padding: 16px 24px;
          font-size: 16px;
        }
        
        .response {
          padding: 14px;
        }
        
        textarea {
          min-height: 80px;
        }
      }
      
      /* Very small screens */
      @media (max-width: 360px) {
        header h1 {
          font-size: 20px;
        }
        
        main {
          padding: 12px 8px;
        }
        
        .panel {
          padding: 12px;
        }
      }
      
      /* Landscape mobile */
      @media (max-width: 768px) and (orientation: landscape) {
        header {
          padding: 12px 16px;
        }
        
        header h1 {
          font-size: 20px;
          margin-bottom: 2px;
        }
        
        header p {
          font-size: 12px;
        }
        
        main {
          padding: 12px 16px;
          gap: 12px;
        }
      }
      
      /* Touch device optimizations */
      @media (hover: none) and (pointer: coarse) {
        button {
          min-height: 44px; /* iOS recommended touch target */
        }
        
        input, select, textarea {
          min-height: 44px;
        }
        
        .response {
          padding: 16px;
        }
      }
      
      /* Dark mode support (system preference) */
      @media (prefers-color-scheme: light) {
        :root {
          --bg-primary: #ffffff;
          --bg-secondary: #f8f9fa;
          --bg-tertiary: #ffffff;
          --border: #e0e0e0;
          --text-primary: #1a1a1a;
          --text-secondary: #4a4a4a;
          --text-muted: #6a6a6a;
        }
        
        body {
          background: var(--bg-primary);
          color: var(--text-primary);
        }
        
        input, select, textarea {
          border-color: #d0d0d0;
          background: var(--bg-tertiary);
        }
      }
    </style>
  </head>
  <body>
    <header>
      <h1>🏛️ Council AI</h1>
      <p class="muted">A minimal web console for running multi-persona consultations.</p>
    </header>
    <main>
      <section class="panel">
        <h2>Consultation Setup</h2>
        <div class="grid">
          <div>
            <label for="provider">Provider</label>
            <select id="provider"></select>
          </div>
          <div>
            <label for="model">Model</label>
            <input id="model" placeholder="gpt-4-turbo-preview" />
          </div>
          <div>
            <label for="base_url">Base URL</label>
            <input id="base_url" placeholder="https://api.openai.com/v1" />
          </div>
          <div>
            <label for="mode">Mode</label>
            <select id="mode"></select>
          </div>
          <div>
            <label for="domain">Domain</label>
            <select id="domain"></select>
          </div>
          <div>
            <label for="members">Members (comma separated IDs)</label>
            <input id="members" placeholder="rams, kahneman" />
          </div>
          <div>
            <label for="api_key">API Key (optional)</label>
            <input id="api_key" placeholder="Leave empty to use env/config" type="password" />
          </div>
        </div>
        <label for="query">Query</label>
        <textarea id="query" placeholder="Ask the council a question..."></textarea>
        <label for="context">Context (optional)</label>
        <textarea id="context" placeholder="Add background or constraints..."></textarea>
        <button id="submit">Consult the Council</button>
        <p class="muted">Tip: leave Members empty to use the domain defaults.</p>
      </section>
      <section class="panel">
        <h2>Result</h2>
        <div id="status" class="muted">No consultation yet.</div>
        <div id="synthesis"></div>
        <div id="responses" class="responses"></div>
      </section>
    </main>
    <script>
      const providerEl = document.getElementById("provider");
      const modelEl = document.getElementById("model");
      const baseUrlEl = document.getElementById("base_url");
      const modeEl = document.getElementById("mode");
      const domainEl = document.getElementById("domain");
      const membersEl = document.getElementById("members");
      const apiKeyEl = document.getElementById("api_key");
      const queryEl = document.getElementById("query");
      const contextEl = document.getElementById("context");
      const submitEl = document.getElementById("submit");
      const statusEl = document.getElementById("status");
      const synthesisEl = document.getElementById("synthesis");
      const responsesEl = document.getElementById("responses");

      function escapeHtml(text) {
        if (text == null) return "";
        const div = document.createElement("div");
        div.textContent = String(text);
        return div.innerHTML;
      }

      async function loadInfo() {
        const res = await fetch("/api/info");
        const data = await res.json();
        providerEl.innerHTML = data.providers.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join("");
        modeEl.innerHTML = data.modes.map(m => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("");
        domainEl.innerHTML = data.domains.map(d => `<option value="${escapeHtml(d.id)}">${escapeHtml(d.name)}</option>`).join("");
        providerEl.value = data.defaults.provider || "openai";
        modelEl.value = data.defaults.model || "";
        baseUrlEl.value = data.defaults.base_url || "";
        modeEl.value = data.defaults.mode || "synthesis";
        domainEl.value = data.defaults.domain || "general";
      }

      function renderResult(result) {
        statusEl.textContent = `Mode: ${result.mode}`;
        statusEl.className = "muted";
        
        if (result.synthesis) {
          synthesisEl.innerHTML = `<div class="synthesis"><h3>Synthesis</h3><p>${escapeHtml(result.synthesis)}</p></div>`;
        } else {
          synthesisEl.innerHTML = "";
        }
        
        responsesEl.innerHTML = "";
        
        if (result.responses && result.responses.length > 0) {
          result.responses.forEach(r => {
            const card = document.createElement("div");
            card.className = "response";
            const personaName = escapeHtml(r.persona_name || r.persona_id || "Unknown");
            const content = escapeHtml(r.content || "");
            const error = r.error ? escapeHtml(r.error) : "";
            card.innerHTML = `
              <div class="badge">${personaName}</div>
              ${content ? `<p>${escapeHtml(content)}</p>` : ""}
              ${error ? `<div class="error">Error: ${escapeHtml(error)}</div>` : ""}
            `;
            responsesEl.appendChild(card);
          });
        } else {
          responsesEl.innerHTML = '<p class="muted">No responses received.</p>';
        }
        
        // Scroll to results on mobile
        if (window.innerWidth <= 768) {
          setTimeout(() => {
            document.querySelector('#status').scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, 100);
        }
      }

      async function submitConsultation() {
        if (!queryEl.value.trim()) {
          statusEl.textContent = "Please enter a query.";
          statusEl.className = "error";
          return;
        }
        
        submitEl.disabled = true;
        statusEl.innerHTML = '<span class="loading"></span>Consulting the council...';
        statusEl.className = "muted";
        synthesisEl.innerHTML = "";
        responsesEl.innerHTML = "";
        
        const payload = {
          query: queryEl.value.trim(),
          context: contextEl.value.trim() || null,
          domain: domainEl.value,
          members: membersEl.value.split(",").map(x => x.trim()).filter(Boolean),
          mode: modeEl.value,
          provider: providerEl.value,
          model: modelEl.value.trim() || null,
          base_url: baseUrlEl.value.trim() || null,
          api_key: apiKeyEl.value.trim() || null
        };
        
        try {
          const res = await fetch("/api/consult", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          
          if (!res.ok) {
            const err = await res.json();
            statusEl.textContent = err.detail || "Request failed.";
            statusEl.className = "error";
            synthesisEl.innerHTML = `<div class="error">${escapeHtml(err.detail || "Request failed.")}</div>`;
          } else {
            const data = await res.json();
            renderResult(data);
          }
        } catch (err) {
          statusEl.textContent = err.message || "Network error. Please check your connection.";
          statusEl.className = "error";
          synthesisEl.innerHTML = `<div class="error">${escapeHtml(err.message || "Network error.")}</div>`;
        } finally {
          submitEl.disabled = false;
        }
      }
      
      submitEl.addEventListener("click", submitConsultation);
      
      // Allow Enter key to submit (but not in textareas)
      queryEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
          e.preventDefault();
          submitConsultation();
        }
      });

      loadInfo();
    </script>
  </body>
</html>
"""
