/**
 * ResultsFilters Component - Advanced filtering for consultation results
 */
import React, { useState, useEffect, useMemo } from 'react';
import { useConsultation } from '../../context/ConsultationContext';

interface FilterState {
  personas: string[];
  providers: string[];
  models: string[];
  dateFrom: string;
  dateTo: string;
  tags: string[];
  minLength: number;
  maxLength: number;
  hasErrors: boolean;
  sortBy: 'persona' | 'timestamp' | 'length' | 'relevance';
  sortOrder: 'asc' | 'desc';
}

interface ResultsFiltersProps {
  onFiltersChange: (filters: Partial<FilterState>) => void;
  availablePersonas?: string[];
  availableProviders?: string[];
  availableModels?: string[];
  availableTags?: string[];
}

const ResultsFilters: React.FC<ResultsFiltersProps> = ({
  onFiltersChange,
  availablePersonas = [],
  availableProviders = [],
  availableModels = [],
  availableTags = [],
}) => {
  const { result } = useConsultation();
  const [filters, setFilters] = useState<FilterState>({
    personas: [],
    providers: [],
    models: [],
    dateFrom: '',
    dateTo: '',
    tags: [],
    minLength: 0,
    maxLength: 10000,
    hasErrors: false,
    sortBy: 'persona',
    sortOrder: 'asc',
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [savedPresets, setSavedPresets] = useState<Record<string, Partial<FilterState>>>({});

  // Extract available options from current results
  const extractedOptions = useMemo(() => {
    if (!result) return { personas: [], providers: [], models: [], tags: [] };

    const personas = new Set<string>();
    const providers = new Set<string>();
    const models = new Set<string>();
    const tags = new Set<string>();

    result.responses.forEach((response) => {
      if (response.persona_name) personas.add(response.persona_name);
      if (response.provider) providers.add(response.provider);
      if (response.model) models.add(response.model);
    });

    // Extract tags from result if available
    if (result.tags) {
      result.tags.forEach((tag) => tags.add(tag));
    }

    return {
      personas: Array.from(personas).sort(),
      providers: Array.from(providers).sort(),
      models: Array.from(models).sort(),
      tags: Array.from(tags).sort(),
    };
  }, [result]);

  // Merge with provided available options
  const allPersonas = useMemo(
    () => Array.from(new Set([...availablePersonas, ...extractedOptions.personas])).sort(),
    [availablePersonas, extractedOptions.personas]
  );

  const allProviders = useMemo(
    () => Array.from(new Set([...availableProviders, ...extractedOptions.providers])).sort(),
    [availableProviders, extractedOptions.providers]
  );

  const allModels = useMemo(
    () => Array.from(new Set([...availableModels, ...extractedOptions.models])).sort(),
    [availableModels, extractedOptions.models]
  );

  const allTags = useMemo(
    () => Array.from(new Set([...availableTags, ...extractedOptions.tags])).sort(),
    [availableTags, extractedOptions.tags]
  );

  // Notify parent of filter changes
  useEffect(() => {
    onFiltersChange(filters);
  }, [filters, onFiltersChange]);

  // Load saved presets from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('council-ai-filter-presets');
    if (saved) {
      try {
        setSavedPresets(JSON.parse(saved));
      } catch (e) {
        console.warn('Failed to load filter presets:', e);
      }
    }
  }, []);

  const updateFilter = <K extends keyof FilterState>(key: K, value: FilterState[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const toggleArrayFilter = (key: 'personas' | 'providers' | 'models' | 'tags', value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: prev[key].includes(value)
        ? prev[key].filter((item) => item !== value)
        : [...prev[key], value],
    }));
  };

  const clearAllFilters = () => {
    setFilters({
      personas: [],
      providers: [],
      models: [],
      dateFrom: '',
      dateTo: '',
      tags: [],
      minLength: 0,
      maxLength: 10000,
      hasErrors: false,
      sortBy: 'persona',
      sortOrder: 'asc',
    });
  };

  const savePreset = () => {
    const name = prompt('Enter preset name:');
    if (name && name.trim()) {
      const newPresets = { ...savedPresets, [name.trim()]: { ...filters } };
      setSavedPresets(newPresets);
      localStorage.setItem('council-ai-filter-presets', JSON.stringify(newPresets));
    }
  };

  const loadPreset = (name: string) => {
    const preset = savedPresets[name];
    if (preset) {
      setFilters((prev) => ({ ...prev, ...preset }));
    }
  };

  const deletePreset = (name: string) => {
    const newPresets = { ...savedPresets };
    delete newPresets[name];
    setSavedPresets(newPresets);
    localStorage.setItem('council-ai-filter-presets', JSON.stringify(newPresets));
  };

  const hasActiveFilters = useMemo(() => {
    return (
      filters.personas.length > 0 ||
      filters.providers.length > 0 ||
      filters.models.length > 0 ||
      filters.dateFrom ||
      filters.dateTo ||
      filters.tags.length > 0 ||
      filters.minLength > 0 ||
      filters.maxLength < 10000 ||
      filters.hasErrors ||
      filters.sortBy !== 'persona' ||
      filters.sortOrder !== 'asc'
    );
  }, [filters]);

  return (
    <div className="results-filters">
      <div className="filters-header">
        <h4>Filter & Sort Results</h4>
        <div className="filters-actions">
          {hasActiveFilters && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={clearAllFilters}>
              Clear All
            </button>
          )}
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? 'Less' : 'More'} Filters
          </button>
        </div>
      </div>

      <div className="filters-content">
        {/* Basic Filters */}
        <div className="filter-group">
          <label>Personas</label>
          <div className="filter-checkboxes">
            {allPersonas.map((persona) => (
              <label key={persona} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={filters.personas.includes(persona)}
                  onChange={() => toggleArrayFilter('personas', persona)}
                />
                <span>{persona}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label>Providers</label>
          <div className="filter-checkboxes">
            {allProviders.map((provider) => (
              <label key={provider} className="checkbox-item">
                <input
                  type="checkbox"
                  checked={filters.providers.includes(provider)}
                  onChange={() => toggleArrayFilter('providers', provider)}
                />
                <span>{provider}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="filter-row">
          <div className="filter-group">
            <label htmlFor="sort-by">Sort by</label>
            <select
              id="sort-by"
              value={filters.sortBy}
              onChange={(e) => updateFilter('sortBy', e.target.value as FilterState['sortBy'])}
            >
              <option value="persona">Persona</option>
              <option value="timestamp">Time</option>
              <option value="length">Length</option>
              <option value="relevance">Relevance</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-order">Order</label>
            <select
              id="sort-order"
              value={filters.sortOrder}
              onChange={(e) =>
                updateFilter('sortOrder', e.target.value as FilterState['sortOrder'])
              }
            >
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </div>
        </div>

        {/* Advanced Filters */}
        {showAdvanced && (
          <>
            <div className="filter-group">
              <label>Models</label>
              <div className="filter-checkboxes">
                {allModels.map((model) => (
                  <label key={model} className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.models.includes(model)}
                      onChange={() => toggleArrayFilter('models', model)}
                    />
                    <span>{model}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label>Tags</label>
              <div className="filter-checkboxes">
                {allTags.map((tag) => (
                  <label key={tag} className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.tags.includes(tag)}
                      onChange={() => toggleArrayFilter('tags', tag)}
                    />
                    <span>{tag}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="filter-row">
              <div className="filter-group">
                <label htmlFor="date-from">Date from</label>
                <input
                  id="date-from"
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => updateFilter('dateFrom', e.target.value)}
                />
              </div>

              <div className="filter-group">
                <label htmlFor="date-to">Date to</label>
                <input
                  id="date-to"
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => updateFilter('dateTo', e.target.value)}
                />
              </div>
            </div>

            <div className="filter-row">
              <div className="filter-group">
                <label htmlFor="min-length">Min length</label>
                <input
                  id="min-length"
                  type="number"
                  min="0"
                  value={filters.minLength}
                  onChange={(e) => updateFilter('minLength', parseInt(e.target.value) || 0)}
                />
              </div>

              <div className="filter-group">
                <label htmlFor="max-length">Max length</label>
                <input
                  id="max-length"
                  type="number"
                  min="0"
                  value={filters.maxLength}
                  onChange={(e) => updateFilter('maxLength', parseInt(e.target.value) || 10000)}
                />
              </div>
            </div>

            <div className="filter-group">
              <label className="checkbox-item">
                <input
                  type="checkbox"
                  checked={filters.hasErrors}
                  onChange={(e) => updateFilter('hasErrors', e.target.checked)}
                />
                <span>Show only responses with errors</span>
              </label>
            </div>

            {/* Filter Presets */}
            <div className="filter-presets">
              <div className="presets-header">
                <label>Filter Presets</label>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={savePreset}
                  disabled={!hasActiveFilters}
                >
                  Save Current
                </button>
              </div>

              {Object.keys(savedPresets).length > 0 && (
                <div className="presets-list">
                  {Object.entries(savedPresets).map(([name]) => (
                    <div key={name} className="preset-item">
                      <button
                        type="button"
                        className="preset-load"
                        onClick={() => loadPreset(name)}
                      >
                        {name}
                      </button>
                      <button
                        type="button"
                        className="preset-delete"
                        onClick={() => deletePreset(name)}
                        title="Delete preset"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ResultsFilters;
