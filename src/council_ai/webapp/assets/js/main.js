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
const saveSettingsEl = document.getElementById("save-settings");
const resetSettingsEl = document.getElementById("reset-settings");

// Active request controller for cancellation
let activeController = null;

// Settings keys for localStorage
const SETTINGS_KEY = 'council_ai_settings';

// Load settings from localStorage
function loadSettings() {
  try {
    const saved = localStorage.getItem(SETTINGS_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (err) {
    console.error('Failed to load settings:', err);
  }
  return null;
}

// Save settings to localStorage
function saveSettings(settings) {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    return true;
  } catch (err) {
    console.error('Failed to save settings:', err);
    return false;
  }
}

// Apply saved settings to form
function applySavedSettings(savedSettings) {
  if (!savedSettings) return;
  
  if (savedSettings.provider && providerEl) {
    providerEl.value = savedSettings.provider;
  }
  if (savedSettings.model && modelEl) {
    modelEl.value = savedSettings.model;
  }
  if (savedSettings.base_url && baseUrlEl) {
    baseUrlEl.value = savedSettings.base_url;
  }
  if (savedSettings.domain && domainEl) {
    domainEl.value = savedSettings.domain;
  }
  if (savedSettings.mode && modeEl) {
    modeEl.value = savedSettings.mode;
  }
}

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
    
    // Load saved settings or use defaults
    const savedSettings = loadSettings();
    
    if (savedSettings) {
      applySavedSettings(savedSettings);
    } else {
      // Apply server defaults
      providerEl.value = data.defaults.provider || "openai";
      modelEl.value = data.defaults.model || "";
      baseUrlEl.value = data.defaults.base_url || "";
      modeEl.value = data.defaults.mode || "synthesis";
      domainEl.value = data.defaults.domain || "general";
    }
  } catch (err) {
    statusEl.textContent = "Failed to load form data.";
    statusEl.className = "error";
  }
}

// Handle save settings button
function handleSaveSettings() {
  const settings = {
    provider: providerEl.value,
    model: modelEl.value,
    base_url: baseUrlEl.value,
    domain: domainEl.value,
    mode: modeEl.value,
  };
  
  if (saveSettings(settings)) {
    // Show success feedback
    const originalText = saveSettingsEl.textContent;
    saveSettingsEl.textContent = "✓ Settings Saved!";
    saveSettingsEl.style.background = "#10b981";
    
    setTimeout(() => {
      saveSettingsEl.textContent = originalText;
      saveSettingsEl.style.background = "";
    }, 2000);
  } else {
    // Show error feedback consistent with success feedback
    const originalText = saveSettingsEl.textContent;
    saveSettingsEl.textContent = "❌ Failed to Save";
    saveSettingsEl.style.background = "#ef4444";
    
    setTimeout(() => {
      saveSettingsEl.textContent = originalText;
      saveSettingsEl.style.background = "";
    }, 3000);
  }
}

// Handle reset settings button
function handleResetSettings() {
  if (confirm("Reset all settings to defaults? This will clear your saved settings.")) {
    localStorage.removeItem(SETTINGS_KEY);
    
    // Show feedback
    const originalText = resetSettingsEl.textContent;
    resetSettingsEl.textContent = "✓ Settings Reset!";
    resetSettingsEl.style.background = "#10b981";
    
    setTimeout(() => {
      resetSettingsEl.textContent = originalText;
      resetSettingsEl.style.background = "";
      // Reload to apply defaults
      location.reload();
    }, 1500);
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

  // Settings buttons
  if (saveSettingsEl) {
    saveSettingsEl.addEventListener("click", handleSaveSettings);
  }
  if (resetSettingsEl) {
    resetSettingsEl.addEventListener("click", handleResetSettings);
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
