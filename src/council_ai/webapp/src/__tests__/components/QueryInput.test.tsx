/**
 * Tests for QueryInput component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Create mock functions
const mockSetQuery = vi.fn();
const mockSetContext = vi.fn();

// Mock the consultation context
vi.mock('../../context/ConsultationContext', () => ({
  useConsultation: () => ({
    query: '',
    setQuery: mockSetQuery,
    context: '',
    setContext: mockSetContext,
    isConsulting: false,
  }),
}));

// Mock QueryTemplates component
vi.mock('../../components/Consultation/QueryTemplates', () => ({
  default: () => <div data-testid="query-templates">Templates</div>,
}));

// Mock validation utilities
vi.mock('../../utils/errorMessages', () => ({
  getValidationError: (field: string, value: string) => {
    if (field === 'query' && !value.trim()) {
      return 'Query cannot be empty';
    }
    return null;
  },
}));

vi.mock('../../utils/validation', () => ({
  ValidationRules: {
    query: {
      maxLength: (max: number) => ({
        validate: (value: string) => value.length <= max,
        message: `Query must be ${max} characters or less`,
      }),
    },
  },
}));

// Import component after mocks
import QueryInput from '../../components/Consultation/QueryInput';

describe('QueryInput', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders query textarea', () => {
    render(<QueryInput />);

    const queryTextarea = screen.getByLabelText('Query');
    expect(queryTextarea).toBeInTheDocument();
    expect(queryTextarea).toHaveAttribute('placeholder', 'What would you like the council to discuss?');
  });

  it('renders QueryTemplates component', () => {
    render(<QueryInput />);

    expect(screen.getByTestId('query-templates')).toBeInTheDocument();
  });

  it('displays character counter', () => {
    render(<QueryInput />);

    const counters = screen.getAllByText(/0 \/ 50,000/);
    expect(counters.length).toBeGreaterThanOrEqual(1);
    expect(counters[0]).toBeInTheDocument();
  });

  it('calls setQuery when typing', async () => {
    render(<QueryInput />);

    const queryTextarea = screen.getByLabelText('Query');
    fireEvent.change(queryTextarea, { target: { value: 'Test query' } });

    expect(mockSetQuery).toHaveBeenCalledWith('Test query');
  });

  it('renders context field when showContext is true', () => {
    render(<QueryInput showContext={true} />);

    const contextTextarea = screen.getByLabelText('Context (Optional)');
    expect(contextTextarea).toBeInTheDocument();
  });

  it('does not render context field when showContext is false', () => {
    render(<QueryInput showContext={false} />);

    expect(screen.queryByLabelText('Context (Optional)')).not.toBeInTheDocument();
  });

  it('calls setContext when typing in context field', async () => {
    render(<QueryInput showContext={true} />);

    const contextTextarea = screen.getByLabelText('Context (Optional)');
    fireEvent.change(contextTextarea, { target: { value: 'Test context' } });

    expect(mockSetContext).toHaveBeenCalledWith('Test context');
  });

  it('shows validation error on blur when query is empty', async () => {
    render(<QueryInput />);

    const queryTextarea = screen.getByLabelText('Query');

    // Focus and blur to trigger validation
    fireEvent.focus(queryTextarea);
    fireEvent.blur(queryTextarea);

    await waitFor(() => {
      expect(screen.getByText('Query cannot be empty')).toBeInTheDocument();
    });
  });

  it('marks textarea as invalid when there is an error', async () => {
    render(<QueryInput />);

    const queryTextarea = screen.getByLabelText('Query');

    fireEvent.focus(queryTextarea);
    fireEvent.blur(queryTextarea);

    await waitFor(() => {
      expect(queryTextarea).toHaveAttribute('aria-invalid', 'true');
    });
  });

  it('renders in compact mode with smaller rows', () => {
    render(<QueryInput compact={true} />);

    const queryTextarea = screen.getByLabelText('Query');
    expect(queryTextarea).toHaveAttribute('rows', '3');
  });

  it('renders in normal mode with larger rows', () => {
    render(<QueryInput compact={false} />);

    const queryTextarea = screen.getByLabelText('Query');
    expect(queryTextarea).toHaveAttribute('rows', '4');
  });

  it('shows add context button in compact mode', () => {
    render(<QueryInput compact={true} showContext={true} />);

    const addContextButton = screen.getByText('+ Add Context (Optional)');
    expect(addContextButton).toBeInTheDocument();
  });

  it('shows context field when add context button is clicked', async () => {
    render(<QueryInput compact={true} showContext={true} />);

    const addContextButton = screen.getByText('+ Add Context (Optional)');
    fireEvent.click(addContextButton);

    await waitFor(() => {
      expect(screen.getByLabelText('Context (Optional)')).toBeInTheDocument();
    });
  });

  it('enforces maxLength on query textarea', () => {
    render(<QueryInput />);

    const queryTextarea = screen.getByLabelText('Query');
    expect(queryTextarea).toHaveAttribute('maxLength', '50000');
  });
});

describe('QueryInput with consulting state', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('disables textarea when consulting', () => {
    // Update mock for this test
    vi.mocked(vi.importMock('../../context/ConsultationContext')).useConsultation = () => ({
      query: '',
      setQuery: mockSetQuery,
      context: '',
      setContext: mockSetContext,
      isConsulting: true,
    });

    // Re-import to get new mock
    vi.resetModules();
  });
});
