# Council AI - Roadmap & TODOs

**Last Updated**: 2026-01-18
**Single Source of Truth**: This file contains all TODOs, planned features, and roadmap items.

---

## ✅ Recently Completed

### Web UI Improvements (2026-01-16)

1. ✅ **Removed Legacy Search Route** - Deleted `/api/history/search_legacy` endpoint
2. ✅ **Added Tags/Notes Editing UI** - History items now support inline editing of tags and notes
3. ✅ **Added View Full Consultation Details** - Modal dialog to view complete consultation history
4. ✅ **Documented Google Docs Feature** - Enhanced TODO documentation with implementation steps

### Web UI Improvements (2026-01-18)

1. ✅ **History Search UI** - Debounced search UI with Ctrl/Cmd+K focus shortcut
2. ✅ **Advanced Filtering** - Date, domain, and mode filters in the history panel
3. ✅ **Consultation Export** - Export menu for markdown and JSON results
4. ✅ **Consultation Comparison** - Side-by-side comparison view for history entries
5. ✅ **Error Boundaries** - App-level error boundaries with fallback UI

### Core Improvements (2026-01-16)

5. ✅ **Concurrent Streaming** - Optimized streaming consultations to run personas in parallel
6. ✅ **Enhanced API Key Detection** - Improved detection of multiple LLM providers
7. ✅ **Robust Fallback Mechanism** - Better fallback handling for LLM providers
8. ✅ **Desktop Launcher** - Created `launch-council-web.command` for macOS

---

## 🔴 High Priority

_No high priority items at this time._

---

## 🟡 Medium Priority

### Web UI Enhancements

#### 1. Session Management UI

- **Status**: 📝 TODO
- **Description**: Backend has session endpoints (`/api/sessions`, `/api/sessions/{id}`), but no UI
- **Implementation**: Add session view/management to history panel
- **Files**: `src/council_ai/webapp/src/components/History/`
- **Estimated Effort**: 4-6 hours

### Integration & Architecture

#### 5. Migrate to shared-ai-utils LLMManager

- **Status**: ✅ COMPLETED
- **Description**: Integrated with shared-ai-utils LLM provider abstraction
- **Implementation**:
  - Added shared-ai-utils as dependency from GitHub repository
  - Using shared_ai_utils.llm.LLMManager for provider management
  - Maintained existing CLI flags/envs compatibility
- **Files**: `pyproject.toml`, `src/council_ai/providers/`, `src/council_ai/core/council.py`
- **Completed**: 2026-01-16

#### 6. Migrate to shared-ai-utils ConfigManager

- **Status**: ✅ COMPLETED
- **Description**: Integrated with shared-ai-utils config manager
- **Implementation**:
  - Using shared_ai_utils.config.ConfigManager
  - Maintained YAML/env compatibility
  - Supports dot-notation key access
- **Files**: `pyproject.toml`, `src/council_ai/core/config.py`
- **Completed**: 2026-01-16

#### 7. Add Pattern-Coach Mode

- **Status**: 📝 TODO
- **Description**: Add pattern-aware council mode with recommendations from feedback-loop
- **Implementation**:
  - Add council "pattern-coach" mode hitting feedback-loop (library or REST)
  - Allow feedback-loop to call council personas for pattern review
- **Files**: `src/council_ai/core/council.py`, new mode implementation
- **Estimated Effort**: 2-3 days
- **Reference**: `planning/integration-plan.md`

#### 8. Add QA Command for sono-eval

- **Status**: 📝 TODO
- **Description**: Optional QA command to run council outputs through sono-eval assessment
- **Implementation**:
  - Add council QA command that calls sono-eval assessment engine
  - Add "assessment" domain preset that points to sono-eval API
- **Files**: `src/council_ai/cli.py`, new command
- **Estimated Effort**: 2-3 days
- **Reference**: `planning/integration-plan.md`

---

## 🟢 Low Priority

### Web UI Enhancements

#### 1. Consultation Sharing

- **Status**: 📝 TODO
- **Description**: No way to share consultations with others
- **Implementation**: Add share/permalink functionality
- **Files**: `src/council_ai/webapp/src/components/History/HistoryItem.tsx`
- **Estimated Effort**: 2-3 hours

#### 2. Keyboard Shortcuts

- **Status**: 📝 TODO
- **Description**: Add keyboard shortcuts for common actions beyond history search (Ctrl/Cmd+K)
- **Implementation**: Add shortcuts for submit and navigation (e.g., Ctrl+Enter, / to focus query)
- **Files**: `src/council_ai/webapp/src/App.tsx`, new hook
- **Estimated Effort**: 2-3 hours

#### 3. Loading States Review

- **Status**: 📝 TODO
- **Description**: Some async operations may lack loading indicators
- **Implementation**: Review and add loading states where missing
- **Files**: Various components
- **Estimated Effort**: 2-3 hours

#### 4. Mobile Responsiveness Review

- **Status**: 📝 TODO
- **Description**: Some components may need mobile optimization
- **Implementation**: Review and enhance mobile CSS
- **Files**: `src/council_ai/webapp/assets/css/mobile.css`, various components
- **Estimated Effort**: 3-4 hours

### Features

#### 15. Google Docs Content Fetching

- **Status**: ⚠️ Incomplete
- **Description**: Google Docs URL fetching requires Google API credentials
- **Current State**: Returns `None`, relies on manually exported/pasted content
- **Implementation**:
  - Set up Google API credentials at `~/.config/council-ai/google_credentials.json`
  - Install `google-api-python-client`: `pip install google-api-python-client`
  - Implement OAuth2 flow for authentication
  - Use Google Docs API to fetch document content
- **Files**: `src/council_ai/webapp/reviewer.py` (line ~1067)
- **Estimated Effort**: 1-2 days
- **Priority**: Low (workaround exists - manual paste)

#### 16. Optional MemU Backend for History

- **Status**: 📝 TODO
- **Description**: Add MemU-backed conversation/history persistence as optional memory backend
- **Implementation**:
  - Add optional MemU backend in council for history storage
  - Feature-flag default off
  - Integration test with in-memory backend
- **Files**: `src/council_ai/core/history.py`
- **Estimated Effort**: 2-3 days
- **Reference**: `planning/integration-plan.md`

---

## 📋 Future Considerations

### Phase 3 Integration Items (from integration-plan.md)

These are lower priority and depend on Phase 1 & 2 completion:

- **drrweb integration**: Add council consult server action for creative intent detection
- **sonotheia-examples integration**: Import regulated-risk presets (SAR/risk scoring personas)
- **tex-assist-coding integration**: Reference shared pattern library (documentation-only)

### Testing & Quality

- Unit tests around provider/config swaps (mocked LLM calls)
- CLI smoke tests: `council quickstart`, pattern CRUD via shared manager
- Contract tests for sono-eval QA hook against local server stub

---

## 📊 Progress Summary

- **Completed**: 13 items (2026-01-16 to 2026-01-18)
- **High Priority**: 0 items
- **Medium Priority**: 5 items
- **Low Priority**: 6 items
- **Future Considerations**: Multiple items (depends on integration phases)

---

## 📝 Notes

- **Integration Plan**: See `planning/integration-plan.md` for detailed integration strategy
- **Changelog**: See `CHANGELOG.md` for release history
- **Contributing**: See `CONTRIBUTING.md` for contribution guidelines

---

## 🔄 How to Update This File

1. When starting work on a TODO, change status from `📝 TODO` to `🚧 In Progress`
2. When completing, move to "Recently Completed" section and mark as `✅`
3. Add new TODOs with appropriate priority and estimated effort
4. Update "Last Updated" date
5. Keep items organized by priority and category
