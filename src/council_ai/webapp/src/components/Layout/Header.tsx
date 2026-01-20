/**
 * Header Component - Application header with navigation
 */
import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  const isReviewer =
    typeof window !== 'undefined' && window.location.pathname.startsWith('/reviewer');

  return (
    <header>
      <h1>🏛️ Council AI</h1>
      <p>Get advice from a council of AI-powered personas with diverse perspectives.</p>
      <nav className="nav">
        <a href="/" className={`nav-link ${!isReviewer ? 'nav-link--active' : ''}`}>
          🏛️ Consultation
        </a>
        <a href="/reviewer" className={`nav-link ${isReviewer ? 'nav-link--active' : ''}`}>
          ⚖️ Reviewer
        </a>
      </nav>
    </header>
  );
};

export default Header;
