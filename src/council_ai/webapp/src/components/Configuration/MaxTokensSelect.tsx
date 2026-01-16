/**
 * MaxTokensSelect Component - Max tokens selection
 */
import React from 'react';
import { useApp } from '../../context/AppContext';

const maxTokenOptions = [
    { value: 500, label: 'Brief (500)' },
    { value: 1000, label: 'Standard (1000)' },
    { value: 2000, label: 'Detailed (2000)' },
    { value: 4000, label: 'Extensive (4000)' },
];

const MaxTokensSelect: React.FC = () => {
    const { settings, updateSettings } = useApp();

    return (
        <div>
            <label htmlFor="max_tokens">Max Tokens</label>
            <select
                id="max_tokens"
                value={settings.max_tokens || 1000}
                onChange={(e) => updateSettings({ max_tokens: parseInt(e.target.value, 10) })}
            >
                {maxTokenOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default MaxTokensSelect;
