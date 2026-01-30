import React, { useId, useState } from 'react';

interface HistoryFiltersProps {
  onFilterChange: (filters: {
    dateFrom?: string;
    dateTo?: string;
    domain?: string;
    mode?: string;
  }) => void;
}

const HistoryFilters: React.FC<HistoryFiltersProps> = ({ onFilterChange }) => {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [domain, setDomain] = useState('');
  const [mode, setMode] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [dateError, setDateError] = useState<string | null>(null);
  const contentId = useId();

  const validateDates = (): boolean => {
    if (dateFrom && dateTo && dateFrom > dateTo) {
      setDateError('Start date must be before end date');
      return false;
    }
    setDateError(null);
    return true;
  };

  const handleApply = () => {
    if (!validateDates()) {
      return;
    }
    onFilterChange({
      dateFrom: dateFrom || undefined,
      dateTo: dateTo || undefined,
      domain: domain.trim() || undefined,
      mode: mode || undefined,
    });
  };

  const handleClear = () => {
    setDateFrom('');
    setDateTo('');
    setDomain('');
    setMode('');
    setDateError(null);
    onFilterChange({});
  };

  const handleDateFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDateFrom(e.target.value);
    if (dateError) {
      validateDates();
    }
  };

  const handleDateToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDateTo(e.target.value);
    if (dateError) {
      validateDates();
    }
  };

  return (
    <div className="history-filters">
      <button
        type="button"
        className="history-filters-header"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls={contentId}
      >
        <span className="history-filters-title">Filters</span>
        <span className="history-filters-toggle">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="history-filters-content" id={contentId}>
          <div className="history-filters-field">
            <label className="history-filters-label">Date From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={handleDateFromChange}
              className="history-filters-input"
              max={dateTo || undefined}
            />
          </div>
          <div className="history-filters-field">
            <label className="history-filters-label">Date To</label>
            <input
              type="date"
              value={dateTo}
              onChange={handleDateToChange}
              className="history-filters-input"
              min={dateFrom || undefined}
            />
            {dateError && (
              <span className="history-filters-error" role="alert">
                {dateError}
              </span>
            )}
          </div>
          <div className="history-filters-field">
            <label className="history-filters-label">Domain</label>
            <input
              type="text"
              placeholder="e.g. coding"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="history-filters-input"
            />
          </div>
          <div className="history-filters-field">
            <label className="history-filters-label">Mode</label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="history-filters-input"
            >
              <option value="">Any</option>
              <option value="synthesis">Synthesis</option>
              <option value="individual">Individual</option>
              <option value="sequential">Sequential</option>
              <option value="debate">Debate</option>
              <option value="vote">Vote</option>
            </select>
          </div>
          <div className="history-filters-actions">
            <button
              type="button"
              onClick={handleClear}
              className="history-filters-btn history-filters-btn--clear"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={handleApply}
              className="history-filters-btn history-filters-btn--apply"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryFilters;
