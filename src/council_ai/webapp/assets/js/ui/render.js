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

      // Update member status to responding
      if (update.persona_id && window.updateMemberStatus) {
        window.updateMemberStatus(update.persona_id, "responding");
      }

      // Get persona data for enhanced card
      const personaId = update.persona_id || "";
      const personaName = escapeHtml(update.persona_name || update.persona_id || "Unknown");
      const emoji = update.persona_emoji || "👤";

      // Try to get full persona data from window (set by main.js)
      const personaData = window.allPersonas?.find(p => p.id === personaId);
      const focusAreas = personaData?.focus_areas || [];
      const personaTitle = personaData?.title || "";
      const personaCategory = personaData?.category || "";

      // Create enhanced response card
      const card = document.createElement("div");
      card.className = "response response-card-enhanced";
      card.id = `response-${personaId}`;
      card.dataset.persona = personaId;

      const focusTags = focusAreas.slice(0, 3).map(area =>
        `<span class="response-focus-tag">${escapeHtml(area)}</span>`
      ).join('');

      card.innerHTML = `
        <div class="response-header">
          <div class="response-persona-info">
            <span class="response-emoji">${emoji}</span>
            <div class="response-persona-details">
              <div class="response-persona-name">${personaName}</div>
              ${personaTitle ? `<div class="response-persona-title">${escapeHtml(personaTitle)}</div>` : ''}
            </div>
          </div>
          <div class="response-actions">
            <button class="response-action-btn" onclick="copyResponse('${personaId}')" title="Copy response">📋</button>
            <button class="response-action-btn" onclick="toggleResponseDetails('${personaId}')" title="View details">ℹ️</button>
          </div>
        </div>
        ${focusTags ? `<div class="response-focus-areas">${focusTags}</div>` : ''}
        <div class="response-content-wrapper">
          <p class="streaming-content"></p>
        </div>
        <div class="response-details" id="response-details-${personaId}" style="display: none;">
          ${personaCategory ? `<div class="response-category"><strong>Category:</strong> ${escapeHtml(personaCategory)}</div>` : ''}
          ${focusAreas.length > 3 ? `<div class="response-all-focus"><strong>All Focus Areas:</strong> ${focusAreas.map(a => escapeHtml(a)).join(', ')}</div>` : ''}
        </div>
      `;
      responsesEl.appendChild(card);

      // Update progress text
      const progressEl = document.getElementById("progress-text");
      if (progressEl) {
        progressEl.textContent = `${emoji} ${personaName} is responding...`;
      }

      // Track this response - find content element in enhanced structure
      const contentEl = card.querySelector(".streaming-content");
      streamingState.activeResponses.set(update.persona_id, {
        card: card,
        content: "",
        contentEl: contentEl,
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
      // Update member status to completed
      if (update.persona_id && window.updateMemberStatus) {
        window.updateMemberStatus(update.persona_id, "completed");
      }

      const completeState = streamingState.activeResponses.get(update.persona_id);
      if (completeState) {
        const response = update.response;
        if (response.error) {
          // Smart Error UI
          completeState.card.classList.add("error-card");
          completeState.contentEl.innerHTML += `
            <div class="status-error" style="margin-top: 8px;">
              <strong>⚠️ Connection Failed</strong>
              <p>${escapeHtml(response.error)}</p>
              <button onclick="window.location.reload()" class="btn btn-secondary" style="margin-top: 8px; font-size: 0.8rem; padding: 4px 12px;">Retry Consultation</button>
            </div>`;
        }
        streamingState.activeResponses.delete(update.persona_id);
      }
      break;

    case "synthesis_start":
      synthesisEl.innerHTML = `
        <div class="synthesis">
          <h3>Synthesis</h3>

          <!-- Consensus Meter -->
          <div class="consensus-meter">
            <div class="consensus-title">
              <span>Council Consensus</span>
              <span id="consensus-value">0%</span>
            </div>
            <div class="consensus-track">
              <div class="consensus-bar" id="consensus-bar" style="width: 0%"></div>
            </div>
          </div>

          <p class="streaming-synthesis"></p>
        </div>
      `;
      streamingState.synthesisContent = "";
      break;

    case "synthesis_chunk":
      streamingState.synthesisContent += update.content;
      const synthesisP = synthesisEl.querySelector(".streaming-synthesis");
      if (synthesisP) {
        // Highlight key terms (simple regex replacement for visual distinctness)
        let formattedContent = escapeHtml(streamingState.synthesisContent)
          .replace(/(\*\*[^*]+\*\*)/g, '<strong>$1</strong>')
          .replace(/(consensus|agreement|unanimous)/gi, '<span class="highlight-agreement">$1</span>')
          .replace(/(disagreement|tension|conflict|dissent)/gi, '<span class="highlight-tension">$1</span>');

        synthesisP.innerHTML = formattedContent;

        // Update Consensus Meter
        updateConsensusMeter(streamingState.synthesisContent);
      }
      break;

    case "synthesis_complete":
      // Final pass to ensure meter is accurate
      updateConsensusMeter(streamingState.synthesisContent);
      streamingState.synthesisContent = "";
      break;

    case "analysis":
      // Render analysis panel at top of synthesis
      const analysisHtml = renderAnalysis(update.data);
      // Prepend
      synthesisEl.innerHTML = analysisHtml + synthesisEl.innerHTML;
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
      statusEl.textContent = `Error: ${update.error || "Unknown error"}`;
      statusEl.className = "error";
      synthesisEl.innerHTML = `<div class="error">${escapeHtml(update.error || "Unknown error")}</div>`;
      break;
  }
}

/**
 * Heuristic to update consensus meter based on text keywords
 */
function updateConsensusMeter(text) {
  const bar = document.getElementById("consensus-bar");
  const val = document.getElementById("consensus-value");
  if (!bar || !val) return;

  const content = text.toLowerCase();
  let score = 50; // Neutral default

  // Positive indicators
  if (content.includes("unanimous")) score = 100;
  else if (content.includes("strong consensus") || content.includes("strongly agree")) score = 90;
  else if (content.includes("general consensus") || content.includes("mostly agree")) score = 75;
  else if (content.includes("agreement")) score += 10;

  // Negative indicators
  if (content.includes("sharp disagreement") || content.includes("conflict")) score = 20;
  else if (content.includes("diverging") || content.includes("different perspectives")) score = 40;
  else if (content.includes("tension")) score -= 10;

  // Clamp
  score = Math.max(0, Math.min(100, score));

  bar.style.width = `${score}%`;
  val.textContent = `${score}%`;

  // Color shift
  if (score > 70) bar.style.background = "var(--accent-green)"; // High agreement
  else if (score < 40) bar.style.background = "var(--accent-red)"; // High conflict
  else bar.style.background = "linear-gradient(90deg, var(--accent-gold), #f4d03f)"; // Mixed
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
 * Render Analysis Result
 */
function renderAnalysis(analysis) {
  if (!analysis) return "";

  const score = analysis.consensus_score || 50;
  let scoreColor = "var(--accent-gold)";
  if (score >= 75) scoreColor = "var(--accent-green)";
  if (score <= 40) scoreColor = "var(--accent-red)";

  let html = '<div class="analysis-panel" style="background: var(--surface-2); padding: 16px; border-radius: 8px; margin-bottom: 24px; border: 1px solid var(--border);">';
  html += '<h3 style="margin-top:0;">🔍 Council Analysis</h3>';

  // Consensus Meter
  html += `
  <div class="consensus-meter" style="margin-bottom: 16px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
        <span style="font-weight: 500;">Consensus Score</span>
        <span style="font-weight: 700; color: ${scoreColor};">${score}/100</span>
    </div>
    <div style="width: 100%; height: 8px; background: var(--surface-1); border-radius: 4px; overflow: hidden;">
        <div style="width: ${score}%; height: 100%; background: ${scoreColor}; transition: width 0.5s;"></div>
    </div>
  </div>
  `;

  html += `<p><strong>Summary:</strong> ${escapeHtml(analysis.consensus_summary)}</p>`;

  if (analysis.key_themes && analysis.key_themes.length) {
    html += `<div style="margin-top: 12px;"><strong>Key Themes:</strong>`;
    html += `<ul style="margin-top: 4px; padding-left: 20px;">`;
    analysis.key_themes.forEach(t => html += `<li>${escapeHtml(t)}</li>`);
    html += `</ul></div>`;
  }

  if (analysis.tensions && analysis.tensions.length) {
    html += `<div style="margin-top: 12px; color: var(--accent-red);"><strong>⚠️ Points of Tension:</strong>`;
    html += `<ul style="margin-top: 4px; padding-left: 20px;">`;
    analysis.tensions.forEach(t => html += `<li>${escapeHtml(t)}</li>`);
    html += `</ul></div>`;
  }

  if (analysis.recommendation) {
    html += `<div style="margin-top: 12px; background: var(--surface-1); padding: 12px; border-left: 3px solid var(--accent-blue);"><strong>💡 Synthesized Recommendation:</strong><br>${escapeHtml(analysis.recommendation)}</div>`;
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

  // Render Analysis (Phase 2)
  if (result.analysis) {
    const analysisHtml = renderAnalysis(result.analysis);
    synthesisEl.innerHTML = analysisHtml + synthesisEl.innerHTML;
  }

  // Phase 3: Add "Review with Council" button
  if (result.responses && result.responses.length > 1) {
    const reviewBtn = document.createElement('button');
    reviewBtn.className = 'btn btn-secondary'; // Assuming CSS class exists
    reviewBtn.innerText = '⚖️ Judicial Review';
    reviewBtn.style.marginTop = '16px';
    reviewBtn.style.width = '100%';
    reviewBtn.onclick = async () => {
      reviewBtn.disabled = true;
      reviewBtn.innerText = 'Preparing Review...';
      try {
        // Extract data to stage
        const payload = {
          question: result.query,
          responses: result.responses.map(r => ({
            persona_name: r.persona_name || r.persona_id,
            content: r.content
          }))
        };

        const resp = await fetch('/api/reviewer/stage', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (resp.ok) {
          const data = await resp.json();
          window.location.href = `/reviewer?staging_id=${data.staging_id}`;
        } else {
          alert('Failed to stage review.');
          reviewBtn.disabled = false;
          reviewBtn.innerText = '⚖️ Judicial Review';
        }
      } catch (e) {
        console.error(e);
        alert('Error initiating review.');
        reviewBtn.disabled = false;
        reviewBtn.innerText = '⚖️ Judicial Review';
      }
    };
    // Append to synthesis element or status element?
    // Synthesis element is good place.
    if (synthesisEl) {
      synthesisEl.appendChild(reviewBtn);
    }
  }

  responsesEl.innerHTML = "";

  if (result.responses && result.responses.length > 0) {
    result.responses.forEach(r => {
      const personaId = r.persona_id || "";
      const personaName = escapeHtml(r.persona_name || r.persona_id || "Unknown");
      const emoji = r.persona_emoji || "👤";
      const content = r.content ? escapeHtml(r.content) : "";
      const error = r.error ? escapeHtml(r.error) : "";

      // Get persona data for enhanced card
      const personaData = window.allPersonas?.find(p => p.id === personaId);
      const focusAreas = personaData?.focus_areas || [];
      const personaTitle = personaData?.title || "";
      const personaCategory = personaData?.category || "";

      const card = document.createElement("div");
      card.className = "response response-card-enhanced";
      card.dataset.persona = personaId;

      const focusTags = focusAreas.slice(0, 3).map(area =>
        `<span class="response-focus-tag">${escapeHtml(area)}</span>`
      ).join('');

      card.innerHTML = `
        <div class="response-header">
          <div class="response-persona-info">
            <span class="response-emoji">${emoji}</span>
            <div class="response-persona-details">
              <div class="response-persona-name">${personaName}</div>
              ${personaTitle ? `<div class="response-persona-title">${escapeHtml(personaTitle)}</div>` : ''}
            </div>
          </div>
          <div class="response-actions">
            <button class="response-action-btn" onclick="copyResponse('${personaId}')" title="Copy response">📋</button>
            <button class="response-action-btn" onclick="toggleResponseDetails('${personaId}')" title="View details">ℹ️</button>
          </div>
        </div>
        ${focusTags ? `<div class="response-focus-areas">${focusTags}</div>` : ''}
        <div class="response-content-wrapper">
          ${content ? `<p>${content}</p>` : ""}
          ${error ? `<div class="error">Error: ${error}</div>` : ""}
        </div>
        <div class="response-details" id="response-details-${personaId}" style="display: none;">
          ${personaCategory ? `<div class="response-category"><strong>Category:</strong> ${escapeHtml(personaCategory)}</div>` : ''}
          ${focusAreas.length > 3 ? `<div class="response-all-focus"><strong>All Focus Areas:</strong> ${focusAreas.map(a => escapeHtml(a)).join(', ')}</div>` : ''}
        </div>
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
