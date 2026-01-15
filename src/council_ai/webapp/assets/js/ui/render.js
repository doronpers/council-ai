/**
 * UI rendering functions - lazy loaded
 */

import { escapeHtml } from '../core/utils.js';

// Track streaming state
const streamingState = {
  activeResponses: new Map(), // persona_id -> {card, content}
  synthesisContent: "",
};

/**
 * Handle streaming update
 */
export function handleStreamUpdate(update, statusEl, synthesisEl, responsesEl) {
  const type = update.type;

  switch (type) {
    case "progress":
      statusEl.innerHTML = `<span class="loading"></span>${escapeHtml(update.message || "Processing...")}`;
      statusEl.className = "muted";
      // Update progress text if available
      const progressTextEl = document.getElementById("progress-text");
      if (progressTextEl && update.message) {
        progressTextEl.textContent = update.message;
      }
      break;

    case "response_start":
      // Hide skeleton once we start getting responses
      const skeleton = document.getElementById("loading-skeleton");
      if (skeleton) skeleton.style.display = "none";

      // Create response card with persona-specific data attribute for styling
      const card = document.createElement("div");
      card.className = "response";
      card.id = `response-${update.persona_id}`;
      card.dataset.persona = update.persona_id || "";
      const personaName = escapeHtml(update.persona_name || update.persona_id || "Unknown");
      const emoji = update.persona_emoji || "👤";
      card.innerHTML = `
        <div class="badge" data-persona="${escapeHtml(update.persona_id || "")}">${emoji} ${personaName}</div>
        <p class="streaming-content"></p>
      `;
      responsesEl.appendChild(card);

      // Update progress text
      const progressEl = document.getElementById("progress-text");
      if (progressEl) {
        progressEl.textContent = `${emoji} ${personaName} is responding...`;
      }

      // Track this response
      streamingState.activeResponses.set(update.persona_id, {
        card: card,
        content: "",
        contentEl: card.querySelector(".streaming-content"),
      });
      break;

    case "response_chunk":
      const responseState = streamingState.activeResponses.get(update.persona_id);
      if (responseState) {
        responseState.content += update.content;
        // textContent automatically treats content as text (no HTML), so don't escape
        responseState.contentEl.textContent = responseState.content;
        // Auto-scroll to latest response
        responseState.card.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
      break;

    case "response_complete":
      const completeState = streamingState.activeResponses.get(update.persona_id);
      if (completeState) {
        const response = update.response;
        if (response.error) {
          completeState.contentEl.innerHTML += `<div class="error">Error: ${escapeHtml(response.error)}</div>`;
        }
        streamingState.activeResponses.delete(update.persona_id);
      }
      break;

    case "synthesis_start":
      synthesisEl.innerHTML = '<div class="synthesis"><h3>Synthesis</h3><p class="streaming-synthesis"></p></div>';
      streamingState.synthesisContent = "";
      break;

    case "synthesis_chunk":
      streamingState.synthesisContent += update.content;
      const synthesisP = synthesisEl.querySelector(".streaming-synthesis");
      if (synthesisP) {
        // textContent automatically treats content as text (no HTML), so don't escape
        synthesisP.textContent = streamingState.synthesisContent;
      }
      break;

    case "synthesis_complete":
      const synthesisPComplete = synthesisEl.querySelector(".streaming-synthesis");
      if (synthesisPComplete) {
        // textContent automatically treats content as text (no HTML), so don't escape
        synthesisPComplete.textContent = update.synthesis || streamingState.synthesisContent;
      }
      streamingState.synthesisContent = "";
      break;

    case "complete":
      statusEl.textContent = `Mode: ${update.result.mode}`;
      statusEl.className = "muted";
      // Final result is already rendered via streaming
      // Scroll to results on mobile
      if (window.innerWidth <= 768) {
        setTimeout(() => {
          document.querySelector('#status').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
      }
      break;

    case "error":
      // textContent doesn't need escaping, but innerHTML does
      statusEl.textContent = `Error: ${update.error || "Unknown error"}`;
      statusEl.className = "error";
      synthesisEl.innerHTML = `<div class="error">${escapeHtml(update.error || "Unknown error")}</div>`;
      break;
  }
}

/**
 * Render structured synthesis with action items, recommendations, pros/cons
 */
function renderStructuredSynthesis(structured) {
  let html = '<div class="synthesis"><h3>Synthesis</h3>';

  if (structured.key_points_of_agreement && structured.key_points_of_agreement.length > 0) {
    html += '<section class="structured-section"><h4>Key Points of Agreement</h4><ul>';
    structured.key_points_of_agreement.forEach(point => {
      html += `<li>${escapeHtml(point)}</li>`;
    });
    html += '</ul></section>';
  }

  if (structured.key_points_of_tension && structured.key_points_of_tension.length > 0) {
    html += '<section class="structured-section"><h4>Key Points of Tension</h4><ul>';
    structured.key_points_of_tension.forEach(point => {
      html += `<li>${escapeHtml(point)}</li>`;
    });
    html += '</ul></section>';
  }

  if (structured.synthesized_recommendation) {
    html += `<section class="structured-section"><h4>Synthesized Recommendation</h4><p>${escapeHtml(structured.synthesized_recommendation)}</p></section>`;
  }

  if (structured.action_items && structured.action_items.length > 0) {
    html += '<section class="structured-section"><h4>Action Items</h4><ul class="action-items">';
    structured.action_items.forEach(item => {
      const priority = item.priority || 'medium';
      const priorityClass = priority.toLowerCase();
      const owner = item.owner ? ` <span class="muted">(${escapeHtml(item.owner)})</span>` : '';
      const due = item.due_date ? ` <span class="muted">- Due: ${escapeHtml(item.due_date)}</span>` : '';
      html += `<li class="action-item priority-${priorityClass}">${escapeHtml(item.description)}${owner}${due}</li>`;
    });
    html += '</ul></section>';
  }

  if (structured.recommendations && structured.recommendations.length > 0) {
    html += '<section class="structured-section"><h4>Recommendations</h4>';
    structured.recommendations.forEach(rec => {
      const confidence = rec.confidence || 'medium';
      const confClass = confidence.toLowerCase();
      html += `<div class="recommendation confidence-${confClass}">`;
      html += `<h5>${escapeHtml(rec.title)}</h5>`;
      html += `<p class="confidence">Confidence: ${escapeHtml(confidence)}</p>`;
      html += `<p>${escapeHtml(rec.description)}</p>`;
      if (rec.rationale) {
        html += `<p class="rationale"><em>Rationale: ${escapeHtml(rec.rationale)}</em></p>`;
      }
      html += '</div>';
    });
    html += '</section>';
  }

  if (structured.pros_cons) {
    html += '<section class="structured-section"><h4>Pros and Cons</h4>';
    if (structured.pros_cons.pros && structured.pros_cons.pros.length > 0) {
      html += '<div class="pros-cons"><div class="pros"><h5>Pros</h5><ul>';
      structured.pros_cons.pros.forEach(pro => {
        html += `<li>${escapeHtml(pro)}</li>`;
      });
      html += '</ul></div>';
    }
    if (structured.pros_cons.cons && structured.pros_cons.cons.length > 0) {
      html += '<div class="cons"><h5>Cons</h5><ul>';
      structured.pros_cons.cons.forEach(con => {
        html += `<li>${escapeHtml(con)}</li>`;
      });
      html += '</ul></div>';
    }
    if (structured.pros_cons.net_assessment) {
      html += `<p class="net-assessment"><strong>Net Assessment:</strong> ${escapeHtml(structured.pros_cons.net_assessment)}</p>`;
    }
    html += '</div></section>';
  }

  html += '</div>';
  return html;
}

/**
 * Render consultation results (non-streaming)
 */
export function renderResult(result, statusEl, synthesisEl, responsesEl) {
  statusEl.textContent = `Mode: ${result.mode}`;
  statusEl.className = "muted";

  // Render structured synthesis if available, otherwise use free-form
  if (result.structured_synthesis) {
    synthesisEl.innerHTML = renderStructuredSynthesis(result.structured_synthesis);
  } else if (result.synthesis) {
    synthesisEl.innerHTML = `<div class="synthesis"><h3>Synthesis</h3><p>${escapeHtml(result.synthesis)}</p></div>`;
  } else {
    synthesisEl.innerHTML = "";
  }

  responsesEl.innerHTML = "";

  if (result.responses && result.responses.length > 0) {
    result.responses.forEach(r => {
      const card = document.createElement("div");
      card.className = "response";
      // Add persona data attribute for styling
      const personaId = r.persona_id || "";
      card.dataset.persona = personaId;
      // Escape once for innerHTML - don't double-escape
      const personaName = escapeHtml(r.persona_name || r.persona_id || "Unknown");
      const emoji = r.persona_emoji || "👤";
      const content = r.content ? escapeHtml(r.content) : "";
      const error = r.error ? escapeHtml(r.error) : "";
      card.innerHTML = `
        <div class="badge" data-persona="${escapeHtml(personaId)}">${emoji} ${personaName}</div>
        ${content ? `<p>${content}</p>` : ""}
        ${error ? `<div class="error">Error: ${error}</div>` : ""}
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
