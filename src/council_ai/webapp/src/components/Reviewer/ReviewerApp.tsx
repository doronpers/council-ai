/**
 * ReviewerApp Component - React implementation of reviewer UI
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Header from '../Layout/Header';
import Modal from '../Layout/Modal';
import { useNotifications } from '../Layout/NotificationContainer';
import type {
  ReviewerJusticeInfo,
  ReviewerRequest,
  ReviewerResponseInput,
  ReviewerResult,
} from '../../types/reviewer';
import { importGoogleDocs, loadReviewerInfo, streamReview } from '../../utils/reviewerApi';

const DEFAULT_RESPONSES: ReviewerResponseInput[] = [
  { id: 1, content: '', source: '' },
  { id: 2, content: '', source: '' },
];

const ReviewerApp: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [responses, setResponses] = useState<ReviewerResponseInput[]>(DEFAULT_RESPONSES);
  const [availableJustices, setAvailableJustices] = useState<ReviewerJusticeInfo[]>([]);
  const [sonotheiaExperts, setSonotheiaExperts] = useState<string[]>([]);
  const [selectedJustices, setSelectedJustices] = useState<string[]>([]);
  const [chair, setChair] = useState('');
  const [viceChair, setViceChair] = useState('');
  const [includeSonotheia, setIncludeSonotheia] = useState(false);
  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2000);

  const [isReviewing, setIsReviewing] = useState(false);
  const [progressStep, setProgressStep] = useState('assembling');
  const [result, setResult] = useState<ReviewerResult | null>(null);
  const [activeTab, setActiveTab] = useState<'summary' | 'assessments' | 'opinions' | 'synthesis'>(
    'summary'
  );
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const [showImportModal, setShowImportModal] = useState(false);
  const [importUrl, setImportUrl] = useState('');
  const [importContent, setImportContent] = useState('');
  const [isImporting, setIsImporting] = useState(false);

  const { showNotification } = useNotifications();

  useEffect(() => {
    const loadInfo = async () => {
      try {
        const info = await loadReviewerInfo();
        setAvailableJustices(info.available_justices);
        // defaultJustices not used in UI
        setSonotheiaExperts(info.sonotheia_experts);
        setSelectedJustices(info.default_justices);
        setChair(info.default_chair);
        setViceChair(info.default_vice_chair);
      } catch (err) {
        showNotification('Failed to load reviewer info. Using defaults.', 'error');
        const fallback = [
          {
            id: 'dempsey',
            name: 'Martin Dempsey',
            title: 'Mission clarity',
            emoji: '🎖️',
            core_question: '',
          },
          {
            id: 'kahneman',
            name: 'Daniel Kahneman',
            title: 'Bias analysis',
            emoji: '🧠',
            core_question: '',
          },
          {
            id: 'rams',
            name: 'Dieter Rams',
            title: 'Design clarity',
            emoji: '🎨',
            core_question: '',
          },
          {
            id: 'treasure',
            name: 'Julian Treasure',
            title: 'Communication',
            emoji: '🔊',
            core_question: '',
          },
          {
            id: 'holman',
            name: 'Pablos Holman',
            title: 'Security',
            emoji: '🔓',
            core_question: '',
          },
          { id: 'taleb', name: 'Nassim Taleb', title: 'Risk', emoji: '🦢', core_question: '' },
          { id: 'grove', name: 'Andy Grove', title: 'Strategy', emoji: '🎯', core_question: '' },
        ];
        setAvailableJustices(fallback);
        setSelectedJustices(fallback.map((j) => j.id));
        setChair('dempsey');
        setViceChair('kahneman');
      }
    };
    loadInfo();
  }, [showNotification]);

  const handleToggleJustice = useCallback(
    (justiceId: string) => {
      setSelectedJustices((prev) => {
        const isSelected = prev.includes(justiceId);
        if (isSelected) {
          const next = prev.filter((id) => id !== justiceId);
          if (chair === justiceId) setChair(next[0] || '');
          if (viceChair === justiceId) setViceChair(next[0] || '');
          return next;
        }
        return [...prev, justiceId];
      });
    },
    [chair, viceChair]
  );

  const handleToggleSonotheia = () => {
    setIncludeSonotheia((prev) => !prev);
    setSelectedJustices((prev) => {
      if (!includeSonotheia) {
        const next = [...prev, ...sonotheiaExperts];
        return Array.from(new Set(next));
      }
      return prev.filter((id) => !sonotheiaExperts.includes(id));
    });
  };

  const handleAddResponse = () => {
    if (responses.length >= 5) return;
    const nextId = responses.length + 1;
    setResponses((prev) => [...prev, { id: nextId, content: '', source: '' }]);
  };

  const handleRemoveResponse = (id: number) => {
    if (responses.length <= 2) return;
    const updated = responses
      .filter((r) => r.id !== id)
      .map((r, index) => ({
        ...r,
        id: index + 1,
      }));
    setResponses(updated);
  };

  const handleResponseChange = (id: number, field: 'content' | 'source', value: string) => {
    setResponses((prev) => prev.map((r) => (r.id === id ? { ...r, [field]: value } : r)));
  };

  const validateReview = () => {
    if (!question.trim()) {
      showNotification('Please enter the original question.', 'error');
      return false;
    }
    const filledResponses = responses.filter((r) => r.content.trim().length > 0);
    if (filledResponses.length < 2) {
      showNotification('Please provide at least 2 responses.', 'error');
      return false;
    }
    if (selectedJustices.length < 3) {
      showNotification('Please select at least 3 justices.', 'error');
      return false;
    }
    return true;
  };

  const handleStartReview = async () => {
    if (!validateReview()) return;
    setError(null);
    setResult(null);
    setIsReviewing(true);
    setProgressStep('assembling');
    setActiveTab('summary');

    const request: ReviewerRequest = {
      question: question.trim(),
      responses: responses
        .filter((r) => r.content.trim().length > 0)
        .map((r, idx) => ({ id: idx + 1, content: r.content.trim(), source: r.source || null })),
      justices: selectedJustices,
      chair: chair || 'dempsey',
      vice_chair: viceChair || 'kahneman',
      include_sonotheia_experts: includeSonotheia,
      provider: provider || null,
      model: model || null,
      base_url: baseUrl || null,
      api_key: apiKey || null,
      temperature,
      max_tokens: maxTokens,
    };

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      await streamReview(
        request,
        (event) => {
          if (event.type === 'council_assembled') {
            setProgressStep('reviewing');
          } else if (event.type === 'phase') {
            if (event.phase === 'individual_review') setProgressStep('reviewing');
            if (event.phase === 'synthesis') setProgressStep('synthesizing');
          } else if (event.type === 'justice_complete') {
            setProgressStep('deliberating');
          } else if (event.type === 'complete' && event.result) {
            setResult(event.result);
          } else if (event.type === 'error') {
            setError(event.error || 'Review failed');
          }
        },
        controller.signal
      );
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        showNotification('Review cancelled.', 'info');
      } else {
        setError(err instanceof Error ? err.message : 'Review failed');
      }
    } finally {
      setIsReviewing(false);
      abortControllerRef.current = null;
    }
  };

  const handleCancelReview = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const handleImport = async () => {
    if (!importUrl.trim() && !importContent.trim()) {
      showNotification('Provide a Google Docs URL or exported content.', 'error');
      return;
    }
    setIsImporting(true);
    try {
      const data = await importGoogleDocs({
        url: importUrl.trim() || null,
        content: importContent.trim() || null,
      });
      if (!data.success) {
        showNotification(data.message || 'Import failed', 'error');
        return;
      }
      setQuestion(data.question || '');
      setResponses(
        data.responses.map((resp, idx) => ({
          id: idx + 1,
          content: resp.content || '',
          source: resp.source || '',
        }))
      );
      setShowImportModal(false);
      showNotification(data.message || 'Import successful', 'success');
    } catch (err) {
      showNotification(err instanceof Error ? err.message : 'Import failed', 'error');
    } finally {
      setIsImporting(false);
    }
  };

  const shouldShowResults = isReviewing || result || error;
  const progressSteps = ['assembling', 'reviewing', 'deliberating', 'synthesizing'];
  const progressIndex = progressSteps.indexOf(progressStep);

  const summaryRanking = useMemo(() => {
    if (!result) return [];
    return result.group_decision.ranking.map((id, idx) => {
      const assessment = result.individual_assessments.find((a) => a.response_id === id);
      return { id, idx, score: assessment?.overall_score || 0 };
    });
  }, [result]);

  return (
    <div className="reviewer-app">
      <Header />
      <div className="container">
        <div className="main-grid">
          <div className="panel">
            <h2>📝 Input</h2>
            <div className="reviewer-input-header">
              <label htmlFor="reviewer-question">Original Question</label>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowImportModal(true)}
              >
                📄 Import from Google Docs
              </button>
            </div>
            <textarea
              id="reviewer-question"
              placeholder="Enter the question that was asked to the LLMs..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />

            <div id="responses-container">
              <label>LLM Responses to Review (2-5)</label>
              {responses.map((response) => (
                <div key={response.id} className="response-card">
                  <div className="response-card-header">
                    <span className="response-number">Response #{response.id}</span>
                    <div className="response-card-actions">
                      <input
                        type="text"
                        placeholder="Source (e.g., GPT-4, Claude)"
                        className="response-source"
                        value={response.source || ''}
                        onChange={(e) =>
                          handleResponseChange(response.id, 'source', e.target.value)
                        }
                      />
                      <button
                        type="button"
                        className="remove-response"
                        onClick={() => handleRemoveResponse(response.id)}
                        disabled={responses.length <= 2}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                  <textarea
                    className="response-textarea response-content"
                    placeholder="Paste the LLM response here..."
                    value={response.content}
                    onChange={(e) => handleResponseChange(response.id, 'content', e.target.value)}
                  />
                </div>
              ))}
            </div>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleAddResponse}
              disabled={responses.length >= 5}
            >
              + Add Response
            </button>

            <div className="button-group">
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleStartReview}
                disabled={isReviewing}
              >
                ⚖️ Begin Review
              </button>
              <button
                type="button"
                className={`btn btn-secondary ${isReviewing ? '' : 'hidden'}`}
                onClick={handleCancelReview}
              >
                Cancel
              </button>
            </div>
          </div>

          <div className="panel">
            <h2>⚙️ Council Configuration</h2>
            <div className="justice-grid">
              {availableJustices.map((justice) => {
                const isSelected = selectedJustices.includes(justice.id);
                const isChair = chair === justice.id;
                const isVice = viceChair === justice.id;
                return (
                  <button
                    type="button"
                    key={justice.id}
                    className={`justice-chip ${isSelected ? 'selected' : ''} ${isChair ? 'chair' : ''} ${isVice ? 'vice-chair' : ''}`}
                    onClick={() => handleToggleJustice(justice.id)}
                  >
                    <span className="justice-emoji">{justice.emoji}</span>
                    <span>{justice.name.split(' ')[0]}</span>
                    {justice.is_sonotheia_expert && <span>📡</span>}
                  </button>
                );
              })}
            </div>
            <p className="help-text">
              Select at least 3 justices. Use the selectors below to assign chair roles.
            </p>

            <div className="settings-grid">
              <div>
                <label htmlFor="reviewer-chair">Chair (Chief Justice)</label>
                <select
                  id="reviewer-chair"
                  value={chair}
                  onChange={(e) => setChair(e.target.value)}
                >
                  <option value="">Select Chair...</option>
                  {selectedJustices.map((id) => {
                    const justice = availableJustices.find((j) => j.id === id);
                    return (
                      <option key={id} value={id}>
                        {justice?.emoji || ''} {justice?.name || id}
                      </option>
                    );
                  })}
                </select>
              </div>
              <div>
                <label htmlFor="reviewer-vice">Vice Chair</label>
                <select
                  id="reviewer-vice"
                  value={viceChair}
                  onChange={(e) => setViceChair(e.target.value)}
                >
                  <option value="">Select Vice Chair...</option>
                  {selectedJustices.map((id) => {
                    const justice = availableJustices.find((j) => j.id === id);
                    return (
                      <option key={id} value={id}>
                        {justice?.emoji || ''} {justice?.name || id}
                      </option>
                    );
                  })}
                </select>
              </div>
            </div>

            <label className="justice-chip">
              <input type="checkbox" checked={includeSonotheia} onChange={handleToggleSonotheia} />
              <span>Include Sonotheia Experts (📡 + ⚖️)</span>
            </label>

            <details>
              <summary>🔧 Advanced Settings</summary>
              <div className="settings-content">
                <div className="settings-grid">
                  <div>
                    <label htmlFor="reviewer-provider">AI Provider</label>
                    <select
                      id="reviewer-provider"
                      value={provider}
                      onChange={(e) => setProvider(e.target.value)}
                    >
                      <option value="">Default (from config)</option>
                      <option value="anthropic">Anthropic (Claude)</option>
                      <option value="openai">OpenAI (GPT)</option>
                      <option value="gemini">Google (Gemini)</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="reviewer-model">Model</label>
                    <input
                      id="reviewer-model"
                      placeholder="Default model"
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                    />
                  </div>
                  <div>
                    <label htmlFor="reviewer-temp">Temperature</label>
                    <input
                      type="number"
                      id="reviewer-temp"
                      value={temperature}
                      min={0}
                      max={2}
                      step={0.1}
                      onChange={(e) => setTemperature(Number(e.target.value))}
                    />
                  </div>
                  <div>
                    <label htmlFor="reviewer-max">Max Tokens</label>
                    <input
                      type="number"
                      id="reviewer-max"
                      value={maxTokens}
                      min={100}
                      max={8000}
                      onChange={(e) => setMaxTokens(Number(e.target.value))}
                    />
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <label htmlFor="reviewer-api-key">API Key (optional)</label>
                    <input
                      type="password"
                      id="reviewer-api-key"
                      placeholder="Uses environment variable if empty"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                    />
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <label htmlFor="reviewer-base-url">Custom Base URL (optional)</label>
                    <input
                      id="reviewer-base-url"
                      placeholder="e.g., https://gateway.ai.vercel.app/v1"
                      value={baseUrl}
                      onChange={(e) => setBaseUrl(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </details>
          </div>

          {shouldShowResults && (
            <div className="panel results-panel">
              <h2>📊 Review Results</h2>

              {isReviewing && (
                <div className="loading">
                  <div className="spinner"></div>
                  <p>The council is deliberating...</p>
                  <div className="progress-steps">
                    {progressSteps.map((step, index) => (
                      <span
                        key={step}
                        className={`progress-step ${progressStep === step ? 'active' : ''} ${index < progressIndex ? 'complete' : ''}`}
                      >
                        {step === 'assembling' && '🏛️ Assembling Court'}
                        {step === 'reviewing' && '📖 Reviewing Responses'}
                        {step === 'deliberating' && '⚖️ Deliberating'}
                        {step === 'synthesizing' && '✨ Synthesizing'}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {error && <div className="status status-error">{error}</div>}

              {result && !isReviewing && (
                <div>
                  {result.warnings.length > 0 && (
                    <div className="status status-info">{result.warnings.join(' ')}</div>
                  )}
                  <div className="results-tabs">
                    {(['summary', 'assessments', 'opinions', 'synthesis'] as const).map((tab) => (
                      <button
                        key={tab}
                        type="button"
                        className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab)}
                      >
                        {tab === 'summary' && 'Summary'}
                        {tab === 'assessments' && 'Individual Assessments'}
                        {tab === 'opinions' && 'Justice Opinions'}
                        {tab === 'synthesis' && 'Synthesized Response'}
                      </button>
                    ))}
                  </div>

                  {activeTab === 'summary' && (
                    <div className="tab-content active">
                      <div className="score-card">
                        <div className="score-header">
                          <div>
                            <h3>🏆 Council Decision</h3>
                            <p>
                              {result.responses_reviewed} responses reviewed by{' '}
                              {result.council_composition.total_justices} justices
                            </p>
                          </div>
                          <div>
                            <div className="winner-badge">
                              Winner: Response #{result.group_decision.winner}
                            </div>
                            <div className="score-badge">
                              {result.group_decision.winner_score.toFixed(1)}/10
                            </div>
                          </div>
                        </div>
                        <h4>📊 Rankings</h4>
                        {summaryRanking.map((item) => (
                          <div key={item.id} className="score-label">
                            <span>#{item.idx + 1}</span>
                            <span>Response #{item.id}</span>
                            <span>{item.score.toFixed(1)}</span>
                          </div>
                        ))}
                        <h4>📜 Majority Opinion</h4>
                        <p>{result.group_decision.majority_opinion}</p>
                        {result.group_decision.dissenting_opinions.length > 0 && (
                          <>
                            <h4>⚠️ Dissenting Opinions</h4>
                            {result.group_decision.dissenting_opinions.map((dissent, idx) => (
                              <p key={`dissent-${idx}`}>&quot;{dissent}&quot;</p>
                            ))}
                          </>
                        )}
                      </div>
                    </div>
                  )}

                  {activeTab === 'assessments' && (
                    <div className="tab-content active">
                      {result.individual_assessments.map((assessment) => (
                        <div key={`assessment-${assessment.response_id}`} className="score-card">
                          <div className="score-header">
                            <h3>
                              Response #{assessment.response_id}{' '}
                              {assessment.source ? `(${assessment.source})` : ''}
                            </h3>
                            <div className="score-badge">
                              {assessment.overall_score.toFixed(1)}/10
                            </div>
                          </div>
                          {Object.entries(assessment.scores).map(([criterion, score]) => (
                            <div key={`${assessment.response_id}-${criterion}`}>
                              <div className="score-label">
                                <span>{(criterion || '').replace(/_/g, ' ')}</span>
                                <span>{score.toFixed(1)}/10</span>
                              </div>
                              <div className="score-bar">
                                <div className="score-fill" style={{ width: `${score * 10}%` }} />
                              </div>
                            </div>
                          ))}
                          {assessment.strengths.length > 0 && (
                            <>
                              <h4>💪 Strengths</h4>
                              <ul>
                                {assessment.strengths.map((strength, idx) => (
                                  <li key={`strength-${idx}`}>{strength}</li>
                                ))}
                              </ul>
                            </>
                          )}
                          {assessment.weaknesses.length > 0 && (
                            <>
                              <h4>⚠️ Weaknesses</h4>
                              <ul>
                                {assessment.weaknesses.map((weakness, idx) => (
                                  <li key={`weakness-${idx}`}>{weakness}</li>
                                ))}
                              </ul>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {activeTab === 'opinions' && (
                    <div className="tab-content active">
                      {result.individual_assessments[0]?.justice_opinions.map((opinion) => {
                        const voteClass =
                          opinion.vote === 'approve'
                            ? 'vote-approve'
                            : opinion.vote === 'dissent'
                              ? 'vote-dissent'
                              : 'vote-reservations';
                        return (
                          <div key={opinion.justice_id} className="opinion-card">
                            <div className="opinion-header">
                              <span>{opinion.justice_emoji}</span>
                              <strong>{opinion.justice_name}</strong>
                              {opinion.role !== 'associate' && (
                                <span className="opinion-role">
                                  {opinion.role === 'chair' ? 'Chair' : 'Vice Chair'}
                                </span>
                              )}
                              <span className={voteClass} style={{ marginLeft: 'auto' }}>
                                {opinion.vote === 'approve'
                                  ? '✓ Approve'
                                  : opinion.vote === 'dissent'
                                    ? '✗ Dissent'
                                    : '~ With Reservations'}
                              </span>
                            </div>
                            <p>{opinion.opinion}</p>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {activeTab === 'synthesis' && (
                    <div className="tab-content active">
                      <div className="synthesis-box">
                        <h3>🔗 Combined Best Elements</h3>
                        <div className="synthesis-content">
                          {result.synthesized_response.combined_best}
                        </div>
                      </div>
                      <div className="synthesis-box">
                        <h3>✨ Refined Final Response</h3>
                        <div className="synthesis-content">
                          {result.synthesized_response.refined_final}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <Modal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        title="Import from Google Docs"
      >
        <div className="import-modal">
          <label htmlFor="docs-url">Google Docs URL</label>
          <input
            id="docs-url"
            placeholder="https://docs.google.com/document/..."
            value={importUrl}
            onChange={(e) => setImportUrl(e.target.value)}
          />
          <label htmlFor="docs-content">Or paste exported content</label>
          <textarea
            id="docs-content"
            placeholder="Paste exported text or HTML..."
            value={importContent}
            onChange={(e) => setImportContent(e.target.value)}
          />
          <div className="button-group">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowImportModal(false)}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleImport}
              disabled={isImporting}
            >
              {isImporting ? 'Importing...' : 'Import'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ReviewerApp;
