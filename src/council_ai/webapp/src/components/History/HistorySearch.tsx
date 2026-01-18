import React, { useState, useEffect, useCallback, useRef } from 'react';
import type { HistoryEntry } from '../../types';
import { loadHistorySearch } from '../../utils/api';

interface HistorySearchProps {
  onResultsChange: (results: HistoryEntry[]) => void;
  onSearchingChange: (isSearching: boolean) => void;
  onQueryChange: (query: string) => void;
  onError?: (message: string) => void;
}

const HistorySearch: React.FC<HistorySearchProps> = ({
  onResultsChange,
  onSearchingChange,
  onQueryChange,
  onError,
}) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Memoize callbacks to avoid dependency issues
  const handleResultsChange = useCallback(
    (results: HistoryEntry[]) => {
      onResultsChange(results);
    },
    [onResultsChange]
  );

  const handleSearchingChange = useCallback(
    (searching: boolean) => {
      onSearchingChange(searching);
    },
    [onSearchingChange]
  );

  const handleError = useCallback(
    (message: string) => {
      if (onError) {
        onError(message);
      }
    },
    [onError]
  );

  useEffect(() => {
    const handleShortcut = (event: KeyboardEvent) => {
      const isModifierPressed = event.metaKey || event.ctrlKey;
      if (!isModifierPressed || event.key.toLowerCase() !== 'k') {
        return;
      }
      event.preventDefault();
      inputRef.current?.focus();
    };

    window.addEventListener('keydown', handleShortcut);
    return () => {
      window.removeEventListener('keydown', handleShortcut);
    };
  }, []);

  useEffect(() => {
    onQueryChange(query);

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(async () => {
      if (query.trim()) {
        setIsSearching(true);
        handleSearchingChange(true);
        try {
          const results = await loadHistorySearch(query);
          handleResultsChange(results);
        } catch (error) {
          console.error('Search failed:', error);
          const errorMessage = error instanceof Error ? error.message : 'Search failed';
          handleError(errorMessage);
          handleResultsChange([]);
        } finally {
          setIsSearching(false);
          handleSearchingChange(false);
        }
      } else {
        // Reset to default history when query is cleared
        handleResultsChange([]);
        setIsSearching(false);
        handleSearchingChange(false);
      }
    }, 300);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [query, handleError, handleResultsChange, handleSearchingChange, onQueryChange]);

  return (
    <div className="history-search">
      <input
        ref={inputRef}
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search history (Ctrl/Cmd+K)..."
        className="history-search-input"
        aria-keyshortcuts="Ctrl+K Meta+K"
      />
      {query && (
        <button
          type="button"
          onClick={() => {
            setQuery('');
            handleResultsChange([]);
          }}
          className="history-search-clear"
          aria-label="Clear search"
        >
          ✕
        </button>
      )}
      {isSearching && (
        <div className="history-search-spinner">
          <span className="loading"></span>
        </div>
      )}
    </div>
  );
};

export default HistorySearch;
