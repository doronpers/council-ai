/**
 * ProgressDashboard Component - Enhanced consultation progress display
 */
import React, { useState, useEffect, useMemo } from 'react';
import { useConsultation } from '../../context/ConsultationContext';
import MemberStatusCard from '../Members/MemberStatusCard';
import ConfirmDialog from '../Layout/ConfirmDialog';

const ProgressDashboard: React.FC = () => {
  const { isConsulting, memberStatuses, statusMessage, cancelConsultation, abortController } =
    useConsultation();
  const [startTime] = useState(() => Date.now());
  const [elapsedTime, setElapsedTime] = useState(0);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);

  // Update elapsed time every second
  useEffect(() => {
    if (!isConsulting) return;

    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [isConsulting, startTime]);

  if (!isConsulting && memberStatuses.length === 0) {
    return null;
  }

  const completedCount = memberStatuses.filter((m) => m.status === 'completed').length;
  const respondingCount = memberStatuses.filter((m) => m.status === 'responding').length;
  const errorCount = memberStatuses.filter((m) => m.status === 'error').length;
  const totalCount = memberStatuses.length;
  const progressPercent = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  // Estimate time remaining based on average response time
  const averageResponseTime = useMemo(() => {
    // Rough estimate: 30-60 seconds per persona response
    return 45;
  }, []);

  const estimatedTimeRemaining = useMemo(() => {
    const remaining = totalCount - completedCount;
    if (remaining === 0) return 0;
    // Add some buffer for synthesis
    return remaining * averageResponseTime + (remaining === 1 ? 10 : 20);
  }, [completedCount, totalCount, averageResponseTime]);

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`;
  };

  const handleCancelClick = () => {
    setShowCancelConfirm(true);
  };

  const handleCancelConfirm = () => {
    cancelConsultation();
    setShowCancelConfirm(false);
  };

  const currentlyResponding = memberStatuses.find((m) => m.status === 'responding');

  return (
    <section className="panel progress-dashboard" id="progress-dashboard">
      <div className="progress-dashboard-header">
        <h2>Consultation Progress</h2>
        {isConsulting && abortController && (
          <button
            type="button"
            className="btn btn-secondary btn-sm progress-dashboard-cancel"
            onClick={handleCancelClick}
            aria-label="Cancel consultation"
          >
            ✕ Cancel
          </button>
        )}
      </div>

      {/* Status message */}
      <div id="status" className="progress-status-message mb-16">
        {statusMessage || 'Assembling council...'}
        {currentlyResponding && (
          <span className="progress-current-persona">
            {' '}
            ({currentlyResponding.emoji} {currentlyResponding.name} responding...)
          </span>
        )}
      </div>

      {/* Progress bar with percentage */}
      <div className="progress-bar-container mb-16">
        <div className="progress-bar-header">
          <span className="progress-percentage">{Math.round(progressPercent)}%</span>
          <span className="progress-count">
            {completedCount} / {totalCount} responses
          </span>
        </div>
        <div className="progress-bar-wrapper">
          <div className="progress-bar" style={{ width: `${progressPercent}%` }} />
        </div>
      </div>

      {/* Time information */}
      <div className="progress-time-info mb-16">
        <div className="progress-time-item">
          <span className="progress-time-label">Elapsed:</span>
          <span className="progress-time-value">{formatTime(elapsedTime)}</span>
        </div>
        {estimatedTimeRemaining > 0 && (
          <div className="progress-time-item">
            <span className="progress-time-label">Est. remaining:</span>
            <span className="progress-time-value">~{formatTime(estimatedTimeRemaining)}</span>
          </div>
        )}
      </div>

      {/* Member status grid with individual progress */}
      <div id="member-status-list" className="member-status-list">
        {memberStatuses.map((member) => (
          <MemberStatusCard key={member.id} member={member} />
        ))}
      </div>

      {/* Summary with status breakdown */}
      <div className="progress-summary mt-12">
        <div className="progress-summary-stats">
          <span className="progress-stat progress-stat--completed">
            ✓ {completedCount} completed
          </span>
          {respondingCount > 0 && (
            <span className="progress-stat progress-stat--responding">
              ⏳ {respondingCount} responding
            </span>
          )}
          {errorCount > 0 && (
            <span className="progress-stat progress-stat--error">✕ {errorCount} errors</span>
          )}
        </div>
      </div>

      <ConfirmDialog
        isOpen={showCancelConfirm}
        onConfirm={handleCancelConfirm}
        onCancel={() => setShowCancelConfirm(false)}
        title="Cancel Consultation"
        message="Are you sure you want to cancel this consultation? All progress will be lost."
        confirmLabel="Cancel Consultation"
        cancelLabel="Continue"
        danger
      />
    </section>
  );
};

export default ProgressDashboard;
