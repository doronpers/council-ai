# Changelog

All notable changes to Council AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- **Added**

- Dieter Rams design audit improvements (January 2026):
  - Favicon (SVG) for web app
  - Type safety: replaced `any` with `unknown` / `Record<string, unknown>` in ConfigDiagnostics, errors.ts, errorLogger.ts, api.ts
  - API error handling: typed parsing, explicit property access, rethrow of `ApiError` in catch so structured errors are not replaced by generic "Request failed"
  - Error logging: log safe error shape (name/message or placeholder) instead of raw error objects to avoid leaking stack/serialized state
  - errors.ts: avoid `"[object Object]"` when classifying plain objects; use `typeof` checks and `'Unknown error'` fallback

- Comprehensive UX Enhancement (January 2026):
  - **Onboarding Wizard**: 6-step guided setup for first-time users (welcome, provider, config, domain, personas, first consultation)
  - **Error Handling System**: Categorized error messages with recovery actions, inline validation, and error logging
  - **Feature Discovery**: Interactive tours, tiered configuration, contextual help icons, and feature highlights
  - **Query Templates**: Example queries by domain and use case
  - **Smart Recommendations**: Domain and persona recommendations based on query analysis
  - **Enhanced Progress Dashboard**: Individual persona progress, time estimates, and cancel functionality
  - **Improved Comparison UI**: More discoverable comparison feature with visual indicators
  - **TTS Surface**: Text-to-speech toggle moved to results toolbar for better discoverability
  - **Pattern-Coach Mode**: Added to mode selection with explanation and documentation links

- Test coverage and robustness improvements:
  - **Reviewer module**: 73 comprehensive tests covering JSON extraction/parsing, request validation, council building, prompt generation, synthesis fallbacks, streaming and API endpoints (`tests/test_reviewer.py`, `tests/test_webapp_reviewer_api.py`).
  - **Web Search tool**: 6 tests for provider behavior, auto-detection, formatting, and function definitions (`tests/test_web_search.py`).
  - **Personal Integration**: 4 tests for detection, manual integration, config loading and status (`tests/test_personal_integration.py`).
  - **Repository Reviewer tool**: 5 tests for context gathering, file truncation, structure formatting and delegation (`tests/test_repository_reviewer.py`).
  - Added small shim `launch-council.py` to improve testability for launcher utilities.

- **Changed**

- CI and test stability updates:
  - Tests that depend on environment-specific API keys were made deterministic (tests now explicitly control or clear environment variables before running).
  - Several assertions relaxed to tolerate both abort and explicit error flows where behavior depends on runtime environment and external services.

- **Fixed**

- Backwards compatibility shims and test fixes:
  - Added `src/council_ai/cli_persona.py` and `src/council_ai/cli_domain.py` to provide compatibility for legacy imports used in tests and external tooling.
  - Added `launch-council.py` shim at repo root to satisfy launcher resolution tests.
  - Fixed multiple failing tests by correcting patched import paths and improving mocks. All new tests pass locally.
  - Addressed intermittent network-dependent test failures by improving mocks and making tests resilient to external API errors.

- **Other**

- Committed and pushed all changes and new tests to `origin/main`.

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
