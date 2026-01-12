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
const cancelEl = document.getElementById("cancel");
const statusEl = document.getElementById("status");
const synthesisEl = document.getElementById("synthesis");
const responsesEl = document.getElementById("responses");
const historyListEl = document.getElementById("history-list");

// TTS DOM elements
const enableTtsEl = document.getElementById("enable_tts");
const ttsOptionsEl = document.getElementById("tts-options");
const ttsVoiceEl = document.getElementById("tts_voice");
const ttsProviderStatusEl = document.getElementById("tts-provider-status");
const synthesisAudioPlayerEl = document.getElementById("synthesis-audio-player");
const synthesisAudioEl = document.getElementById("synthesis-audio");

// Active request controller for cancellation
let activeController = null;

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

    // Initialize TTS settings
    if (data.tts) {
      enableTtsEl.checked = data.tts.enabled || false;
      ttsOptionsEl.style.display = enableTtsEl.checked ? "block" : "none";

      // Update provider status
      const hasKeys = data.tts.has_elevenlabs_key || data.tts.has_openai_key;
      if (hasKeys) {
        const providers = [];
        if (data.tts.has_elevenlabs_key) providers.push("ElevenLabs");
        if (data.tts.has_openai_key) providers.push("OpenAI");
        ttsProviderStatusEl.textContent = `Available providers: ${providers.join(", ")}`;
        ttsProviderStatusEl.className = "field-hint success";
      } else {
        ttsProviderStatusEl.textContent = "No TTS API keys configured";
        ttsProviderStatusEl.className = "field-hint error";
        enableTtsEl.disabled = true;
      }

      // Load voices
      if (hasKeys) {
        loadTtsVoices();
      }
    }
  } catch (err) {
    statusEl.textContent = "Failed to load form data.";
    statusEl.className = "error";
  }
}

// Load available TTS voices
async function loadTtsVoices() {
  try {
    const res = await fetch("/api/tts/voices");
    const data = await res.json();

    // Populate voice dropdown
    const voiceOptions = ['<option value="">Default voice</option>'];

    if (data.voices.primary && data.voices.primary.length > 0) {
      voiceOptions.push('<optgroup label="Primary (ElevenLabs/OpenAI)">');
      data.voices.primary.forEach(v => {
        const label = v.name || v.id;
        voiceOptions.push(`<option value="${escapeHtml(v.id)}">${escapeHtml(label)}</option>`);
      });
      voiceOptions.push('</optgroup>');
    }

    if (data.voices.fallback && data.voices.fallback.length > 0) {
      voiceOptions.push('<optgroup label="Fallback">');
      data.voices.fallback.forEach(v => {
        const label = v.name || v.id;
        voiceOptions.push(`<option value="${escapeHtml(v.id)}">${escapeHtml(label)}</option>`);
      });
      voiceOptions.push('</optgroup>');
    }

    ttsVoiceEl.innerHTML = voiceOptions.join("");

    // Set default voice if available
    if (data.default_voice) {
      ttsVoiceEl.value = data.default_voice;
    }
  } catch (err) {
    console.error("Failed to load TTS voices:", err);
  }
}

// Generate TTS audio for synthesis
async function generateSynthesisTTS(synthesisText) {
  if (!enableTtsEl.checked || !synthesisText) return;

  try {
    synthesisAudioPlayerEl.style.display = "block";
    synthesisAudioEl.src = "";

    // Show loading state
    const loadingIndicator = document.createElement("div");
    loadingIndicator.className = "tts-loading";
    loadingIndicator.textContent = "Generating audio...";
    synthesisAudioPlayerEl.insertBefore(loadingIndicator, synthesisAudioEl);

    const res = await fetch("/api/tts/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: synthesisText,
        voice: ttsVoiceEl.value || null
      })
    });

    if (!res.ok) {
      throw new Error("TTS generation failed");
    }

    const data = await res.json();

    // Remove loading indicator
    if (loadingIndicator.parentNode) {
      loadingIndicator.remove();
    }

    // Set audio source and show player
    synthesisAudioEl.src = data.audio_url;
    synthesisAudioEl.load();
  } catch (err) {
    console.error("TTS generation error:", err);
    synthesisAudioPlayerEl.style.display = "none";
  }
}

// Handle consultation submission (with streaming support)
async function handleSubmit(useStreaming = true) {
  if (!queryEl.value.trim()) {
    statusEl.textContent = "Please enter a query.";
    statusEl.className = "error";
    return;
  }

  // Create abort controller for cancellation
  activeController = new AbortController();

  submitEl.disabled = true;
  cancelEl.style.display = "block";
  statusEl.innerHTML = '<span class="loading"></span>Consulting the council...';
  statusEl.className = "muted";
  synthesisEl.innerHTML = "";
  responsesEl.innerHTML = "";

  // Hide audio player
  synthesisAudioPlayerEl.style.display = "none";
  synthesisAudioEl.src = "";

  const payload = {
    query: queryEl.value.trim(),
    context: contextEl.value.trim() || null,
    domain: domainEl.value,
    members: membersEl.value.split(",").map(x => x.trim()).filter(Boolean),
    mode: modeEl.value,
    provider: providerEl.value,
    model: modelEl.value.trim() || null,
    base_url: baseUrlEl.value.trim() || null,
    api_key: apiKeyEl.value.trim() || null,
    enable_tts: enableTtsEl.checked
  };

  try {
    if (useStreaming) {
      // Use streaming endpoint
      const render = await getRenderModule();
      const response = await fetch("/api/consult/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: activeController.signal
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

              // Trigger TTS when synthesis is complete
              if (data.type === "synthesis_complete" && data.synthesis) {
                generateSynthesisTTS(data.synthesis);
              } else if (data.type === "complete" && data.result && data.result.synthesis) {
                generateSynthesisTTS(data.result.synthesis);
              }
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

      // Generate TTS for synthesis
      if (data.synthesis) {
        generateSynthesisTTS(data.synthesis);
      }
    }
    // Refresh history after successful consultation
    loadHistory();
  } catch (err) {
    if (err.name === 'AbortError') {
      statusEl.textContent = "Consultation cancelled.";
      statusEl.className = "muted";
    } else {
      statusEl.textContent = err.message || "Network error. Please check your connection.";
      statusEl.className = "error";
      synthesisEl.innerHTML = `<div class="error">${escapeHtml(err.message || "Network error.")}</div>`;
    }
  } finally {
    submitEl.disabled = false;
    cancelEl.style.display = "none";
    activeController = null;
  }
}

// Handle cancellation
function handleCancel() {
  if (activeController) {
    activeController.abort();
  }
}

// Load consultation history
async function loadHistory() {
  if (!historyListEl) return;

  try {
    const res = await fetch("/api/history?limit=5");
    const data = await res.json();

    if (data.consultations && data.consultations.length > 0) {
      historyListEl.innerHTML = data.consultations.map(c => {
        const query = c.query || "Unknown query";
        const truncatedQuery = query.length > 60 ? query.substring(0, 60) + "..." : query;
        const date = c.timestamp ? new Date(c.timestamp).toLocaleDateString() : "";
        const mode = c.mode || "";
        return `
          <div class="history-item" data-id="${escapeHtml(c.id || "")}">
            <div class="query">${escapeHtml(truncatedQuery)}</div>
            <div class="meta">${escapeHtml(mode)} - ${escapeHtml(date)}</div>
          </div>
        `;
      }).join("");
    } else {
      historyListEl.innerHTML = '<p class="muted">No recent consultations.</p>';
    }
  } catch (err) {
    historyListEl.innerHTML = '<p class="muted">History unavailable.</p>';
  }
}

// Initialize application
async function initApp() {
  // Set up event listeners
  submitEl.addEventListener("click", () => handleSubmit());

  // Cancel button listener
  if (cancelEl) {
    cancelEl.addEventListener("click", handleCancel);
  }

  // TTS toggle listener
  if (enableTtsEl) {
    enableTtsEl.addEventListener("change", () => {
      ttsOptionsEl.style.display = enableTtsEl.checked ? "block" : "none";
    });
  }

  // Ctrl+Enter to submit from query or context textareas
  const handleKeyboardSubmit = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };
  queryEl.addEventListener("keydown", handleKeyboardSubmit);
  contextEl.addEventListener("keydown", handleKeyboardSubmit);

  // Lazy load mobile features on mobile devices
  if (window.matchMedia('(max-width: 768px)').matches) {
    import('./lazy/mobile.js').then(module => {
      module.initMobileFeatures();
    });
  }

  // Initialize form and load history
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      initForm();
      loadHistory();
    }, { timeout: 2000 });
  } else {
    setTimeout(() => {
      initForm();
      loadHistory();
    }, 100);
  }
}

// Start app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
