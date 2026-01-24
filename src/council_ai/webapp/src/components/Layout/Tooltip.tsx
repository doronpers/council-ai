/**
 * Tooltip Component - Accessible tooltip for form elements
 */
import React, { useState, useRef, useEffect } from 'react';
import './Tooltip.css';

interface TooltipProps {
  content: string | React.ReactNode;
  children: React.ReactElement;
  position?: 'top' | 'bottom' | 'left' | 'right';
  disabled?: boolean;
}

const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  disabled = false,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState(position);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isVisible || !tooltipRef.current || !triggerRef.current) return;

    const tooltip = tooltipRef.current;
    const trigger = triggerRef.current;
    const rect = trigger.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Auto-adjust position based on viewport
    let adjustedPosition = position;

    if (position === 'top' && rect.top < tooltipRect.height + 10) {
      adjustedPosition = 'bottom';
    } else if (position === 'bottom' && rect.bottom + tooltipRect.height + 10 > viewportHeight) {
      adjustedPosition = 'top';
    } else if (position === 'left' && rect.left < tooltipRect.width + 10) {
      adjustedPosition = 'right';
    } else if (position === 'right' && rect.right + tooltipRect.width + 10 > viewportWidth) {
      adjustedPosition = 'left';
    }

    setTooltipPosition(adjustedPosition);
  }, [isVisible, position]);

  if (disabled || !content) {
    return children;
  }

  const handleMouseEnter = () => setIsVisible(true);
  const handleMouseLeave = () => setIsVisible(false);
  const handleFocus = () => setIsVisible(true);
  const handleBlur = () => setIsVisible(false);

  const triggerElement = React.cloneElement(children, {
    ref: triggerRef,
    onMouseEnter: handleMouseEnter,
    onMouseLeave: handleMouseLeave,
    onFocus: handleFocus,
    onBlur: handleBlur,
    'aria-describedby': isVisible ? 'tooltip' : undefined,
  });

  return (
    <div className="tooltip-wrapper">
      {triggerElement}
      {isVisible && (
        <div
          id="tooltip"
          ref={tooltipRef}
          className={`tooltip tooltip--${tooltipPosition}`}
          role="tooltip"
        >
          {content}
        </div>
      )}
    </div>
  );
};

export default Tooltip;
