/**
 * Council AI - React Application Entry Point
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import ReviewerApp from './components/Reviewer/ReviewerApp';
import { NotificationProvider } from './components/Layout/NotificationContainer';

// Import global styles
import './styles/index.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error(
    'Failed to find the root element. Make sure index.html has <div id="root"></div>'
  );
}

const isReviewerRoute = window.location.pathname.startsWith('/reviewer');

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    {isReviewerRoute ? (
      <NotificationProvider>
        <ReviewerApp />
      </NotificationProvider>
    ) : (
      <App />
    )}
  </React.StrictMode>
);
