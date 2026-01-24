/**
 * HelpIcon Component - Help icon with tooltip
 */
import React from 'react';
import HelpTooltip from './HelpTooltip';

interface HelpIconProps {
  content: string | React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

const HelpIcon: React.FC<HelpIconProps> = ({ content, position = 'top', className = '' }) => {
  return (
    <HelpTooltip content={content} position={position}>
      <button type="button" className={`help-icon ${className}`} aria-label="Help" tabIndex={0}>
        <span aria-hidden="true">ℹ️</span>
      </button>
    </HelpTooltip>
  );
};

export default HelpIcon;
