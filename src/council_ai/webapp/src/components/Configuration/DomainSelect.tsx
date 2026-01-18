/**
 * DomainSelect Component - Domain selection dropdown
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

const DomainSelect: React.FC = () => {
  const { domains, settings, updateSettings, setSelectedMembers } = useApp();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newDomain = e.target.value;
    updateSettings({ domain: newDomain });

    // Clear custom members when domain changes
    setSelectedMembers([]);
  };

  return (
    <div>
      <label htmlFor="domain">Domain</label>
      <select id="domain" value={settings.domain || ''} onChange={handleChange}>
        {domains.map((domain) => (
          <option key={domain.id} value={domain.id}>
            {domain.name}
            {domain.default_personas.length > 0
              ? ` (${domain.default_personas.length} members)`
              : ''}
          </option>
        ))}
      </select>
      <p className="field-hint">Saved to browser</p>
    </div>
  );
};

export default DomainSelect;
