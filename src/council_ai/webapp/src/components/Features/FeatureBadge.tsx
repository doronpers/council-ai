/**
 * FeatureBadge Component - Badge for new or popular features
 */
import React from 'react';

interface FeatureBadgeProps {
  type: 'new' | 'popular';
  className?: string;
}

const FeatureBadge: React.FC<FeatureBadgeProps> = ({ type, className = '' }) => {
  return (
    <span className={`feature-badge feature-badge--${type} ${className}`}>
      {type === 'new' ? 'New' : 'Popular'}
    </span>
  );
};

export default FeatureBadge;
