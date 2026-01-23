import React, { createContext, useCallback, useContext, useState } from 'react';
import { logger, createLogContext } from '../utils/logger';

interface HistoryMessage {
  id: string;
  text: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: number;
}

interface StatusHistoryContextType {
  messages: HistoryMessage[];
  addMessage: (text: string, type?: 'info' | 'success' | 'warning' | 'error') => void;
  clearMessages: () => void;
  removeMessage: (id: string) => void;
}

const StatusHistoryContext = createContext<StatusHistoryContextType | undefined>(undefined);

export const StatusHistoryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<HistoryMessage[]>([]);

  const addMessage = useCallback(
    (text: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
      const id = `${Date.now()}-${Math.random()}`;
      const message: HistoryMessage = { id, text, type, timestamp: Date.now() };

      setMessages((prev) => [message, ...prev].slice(0, 20)); // Keep last 20 messages

      logger.info(`Status message: ${text}`, createLogContext('StatusHistory'));

      // Auto-remove after 8 seconds
      setTimeout(() => {
        setMessages((prev) => prev.filter((m) => m.id !== id));
      }, 8000);
    },
    []
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const removeMessage = useCallback((id: string) => {
    setMessages((prev) => prev.filter((m) => m.id !== id));
  }, []);

  return (
    <StatusHistoryContext.Provider value={{ messages, addMessage, clearMessages, removeMessage }}>
      {children}
    </StatusHistoryContext.Provider>
  );
};

export const useStatusHistory = (): StatusHistoryContextType => {
  const context = useContext(StatusHistoryContext);
  if (!context) {
    throw new Error('useStatusHistory must be used within StatusHistoryProvider');
  }
  return context;
};
