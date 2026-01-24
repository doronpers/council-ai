/**
 * ModeSelect Component - Consultation mode selection with descriptions
 */
import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import HelpIcon from '../Help/HelpIcon';
import { getHelpContent, formatHelpContent } from '../../data/helpContent';

const MODE_DESCRIPTIONS: Record<string, string> = {
  individual: 'Each member responds separately',
  sequential: 'Members respond in order, seeing previous responses',
  synthesis: 'Individual responses + synthesized summary (recommended)',
  debate: 'Members can respond to each other in multiple rounds',
  vote: 'Members vote on a decision',
  pattern_coach:
    'Get advice based on software design patterns from the pattern library. Enhances synthesis with relevant patterns.',
};

const MODE_DOCUMENTATION: Record<string, string | null> = {
  pattern_coach: 'https://github.com/doronpers/shared-ai-utils/blob/main/README.md#pattern-library',
};

const ModeSelect: React.FC = () => {
  const { modes, settings, updateSettings } = useApp();
  const [showPatternCoachInfo, setShowPatternCoachInfo] = useState(false);

  const selectedMode = settings.mode || '';
  const selectedDescription = MODE_DESCRIPTIONS[selectedMode] || '';
  const selectedDocLink = MODE_DOCUMENTATION[selectedMode];

  return (
    <div>
      <div className="flex-between mb-8">
        <div className="config-field-label-wrapper">
          <label htmlFor="mode">Mode</label>
          <HelpIcon content={formatHelpContent(getHelpContent('mode')!)} position="right" />
        </div>
        {selectedMode === 'pattern_coach' && (
          <button
            type="button"
            className="btn-minimal btn-small"
            onClick={() => setShowPatternCoachInfo(!showPatternCoachInfo)}
            aria-label="Toggle pattern coach information"
          >
            ℹ️ Info
          </button>
        )}
      </div>
      <select
        id="mode"
        value={selectedMode}
        onChange={(e) => updateSettings({ mode: e.target.value })}
        aria-describedby={selectedDescription ? 'mode-description' : undefined}
      >
        {modes.map((mode) => {
          const displayName =
            mode === 'pattern_coach'
              ? 'Pattern Coach'
              : mode.charAt(0).toUpperCase() + mode.slice(1);
          return (
            <option key={mode} value={mode}>
              {displayName}
            </option>
          );
        })}
      </select>
      {selectedDescription && (
        <p id="mode-description" className="field-hint">
          {selectedDescription}
          {selectedDocLink && (
            <>
              {' '}
              <a
                href={selectedDocLink}
                target="_blank"
                rel="noopener noreferrer"
                className="field-hint-link"
                onClick={(e) => e.stopPropagation()}
              >
                Learn more
              </a>
            </>
          )}
        </p>
      )}
      {showPatternCoachInfo && selectedMode === 'pattern_coach' && (
        <div className="mode-info-panel">
          <h4 className="mode-info-title">Pattern Coach Mode</h4>
          <p className="mode-info-description">
            Pattern Coach enhances consultations by automatically suggesting relevant software
            design patterns from the pattern library. The council will receive pattern context
            before synthesizing their advice, helping you apply proven design solutions to your
            questions.
          </p>
          <p className="mode-info-description">
            <strong>Best for:</strong> Code reviews, architecture decisions, design pattern
            questions, and software engineering consultations.
          </p>
          {selectedDocLink && (
            <a
              href={selectedDocLink}
              target="_blank"
              rel="noopener noreferrer"
              className="mode-info-link"
            >
              View Pattern Library Documentation →
            </a>
          )}
        </div>
      )}
      <p className="field-hint">Saved to browser</p>
    </div>
  );
};

export default ModeSelect;
