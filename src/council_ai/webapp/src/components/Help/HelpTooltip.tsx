/**
 * HelpTooltip Component - Position-aware tooltip with rich content support
 */
import React, { useState, useRef, useEffect } from 'react';
import './HelpTooltip.css';

interface HelpTooltipProps {
  content: string | React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  children: React.ReactElement;
  maxWidth?: number;
}

const HelpTooltip: React.FC<HelpTooltipProps> = ({
  content,
  children,
  position = 'top',
  maxWidth = 300,
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
    const margin = 10;

    // Auto-adjust position based on viewport
    let adjustedPosition = position;

    if (position === 'top' && rect.top < tooltipRect.height + margin) {
      adjustedPosition = 'bottom';
    } else if (
      position === 'bottom' &&
      rect.bottom + tooltipRect.height + margin > viewportHeight
    ) {
      adjustedPosition = 'top';
    } else if (position === 'left' && rect.left < tooltipRect.width + margin) {
      adjustedPosition = 'right';
    } else if (position === 'right' && rect.right + tooltipRect.width + margin > viewportWidth) {
      adjustedPosition = 'left';
    }

    setTooltipPosition(adjustedPosition);
  }, [isVisible, position]);

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
    'aria-describedby': isVisible ? 'help-tooltip' : undefined,
  });

  return (
    <div className="help-tooltip-wrapper">
      {triggerElement}
      {isVisible && (
        <div
          id="help-tooltip"
          ref={tooltipRef}
          className={`help-tooltip help-tooltip--${tooltipPosition}`}
          role="tooltip"
          style={{ maxWidth: `${maxWidth}px` }}
        >
          <div className="help-tooltip-content">{content}</div>
        </div>
      )}
    </div>
  );
};

export default HelpTooltip;
