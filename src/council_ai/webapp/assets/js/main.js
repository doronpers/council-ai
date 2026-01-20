/**
 * Main application entry point
 * Version: 2024-12-20-fix-null-checks
 */

// Verify this version is loaded
console.log('%c[COUNCIL AI] main.js loaded - Version: 2024-12-20-fix-null-checks', 'color: green; font-weight: bold; font-size: 14px;');

// Import main CSS - Vite will process this
import '../css/main.css';
import '../css/selection.css';

import { escapeHtml } from './core/utils.js';
import { loadInfo, submitConsultation } from './core/api.js';

// DOM element references - will be null if elements don't exist
const providerEl = document.getElementById('provider');
const modelEl = document.getElementById('model');
const baseUrlEl = document.getElementById('base_url');
const modeEl = document.getElementById('mode');
const domainEl = document.getElementById('domain');
const membersEl = document.getElementById('members'); // Now hidden input
const apiKeyEl = document.getElementById('api_key');
const queryEl = document.getElementById('query');
const contextEl = document.getElementById('context');
const submitEl = document.getElementById('submit');
const cancelEl = document.getElementById('cancel');
const statusEl = document.getElementById('status');
const synthesisEl = document.getElementById('synthesis');
const responsesEl = document.getElementById('responses');
const historyListEl = document.getElementById('history-list');
const saveSettingsEl = document.getElementById('save-settings');
const resetSettingsEl = document.getElementById('reset-settings');
const temperatureEl = document.getElementById('temperature');
const temperatureValueEl = document.getElementById('temperature-value');
const maxTokensEl = document.getElementById('max_tokens');

// #region agent log
// Log missing critical elements at module load
const criticalElements = { queryEl, submitEl, statusEl };
const missingCritical = Object.entries(criticalElements)
  .filter(([_, el]) => !el)
  .map(([name, _]) => name);
if (missingCritical.length > 0) {
  console.warn('[DEBUG] Critical DOM elements missing at module load:', missingCritical);
}
// #endregion

// TTS DOM elements
const enableTtsEl = document.getElementById('enable_tts');
const ttsOptionsEl = document.getElementById('tts-options');
const ttsVoiceEl = document.getElementById('tts_voice');
const ttsProviderStatusEl = document.getElementById('tts-provider-status');
const synthesisAudioPlayerEl = document.getElementById('synthesis-audio-player');
const synthesisAudioEl = document.getElementById('synthesis-audio');

// Active request controller for cancellation
let activeController = null;

// Consultation progress tracking
const consultationState = {
  totalMembers: 0,
  responding: new Set(),
  completed: new Set(),
  pending: new Set(),
  memberData: new Map(), // persona_id -> {name, emoji, status}
};

// Settings keys for localStorage
const SETTINGS_KEY = 'council_ai_settings';

// Store model capabilities data
let modelCapabilities = [];

// Store persona and domain data
let allPersonas = [];
let allDomains = [];

// DOM element references for member preview
const memberCardsEl = document.getElementById('member-cards');
const memberCountEl = document.getElementById('member-count');
const toggleComparisonEl = document.getElementById('toggle-comparison');

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

// Update model dropdown based on selected provider
function updateModelDropdown(provider) {
  if (!provider || modelCapabilities.length === 0) return;
  if (!modelEl) {
    console.error('[DEBUG] modelEl is null in updateModelDropdown');
    return;
  }

  const providerInfo = modelCapabilities.find((cap) => cap.provider === provider);
  if (!providerInfo) return;

  // Save current model value
  const currentModel = modelEl.value;

  // Build model options
  const options = ['<option value="">Default model for provider</option>'];

  if (providerInfo.models && providerInfo.models.length > 0) {
    providerInfo.models.forEach((model) => {
      options.push(`<option value="${escapeHtml(model)}">${escapeHtml(model)}</option>`);
    });
  }

  // Add default model if available
  if (providerInfo.default_model && !providerInfo.models.includes(providerInfo.default_model)) {
    options.push(
      `<option value="${escapeHtml(providerInfo.default_model)}">${escapeHtml(providerInfo.default_model)} (default)</option>`
    );
  }

  modelEl.innerHTML = options.join('');

  // Restore saved value if it's valid for this provider
  if (currentModel) {
    modelEl.value = currentModel;
  }
}

// Apply saved settings to form
function applySavedSettings(savedSettings) {
  if (!savedSettings) return;

  if (savedSettings.provider && providerEl) {
    providerEl.value = savedSettings.provider;
    updateModelDropdown(savedSettings.provider);
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
  if (savedSettings.temperature !== undefined && temperatureEl) {
    temperatureEl.value = savedSettings.temperature;
    if (temperatureValueEl) temperatureValueEl.textContent = savedSettings.temperature;
  }
  if (savedSettings.max_tokens && maxTokensEl) {
    maxTokensEl.value = savedSettings.max_tokens;
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

// Render member cards based on selected members
function renderMemberCards(selectedMemberIds, allPersonas) {
  if (!memberCardsEl || !allPersonas || allPersonas.length === 0) return;

  // Get selected personas
  const selectedPersonas = selectedMemberIds
    .map((id) => allPersonas.find((p) => p.id === id))
    .filter(Boolean);

  if (selectedPersonas.length === 0) {
    memberCardsEl.innerHTML =
      '<p class="muted" style="text-align: center; padding: 24px;">No members selected. Choose a domain or add custom members.</p>';
    if (memberCountEl) memberCountEl.textContent = '0 members selected';
    return;
  }

  // Render cards
  memberCardsEl.innerHTML = selectedPersonas
    .map((persona) => {
      const focusAreas = (persona.focus_areas || []).slice(0, 3); // Show first 3 focus areas
      const focusTags = focusAreas
        .map((area) => `<span class="focus-tag">${escapeHtml(area)}</span>`)
        .join('');
      return `
      <div class="member-card member-card--selected" data-persona-id="${escapeHtml(persona.id)}">
        <div class="member-card-header">
          <span class="member-emoji">${escapeHtml(persona.emoji || '👤')}</span>
          <div class="member-info">
            <div class="member-name">${escapeHtml(persona.name || persona.id)}</div>
            <div class="member-title">${escapeHtml(persona.title || '')}</div>
          </div>
        </div>
        ${focusTags ? `<div class="member-focus-areas">${focusTags}</div>` : ''}
      </div>
    `;
    })
    .join('');

  // Update count
  if (memberCountEl) {
    memberCountEl.textContent = `${selectedPersonas.length} ${selectedPersonas.length === 1 ? 'member' : 'members'} selected`;
  }
}

// Get currently selected member IDs
function getSelectedMemberIds() {
  // #region agent log
  if (!membersEl) {
    console.error('[DEBUG] membersEl is null in getSelectedMemberIds');
    fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:221',message:'membersEl is null in getSelectedMemberIds',data:{membersElNull:true},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  }
  if (!domainEl) {
    console.error('[DEBUG] domainEl is null in getSelectedMemberIds');
    fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:221',message:'domainEl is null in getSelectedMemberIds',data:{domainElNull:true},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  }
  // #endregion

  if (membersEl && membersEl.value) {
    const customMembers = membersEl.value
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);
    if (customMembers.length > 0) {
      return customMembers;
    }
  }

  // Get from domain
  if (domainEl && domainEl.value) {
    const selectedDomain = allDomains.find((d) => d.id === domainEl.value);
    if (selectedDomain && selectedDomain.default_personas) {
      return selectedDomain.default_personas;
    }
  }

  return [];
}

// Update member preview when domain or members change
function updateMemberPreview() {
  const selectedIds = getSelectedMemberIds();
  renderMemberCards(selectedIds, allPersonas);
}

// Render the checkbox grid for custom member selection
function renderMemberSelection() {
  const container = document.getElementById('members-container');
  if (!container || !allPersonas) return;

  container.innerHTML = allPersonas
    .map(
      (p) => `
    <label class="member-selection-item">
      <input type="checkbox" value="${escapeHtml(p.id)}" class="member-checkbox">
      <div class="member-selection-card">
        <span class="member-emoji">${escapeHtml(p.emoji)}</span>
        <span class="member-name-small">${escapeHtml(p.name)}</span>
      </div>
    </label>
  `
    )
    .join('');

  // Add listeners
  container.querySelectorAll('input').forEach((input) => {
    input.addEventListener('change', updateHiddenMembersInput);
  });
}

// Update the hidden input based on checkboxes
function updateHiddenMembersInput() {
  const container = document.getElementById('members-container');
  if (!container) return;
  if (!membersEl) {
    console.error('[DEBUG] membersEl is null in updateHiddenMembersInput');
    return;
  }

  const checked = Array.from(container.querySelectorAll('input:checked')).map((cb) => cb.value);
  membersEl.value = checked.join(',');
  updateMemberPreview();
}

// Sync checkboxes with the hidden input (e.g. after domain reset)
function syncCheckboxesToInput() {
  const container = document.getElementById('members-container');
  if (!container) return;
  if (!membersEl) {
    console.error('[DEBUG] membersEl is null in syncCheckboxesToInput');
    return;
  }

  const currentIds = membersEl.value
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  container.querySelectorAll('input').forEach((input) => {
    input.checked = currentIds.includes(input.value);
  });
}

// Initialize form with API data
async function initForm() {
  try {
    const data = await loadInfo();

    // Store model capabilities for later use
    modelCapabilities = data.models || [];

    // Store persona and domain data
    allPersonas = data.personas || [];
    allDomains = data.domains || [];

    // Make available globally for render.js
    window.allPersonas = allPersonas;

    if (!providerEl || !modeEl || !domainEl) {
      console.error('[DEBUG] Missing critical DOM elements in initForm', {
        providerEl: !!providerEl,
        modeEl: !!modeEl,
        domainEl: !!domainEl,
      });
      statusEl.textContent = 'Failed to initialize form: missing DOM elements.';
      statusEl.className = 'error';
      return;
    }

    providerEl.innerHTML = data.providers
      .map((p) => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`)
      .join('');
    modeEl.innerHTML = data.modes
      .map((m) => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`)
      .join('');
    // Enhanced domain dropdown with member count
    domainEl.innerHTML = data.domains
      .map((d) => {
        const memberCount = d.default_personas ? d.default_personas.length : 0;
        return `<option value="${escapeHtml(d.id)}">${escapeHtml(d.name)}${memberCount > 0 ? ` (${memberCount} members)` : ''}</option>`;
      })
      .join('');
    providerEl.value = data.defaults.provider || 'openai';
    if (baseUrlEl) baseUrlEl.value = data.defaults.base_url || '';
    modeEl.value = data.defaults.mode || 'synthesis';
    domainEl.value = data.defaults.domain || 'general';

    // Update model dropdown for initial provider
    updateModelDropdown(providerEl.value);

    // Add event listener for provider changes
    providerEl.addEventListener('change', () => {
      updateModelDropdown(providerEl.value);
    });

    // Add event listeners for domain and member changes
    domainEl.addEventListener('change', () => {
      updateMemberPreview();
      // Clear custom members when domain changes
      if (membersEl) {
        membersEl.value = '';
        syncCheckboxesToInput();
      }
    });

    // Initialize member selection grid
    renderMemberSelection();

    if (membersEl) {
      // If we manually change the hidden input, sync everything (rare case)
      membersEl.addEventListener('change', () => {
        syncCheckboxesToInput();
        updateMemberPreview();
      });
    }

    // Initialize TTS settings
    if (data.tts) {
      enableTtsEl.checked = data.tts.enabled || false;
      ttsOptionsEl.style.display = enableTtsEl.checked ? 'block' : 'none';

      // Update provider status
      const hasKeys = data.tts.has_elevenlabs_key || data.tts.has_openai_key;
      if (hasKeys) {
        const providers = [];
        if (data.tts.has_elevenlabs_key) providers.push('ElevenLabs');
        if (data.tts.has_openai_key) providers.push('OpenAI');
        ttsProviderStatusEl.textContent = `Available providers: ${providers.join(', ')}`;
        ttsProviderStatusEl.className = 'field-hint success';
      } else {
        ttsProviderStatusEl.textContent = 'No TTS API keys configured';
        ttsProviderStatusEl.className = 'field-hint error';
        enableTtsEl.disabled = true;
      }

      // Load voices
      if (hasKeys) {
        loadTtsVoices();
      }
    }

    // Load saved settings or use defaults
    const savedSettings = loadSettings();

    if (savedSettings) {
      applySavedSettings(savedSettings);
    } else {
      // Apply server defaults
      if (providerEl) providerEl.value = data.defaults.provider || 'openai';
      if (providerEl) updateModelDropdown(providerEl.value);
      if (baseUrlEl) baseUrlEl.value = data.defaults.base_url || '';
      if (modeEl) modeEl.value = data.defaults.mode || 'synthesis';
      if (domainEl) domainEl.value = data.defaults.domain || 'general';
      if (temperatureEl) temperatureEl.value = 0.7;
      if (temperatureValueEl) temperatureValueEl.textContent = '0.7';
      if (maxTokensEl) maxTokensEl.value = '1000';
    }

    // Initialize member preview
    syncCheckboxesToInput();
    updateMemberPreview();

    // Initialize comparison mode toggle
    if (toggleComparisonEl) {
      toggleComparisonEl.addEventListener('click', () => {
        const isComparison = responsesEl.classList.toggle('comparison-mode');
        toggleComparisonEl.textContent = isComparison ? '📋 List View' : '📊 Compare Responses';
      });
    }
  } catch {
    statusEl.textContent = 'Failed to load form data.';
    statusEl.className = 'error';
  }
}

// Load available TTS voices
async function loadTtsVoices() {
  try {
    const res = await fetch('/api/tts/voices');
    const data = await res.json();

    // Populate voice dropdown
    const voiceOptions = ['<option value="">Default voice</option>'];

    if (data.voices.primary && data.voices.primary.length > 0) {
      voiceOptions.push('<optgroup label="Primary (ElevenLabs/OpenAI)">');
      data.voices.primary.forEach((v) => {
        const label = v.name || v.id;
        voiceOptions.push(`<option value="${escapeHtml(v.id)}">${escapeHtml(label)}</option>`);
      });
      voiceOptions.push('</optgroup>');
    }

    if (data.voices.fallback && data.voices.fallback.length > 0) {
      voiceOptions.push('<optgroup label="Fallback">');
      data.voices.fallback.forEach((v) => {
        const label = v.name || v.id;
        voiceOptions.push(`<option value="${escapeHtml(v.id)}">${escapeHtml(label)}</option>`);
      });
      voiceOptions.push('</optgroup>');
    }

    ttsVoiceEl.innerHTML = voiceOptions.join('');

    // Set default voice if available
    if (data.default_voice) {
      ttsVoiceEl.value = data.default_voice;
    }
  } catch (err) {
    console.error('Failed to load TTS voices:', err);
  }
}

// Generate TTS audio for synthesis
async function generateSynthesisTTS(synthesisText) {
  if (!enableTtsEl.checked || !synthesisText) return;

  try {
    synthesisAudioPlayerEl.style.display = 'block';
    synthesisAudioEl.src = '';

    // Show loading state
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'tts-loading';
    loadingIndicator.textContent = 'Generating audio...';
    synthesisAudioPlayerEl.insertBefore(loadingIndicator, synthesisAudioEl);

    const res = await fetch('/api/tts/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: synthesisText,
        voice: ttsVoiceEl.value || null,
      }),
    });

    if (!res.ok) {
      throw new Error('TTS generation failed');
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
    console.error('TTS generation error:', err);
    synthesisAudioPlayerEl.style.display = 'none';
  }
}

// Handle save settings button
function handleSaveSettings() {
  if (!providerEl || !modelEl || !baseUrlEl || !domainEl || !modeEl || !temperatureEl || !maxTokensEl) {
    console.error('[DEBUG] Missing DOM elements in handleSaveSettings', {
      providerEl: !!providerEl,
      modelEl: !!modelEl,
      baseUrlEl: !!baseUrlEl,
      domainEl: !!domainEl,
      modeEl: !!modeEl,
      temperatureEl: !!temperatureEl,
      maxTokensEl: !!maxTokensEl,
    });
    return;
  }

  const settings = {
    provider: providerEl.value,
    model: modelEl.value,
    base_url: baseUrlEl.value,
    domain: domainEl.value,
    mode: modeEl.value,
    temperature: parseFloat(temperatureEl.value),
    max_tokens: parseInt(maxTokensEl.value),
  };

  if (saveSettings(settings)) {
    // Show success feedback
    const originalText = saveSettingsEl.textContent;
    saveSettingsEl.textContent = '✓ Settings Saved!';
    saveSettingsEl.style.background = '#10b981';

    setTimeout(() => {
      saveSettingsEl.textContent = originalText;
      saveSettingsEl.style.background = '';
    }, 2000);
  } else {
    // Show error feedback consistent with success feedback
    const originalText = saveSettingsEl.textContent;
    saveSettingsEl.textContent = '❌ Failed to Save';
    saveSettingsEl.style.background = '#ef4444';

    setTimeout(() => {
      saveSettingsEl.textContent = originalText;
      saveSettingsEl.style.background = '';
    }, 3000);
  }
}

// Handle reset settings button
function handleResetSettings() {
  if (confirm('Reset all settings to defaults? This will clear your saved settings.')) {
    localStorage.removeItem(SETTINGS_KEY);

    // Show feedback
    const originalText = resetSettingsEl.textContent;
    resetSettingsEl.textContent = '✓ Settings Reset!';
    resetSettingsEl.style.background = '#10b981';

    setTimeout(() => {
      resetSettingsEl.textContent = originalText;
      resetSettingsEl.style.background = '';
      // Reload to apply defaults
      location.reload();
    }, 1500);
  }
}

// Initialize progress dashboard with selected members
function initializeProgressDashboard(selectedMemberIds) {
  const progressDashboard = document.getElementById('progress-dashboard');
  const memberStatusList = document.getElementById('member-status-list');
  const progressBar = document.getElementById('progress-bar');
  const progressSummary = document.getElementById('progress-summary');

  if (!progressDashboard || !memberStatusList) return;

  // Reset state
  consultationState.totalMembers = selectedMemberIds.length;
  consultationState.responding.clear();
  consultationState.completed.clear();
  consultationState.pending.clear();
  consultationState.memberData.clear();

  // Initialize member data
  selectedMemberIds.forEach((personaId) => {
    const persona = allPersonas.find((p) => p.id === personaId);
    consultationState.memberData.set(personaId, {
      name: persona?.name || personaId,
      emoji: persona?.emoji || '👤',
      status: 'pending',
    });
    consultationState.pending.add(personaId);
  });

  // Render initial status cards
  updateMemberStatusCards();

  // Reset progress bar
  if (progressBar) {
    progressBar.style.width = '0%';
  }

  // Update summary
  if (progressSummary) {
    progressSummary.textContent = `0 of ${consultationState.totalMembers} members have responded`;
  }

  // Show dashboard
  progressDashboard.style.display = 'block';
}

// Update member status cards
function updateMemberStatusCards() {
  const memberStatusList = document.getElementById('member-status-list');
  if (!memberStatusList) return;

  const cards = Array.from(consultationState.memberData.entries())
    .map(([personaId, data]) => {
      const status = data.status;
      let statusIcon = '⏳';
      let statusText = 'Pending';
      let statusClass = 'member-status-card--pending';

      if (status === 'responding') {
        statusIcon = '💭';
        statusText = 'Responding...';
        statusClass = 'member-status-card--responding';
      } else if (status === 'completed') {
        statusIcon = '✓';
        statusText = 'Completed';
        statusClass = 'member-status-card--completed';
      }

      return `
      <div class="member-status-card ${statusClass}" data-persona-id="${escapeHtml(personaId)}">
        <span class="member-status-emoji">${data.emoji}</span>
        <div class="member-status-info">
          <div class="member-status-name">${escapeHtml(data.name)}</div>
          <div class="member-status-text">${statusIcon} ${statusText}</div>
        </div>
      </div>
    `;
    })
    .join('');

  memberStatusList.innerHTML = cards;
  updateProgressBar();
}

// Update progress bar and summary
function updateProgressBar() {
  const progressBar = document.getElementById('progress-bar');
  const progressSummary = document.getElementById('progress-summary');

  const completed = consultationState.completed.size;
  const total = consultationState.totalMembers;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  if (progressBar) {
    progressBar.style.width = `${percentage}%`;
  }

  if (progressSummary) {
    const responding = consultationState.responding.size;
    if (responding > 0) {
      progressSummary.textContent = `${completed} of ${total} members completed, ${responding} responding...`;
    } else {
      progressSummary.textContent = `${completed} of ${total} members have responded`;
    }
  }
}

// Update member status
function updateMemberStatus(personaId, status) {
  const memberData = consultationState.memberData.get(personaId);
  if (!memberData) return;

  // Remove from old status sets
  consultationState.responding.delete(personaId);
  consultationState.completed.delete(personaId);
  consultationState.pending.delete(personaId);

  // Add to new status set
  memberData.status = status;
  if (status === 'responding') {
    consultationState.responding.add(personaId);
  } else if (status === 'completed') {
    consultationState.completed.add(personaId);
  } else {
    consultationState.pending.add(personaId);
  }

  updateMemberStatusCards();
}

// Make updateMemberStatus available globally for render.js
window.updateMemberStatus = updateMemberStatus;

// Make allPersonas available globally for render.js
window.allPersonas = allPersonas;

// Handle consultation submission (with streaming support)
async function handleSubmit(useStreaming = true) {
  console.log('[DEBUG] handleSubmit called - version 2024-12-20-fix-null-checks');
  try {
  // #region agent log
  const missingElements = [];
  if (!queryEl) missingElements.push('queryEl');
  if (!contextEl) missingElements.push('contextEl');
  if (!domainEl) missingElements.push('domainEl');
  if (!membersEl) missingElements.push('membersEl');
  if (!modeEl) missingElements.push('modeEl');
  if (!providerEl) missingElements.push('providerEl');
  if (!modelEl) missingElements.push('modelEl');
  if (!baseUrlEl) missingElements.push('baseUrlEl');
  if (!apiKeyEl) missingElements.push('apiKeyEl');
  if (!enableTtsEl) missingElements.push('enableTtsEl');
  if (!temperatureEl) missingElements.push('temperatureEl');
  if (!maxTokensEl) missingElements.push('maxTokensEl');
  if (!statusEl) missingElements.push('statusEl');
  if (!submitEl) missingElements.push('submitEl');
  if (missingElements.length > 0) {
    console.error('[DEBUG] Missing DOM elements:', missingElements);
    fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:674',message:'Missing DOM elements detected',data:{missingElements},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'ALL'})}).catch(()=>{});
  }
  // #endregion

  if (!queryEl || !queryEl.value || !queryEl.value.trim()) {
    if (statusEl) {
      statusEl.textContent = 'Please enter a query.';
      statusEl.className = 'error';
    }
    return;
  }

  // Validate critical DOM elements before proceeding
  if (!submitEl || !statusEl || !synthesisEl || !responsesEl) {
    console.error('[DEBUG] Missing critical DOM elements in handleSubmit', {
      submitEl: !!submitEl,
      statusEl: !!statusEl,
      synthesisEl: !!synthesisEl,
      responsesEl: !!responsesEl,
    });
    return;
  }

  // Create abort controller for cancellation
  activeController = new AbortController();

  submitEl.disabled = true;
  if (cancelEl) cancelEl.style.display = 'block';

  // Show skeleton loader with progress
  const loadingSkeleton = document.getElementById('loading-skeleton');
  const progressText = document.getElementById('progress-text');
  if (loadingSkeleton) loadingSkeleton.style.display = 'block';
  if (progressText) progressText.textContent = 'Assembling council...';

  statusEl.innerHTML = '';
  statusEl.className = 'muted';
  synthesisEl.innerHTML = '';
  responsesEl.innerHTML = '';

  // Hide audio player
  if (synthesisAudioPlayerEl) synthesisAudioPlayerEl.style.display = 'none';
  if (synthesisAudioEl) synthesisAudioEl.src = '';

  // Initialize progress dashboard
  const selectedMemberIds = getSelectedMemberIds();
  initializeProgressDashboard(selectedMemberIds);

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:706',message:'Checking DOM elements before payload construction',data:{queryEl:!!queryEl,contextEl:!!contextEl,domainEl:!!domainEl,membersEl:!!membersEl,modeEl:!!modeEl,providerEl:!!providerEl,modelEl:!!modelEl,baseUrlEl:!!baseUrlEl,apiKeyEl:!!apiKeyEl,enableTtsEl:!!enableTtsEl,temperatureEl:!!temperatureEl,maxTokensEl:!!maxTokensEl},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:707',message:'Accessing queryEl.value',data:{queryElNull:queryEl===null,queryElUndefined:queryEl===undefined,queryElValueNull:queryEl&&queryEl.value===null,queryElValueUndefined:queryEl&&queryEl.value===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion
  if (!queryEl || !queryEl.value) {
    console.error('[DEBUG] queryEl or queryEl.value is null/undefined at payload construction');
    if (statusEl) {
      statusEl.textContent = 'Error: Query element not found.';
      statusEl.className = 'error';
    }
    return;
  }
  const queryValue = queryEl.value.trim();

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:708',message:'Accessing contextEl.value',data:{contextElNull:contextEl===null,contextElUndefined:contextEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
  // #endregion
  const contextValue = contextEl ? contextEl.value.trim() || null : null;

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:709',message:'Accessing domainEl.value',data:{domainElNull:domainEl===null,domainElUndefined:domainEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion
  const domainValue = domainEl ? domainEl.value : '';

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:710',message:'Accessing membersEl.value',data:{membersElNull:membersEl===null,membersElUndefined:membersEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  const membersValue = membersEl ? membersEl.value
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean) : [];

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:714',message:'Accessing modeEl.value',data:{modeElNull:modeEl===null,modeElUndefined:modeEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion
  const modeValue = modeEl ? modeEl.value : '';

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:715',message:'Accessing providerEl.value',data:{providerElNull:providerEl===null,providerElUndefined:providerEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion
  const providerValue = providerEl ? providerEl.value : '';

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:716',message:'Accessing modelEl.value',data:{modelElNull:modelEl===null,modelElUndefined:modelEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
  // #endregion
  const modelValue = modelEl ? modelEl.value.trim() || null : null;

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:717',message:'Accessing baseUrlEl.value',data:{baseUrlElNull:baseUrlEl===null,baseUrlElUndefined:baseUrlEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
  // #endregion
  const baseUrlValue = baseUrlEl ? baseUrlEl.value.trim() || null : null;

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:718',message:'Accessing apiKeyEl.value',data:{apiKeyElNull:apiKeyEl===null,apiKeyElUndefined:apiKeyEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
  // #endregion
  const apiKeyValue = apiKeyEl ? apiKeyEl.value.trim() || null : null;

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:719',message:'Accessing enableTtsEl.checked',data:{enableTtsElNull:enableTtsEl===null,enableTtsElUndefined:enableTtsEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
  // #endregion
  const enableTtsValue = enableTtsEl ? enableTtsEl.checked : false;

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:720',message:'Accessing temperatureEl.value',data:{temperatureElNull:temperatureEl===null,temperatureElUndefined:temperatureEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'G'})}).catch(()=>{});
  // #endregion
  const temperatureValue = temperatureEl ? parseFloat(temperatureEl.value) : 0.7;

  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/0a386429-06d9-4e71-8f3b-df941c2f1de1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.js:721',message:'Accessing maxTokensEl.value',data:{maxTokensElNull:maxTokensEl===null,maxTokensElUndefined:maxTokensEl===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'G'})}).catch(()=>{});
  // #endregion
  const maxTokensValue = maxTokensEl ? parseInt(maxTokensEl.value) : 1000;

  const payload = {
    query: queryValue,
    context: contextValue,
    domain: domainValue,
    members: membersValue,
    mode: modeValue,
    provider: providerValue,
    model: modelValue,
    base_url: baseUrlValue,
    api_key: apiKeyValue,
    enable_tts: enableTtsValue,
    temperature: temperatureValue,
    max_tokens: maxTokensValue,
  };

  try {
    if (useStreaming) {
      // Use streaming endpoint
      const render = await getRenderModule();
      const response = await fetch('/api/consult/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: activeController.signal,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Request failed.');
      }

      // Read SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              render.handleStreamUpdate(data, statusEl, synthesisEl, responsesEl);

              // Trigger TTS when synthesis is complete
              if (data.type === 'synthesis_complete' && data.synthesis) {
                generateSynthesisTTS(data.synthesis);
              } else if (data.type === 'complete' && data.result && data.result.synthesis) {
                generateSynthesisTTS(data.result.synthesis);
              }
            } catch {
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
    console.error('[DEBUG] Error in handleSubmit:', err);
    if (err.name === 'AbortError') {
      if (statusEl) {
        statusEl.textContent = 'Consultation cancelled.';
        statusEl.className = 'muted';
      }
    } else {
      const errorMsg = err.message || 'Network error. Please check your connection.';
      if (statusEl) {
        statusEl.textContent = errorMsg;
        statusEl.className = 'error';
      }
      if (synthesisEl) {
        synthesisEl.innerHTML = `<div class="error">${escapeHtml(errorMsg)}</div>`;
      }
    }
  } finally {
    if (submitEl) submitEl.disabled = false;
    if (cancelEl) cancelEl.style.display = 'none';
    activeController = null;

    // Hide skeleton loader
    const loadingSkeleton = document.getElementById('loading-skeleton');
    if (loadingSkeleton) loadingSkeleton.style.display = 'none';
  }
  } catch (outerErr) {
    // Catch any errors that occur before the inner try-catch (e.g., null reference errors)
    console.error('[DEBUG] Outer error in handleSubmit (likely null reference):', outerErr);
    console.error('[DEBUG] Error stack:', outerErr.stack);
    if (statusEl) {
      statusEl.textContent = `Error: ${outerErr.message || 'Unknown error'}. Check console for details.`;
      statusEl.className = 'error';
    }
    if (submitEl) submitEl.disabled = false;
    if (cancelEl) cancelEl.style.display = 'none';
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
    const res = await fetch('/api/history?limit=5');
    const data = await res.json();

    if (data.consultations && data.consultations.length > 0) {
      historyListEl.innerHTML = data.consultations
        .map((c) => {
          const query = c.query || 'Unknown query';
          const truncatedQuery = query.length > 60 ? query.substring(0, 60) + '...' : query;
          const date = c.timestamp ? new Date(c.timestamp).toLocaleDateString() : '';
          const mode = c.mode || '';
          return `
          <div class="history-item" data-id="${escapeHtml(c.id || '')}">
            <div class="query">${escapeHtml(truncatedQuery)}</div>
            <div class="meta">${escapeHtml(mode)} - ${escapeHtml(date)}</div>
          </div>
        `;
        })
        .join('');
    } else {
      historyListEl.innerHTML = '<p class="muted">No recent consultations.</p>';
    }
  } catch {
    historyListEl.innerHTML = '<p class="muted">History unavailable.</p>';
  }
}

// Initialize application
async function initApp() {
  // Set up event listeners
  if (!submitEl) {
    console.error('[DEBUG] submitEl is null in initApp - cannot attach event listener');
    return;
  }
  submitEl.addEventListener('click', () => handleSubmit());

  // Cancel button listener
  if (cancelEl) {
    cancelEl.addEventListener('click', handleCancel);
  }

  // TTS toggle listener
  if (enableTtsEl) {
    enableTtsEl.addEventListener('change', () => {
      ttsOptionsEl.style.display = enableTtsEl.checked ? 'block' : 'none';
    });
  }

  // Temperature slider listener
  if (temperatureEl && temperatureValueEl) {
    temperatureEl.addEventListener('input', () => {
      temperatureValueEl.textContent = temperatureEl.value;
    });
  }

  // Settings buttons
  if (saveSettingsEl) {
    saveSettingsEl.addEventListener('click', handleSaveSettings);
  }
  if (resetSettingsEl) {
    resetSettingsEl.addEventListener('click', handleResetSettings);
  }

  // System Status / Diagnostics
  const systemStatusBtn = document.getElementById('system-status-btn');
  const diagnosticsModal = document.getElementById('diagnostics-modal');
  const refreshDiagnosticsBtn = document.getElementById('refresh-diagnostics');

  if (systemStatusBtn && diagnosticsModal) {
    systemStatusBtn.addEventListener('click', () => {
      diagnosticsModal.style.display = 'flex';
      runDiagnostics();
    });

    refreshDiagnosticsBtn.addEventListener('click', runDiagnostics);

    // Close on outside click
    diagnosticsModal.addEventListener('click', (e) => {
      if (e.target === diagnosticsModal) diagnosticsModal.style.display = 'none';
    });
  }

  // Ctrl+Enter to submit from query or context textareas
  const handleKeyboardSubmit = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };
  queryEl.addEventListener('keydown', handleKeyboardSubmit);
  contextEl.addEventListener('keydown', handleKeyboardSubmit);

  // Lazy load mobile features on mobile devices
  if (window.matchMedia('(max-width: 768px)').matches) {
    import('./lazy/mobile.js').then((module) => {
      module.initMobileFeatures();
    });
  }

  // Initialize form and load history
  if ('requestIdleCallback' in window) {
    requestIdleCallback(
      () => {
        initForm();
        loadHistory();
      },
      { timeout: 2000 }
    );
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

// Run diagnostics logic
async function runDiagnostics() {
  const contentEl = document.getElementById('diagnostics-content');
  contentEl.innerHTML =
    '<div style="text-align: center; padding: 40px;"><span class="loading"></span> Running diagnostics...</div>';

  try {
    const res = await fetch('/api/diagnostics');
    const data = await res.json();

    // Helper to escape HTML
    const escapeHtml = (unsafe) => {
      return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    };

    // Render Keys Table
    let html =
      '<h3>API Keys</h3><table style="width:100%; border-collapse: collapse; margin-bottom: 24px;">';
    html +=
      '<tr style="border-bottom: 1px solid var(--border); text-align: left;"><th style="padding: 8px;">Provider</th><th style="padding: 8px;">Status</th><th style="padding: 8px;">Details</th></tr>';

    for (const [provider, status] of Object.entries(data.keys.provider_status)) {
      const hasKey = status.has_key;
      const icon = hasKey ? '✅' : '❌';
      const color = hasKey ? 'var(--accent-green)' : 'var(--accent-red)';
      const keyPrefix = status.key_prefix || (status.env_var ? 'Env Var' : '***');
      const details = hasKey
        ? `Prefix: ${escapeHtml(keyPrefix)}`
        : `Missing (${status.env_var || ''})`;

      html += `
                <tr style="border-bottom: 1px solid var(--border);">
                    <td style="padding: 8px;">${escapeHtml(provider)}</td>
                    <td style="padding: 8px; color: ${color}; font-weight: 500;">${icon} ${hasKey ? 'Configured' : 'Missing'}</td>
                    <td style="padding: 8px; color: var(--text-secondary); font-size: 0.9em;">${details}</td>
                </tr>
            `;
    }
    html += '</table>';

    // Render Connectivity
    html += '<h3>Connectivity Test</h3>';
    if (Object.keys(data.connectivity).length > 0) {
      html += '<table style="width:100%; border-collapse: collapse; margin-bottom: 24px;">';
      html +=
        '<tr style="border-bottom: 1px solid var(--border); text-align: left;"><th style="padding: 8px;">Provider</th><th style="padding: 8px;">Result</th><th style="padding: 8px;">Latency</th><th style="padding: 8px;">Message</th></tr>';

      for (const [provider, res] of Object.entries(data.connectivity)) {
        const icon = res.ok ? '✅' : '❌';
        const color = res.ok ? 'var(--accent-green)' : 'var(--accent-red)';

        html += `
                    <tr style="border-bottom: 1px solid var(--border);">
                        <td style="padding: 8px;">${escapeHtml(provider)}</td>
                        <td style="padding: 8px; color: ${color}; font-weight: 500;">${icon} ${res.ok ? 'Online' : 'Failed'}</td>
                        <td style="padding: 8px;">${Math.round(res.latency_ms)}ms</td>
                        <td style="padding: 8px; color: var(--text-secondary); font-size: 0.9em;">${escapeHtml(res.message || '')}</td>
                    </tr>
                `;
      }
      html += '</table>';
    } else {
      html += '<p class="muted">No configured providers to test.</p>';
    }

    // Render TTS
    html += '<h3>Voice (TTS)</h3>';
    if (Object.keys(data.tts).length > 0) {
      html += '<table style="width:100%; border-collapse: collapse; margin-bottom: 24px;">';
      for (const [provider, res] of Object.entries(data.tts)) {
        const icon = res.ok ? '✅' : '❌';
        const color = res.ok ? 'var(--accent-green)' : 'var(--accent-red)';

        html += `
                    <tr style="border-bottom: 1px solid var(--border);">
                        <td style="padding: 8px;">${escapeHtml(provider)}</td>
                        <td style="padding: 8px; color: ${color}; font-weight: 500;">${icon} ${res.ok ? 'Ready' : 'Error'}</td>
                        <td style="padding: 8px; color: var(--text-secondary); font-size: 0.9em;">${escapeHtml(res.msg || '')}</td>
                    </tr>
                `;
      }
      html += '</table>';
    } else {
      html += '<p class="muted">No TTS providers configured.</p>';
    }

    contentEl.innerHTML = html;
  } catch (err) {
    contentEl.innerHTML = `<div class="error">Failed to run diagnostics: ${escapeHtml(err.message)}</div>`;
  }
}
