/**
 * TagInput Component - Tokenized tag input with explicit Save/Cancel
 */
import React, { useState, KeyboardEvent, useRef } from 'react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  maxTagLength?: number;
  maxTags?: number;
}

const TagInput: React.FC<TagInputProps> = ({
  tags,
  onChange,
  placeholder = 'Add tags...',
  disabled = false,
  maxTagLength = 50,
  maxTags = 10,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleInputKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (disabled) return;

    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      const newTag = inputValue.trim();

      // Validate tag
      if (newTag.length === 0) {
        setInputValue('');
        return;
      }

      if (newTag.length > maxTagLength) {
        // Could show error message here
        return;
      }

      if (tags.length >= maxTags) {
        // Could show error message here
        return;
      }

      // Check for duplicates (case-insensitive)
      const tagLower = newTag.toLowerCase();
      if (!tags.some((tag) => tag.toLowerCase() === tagLower)) {
        onChange([...tags, newTag]);
      }
      setInputValue('');
    } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
      // Remove last tag when backspace is pressed on empty input
      onChange(tags.slice(0, -1));
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    if (disabled) return;
    onChange(tags.filter((tag) => tag !== tagToRemove));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    setInputValue(e.target.value);
  };

  return (
    <div className="tag-input-container">
      <div
        className={`tag-input-wrapper ${focused ? 'tag-input-wrapper--focused' : ''} ${disabled ? 'tag-input-wrapper--disabled' : ''}`}
        onClick={() => !disabled && inputRef.current?.focus()}
      >
        {tags.map((tag, index) => (
          <span key={`${tag}-${index}`} className="tag-chip">
            {tag}
            {!disabled && (
              <button
                type="button"
                className="tag-chip-remove"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveTag(tag);
                }}
                aria-label={`Remove ${tag}`}
              >
                ×
              </button>
            )}
          </span>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleInputKeyDown}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={tags.length === 0 ? placeholder : ''}
          disabled={disabled}
          className="tag-input-field"
        />
      </div>
      {tags.length > 0 && (
        <div className="tag-input-hint">Press Enter to add, Backspace to remove last tag</div>
      )}
    </div>
  );
};

export default TagInput;
