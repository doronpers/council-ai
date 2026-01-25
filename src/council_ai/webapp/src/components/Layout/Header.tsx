/**
 * Header Component - Application header with navigation and tours
 */
import React, { useState } from 'react';
import FeatureTour from '../Features/FeatureTour';
import { featureTours, getAvailableTours } from '../../data/featureTours';
import './Header.css';

const Header: React.FC = () => {
  const isReviewer =
    typeof window !== 'undefined' && window.location.pathname.startsWith('/reviewer');
  const [activeTour, setActiveTour] = useState<string | null>(null);

  const availableTours = getAvailableTours();
  const currentTour = activeTour ? featureTours[activeTour] : null;

  const handleTourSelect = (tourId: string) => {
    setActiveTour(tourId);
  };

  const handleTourClose = () => {
    setActiveTour(null);
  };

  const handleTourComplete = () => {
    setActiveTour(null);
  };

  return (
    <>
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
          {!isReviewer && (
            <div className="nav-tour-dropdown">
              <button
                type="button"
                className="nav-link nav-link--tour"
                onClick={(e) => {
                  e.preventDefault();
                  // Toggle dropdown or show tour menu
                  const menu = document.getElementById('tour-menu');
                  if (menu) {
                    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
                  }
                }}
              >
                📚 Take Tour
              </button>
              <div id="tour-menu" className="nav-tour-menu" style={{ display: 'none' }}>
                <button
                  type="button"
                  className="nav-tour-menu-item"
                  onClick={() => {
                    // Trigger onboarding by setting localStorage flag
                    localStorage.setItem('council-start-onboarding', 'true');
                    window.location.reload();
                    const menu = document.getElementById('tour-menu');
                    if (menu) menu.style.display = 'none';
                  }}
                >
                  🎯 Getting Started
                </button>
                {availableTours.map((tour) => (
                  <button
                    key={tour.id}
                    type="button"
                    className="nav-tour-menu-item"
                    onClick={() => {
                      handleTourSelect(tour.id);
                      const menu = document.getElementById('tour-menu');
                      if (menu) menu.style.display = 'none';
                    }}
                  >
                    {tour.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Feature Tour */}
      {currentTour && (
        <FeatureTour
          steps={currentTour.steps}
          isOpen={!!currentTour}
          onClose={handleTourClose}
          onComplete={handleTourComplete}
          tourId={currentTour.id}
        />
      )}
    </>
  );
};

export default Header;
