/**
 * Header Component - Application header with navigation
 */
import React from 'react';

const Header: React.FC = () => {
  return (
    <header>
      <h1>Council AI</h1>
      <p>Get advice from a council of AI-powered personas with diverse perspectives.</p>
      <nav className="nav">
        <a href="/" className="nav-link active">
          Consultation
        </a>
        <a href="/reviewer_ui.html" className="nav-link">
          Reviewer
        </a>
        <button
          className="nav-link"
          onClick={() => {
            const modal = document.getElementById('diagnostics-modal');
            if (modal) modal.style.display = 'flex';
          }}
        >
          🏥 Council Doctor
        </button>
      </nav>
    </header>
  );
};

export default Header;
