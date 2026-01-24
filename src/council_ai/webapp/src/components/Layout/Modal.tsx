/**
 * Modal Component - Reusable modal with proper focus management
 */
import React, { useEffect, useRef, useCallback } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  maxWidth?: string;
  showCloseButton?: boolean;
  className?: string;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = '800px',
  showCloseButton = true,
  className = '',
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const bodyOverflowRef = useRef<string>('');

  // Memoize escape handler to avoid dependency issues
  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    },
    [isOpen, onClose]
  );

  useEffect(() => {
    if (isOpen) {
      // Store the previously focused element
      const activeElement = document.activeElement;
      if (activeElement instanceof HTMLElement) {
        previousActiveElement.current = activeElement;
      }

      // Store original body overflow
      bodyOverflowRef.current = document.body.style.overflow;

      // Focus the modal container
      if (modalRef.current) {
        modalRef.current.focus();
      }

      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';

      // Handle Escape key
      document.addEventListener('keydown', handleEscape);

      return () => {
        document.removeEventListener('keydown', handleEscape);
        // Restore original body overflow
        document.body.style.overflow = bodyOverflowRef.current;
        // Restore focus to previous element
        if (previousActiveElement.current) {
          previousActiveElement.current.focus();
        }
      };
    } else {
      // Cleanup on unmount if modal was open
      document.body.style.overflow = bodyOverflowRef.current;
    }
  }, [isOpen, handleEscape]);

  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="modal-backdrop"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      <div
        ref={modalRef}
        className={`modal-content ${className}`}
        style={{ maxWidth }}
        onClick={(e) => e.stopPropagation()}
        tabIndex={-1}
      >
        {(title || showCloseButton) && (
          <div className="modal-header">
            {title && (
              <h3 id="modal-title" className="modal-title">
                {title}
              </h3>
            )}
            {showCloseButton && (
              <button
                type="button"
                className="modal-close-btn"
                onClick={onClose}
                aria-label="Close modal"
              >
                ×
              </button>
            )}
          </div>
        )}
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
