/**
 * FeatureTour Component - Step-by-step guided tours for complex features
 */
import React, { useState, useEffect, useRef } from 'react';
import './FeatureTour.css';

export interface TourStep {
  target: string; // CSS selector or element ID
  title: string;
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

interface FeatureTourProps {
  steps: TourStep[];
  isOpen: boolean;
  onClose: () => void;
  onComplete?: () => void;
  tourId: string; // For tracking completion
}

const FeatureTour: React.FC<FeatureTourProps> = ({
  steps,
  isOpen,
  onClose,
  onComplete,
  tourId,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  const currentStepData = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  // Find and highlight target element
  useEffect(() => {
    if (!isOpen || !currentStepData) return;

    const element = document.querySelector(currentStepData.target) as HTMLElement;
    if (element) {
      setTargetElement(element);
      // Scroll element into view
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      setTargetElement(null);
    }
  }, [isOpen, currentStep, currentStepData]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowRight' && !isLastStep) {
        handleNext();
      } else if (e.key === 'ArrowLeft' && !isFirstStep) {
        handlePrevious();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, currentStep, isLastStep, isFirstStep]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // Mark tour as completed
    try {
      const completedTours = JSON.parse(localStorage.getItem('council-completed-tours') || '[]');
      if (!completedTours.includes(tourId)) {
        completedTours.push(tourId);
        localStorage.setItem('council-completed-tours', JSON.stringify(completedTours));
      }
    } catch (e) {
      console.warn('Failed to save tour completion:', e);
    }

    onComplete?.();
    onClose();
  };

  const handleSkip = () => {
    onClose();
  };

  if (!isOpen || !currentStepData) {
    return null;
  }

  // Calculate position for tooltip
  const getTooltipPosition = () => {
    if (!targetElement) return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };

    const rect = targetElement.getBoundingClientRect();
    const position = currentStepData.position || 'bottom';
    const margin = 20;

    switch (position) {
      case 'top':
        return {
          bottom: window.innerHeight - rect.top + margin + 'px',
          left: rect.left + rect.width / 2 + 'px',
          transform: 'translateX(-50%)',
        };
      case 'bottom':
        return {
          top: rect.bottom + margin + 'px',
          left: rect.left + rect.width / 2 + 'px',
          transform: 'translateX(-50%)',
        };
      case 'left':
        return {
          top: rect.top + rect.height / 2 + 'px',
          right: window.innerWidth - rect.left + margin + 'px',
          transform: 'translateY(-50%)',
        };
      case 'right':
        return {
          top: rect.top + rect.height / 2 + 'px',
          left: rect.right + margin + 'px',
          transform: 'translateY(-50%)',
        };
      default:
        return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
    }
  };

  return (
    <>
      {/* Overlay */}
      <div ref={overlayRef} className="feature-tour-overlay" onClick={handleSkip} />

      {/* Highlight box around target */}
      {targetElement && (
        <div
          className="feature-tour-highlight"
          style={{
            top: targetElement.getBoundingClientRect().top + window.scrollY + 'px',
            left: targetElement.getBoundingClientRect().left + window.scrollX + 'px',
            width: targetElement.getBoundingClientRect().width + 'px',
            height: targetElement.getBoundingClientRect().height + 'px',
          }}
        />
      )}

      {/* Tooltip */}
      <div className="feature-tour-tooltip" style={getTooltipPosition()}>
        <div className="feature-tour-tooltip-header">
          <h3 className="feature-tour-tooltip-title">{currentStepData.title}</h3>
          <button
            type="button"
            className="feature-tour-tooltip-close"
            onClick={handleSkip}
            aria-label="Close tour"
          >
            ×
          </button>
        </div>
        <div className="feature-tour-tooltip-content">{currentStepData.content}</div>
        <div className="feature-tour-tooltip-footer">
          <div className="feature-tour-progress">
            Step {currentStep + 1} of {steps.length}
          </div>
          <div className="feature-tour-tooltip-actions">
            {!isFirstStep && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={handlePrevious}>
                Previous
              </button>
            )}
            <button type="button" className="btn btn-secondary btn-sm" onClick={handleSkip}>
              Skip Tour
            </button>
            <button type="button" className="btn btn-primary btn-sm" onClick={handleNext}>
              {isLastStep ? 'Finish' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default FeatureTour;
