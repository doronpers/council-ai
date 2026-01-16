/**
 * Council AI - React Application Entry Point
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Import global styles
import './styles/index.css';

const rootElement = document.getElementById('root');

if (!rootElement) {
    throw new Error('Failed to find the root element. Make sure index.html has <div id="root"></div>');
}

ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
