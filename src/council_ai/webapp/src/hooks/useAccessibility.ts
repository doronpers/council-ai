import { useEffect, useRef } from 'react';

/**
 * Custom hook for managing focus trap within a modal or dialog
 * Ensures tab navigation stays within the provided element
 */
export const useFocusTrap = (shouldTrap: boolean = true) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!shouldTrap || !ref.current) {
      return;
    }

    const trapElement = ref.current;
    const focusableElements = trapElement.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) {
      return;
    }

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') {
        return;
      }

      const activeElement = document.activeElement as HTMLElement;

      if (event.shiftKey) {
        // Shift + Tab
        if (activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    };

    trapElement.addEventListener('keydown', handleKeyDown);
    firstElement.focus();

    return () => {
      trapElement.removeEventListener('keydown', handleKeyDown);
    };
  }, [shouldTrap]);

  return ref;
};

/**
 * Custom hook for managing focus restoration
 * Saves the focused element before an action and restores it after
 */
export const useFocusRestoration = () => {
  const previouslyFocusedElement = useRef<HTMLElement | null>(null);

  const saveFocus = () => {
    previouslyFocusedElement.current = document.activeElement as HTMLElement;
  };

  const restoreFocus = () => {
    if (previouslyFocusedElement.current?.focus) {
      previouslyFocusedElement.current.focus();
    }
  };

  return { saveFocus, restoreFocus };
};

/**
 * Custom hook for announce screen reader messages
 * Useful for dynamic content updates that screen readers should announce
 */
export const useAnnounce = () => {
  const ref = useRef<HTMLDivElement>(null);

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (!ref.current) {
      return;
    }

    ref.current.setAttribute('role', 'status');
    ref.current.setAttribute('aria-live', priority);
    ref.current.setAttribute('aria-atomic', 'true');
    ref.current.textContent = message;

    // Clear after announcement
    setTimeout(() => {
      if (ref.current) {
        ref.current.textContent = '';
      }
    }, 1000);
  };

  return { ref, announce };
};
