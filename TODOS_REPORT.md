# TODO Report - Council AI

**⚠️ DEPRECATED**: This file has been consolidated into [ROADMAP.md](./ROADMAP.md).
Please refer to ROADMAP.md for the current TODO list and roadmap.

Generated: 2026-01-16 (Archived)

## ✅ Completed Web UI TODOs

### 1. Removed Legacy Search Route
- **File**: `src/council_ai/webapp/app.py`
- **Status**: ✅ Completed
- **Action**: Removed `/api/history/search_legacy` endpoint that was marked for removal

### 2. Added Tags/Notes Editing UI
- **Files**:
  - `src/council_ai/webapp/src/components/History/HistoryItem.tsx`
  - `src/council_ai/webapp/src/types/index.ts`
  - `src/council_ai/webapp/src/utils/api.ts`
- **Status**: ✅ Completed
- **Features Added**:
  - Edit button on history items
  - Inline editing form for tags (comma-separated) and notes
  - Save/cancel functionality
  - Visual display of tags and notes in history list

### 3. Added View Full Consultation Details
- **Files**:
  - `src/council_ai/webapp/src/components/History/HistoryItem.tsx`
  - `src/council_ai/webapp/src/components/History/HistoryPanel.tsx`
  - `src/council_ai/webapp/src/utils/api.ts`
- **Status**: ✅ Completed
- **Features Added**:
  - View button on history items
  - Modal dialog showing full consultation details
  - Displays query, context, all responses, and synthesis
  - Click outside to close

### 4. Documented Google Docs Feature
- **File**: `src/council_ai/webapp/reviewer.py`
- **Status**: ✅ Completed
- **Action**: Enhanced TODO documentation with implementation steps

---

## 📋 Remaining TODOs and Incomplete Features

### 1. Google Docs Content Fetching (Reviewer)
- **File**: `src/council_ai/webapp/reviewer.py` (line ~1067)
- **Status**: ⚠️ Incomplete
- **Description**: Google Docs URL fetching requires Google API credentials
- **Current State**: Returns `None`, relies on manually exported/pasted content
- **Requirements**:
  - Google API credentials at `~/.config/council-ai/google_credentials.json`
  - Install `google-api-python-client`
  - Implement OAuth2 flow
  - Use Google Docs API to fetch content
- **Priority**: Low (workaround exists - manual paste)

### 2. Integration Plan Items (Planning Document)
- **File**: `planning/integration-plan.md`
- **Status**: 📝 Planned
- **Description**: Integration tasks with other repositories
- **Key Items**:
  - Swap provider glue to `shared_ai_utils.llm.LLMManager`
  - Replace config loading with `shared_ai_utils.config.ConfigManager`
  - Migrate feedback-loop to shared utilities
  - Add council "pattern-coach" mode
  - Add council QA command for sono-eval
  - Add optional MemU backend for history storage
- **Priority**: Medium (architectural improvements)

### 3. Consultation Auto-Save Comment
- **File**: `src/council_ai/webapp/app.py` (line ~433)
- **Status**: ℹ️ Informational (not a TODO)
- **Description**: Comment explains that consultations are auto-saved, but API allows updating tags/notes
- **Action**: No action needed - this is working as designed

---

## 🔍 Other Potential Improvements (Not Documented as TODOs)

### 1. History Search UI
- **Status**: Missing
- **Description**: Backend has `/api/history/search` endpoint, but no UI component
- **Suggestion**: Add search bar to HistoryPanel component

### 2. Session Management UI
- **Status**: Missing
- **Description**: Backend has session endpoints (`/api/sessions`, `/api/sessions/{id}`), but no UI
- **Suggestion**: Add session view/management to history panel

### 3. Consultation Export
- **Status**: Missing
- **Description**: No way to export consultations (JSON, Markdown, PDF)
- **Suggestion**: Add export functionality to history items

### 4. Consultation Sharing
- **Status**: Missing
- **Description**: No way to share consultations with others
- **Suggestion**: Add share/permalink functionality

### 5. Advanced Filtering
- **Status**: Missing
- **Description**: History panel shows all consultations, no filtering by date/domain/mode
- **Suggestion**: Add filter controls to HistoryPanel

### 6. Consultation Comparison
- **Status**: Missing
- **Description**: No way to compare multiple consultations side-by-side
- **Suggestion**: Add comparison view

### 7. Keyboard Shortcuts
- **Status**: Missing
- **Description**: No keyboard shortcuts for common actions
- **Suggestion**: Add keyboard shortcuts (e.g., Ctrl+Enter to submit)

### 8. Mobile Responsiveness
- **Status**: Partial
- **Description**: Some components may need mobile optimization
- **Suggestion**: Review and enhance mobile CSS

### 9. Error Boundaries
- **Status**: Missing
- **Description**: React error boundaries not implemented
- **Suggestion**: Add error boundaries for better error handling

### 10. Loading States
- **Status**: Partial
- **Description**: Some async operations may lack loading indicators
- **Suggestion**: Review and add loading states where missing

---

## 📊 Summary

- **Completed**: 4 web UI TODOs
- **Remaining**: 1 incomplete feature (Google Docs - low priority)
- **Planned**: Integration plan items (medium priority)
- **Potential Improvements**: 10 identified areas for enhancement

---

## 🎯 Recommended Next Steps

1. **High Priority**: None (all critical TODOs completed)
2. **Medium Priority**:
   - Implement history search UI
   - Add session management UI
   - Consider integration plan items
3. **Low Priority**:
   - Google Docs fetching (if needed)
   - Export functionality
   - Advanced filtering
   - Other enhancements as needed
