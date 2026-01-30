/**
 * Input validation utilities
 */

import React from 'react';

export interface ValidationRule {
  validate: (value: string) => boolean;
  message: string;
}

export const ValidationRules = {
  /**
   * Query validation
   */
  query: {
    notEmpty: {
      validate: (value: string) => value.trim().length > 0,
      message: 'Query cannot be empty',
    },
    maxLength: (max: number = 2000): ValidationRule => ({
      validate: (value: string) => value.length <= max,
      message: `Query must be ${max} characters or less`,
    }),
    minLength: (min: number = 5): ValidationRule => ({
      validate: (value: string) => value.trim().length >= min,
      message: `Query must be at least ${min} characters`,
    }),
  },

  /**
   * API key validation
   */
  apiKey: {
    notEmpty: {
      validate: (value: string) => value.trim().length > 0,
      message: 'API key cannot be empty',
    },
    notPlaceholder: {
      validate: (value: string) =>
        !['your-api-key-here', 'placeholder', 'xxx'].includes(value.toLowerCase()),
      message: 'Please enter your actual API key',
    },
    minLength: (min: number = 10): ValidationRule => ({
      validate: (value: string) => value.length >= min,
      message: `API key must be at least ${min} characters`,
    }),
  },

  /**
   * URL validation
   */
  url: {
    valid: {
      validate: (value: string) => {
        if (!value.trim()) return true; // Optional field
        try {
          new URL(value);
          return true;
        } catch {
          return false;
        }
      },
      message: 'Please enter a valid URL',
    },
  },

  /**
   * Email validation
   */
  email: {
    valid: {
      validate: (value: string) => {
        if (!value.trim()) return true; // Optional field
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
      },
      message: 'Please enter a valid email address',
    },
  },

  /**
   * Number validation
   */
  number: {
    valid: {
      validate: (value: string) => !isNaN(Number(value)) && value.trim().length > 0,
      message: 'Please enter a valid number',
    },
    min: (min: number): ValidationRule => ({
      validate: (value: string) => Number(value) >= min,
      message: `Value must be at least ${min}`,
    }),
    max: (max: number): ValidationRule => ({
      validate: (value: string) => Number(value) <= max,
      message: `Value must be at most ${max}`,
    }),
  },
};

/**
 * Validate a field against multiple rules
 */
export const validateField = (value: string, rules: ValidationRule[]): string | null => {
  for (const rule of rules) {
    if (!rule.validate(value)) {
      return rule.message;
    }
  }
  return null;
};

/**
 * Validate multiple fields
 */
export const validateFields = (
  fields: Record<string, string>,
  rules: Record<string, ValidationRule[]>
): Record<string, string> => {
  const errors: Record<string, string> = {};

  for (const [fieldName, fieldValue] of Object.entries(fields)) {
    const fieldRules = rules[fieldName];
    if (!fieldRules) continue;

    const error = validateField(fieldValue, fieldRules);
    if (error) {
      errors[fieldName] = error;
    }
  }

  return errors;
};

/**
 * React hook for form validation
 */
export const useFormValidation = <T extends Record<string, string>>(
  initialValues: T,
  rules: Record<keyof T, ValidationRule[]>
) => {
  const [values, setValues] = React.useState(initialValues);
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [touched, setTouched] = React.useState<Record<string, boolean>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));

    // Validate on change if field has been touched
    if (touched[name]) {
      const fieldRules = rules[name as keyof T];
      if (fieldRules) {
        const error = validateField(value, fieldRules);
        setErrors((prev) => ({
          ...prev,
          [name]: error || '',
        }));
      }
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    const fieldRules = rules[name as keyof T];
    if (fieldRules) {
      const error = validateField(value, fieldRules);
      setErrors((prev) => ({
        ...prev,
        [name]: error || '',
      }));
    }
  };

  const validate = (): boolean => {
    const newErrors = validateFields(values, rules as Record<string, ValidationRule[]>);
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  };

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validate,
    reset,
    setValues,
  };
};
