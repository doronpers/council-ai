# Web App Guide

Council AI includes a standalone web UI for running consultations, managing settings, viewing history, and using the LLM Response Reviewer.

## Architecture

The web app is built with:

- **React 18** with TypeScript
- **Vite** for build tooling
- **Dieter Rams-inspired design** - Minimal, functional, beautiful
- **Shared CSS tokens** - Consistent styling across main app and reviewer UI
- **Reusable components** - Modal, TagInput, and other shared UI elements

## Quick start (CLI)

1. Install web dependencies:

```bash
pip install -e ".[web]"
```

1. Start the server (with auto-reload):

```bash
council web --reload
```

1. Open the UI:

- `http://127.0.0.1:8000`

> Tip: `council ui` opens the UI in your default browser.

## 1-click launchers

The repo includes convenience launchers:

- **Standard**: `bin/launch-council-web.command` (macOS) / `bin/launch-council.bat` (Windows)
- **LAN mode**: `bin/launch-council-lan.command` / `bin/launch-council-lan.bat` (binds host so other devices can connect)
- **Persistent**: `bin/launch-council-persistent.command` / `bin/launch-council-persistent.bat` (auto-restart)

For reviewer-specific launchers and options (ports, no-browser, reload), see `documentation/REVIEWER_SETUP.md` (section: Launch the Reviewer).

For accessing a running host from another device:

- `connect-to-council.bat` (Windows helper)

## Local LLMs / custom endpoints

The UI supports OpenAI-compatible base URLs (e.g., Ollama, LM Studio, custom gateways).

Common base URLs:

- **Ollama**: `http://localhost:11434/v1`
- **LM Studio**: `http://localhost:1234/v1`

In the UI, set **Provider**, then set **Base URL** in Advanced Settings.

## History Management

The history panel provides comprehensive consultation management:

### Features

- **Search**: Real-time search across consultation history with debounced queries (Ctrl/Cmd+K to focus)
- **Filters**: Filter by date range, domain, and consultation mode
- **Tags & Notes**: Add structured tags and notes to consultations for better organization
  - Tokenized tag input with Enter to add, Backspace to remove
  - Explicit Save/Cancel buttons for metadata edits
- **Detail View**: Modal-based detail view with proper focus management
- **Comparison**: Select two consultations to compare synthesis and responses side-by-side
  - Prominent "Compare" button on each history item
  - Visual indicators showing which items are selected (Slot A/B)
  - Clear comparison bar with "View Comparison" button
- **Empty States**: Clear messaging when no results are found
- **Load More**: Incremental loading for longer histories

### Comparison Feature Discovery

The comparison feature is now more discoverable:

- Each history item has a prominent "Compare" button
- When one item is selected, a comparison bar appears showing "Select consultation B"
- Selected items are visually highlighted with badges (A/B)
- "View Comparison" button appears when both slots are filled

## First-Time User Experience

### Onboarding Wizard

First-time users are automatically presented with a comprehensive 6-step onboarding wizard that guides them through the entire setup process:

1. **Welcome & Overview** - Introduces Council AI concept, shows value proposition, and highlights key features (14 personas, 15 domains, multiple modes, free LM Studio option)

2. **Provider Selection** - Guides users through choosing between:
   - **LM Studio** (recommended for beginners) - Free, local, private, no API key needed
   - **Cloud Providers** - Anthropic, OpenAI, or Google Gemini (requires API key)

3. **Configuration** - Helps set up:
   - API key (for cloud providers) or base URL (for LM Studio)
   - Real-time validation with helpful error messages

4. **Domain Selection** - Explains domains with examples and recommends based on use case:
   - Shows domain descriptions
   - Pre-selects recommended personas for chosen domain

5. **Persona Introduction** - Introduces 2-3 key personas for the selected domain:
   - Shows persona emoji, name, title, and core question
   - Explains how personas provide diverse perspectives

6. **First Consultation** - Pre-fills an example query based on selected domain:
   - Guides through writing and submitting first consultation
   - Shows what to expect (individual responses + synthesis)

**Features:**

- Progress bar showing step X of Y
- "Skip for now" option on each step
- "Back" button for navigation
- Completion celebration
- Progress saved to localStorage (can resume if interrupted)

**Accessing Onboarding Later:**

- Click "📚 Take Tour" in the header menu
- Select "🎯 Getting Started" to restart onboarding

### Contextual Help System

Throughout the web app, contextual help icons (ℹ️) provide detailed information:

- **Provider Selection** - Explains differences between providers
- **Base URL** - Shows how to find LM Studio URL
- **Domain Selection** - Explains what each domain is for
- **Persona Selection** - Shows which personas work best together
- **Consultation Modes** - Explains when to use each mode
- **Configuration Fields** - Provides examples and best practices

Help tooltips are position-aware (automatically adjust to viewport) and include:

- Clear descriptions
- Examples
- Links to detailed documentation

### Components

- **HistoryPanel**: Main history display with search and filters
- **HistoryItem**: Individual consultation entry with edit/delete/view actions
- **HistorySearch**: Debounced search input with loading states
- **HistoryFilters**: Collapsible filter panel with date validation
- **TagInput**: Tokenized tag input component with validation
- **Modal**: Reusable modal component with accessibility features
- **ComparisonView**: Side-by-side consultation comparison

## Reviewer UI

The reviewer is available at:

- `http://127.0.0.1:8000/reviewer`

The reviewer UI shares header and navigation styles with the main app for a consistent experience.

For a dedicated reviewer launcher and detailed usage, see `documentation/REVIEWER_SETUP.md`.

## Error Handling & User Feedback

The web app includes comprehensive error handling and user feedback systems:

### Error Message System

- **Categorized Errors**: Network, validation, API, configuration, rate limiting, quota errors
- **User-Friendly Messages**: Clear, actionable error messages with technical details in expandable sections
- **Recovery Actions**: Contextual buttons like "Retry", "Open Settings", "Check Diagnostics"
- **Error Logging**: Client-side error logging with context and sanitization (sensitive data removed)

### Inline Validation

- **Real-Time Validation**: Inputs validate as you type (query, API key, base URL)
- **Visual Feedback**: Error states with red borders and error messages
- **Submit Button Tooltips**: Explains why button is disabled with specific validation errors
- **Field Hints**: Helpful hints and success indicators for valid inputs

### Progress Feedback

- **Detailed Progress Dashboard**: Shows individual persona progress, elapsed time, estimated time remaining
- **Status Messages**: Clear status updates during consultations
- **Cancel Functionality**: Ability to cancel consultations with confirmation
- **Error Recovery**: Automatic retry with exponential backoff for network errors

For detailed error handling documentation, see [Error Handling Guide](ERROR_HANDLING.md).

## Feature Discovery & Progressive Disclosure

### Feature Tours

Interactive step-by-step guided tours help users discover features:

- **Getting Started Tour**: Basic consultation flow (query, domain, submit)
- **Advanced Features Tour**: Comparison, TTS, pattern-coach mode
- **Configuration Tour**: Provider setup, custom personas
- **History Management Tour**: Search, filters, export

**Accessing Tours:**

- Click "📚 Take Tour" in the header menu
- Select a tour from the dropdown
- Tours highlight elements with overlays and provide explanations
- Progress is saved (can skip and resume later)

### Tiered Configuration

Configuration is organized into three tiers for progressive disclosure:

- **Basic Tier**: Essential settings (domain, provider, API key)
- **Intermediate Tier**: Personas, mode, model selection
- **Advanced Tier**: Base URL, temperature, max tokens, web search, reasoning modes

Each tier is collapsible, preventing new users from being overwhelmed while keeping advanced options accessible.

### Feature Highlights

- **Feature Cards**: Highlight new or popular features in empty states
- **"New" Badges**: Visual indicators for recently added features
- **Contextual Prompts**: Suggestions for unused features after certain actions
- **Help Icons**: Contextual help throughout the interface

## Component Library

### Modal Component

Reusable modal dialog with:

- Proper focus management (traps focus, restores on close)
- Escape key handling
- Backdrop click to close
- ARIA attributes for accessibility
- Body scroll lock when open

**Usage:**

```tsx
<Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="Modal Title">
  {/* Modal content */}
</Modal>
```

### TagInput Component

Tokenized tag input with:

- Enter to add tags
- Backspace to remove last tag
- Visual tag chips with remove buttons
- Tag validation (max length, max count, duplicates)
- Disabled state support

**Usage:**

```tsx
<TagInput tags={tags} onChange={setTags} placeholder="Add tags..." maxTagLength={50} maxTags={10} />
```

### Export Tools

Results can be exported as:

- Markdown (`.md`)
- JSON (`.json`)
- Copy synthesis to clipboard

Exports are available from the Results panel toolbar.

## Styling System

The app uses a shared CSS token system (`assets/css/shared.css`) for consistency:

- **Design tokens**: Colors, typography, spacing, shadows
- **Shared components**: Header, navigation, buttons
- **Theme support**: Light/dark mode via CSS variables
- **Responsive**: Mobile-first responsive design

Both the main app and reviewer UI import shared styles, ensuring visual consistency across the application.
