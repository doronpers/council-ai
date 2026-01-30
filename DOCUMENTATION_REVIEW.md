# Documentation Review and Revision Plan

**Date:** January 25, 2026
**Status:** Comprehensive review complete with detailed findings and action plan

---

## Executive Summary

The Council AI documentation is largely well-organized but suffers from:

1. **Redundancy**: Multiple quick-start guides scattered across root and documentation/
2. **Outdated content**: Setup guides reference obsolete scripts and processes
3. **Unclear structure**: 6+ setup-related files with overlapping information
4. **Weak navigation**: Entry points are unclear for new users (QUICK_START.md vs README.md)
5. **Planning noise**: Planning documents mixed with user-facing docs

**Total identified issues:** 23 items requiring consolidation, correction, or removal

---

## Issues Identified

### Category 1: Redundant Quick Start / Setup Guides (CRITICAL)

**Files with overlapping quick-start content:**

1. `README.md` (lines 1-100) - Has "Quickstart (Zero Cost)"
2. `QUICK_START.md` (root level) - Full setup guide
3. `SETUP_VENV.md` - Virtual environment setup
4. `VENV_MANAGEMENT.md` - Venv troubleshooting (300 lines!)
5. `WHICH_REPO.md` - Repository selection guide
6. `documentation/README.md` - Links to all guides

**Impact:** New users see 6+ conflicting entry points and don't know where to start
**Severity:** 🔴 HIGH

**Recommendation:** Consolidate into single, clear flow:

- **README.md** = Marketing + "First 5 minutes" (keep it short: 200 lines max)
- **GETTING_STARTED.md** (new) = Detailed setup with virtual env instructions
- Archive SETUP_VENV.md, VENV_MANAGEMENT.md, QUICK_START.md (keep as redirects in Git history)

---

### Category 2: Repository Confusion (MEDIUM)

**Files causing confusion about dual-repo workflow:**

1. `WHICH_REPO.md` - Explains council-ai vs council-ai-personal
2. `QUICK_START.md` - Has "Which Directory Should I Use?" section
3. `README.md` - Has "Repository Structure" section with repo info
4. `documentation/README.md` - Links to main README

**Impact:** Users unsure which repo to work in; duplicated guidance
**Severity:** 🟡 MEDIUM

**Recommendation:**

- Consolidate repo guidance into single `REPOSITORY_STRUCTURE.md`
- Link from README.md with clear "start here" section
- Archive WHICH_REPO.md (content moved to REPOSITORY_STRUCTURE.md)

---

### Category 3: Web Search & Reasoning Documentation (MEDIUM)

**Overlapping content:**

- `WEB_APP.md` (lines ~150-200) - Mentions web search setup
- `WEB_SEARCH_AND_REASONING.md` (463 lines) - Comprehensive guide
- `QUICK_REFERENCE.md` (lines 20-50) - Code examples for web search

**Issue:** Users can't tell which is canonical; WEB_APP.md duplicates reasoning explanation
**Severity:** 🟡 MEDIUM

**Recommendation:**

- Keep `WEB_SEARCH_AND_REASONING.md` as canonical
- Remove reasoning explanation from WEB_APP.md (leave web search config basics)
- Add cross-link in WEB_APP.md: "For full web search and reasoning guide, see [Web Search & Reasoning](WEB_SEARCH_AND_REASONING.md)"

---

### Category 4: Outdated or Incorrect Content (MEDIUM)

**Specific issues:**

1. **SETUP_VENV.md** (94 lines)
   - References `./scripts/setup-venv.sh` (is this the right path?)
   - References `activate-env` scripts (may not exist in current setup)
   - Status: Potentially obsolete; should verify script locations
   - **Action:** Archive with deprecation notice

2. **VENV_MANAGEMENT.md** (300 lines!)
   - Focuses on troubleshooting double venv activation
   - Very specialized problem; not onboarding content
   - **Action:** Move to `TROUBLESHOOTING.md` or archive

3. **CONTRIBUTING.md** (lines 1-100)
   - Still accurate for contributing but could reference GETTING_STARTED
   - No major issues but could be streamlined

4. **WEB_APP.md** (line ~80)
   - References "LAN mode" launchers; verify they exist in `bin/`
   - **Action:** Verify launcher filenames and update if changed

---

### Category 5: Planning/Internal Documents Mixed in User Docs (LOW)

**Files that shouldn't be in user-facing docs:**

1. `CODEX_AUTOMATION.md` - Internal AI agent automation
2. `CODEX_ENV_SETUP.md` - Internal setup instructions
3. `MERGE_INSTRUCTIONS.md` - Internal merge procedure
4. `CONFLICT_RESOLUTION_GUIDE.md` - Internal conflict handling
5. `ARCHETYPE_GUIDE.md` - Internal persona archetype system
6. `/Archive/*` (8 report files) - Project management artifacts

**Impact:** Clutters root directory; confuses new users
**Severity:** 🟢 LOW (but annoying)

**Recommendation:**

- Move to `/documentation/internal/` or `/planning/`
- Update `.gitignore` or mark as "internal" in names
- Remove from primary navigation

---

### Category 6: Minor Documentation Gaps or Improvements

**Missing or incomplete guidance:**

1. **No troubleshooting guide** - Users hitting errors have nowhere to go
   - Recommend: Create `TROUBLESHOOTING.md` with common issues

2. **Configuration precedence unclear** - `CONFIGURATION.md` exists but is not well-linked from README
   - Recommend: Add link in README under "Configuration" section

3. **No "Common Tasks" guide** - e.g., "How do I add a custom persona?"
   - This exists in CONTRIBUTING.md but isn't discoverable
   - Recommend: Create `COMMON_TASKS.md` or expand documentation/README.md

4. **LLM Response Reviewer** - Good guide but buried
   - Referenced in WEB_APP.md and documentation/README.md
   - Recommend: Add to primary README "Features" section with link to REVIEWER_SETUP.md

---

## Proposed New Documentation Structure

### Root-Level (High-Level Only)

```
README.md                          # Marketing + "Getting Started" (200 lines)
GETTING_STARTED.md (new)          # Detailed setup + venv guide
REPOSITORY_STRUCTURE.md (new)     # Explains dual-repo workflow
CONTRIBUTING.md                    # For contributors (unchanged)
SECURITY.md                        # Security guidelines (unchanged)
CHANGELOG.md                       # Release notes (unchanged)
LICENSE                            # MIT (unchanged)
```

### Documentation Folder (User-Facing)

```
documentation/
├── README.md                      # Index (updated to reference new structure)
├── QUICK_REFERENCE.md             # Copy/paste examples
├── CONFIGURATION.md               # Config guide (unchanged)
├── PERSONAS_AND_DOMAINS.md        # Persona reference (unchanged)
├── WEB_APP.md                     # UI guide (updated, de-duplicated)
├── WEB_SEARCH_AND_REASONING.md    # Canonical search/reasoning guide
├── CONTEXT_INJECTION_GUIDE.md     # Context loading guide
├── REVIEWER_SETUP.md              # LLM reviewer guide
├── ERROR_HANDLING.md              # Error handling (unchanged)
├── API_REFERENCE.md               # Python API reference (unchanged)
├── DOCS_MAINTENANCE.md            # For doc maintainers (unchanged)
├── TROUBLESHOOTING.md (new)       # Common issues and solutions
├── COMMON_TASKS.md (new)          # How-to guide for common operations
├── decisions/                     # Internal decisions (unchanged)
└── internal/ (new)                # Internal/planning docs
    ├── CONSOLIDATION_PLAN.md
    ├── DOCUMENTATION_REVISION_PLAN.md
    └── [other planning docs]
```

### Files to Archive/Remove

- `QUICK_START.md` → Archive (content moved to GETTING_STARTED.md)
- `SETUP_VENV.md` → Archive (content moved to GETTING_STARTED.md)
- `VENV_MANAGEMENT.md` → Archive or integrate into TROUBLESHOOTING.md
- `WHICH_REPO.md` → Archive (content moved to REPOSITORY_STRUCTURE.md)
- Move to `/documentation/internal/`:
  - `CODEX_AUTOMATION.md`
  - `CODEX_ENV_SETUP.md`
  - `MERGE_INSTRUCTIONS.md`
  - `CONFLICT_RESOLUTION_GUIDE.md`
  - `ARCHETYPE_GUIDE.md`

---

## Detailed Action Items

### Phase 1: Foundation (Critical)

**Task 1.1: Create GETTING_STARTED.md**

- Consolidate setup instructions from QUICK_START.md, SETUP_VENV.md
- Include venv setup for Windows, macOS, Linux
- Add environment variables section
- Add API key configuration
- Estimated length: 150-200 lines
- **Priority:** 🔴 High

**Task 1.2: Create REPOSITORY_STRUCTURE.md**

- Move content from WHICH_REPO.md
- Clarify council-ai vs council-ai-personal workflow
- Add personal integration workflow
- Estimated length: 80-100 lines
- **Priority:** 🔴 High

**Task 1.3: Update README.md**

- Trim to 200-250 lines (currently 1236!)
- Move detailed setup to GETTING_STARTED.md
- Add "Getting Started" section with clear navigation
- Keep feature overview + marketing
- Add "Learn More" section linking to key docs
- **Priority:** 🔴 High

### Phase 2: Consolidation (Important)

**Task 2.1: De-duplicate WEB_SEARCH_AND_REASONING.md**

- Remove reasoning mode explanation from WEB_APP.md
- Add cross-link in WEB_APP.md to canonical guide
- Verify all examples are correct
- **Priority:** 🟡 Medium

**Task 2.2: Create TROUBLESHOOTING.md**

- Common issues: "Connection refused", "Port already in use", "Virtual env issues"
- Include VENV_MANAGEMENT.md troubleshooting
- Link to relevant docs
- Estimated length: 100-150 lines
- **Priority:** 🟡 Medium

**Task 2.3: Create COMMON_TASKS.md**

- "Add custom persona" (link to CONTRIBUTING.md)
- "Create custom domain"
- "Enable web search"
- "Use custom LLM provider"
- "Run with multiple LLMs"
- Estimated length: 150-200 lines
- **Priority:** 🟡 Medium

### Phase 3: Organization (Important)

**Task 3.1: Create documentation/internal/ folder**

- Move internal planning docs
- Update links in documentation/README.md
- Add .gitkeep or README explaining purpose
- **Priority:** 🟢 Low

**Task 3.2: Archive root-level duplicates**

- Move QUICK_START.md → Archive/QUICK_START.md.archived
- Move SETUP_VENV.md → Archive/SETUP_VENV.md.archived
- Move VENV_MANAGEMENT.md → Archive/VENV_MANAGEMENT.md.archived
- Move WHICH_REPO.md → Archive/WHICH_REPO.md.archived
- Keep in Git history via Archive/ folder
- **Priority:** 🟢 Low

**Task 3.3: Update documentation/README.md**

- Update links to reflect new structure
- Reorganize sections to match new doc layout
- Add "Getting Started" at top
- **Priority:** 🟢 Low

### Phase 4: Verification (Support)

**Task 4.1: Verify launcher scripts exist**

- Check `/bin/launch-council.bat`, `/bin/launch-council-web.command`, etc.
- Update WEB_APP.md if filenames differ
- **Priority:** 🔵 Depends on Phase 1

**Task 4.2: Verify example code**

- Check QUICK_REFERENCE.md examples work
- Verify API_REFERENCE.md examples
- Run documentation/examples/ if they exist
- **Priority:** 🔵 Depends on Phase 1

**Task 4.3: Update cross-links**

- Search all docs for dead links
- Update internal references
- Verify relative link paths work
- **Priority:** 🟢 Low

---

## Success Criteria

✅ **New users can start in < 5 minutes** by following README → GETTING_STARTED.md
✅ **No more than 3 quick-start entry points** (currently 6+)
✅ **Clear repository structure** explained in one place (REPOSITORY_STRUCTURE.md)
✅ **Web search & reasoning** has single canonical guide
✅ **No broken links** in documentation
✅ **< 300 lines in README** (currently 1236)
✅ **Troubleshooting guide exists** for common issues
✅ **Internal docs separated** from user-facing docs

---

## Implementation Order

1. ✏️ Create GETTING_STARTED.md (consolidate setup)
2. ✏️ Create REPOSITORY_STRUCTURE.md (clarify repos)
3. ✏️ Update README.md (trim to essentials)
4. ✏️ Update documentation/README.md (reorg sections)
5. ✏️ De-duplicate WEB_SEARCH_AND_REASONING.md
6. ✏️ Create TROUBLESHOOTING.md
7. ✏️ Create COMMON_TASKS.md
8. 📦 Move internal docs to documentation/internal/
9. 📚 Archive old setup guides
10. ✅ Final verification and broken link fixes

---

## Notes

- This plan preserves all useful information while improving organization
- Git history is preserved via archiving rather than deletion
- New users get clearer guidance with less reading
- Maintenance burden reduced by removing duplication
- Estimated effort: 2-3 hours for full implementation
