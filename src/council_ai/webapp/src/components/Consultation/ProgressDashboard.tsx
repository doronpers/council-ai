/**
 * ProgressDashboard Component - Consultation progress display
 */
import React from 'react';
import { useConsultation } from '../../context/ConsultationContext';
import MemberStatusCard from '../Members/MemberStatusCard';

const ProgressDashboard: React.FC = () => {
    const { isConsulting, memberStatuses, statusMessage } = useConsultation();

    if (!isConsulting && memberStatuses.length === 0) {
        return null;
    }

    const completedCount = memberStatuses.filter((m) => m.status === 'completed').length;
    const totalCount = memberStatuses.length;
    const progressPercent = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

    return (
        <section className="panel progress-dashboard" id="progress-dashboard">
            <h2>Progress</h2>

            {/* Status message */}
            <div id="status" className="muted" style={{ marginBottom: '16px' }}>
                {statusMessage}
            </div>

            {/* Progress bar */}
            <div className="progress-bar-container" style={{ marginBottom: '16px' }}>
                <div
                    className="progress-bar"
                    style={{ width: `${progressPercent}%` }}
                />
            </div>

            {/* Member status grid */}
            <div id="member-status-list" className="member-status-list">
                {memberStatuses.map((member) => (
                    <MemberStatusCard key={member.id} member={member} />
                ))}
            </div>

            {/* Summary */}
            <div className="progress-summary" style={{ marginTop: '12px' }}>
                <span className="muted">
                    {completedCount} of {totalCount} responses received
                </span>
            </div>
        </section>
    );
};

export default ProgressDashboard;
