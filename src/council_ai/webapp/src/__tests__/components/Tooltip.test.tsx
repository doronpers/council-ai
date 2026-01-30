/**
 * Tests for Tooltip component
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Tooltip from '../../components/Layout/Tooltip';

// Mock getBoundingClientRect to return centered viewport values
// so the auto-adjust logic doesn't override the requested position
const mockGetBoundingClientRect = () =>
  ({
    top: 200,
    left: 200,
    bottom: 250,
    right: 300,
    width: 100,
    height: 50,
    x: 200,
    y: 200,
    toJSON: () => {},
  }) as DOMRect;

describe('Tooltip', () => {
  const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;

  beforeEach(() => {
    Element.prototype.getBoundingClientRect = mockGetBoundingClientRect;
  });

  afterEach(() => {
    Element.prototype.getBoundingClientRect = originalGetBoundingClientRect;
  });

  it('renders children without tooltip initially', () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );

    expect(screen.getByText('Hover me')).toBeInTheDocument();
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('shows tooltip on mouse enter', async () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );

    const button = screen.getByText('Hover me');
    fireEvent.mouseEnter(button);

    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument();
      expect(screen.getByText('Tooltip text')).toBeInTheDocument();
    });
  });

  it('hides tooltip on mouse leave', async () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );

    const button = screen.getByText('Hover me');

    fireEvent.mouseEnter(button);
    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });

    fireEvent.mouseLeave(button);
    await waitFor(() => {
      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    });
  });

  it('shows tooltip on focus', async () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Focus me</button>
      </Tooltip>
    );

    const button = screen.getByText('Focus me');
    fireEvent.focus(button);

    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });
  });

  it('hides tooltip on blur', async () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Focus me</button>
      </Tooltip>
    );

    const button = screen.getByText('Focus me');

    fireEvent.focus(button);
    await waitFor(() => {
      expect(screen.getByRole('tooltip')).toBeInTheDocument();
    });

    fireEvent.blur(button);
    await waitFor(() => {
      expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    });
  });

  it('applies correct position class', async () => {
    render(
      <Tooltip content="Tooltip text" position="bottom">
        <button>Hover me</button>
      </Tooltip>
    );

    const button = screen.getByText('Hover me');
    fireEvent.mouseEnter(button);

    await waitFor(() => {
      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('tooltip--bottom');
    });
  });

  it('uses top position by default', async () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );

    const button = screen.getByText('Hover me');
    fireEvent.mouseEnter(button);

    await waitFor(() => {
      const tooltip = screen.getByRole('tooltip');
      expect(tooltip).toHaveClass('tooltip--top');
    });
  });

  it('renders children only when disabled', () => {
    render(
      <Tooltip content="Tooltip text" disabled>
        <button>Click me</button>
      </Tooltip>
    );

    const button = screen.getByText('Click me');
    fireEvent.mouseEnter(button);

    // Tooltip should not appear when disabled
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('renders children only when content is empty', () => {
    render(
      <Tooltip content="">
        <button>Click me</button>
      </Tooltip>
    );

    const button = screen.getByText('Click me');
    fireEvent.mouseEnter(button);

    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('supports React node as content', async () => {
    render(
      <Tooltip content={<span data-testid="custom-content">Custom content</span>}>
        <button>Hover me</button>
      </Tooltip>
    );

    const button = screen.getByText('Hover me');
    fireEvent.mouseEnter(button);

    await waitFor(() => {
      expect(screen.getByTestId('custom-content')).toBeInTheDocument();
      expect(screen.getByText('Custom content')).toBeInTheDocument();
    });
  });

  it('sets aria-describedby when tooltip is visible', async () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );

    const button = screen.getByText('Hover me');

    // Initially no aria-describedby
    expect(button).not.toHaveAttribute('aria-describedby');

    fireEvent.mouseEnter(button);

    await waitFor(() => {
      expect(button).toHaveAttribute('aria-describedby', 'tooltip');
    });
  });

  it('wraps children in tooltip-wrapper', () => {
    render(
      <Tooltip content="Tooltip text">
        <button>Hover me</button>
      </Tooltip>
    );

    const wrapper = document.querySelector('.tooltip-wrapper');
    expect(wrapper).toBeInTheDocument();
  });
});
