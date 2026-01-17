/**
 * SynthesisCard Component - Display synthesis result
 */
import React from 'react';
import AudioPlayer from './AudioPlayer';

interface SynthesisCardProps {
    content: string;
    isStreaming?: boolean;
}

const SynthesisCard: React.FC<SynthesisCardProps> = ({ content, isStreaming = false }) => {
    return (
        <div className="synthesis">
            <h3>
                📋 Synthesis
                {isStreaming && <span className="loading" style={{ marginLeft: '8px' }}></span>}
            </h3>
            <div className="synthesis-content">
                <p style={{ whiteSpace: 'pre-wrap' }}>{content}</p>
            </div>
            {!isStreaming && <AudioPlayer synthesisText={content} />}
        </div>
    );
};

export default SynthesisCard;
