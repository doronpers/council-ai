/**
 * FeatureCard Component - Feature cards for communicating feature value
 */
import React from 'react';
import type { FeatureBenefit } from '../../data/featureBenefits';
import './FeatureCard.css';

interface FeatureCardProps {
  feature: FeatureBenefit;
  onEnable?: () => void;
  onLearnMore?: () => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ feature, onEnable, onLearnMore }) => {
  return (
    <div className="feature-card">
      <div className="feature-card-header">
        <div className="feature-card-icon">{feature.icon}</div>
        <div className="feature-card-title-section">
          <h4 className="feature-card-title">{feature.name}</h4>
          {feature.badge && (
            <span className={`feature-card-badge feature-card-badge--${feature.badge}`}>
              {feature.badge}
            </span>
          )}
        </div>
      </div>
      <p className="feature-card-description">{feature.description}</p>
      {feature.useCases && feature.useCases.length > 0 && (
        <div className="feature-card-use-cases">
          <strong>Use cases:</strong>
          <ul>
            {feature.useCases.map((useCase, index) => (
              <li key={index}>{useCase}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="feature-card-actions">
        {onEnable && (
          <button type="button" className="btn btn-primary btn-sm" onClick={onEnable}>
            Enable
          </button>
        )}
        {onLearnMore && (
          <button type="button" className="btn btn-secondary btn-sm" onClick={onLearnMore}>
            Learn More
          </button>
        )}
        {feature.documentationUrl && (
          <a
            href={feature.documentationUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-minimal btn-sm"
          >
            Documentation →
          </a>
        )}
      </div>
    </div>
  );
};

export default FeatureCard;
