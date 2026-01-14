# Changelog

All notable changes to Council AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- LLM Response Reviewer - Supreme Court-style review system for evaluating multiple LLM responses
  - 7-justice default council with optional 9-justice Sonotheia mode
  - Multi-dimensional scoring (accuracy, consistency, insights, error detection)
  - REST API endpoints for programmatic access
  - Streaming support via Server-Sent Events
  - Dedicated launcher script (`launch-reviewer.py`)
  - Web UI for interactive review sessions
  - Comprehensive documentation in `documentation/REVIEWER_SETUP.md`

### Changed
- Improved installation command documentation with proper quoting for bash compatibility
- Enhanced API key configuration documentation with cross-references

## [1.0.0] - 2026-01-11

### Added
- Initial release of Council AI
- 7 built-in expert personas (Rams, Kahneman, Grove, Taleb, Holman, Dempsey, Treasure)
- 12 domain presets (coding, business, startup, product, leadership, creative, writing, career, decisions, devops, data, general)
- Multi-provider LLM support (Anthropic, OpenAI, custom HTTP endpoints)
- 5 consultation modes (individual, synthesis, sequential, debate, vote)
- Full CLI with interactive mode
- Python API with async support
- Session tracking and history
- Export to Markdown and JSON
- Comprehensive test suite (53+ tests)
- Documentation and examples
- Contributing guidelines

### Features
- **Council Creation**: Domain-based or custom assembly
- **Persona Management**: Full CRUD operations, trait management
- **Consultation**: Multiple modes with synthesis
- **Customization**: Create custom personas, adjust weights, modify traits
- **Configuration**: YAML-based config with CLI management
- **Extensibility**: Hooks for pre/post processing

### Documentation
- Comprehensive README with examples
- Quickstart demo (no API key required)
- Contributing guidelines
- Security policy
- Example scripts

[1.0.0]: https://github.com/doronpers/council-ai/releases/tag/v1.0.0
