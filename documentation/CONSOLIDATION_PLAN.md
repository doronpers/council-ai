# Documentation Consolidation Plan

## Summary

This document lists recommended small consolidations to reduce duplication and improve discoverability. These are low-risk, incremental edits intended to be implemented via small PRs.

## Recommended consolidations

1. **Web Search & Reasoning** (`WEB_SEARCH_AND_REASONING.md`)
   - Make `WEB_SEARCH_AND_REASONING.md` the canonical guide for enabling web search providers and reasoning modes.
   - Move any overlapping explanation from `WEB_APP.md` into the canonical guide (keep webapp-specific run instructions in `WEB_APP.md`).

2. **LLM Response Reviewer** (`REVIEWER_SETUP.md`)
   - Centralize reviewer configuration, examples, and API usage in `REVIEWER_SETUP.md` and add a short "Quick Start" example.
   - Remove duplicated content from UI docs and link back to the canonical reviewer guide.

3. **Configuration Templates** (`CONFIGURATION.md`)
   - Ensure `.env` examples and precedence rules are consolidated in `CONFIGURATION.md`.
   - Add a short subsection showing realistic examples (local LM Studio vs cloud provider).

4. **Onboarding / Start Here**
   - Create a short "Start Here" page if needed (index or `documentation/README.md` is acceptable) that links Quickstart, Web App, Reviewer, and Examples.

5. **Small housekeeping tasks**
   - Fix obvious typos and broken links.
   - Ensure all documentation pages have a canonical location and are listed in `documentation/README.md`.

## Implementation notes

- Perform each consolidation in a dedicated small PR with tests/checks: update links, run `pre-commit`, and add a changelog entry for significant structural changes.
- Prefer redirecting in-place via cross-links when uncertain instead of deleting content immediately.

## Next steps

- Review the plan and mark items you'd like me to implement.
- After approval, I will submit small PRs for each consolidation, starting with the Web Search & Reasoning canonicalization and the Reviewer guide consolidation.
