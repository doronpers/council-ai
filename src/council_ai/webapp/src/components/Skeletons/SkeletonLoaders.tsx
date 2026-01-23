import React from 'react';
import '../styles/skeletons.css';

/**
 * Generic skeleton loader with pulse animation
 */
export const Skeleton: React.FC<{
  width?: string | number;
  height?: string | number;
  className?: string;
}> = ({ width = '100%', height = '16px', className = '' }) => (
  <div
    className={`skeleton ${className}`}
    style={{
      width: typeof width === 'number' ? `${width}px` : width,
      height: typeof height === 'number' ? `${height}px` : height,
    }}
  />
);

/**
 * Response card skeleton
 */
export const ResponseCardSkeleton: React.FC = () => (
  <div className="response-card-skeleton">
    <div className="response-card-skeleton-header">
      <Skeleton width="30%" height="20px" />
      <Skeleton width="15%" height="20px" />
    </div>
    <div className="response-card-skeleton-body">
      <Skeleton width="100%" height="12px" />
      <Skeleton width="100%" height="12px" />
      <Skeleton width="85%" height="12px" />
      <Skeleton width="100%" height="12px" />
      <Skeleton width="70%" height="12px" />
    </div>
  </div>
);

/**
 * Analysis card skeleton
 */
export const AnalysisCardSkeleton: React.FC = () => (
  <div className="analysis-card-skeleton">
    <Skeleton width="40%" height="24px" className="mb-16" />
    <div className="mb-24">
      <Skeleton width="25%" height="16px" className="mb-8" />
      <Skeleton width="100%" height="10px" className="mb-4" />
      <Skeleton width="100%" height="10px" />
    </div>
    <div className="mb-24">
      <Skeleton width="25%" height="16px" className="mb-8" />
      <Skeleton width="100%" height="10px" className="mb-4" />
      <Skeleton width="90%" height="10px" />
    </div>
  </div>
);

/**
 * Synthesis card skeleton
 */
export const SynthesisCardSkeleton: React.FC = () => (
  <div className="synthesis-card-skeleton">
    <Skeleton width="35%" height="24px" className="mb-16" />
    <Skeleton width="100%" height="12px" className="mb-8" />
    <Skeleton width="100%" height="12px" className="mb-8" />
    <Skeleton width="85%" height="12px" />
  </div>
);

/**
 * Results panel skeleton (multiple responses loading)
 */
export const ResultsPanelSkeleton: React.FC = () => (
  <div className="results-panel-skeleton">
    <ResponseCardSkeleton />
    <ResponseCardSkeleton />
    <ResponseCardSkeleton />
    <AnalysisCardSkeleton />
    <SynthesisCardSkeleton />
  </div>
);
