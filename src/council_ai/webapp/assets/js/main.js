/**
 * Main application entry point
 */

// Import main CSS - Vite will process this
import '../css/main.css';

import { escapeHtml } from './core/utils.js';
import { loadInfo, submitConsultation } from './core/api.js';

// DOM element references
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

// Lazy load render module
let renderModule = null;
async function getRenderModule() {
  if (!renderModule) {
    renderModule = await import('./ui/render.js');
  }
  return renderModule;
}

// Initialize form with API data
async function initForm() {
  try {
    const data = await loadInfo();
    providerEl.innerHTML = data.providers.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join("");
    modeEl.innerHTML = data.modes.map(m => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("");
    domainEl.innerHTML = data.domains.map(d => `<option value="${escapeHtml(d.id)}">${escapeHtml(d.name)}</option>`).join("");
    providerEl.value = data.defaults.provider || "openai";
    modelEl.value = data.defaults.model || "";
    baseUrlEl.value = data.defaults.base_url || "";
    modeEl.value = data.defaults.mode || "synthesis";
    domainEl.value = data.defaults.domain || "general";
  } catch (err) {
    statusEl.textContent = "Failed to load form data.";
    statusEl.className = "error";
  }
}

// Handle consultation submission (with streaming support)
async function handleSubmit(useStreaming = true) {
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
    if (useStreaming) {
      // Use streaming endpoint
      const render = await getRenderModule();
      const response = await fetch("/api/consult/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Request failed.");
      }
      
      // Read SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              render.handleStreamUpdate(data, statusEl, synthesisEl, responsesEl);
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } else {
      // Use non-streaming endpoint
      const data = await submitConsultation(payload);
      const render = await getRenderModule();
      render.renderResult(data, statusEl, synthesisEl, responsesEl);
    }
  } catch (err) {
    statusEl.textContent = err.message || "Network error. Please check your connection.";
    statusEl.className = "error";
    synthesisEl.innerHTML = `<div class="error">${escapeHtml(err.message || "Network error.")}</div>`;
  } finally {
    submitEl.disabled = false;
  }
}

// Initialize application
async function initApp() {
  // Set up event listeners
  submitEl.addEventListener("click", handleSubmit);
  
  // Allow Enter key to submit (but not in textareas)
  queryEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  });
  
  // Lazy load mobile features on mobile devices
  // This will also lazy load mobile.css
  if (window.matchMedia('(max-width: 768px)').matches) {
    import('./lazy/mobile.js').then(module => {
      module.initMobileFeatures();
    });
  }
  
  // Initialize form (lazy load API info on first interaction or immediately)
  // Using requestIdleCallback for better performance
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      initForm();
    }, { timeout: 2000 });
  } else {
    // Fallback for browsers without requestIdleCallback
    setTimeout(initForm, 100);
  }
}

// Start app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
