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
- **Empty States**: Clear messaging when no results are found
- **Load More**: Incremental loading for longer histories

## Onboarding

First-time users see a guided onboarding wizard that walks through:

- Choosing a domain
- Selecting members
- Configuring provider and API key (see `documentation/WEB_SEARCH_AND_REASONING.md` for details on enabling web search and reasoning modes)
- Writing the first query

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
