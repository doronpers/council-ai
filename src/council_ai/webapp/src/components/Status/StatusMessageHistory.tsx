import React from 'react';
import { useStatusHistory } from '../../context/StatusHistoryContext';
import '../../styles/status-history.css';

const StatusMessageHistory: React.FC = () => {
  const { messages, removeMessage } = useStatusHistory();

  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="status-history">
      <div className="status-history-list">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`status-message status-message--${message.type} status-message--enter`}
          >
            <div className="status-message-content">
              <span className="status-message-text">{message.text}</span>
              <button
                type="button"
                className="status-message-close"
                onClick={() => removeMessage(message.id)}
                aria-label="Dismiss message"
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatusMessageHistory;
