# LLM Cognition & Development Notes

This document captures the thinking process, design decisions, and architectural insights encountered during the development of Council AI. It serves as a reference for understand "how" and "why" certain choices were made.

## Principles of Interaction

1.  **Systematic Problem Solving**: When faced with multiple failures (like pre-commit blocks), I prioritize by "ease of fix" vs "impact." I start with low-hanging fruit (docstrings, unused imports) to clear the "noise" and then tackle complex logic or type errors.
2.  **Iterative Refinement**: I don't aim for perfection in the first pass if the problem is multifaceted. I apply a batch of fixes, re-run the validation, and narrow down the remaining issues.
3.  **Proactive Maintenance**: If I see a script like `get_recent_files.py` that is becoming unwieldy or non-standard, I refactor it early to prevent technical debt.

## Technical Deep Dives

### Pre-commit & CI/CD
- **Problem**: `detect-secrets` was extremely slow due to a massive baseline file containing false positives from cache directories.
- **Solution**: Added specific `exclude` patterns in `.pre-commit-config.yaml` to ignore `.mypy_cache`, `.venv`, and other transient folders. This restored the health of the hook.

### Type Safety with Mypy
- ** SQLAlchemy vs Mypy**: Traditional `declarative_base()` is hard for Mypy to trace. Moving to `class Base(DeclarativeBase): pass` (SQLAlchemy 2.0 style) provides much better type inference for models.
- **Async Iterators**: In `tts.py`, the `async def` on an abstract method that returns an `AsyncIterator` was causing issues because an `async def` implies a `Coroutine`. Changing it to a standard `def` that returns the `AsyncIterator` type correctly matches the implementation.

## Lessons Learned

- **Syntax Errors in Replacements**: When using `replace_file_content` on large f-strings, it's easy to accidentally miss a closing quote or introduce a mismatch if the target content isn't perfectly matched. **Action**: Re-read the file around the error line to ensure indentation and string termination are intact.
- **YAML Multi-document**: K8s files often have multiple documents. Standard `check-yaml` hooks need the `--allow-multiple-documents` flag to avoid failing on these files.

## Meta-Thinking

When the user asks for "thinking notes," I interpret this as a desire for a "Developer Journal" or "Design Doc." I aim to provide context that isn't always obvious from the code diffs alone.
