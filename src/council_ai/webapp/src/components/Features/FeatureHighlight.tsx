/**
 * FeatureHighlight Component - Feature cards, tooltips, and announcements
 */
import React, { useState } from 'react';
import './FeatureHighlight.css';

interface FeatureHighlightProps {
  title: string;
  description: string;
  icon?: string;
  badge?: 'new' | 'popular' | null;
  onDismiss?: () => void;
  onAction?: () => void;
  actionLabel?: string;
  children?: React.ReactNode;
}

const FeatureHighlight: React.FC<FeatureHighlightProps> = ({
  title,
  description,
  icon,
  badge,
  onDismiss,
  onAction,
  actionLabel,
  children,
}) => {
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) {
    return null;
  }

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.();
  };

  return (
    <div className="feature-highlight">
      {badge && (
        <span className={`feature-highlight-badge feature-highlight-badge--${badge}`}>
          {badge === 'new' ? 'New' : 'Popular'}
        </span>
      )}
      <div className="feature-highlight-content">
        {icon && <div className="feature-highlight-icon">{icon}</div>}
        <div className="feature-highlight-text">
          <h4 className="feature-highlight-title">{title}</h4>
          <p className="feature-highlight-description">{description}</p>
          {children}
        </div>
        {onDismiss && (
          <button
            type="button"
            className="feature-highlight-dismiss"
            onClick={handleDismiss}
            aria-label="Dismiss"
          >
            ×
          </button>
        )}
      </div>
      {onAction && (
        <div className="feature-highlight-actions">
          <button type="button" className="btn btn-primary btn-sm" onClick={onAction}>
            {actionLabel || 'Learn More'}
          </button>
        </div>
      )}
    </div>
  );
};

export default FeatureHighlight;
