/**
 * HistoryPanel Component - Consultation history display
 */
import React, { useState, useEffect, useCallback } from 'react';
import { loadHistory } from '../../utils/api';
import type { HistoryEntry, ConsultationResult } from '../../types';
import { truncate } from '../../utils/helpers';
import HistorySearch from './HistorySearch';
import HistoryFilters from './HistoryFilters';
import HistoryItem from './HistoryItem';
import Modal from '../Layout/Modal';
import ComparisonView from '../Results/ComparisonView';
import { useNotifications } from '../Layout/NotificationContainer';

interface CompareSelection {
  entry: HistoryEntry;
  result: ConsultationResult;
}

const HistoryPanel: React.FC = () => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewingResult, setViewingResult] = useState<ConsultationResult | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<HistoryEntry[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [filters, setFilters] = useState<{
    dateFrom?: string;
    dateTo?: string;
    domain?: string;
    mode?: string;
  }>({});
  const [displayLimit, setDisplayLimit] = useState(20);
  const [hasMore, setHasMore] = useState(false);
  const [compareLeft, setCompareLeft] = useState<CompareSelection | null>(null);
  const [compareRight, setCompareRight] = useState<CompareSelection | null>(null);
  const { showNotification } = useNotifications();

  const fetchHistory = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await loadHistory(displayLimit, filters);
      setHistory(data);
      setHasMore(data.length >= displayLimit);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setIsLoading(false);
    }
  }, [filters, displayLimit]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const displayHistory = searchQuery ? searchResults : history;

  // Reset to default history when search query is cleared
  useEffect(() => {
    if (!searchQuery) {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const handleLoadMore = () => {
    setDisplayLimit((prev) => prev + 20);
  };

  const handleCompareSelection = (entry: HistoryEntry, result: ConsultationResult) => {
    setViewingResult(null);
    if (compareLeft?.entry.id === entry.id) {
      setCompareLeft(null);
      return;
    }
    if (compareRight?.entry.id === entry.id) {
      setCompareRight(null);
      return;
    }

    if (!compareLeft) {
      setCompareLeft({ entry, result });
      showNotification('Added to comparison A', 'info');
      return;
    }
    if (!compareRight) {
      setCompareRight({ entry, result });
      showNotification('Added to comparison B', 'info');
      return;
    }

    setCompareLeft(compareRight);
    setCompareRight({ entry, result });
    showNotification('Replaced comparison A', 'info');
  };

  const clearComparison = () => {
    setCompareLeft(null);
    setCompareRight(null);
  };

  const swapComparison = () => {
    setCompareLeft(compareRight);
    setCompareRight(compareLeft);
  };

  const comparisonReady = compareLeft && compareRight;

  return (
    <section className="panel" id="history-section">
      <h2>Recent Consultations</h2>

      <div className="history-search-wrapper">
        <HistorySearch
          onResultsChange={setSearchResults}
          onSearchingChange={setIsSearching}
          onQueryChange={setSearchQuery}
          onError={(message) => showNotification(`History search failed: ${message}`, 'error')}
        />
      </div>

      <HistoryFilters onFilterChange={setFilters} />

      {(compareLeft || compareRight) && (
        <div className="history-compare-bar">
          <div className="history-compare-slots">
            <div
              className={`history-compare-slot ${compareLeft ? 'history-compare-slot--active' : ''}`}
            >
              <span className="history-compare-label">A</span>
              <span className="history-compare-text">
                {compareLeft ? truncate(compareLeft.entry.query, 40) : 'Select a consultation'}
              </span>
            </div>
            <div
              className={`history-compare-slot ${compareRight ? 'history-compare-slot--active' : ''}`}
            >
              <span className="history-compare-label">B</span>
              <span className="history-compare-text">
                {compareRight ? truncate(compareRight.entry.query, 40) : 'Select a consultation'}
              </span>
            </div>
          </div>
          <div className="history-compare-actions">
            <button type="button" className="btn btn-secondary btn-sm" onClick={clearComparison}>
              Clear
            </button>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="empty-state">
          <span className="loading"></span> Loading history...
        </div>
      )}

      {error && (
        <div className="empty-state">
          <p className="error">{error}</p>
        </div>
      )}

      {!isLoading && !error && displayHistory.length === 0 && (
        <div className="empty-state">
          <p>
            {searchQuery
              ? isSearching
                ? 'Searching history...'
                : 'No matching results found'
              : 'No recent consultations'}
          </p>
          {!searchQuery && <p className="hint">Your consultation history will appear here.</p>}
          {searchQuery && !isSearching && (
            <button
              type="button"
              className="btn-secondary empty-state-clear-btn"
              onClick={() => setSearchQuery('')}
            >
              Clear search
            </button>
          )}
        </div>
      )}

      {!isLoading && !error && displayHistory.length > 0 && (
        <>
          <div
            id="history-list"
            className={`history-list ${isSearching ? 'history-list--searching' : ''}`}
          >
            {displayHistory.map((entry) => (
              <HistoryItem
                key={entry.id}
                entry={entry}
                onDeleted={fetchHistory}
                onView={setViewingResult}
                onCompare={handleCompareSelection}
              />
            ))}
          </div>

          {!searchQuery && hasMore && (
            <div className="history-load-more">
              <button type="button" className="btn btn-secondary" onClick={handleLoadMore}>
                Load More Consultations
              </button>
            </div>
          )}
        </>
      )}

      <Modal
        isOpen={!!viewingResult}
        onClose={() => setViewingResult(null)}
        title="Consultation Details"
      >
        {viewingResult && (
          <>
            <div className="detail-section">
              <span className="detail-label">Query:</span>
              <div className="detail-content">{viewingResult.query}</div>
            </div>
            {viewingResult.context && (
              <div className="detail-section">
                <span className="detail-label">Context:</span>
                <div className="detail-content">{viewingResult.context}</div>
              </div>
            )}
            <div className="detail-section">
              <span className="detail-label">Responses ({viewingResult.responses.length}):</span>
              <div className="detail-content detail-content--scrollable">
                {viewingResult.responses.map((response, i) => (
                  <div
                    key={`${response.persona_name}-${i}-${response.content.substring(0, 20)}`}
                    className="response-item"
                  >
                    <div className="response-item-header">
                      {response.persona_emoji} {response.persona_name} ({response.persona_title})
                    </div>
                    <div className="response-item-content">{response.content}</div>
                  </div>
                ))}
              </div>
            </div>
            {viewingResult.synthesis && (
              <div className="detail-section">
                <span className="detail-label">Synthesis:</span>
                <div className="detail-content detail-content--highlight">
                  {viewingResult.synthesis}
                </div>
              </div>
            )}
          </>
        )}
      </Modal>

      <Modal isOpen={!!comparisonReady} onClose={clearComparison} title="Consultation Comparison">
        {comparisonReady && (
          <ComparisonView
            leftResult={compareLeft.result}
            rightResult={compareRight.result}
            leftLabel={truncate(compareLeft.entry.query, 40)}
            rightLabel={truncate(compareRight.entry.query, 40)}
            onSwap={swapComparison}
          />
        )}
      </Modal>
    </section>
  );
};

export default HistoryPanel;
