/**
 * UI rendering functions - lazy loaded
 */

import { escapeHtml } from '../core/utils.js';

/**
 * Render consultation results
 */
export function renderResult(result, statusEl, synthesisEl, responsesEl) {
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
