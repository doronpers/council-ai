# Changelog

All notable changes to Council AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- **Added**

- LLM Response Reviewer - Supreme Court-style review system for evaluating multiple LLM responses
  - 9-justice default council with specialist support
  - Multi-dimensional scoring (accuracy, consistency, insights, error detection, Sonotheia relevance)
  - REST API endpoints for programmatic access
  - Streaming support via Server-Sent Events
  - Dedicated launcher script (`launch-reviewer.py`)
  - Web UI for interactive review sessions
  - Comprehensive documentation in `documentation/REVIEWER_SETUP.md`
- History search keyboard shortcut (Ctrl/Cmd+K) for the web UI

- **Changed**

- Improved installation command documentation with proper quoting for bash compatibility
- Enhanced API key configuration documentation with cross-references
- Updated persona roster documentation and IDs to reflect 14 built-in personas
- Refined history panel UI styling and filter accessibility
- Design Audit & Polish:
  - Updated Persona configurations (Rams, Kahneman, Taleb) with specific default models (`gpt-4-turbo`, `claude-3-opus`) for more nuanced responses
  - Replaced "Custom Members" text input in Web UI with a visual selection grid
  - Added 120s timeout to council member queries to prevent system hangs
  - Refactored frontend logic for better modularity
- **Frontend Architecture Migration (v2.0.0)**:
  - Migrated from Vanilla JavaScript to React 18 with TypeScript
  - Created 25+ modular components organized by feature area
  - Implemented Context API for state management
  - Added TypeScript for type safety
  - Preserved Dieter Rams aesthetic (all CSS retained)
  - Build produces optimized chunks: react-vendor (138KB), main (26KB)

- **Fixed**

- Fixed 12 failing tests by correcting import paths and mock configurations
- Removed hardcoded developer path for MemU integration (security issue)
- Made MemU integration configurable via `MEMU_PATH` environment variable
- Standardized placeholder API key detection across all modules using `is_placeholder_key()` function
- Improved error handling in CLI to catch all exception types
- Fixed import sorting issues
- Extracted duplicated council assembly code into reusable helper function
- Improved test infrastructure with better mocking support
- Surface history search errors as notifications instead of silent console errors

## [1.0.0] - 2026-01-11

- **Added**

- Initial release of Council AI
- 9 built-in expert personas (Rams, Kahneman, Grove, Taleb, Holman, Dempsey, Treasure, signal_analyst, compliance_auditor)
- 14 domain presets (coding, business, startup, product, leadership, creative, writing, career, decisions, devops, data, general, llm_review, sonotheia)
- Multi-provider LLM support (Anthropic, OpenAI, custom HTTP endpoints)
- 5 consultation modes (individual, synthesis, sequential, debate, vote)
- Full CLI with interactive mode
- Python API with async support
- Session tracking and history
- Export to Markdown and JSON
- Comprehensive test suite (53+ tests)
- Documentation and examples
- Contributing guidelines

- **Features**

- **Council Creation**: Domain-based or custom assembly
- **Persona Management**: Full CRUD operations, trait management
- **Consultation**: Multiple modes with synthesis
- **Customization**: Create custom personas, adjust weights, modify traits
- **Configuration**: YAML-based config with CLI management
- **Extensibility**: Hooks for pre/post processing

- **Documentation**

- Comprehensive README with examples
- Quickstart demo (no API key required)
- Contributing guidelines
- Security policy
- Example scripts

[1.0.0]: https://github.com/doronpers/council-ai/releases/tag/v1.0.0
