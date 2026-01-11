"""FastAPI app for Council AI web UI and API."""

from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from council_ai import Council
from council_ai.core.config import ConfigManager, get_api_key
from council_ai.core.council import ConsultationMode
from council_ai.core.persona import PersonaCategory, list_personas
from council_ai.domains import list_domains
from council_ai.providers import list_providers

app = FastAPI(title="Council AI", version="1.0.0")


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
    return HTMLResponse(_INDEX_HTML)


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
        result = await council.consult_async(payload.query, context=payload.context, mode=mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ConsultResponse(
        synthesis=result.synthesis,
        responses=[r.to_dict() for r in result.responses],
        mode=result.mode,
    )


_INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Council AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      :root { color-scheme: light dark; }
      body { font-family: system-ui, sans-serif; margin: 0; background: #0c0f14; color: #f6f7fb; }
      header { padding: 32px; border-bottom: 1px solid #1f2430; background: #0f1219; }
      header h1 { margin: 0 0 8px; font-size: 28px; }
      header p { margin: 0; color: #b2b7c2; }
      main { display: grid; gap: 24px; padding: 32px; max-width: 1100px; margin: 0 auto; }
      .panel { background: #141824; border: 1px solid #1f2430; border-radius: 12px; padding: 20px; }
      label { display: block; margin-bottom: 6px; color: #d4d7dd; font-weight: 600; }
      input, select, textarea { width: 100%; margin-bottom: 12px; padding: 10px; border-radius: 8px; border: 1px solid #2a3140; background: #0e1118; color: #f6f7fb; }
      textarea { min-height: 120px; resize: vertical; }
      button { background: #3b82f6; color: white; border: none; padding: 12px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; }
      button:disabled { opacity: 0.6; cursor: not-allowed; }
      .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
      .responses { display: grid; gap: 12px; }
      .response { background: #0e121a; border: 1px solid #23293a; padding: 12px; border-radius: 8px; }
      .muted { color: #9aa3b2; font-size: 14px; }
      .badge { background: #1f2937; padding: 2px 8px; border-radius: 999px; font-size: 12px; }
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
            <input id="model" placeholder="gpt-5.2" />
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

      async function loadInfo() {
        const res = await fetch("/api/info");
        const data = await res.json();
        providerEl.innerHTML = data.providers.map(p => `<option value="${p}">${p}</option>`).join("");
        modeEl.innerHTML = data.modes.map(m => `<option value="${m}">${m}</option>`).join("");
        domainEl.innerHTML = data.domains.map(d => `<option value="${d.id}">${d.name}</option>`).join("");
        providerEl.value = data.defaults.provider || "openai";
        modelEl.value = data.defaults.model || "";
        baseUrlEl.value = data.defaults.base_url || "";
        modeEl.value = data.defaults.mode || "synthesis";
        domainEl.value = data.defaults.domain || "general";
      }

      function renderResult(result) {
        statusEl.textContent = `Mode: ${result.mode}`;
        synthesisEl.innerHTML = result.synthesis ? `<h3>Synthesis</h3><p>${result.synthesis}</p>` : "";
        responsesEl.innerHTML = "";
        result.responses.forEach(r => {
          const card = document.createElement("div");
          card.className = "response";
          card.innerHTML = `
            <div class="badge">${r.persona_name || r.persona_id}</div>
            <p>${r.content}</p>
            ${r.error ? `<p class="muted">Error: ${r.error}</p>` : ""}
          `;
          responsesEl.appendChild(card);
        });
      }

      submitEl.addEventListener("click", async () => {
        submitEl.disabled = true;
        statusEl.textContent = "Consulting...";
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
          } else {
            const data = await res.json();
            renderResult(data);
          }
        } catch (err) {
          statusEl.textContent = err.message || "Request failed.";
        } finally {
          submitEl.disabled = false;
        }
      });

      loadInfo();
    </script>
  </body>
</html>
"""
