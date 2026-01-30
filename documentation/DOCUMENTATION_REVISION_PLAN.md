# Council AI - Documentation Revision Plan

**Date:** 2026-01-24  
**Status:** Ready for Implementation  
**Scope:** Comprehensive documentation review and revision

---

## Executive Summary

This plan identifies documentation issues, redundancies, and gaps following the comprehensive UX enhancement implementation (January 2026). The revision will ensure all documentation is current, accurately reflects new features, and is expertly organized for both users and developers.

**Key Findings:**

- Missing documentation for new UX features (onboarding, error handling, feature discovery)
- Redundant content across multiple files
- Outdated references to removed/renamed features
- Inconsistent organization between root-level and documentation/ files
- Missing cross-references and navigation improvements

---

## Phase 1: Critical Updates (New Features)

### 1.1 Web App Onboarding Documentation

**Current State:**

- `WEB_APP.md` mentions onboarding briefly but lacks detail
- No documentation for the 6-step onboarding wizard
- Missing information about contextual help system

**Actions:**

1. **Update `WEB_APP.md`** - Add comprehensive "First-Time User Experience" section:
   - Document the 6-step onboarding wizard (welcome, provider, config, domain, personas, first consultation)
   - Explain onboarding context and localStorage persistence
   - Document "Take Tour" functionality in header
   - Add screenshots or detailed descriptions of each step

2. **Update `README.md`** - Enhance "Web App" section:
   - Add note about automatic onboarding for first-time users
   - Reference `WEB_APP.md` for detailed onboarding guide
   - Update quickstart to mention onboarding wizard

**Files to Modify:**

- `documentation/WEB_APP.md`
- `README.md`

---

### 1.2 Error Handling & User Feedback Documentation

**Current State:**

- No documentation for comprehensive error message system
- Missing information about inline validation
- No documentation for error recovery actions

**Actions:**

1. **Create `documentation/ERROR_HANDLING.md`** (NEW):
   - Document error message catalog and categories
   - Explain inline validation for inputs (query, API key, base URL)
   - Document error recovery actions (retry, fix, diagnostics)
   - Explain error logging and client-side error tracking
   - Include examples of common errors and recovery paths

2. **Update `WEB_APP.md`** - Add "Error Handling" section:
   - Reference new error handling guide
   - Explain user-facing error messages
   - Document validation feedback in UI

**Files to Create:**

- `documentation/ERROR_HANDLING.md` (NEW)

**Files to Modify:**

- `documentation/WEB_APP.md`

---

### 1.3 Feature Discovery & Progressive Disclosure Documentation

**Current State:**

- No documentation for feature tours
- Missing information about tiered configuration
- No documentation for feature highlights and badges

**Actions:**

1. **Update `WEB_APP.md`** - Add "Feature Discovery" section:
   - Document feature tours (getting started, advanced features, configuration, history)
   - Explain tiered configuration (basic/intermediate/advanced)
   - Document feature highlights and "New" badges
   - Explain contextual help icons

2. **Update `README.md`** - Enhance "Web App Features" section:
   - Add mention of feature tours
   - Document progressive disclosure in configuration
   - Reference feature discovery capabilities

**Files to Modify:**

- `documentation/WEB_APP.md`
- `README.md`

---

## Phase 2: Consolidation & Redundancy Removal

### 2.1 Web App Documentation Consolidation

**Current State:**

- `README.md` has extensive web app section
- `WEB_APP.md` duplicates some content
- Inconsistent information between files

**Actions:**

1. **Establish `WEB_APP.md` as canonical web app guide:**
   - Move detailed web app content from `README.md` to `WEB_APP.md`
   - Keep only high-level overview in `README.md` with link to `WEB_APP.md`
   - Ensure `WEB_APP.md` is comprehensive and self-contained

2. **Remove redundant sections:**
   - Remove duplicate launcher instructions (keep in `WEB_APP.md`)
   - Remove duplicate TTS documentation (consolidate in `WEB_APP.md`)
   - Remove duplicate history management (consolidate in `WEB_APP.md`)

**Files to Modify:**

- `README.md` (reduce web app section, add link)
- `documentation/WEB_APP.md` (expand and consolidate)

---

### 2.2 Configuration Documentation Consolidation

**Current State:**

- `README.md` has configuration section
- `CONFIGURATION.md` exists but may be incomplete
- `.env` examples scattered across multiple files

**Actions:**

1. **Enhance `CONFIGURATION.md`:**
   - Ensure it's the single source of truth for configuration
   - Add comprehensive `.env` examples (LM Studio, cloud providers)
   - Document config file precedence clearly
   - Add examples for common scenarios

2. **Update `README.md`:**
   - Reduce configuration section to high-level overview
   - Link to `CONFIGURATION.md` for details
   - Keep only essential quickstart configuration info

**Files to Modify:**

- `documentation/CONFIGURATION.md`
- `README.md`

---

### 2.3 Quickstart Documentation Consolidation

**Current State:**

- `README.md` has quickstart section
- `QUICK_START.md` exists separately
- `CODEX_ENV_SETUP.md` has setup instructions
- Potential overlap and confusion

**Actions:**

1. **Review and consolidate:**
   - Determine if `QUICK_START.md` adds value beyond `README.md`
   - If redundant, merge into `README.md` and remove `QUICK_START.md`
   - If unique, ensure clear differentiation and cross-links

2. **Clarify `CODEX_ENV_SETUP.md` purpose:**
   - Ensure it's clearly marked as Codex-specific
   - Add note if it's for AI agents, not end users
   - Consider moving to `.agent/` or `.codex/` directory if appropriate

**Files to Review:**

- `QUICK_START.md`
- `CODEX_ENV_SETUP.md`
- `README.md`

---

## Phase 3: Outdated Content Removal

### 3.1 Remove/Archive Historical Reports

**Current State:**

- `DESIGN_AUDIT_REPORT.md` - Historical audit (January 2026)
- `IMPLEMENTATION_SUMMARY.md` - Historical implementation summary
- `COUNCIL_AI_MEMORY_PERSONALIZATION_REPORT_2026-01-19.md` - Historical report
- `PHASE4_COMPLETION_REPORT.md` - Historical report
- `PHASE_2_WCAG_AUDIT.md` - Historical audit
- `COMPREHENSIVE_HARDENING_SUMMARY.md` - Historical summary

**Actions:**

1. **Move to Archive:**
   - Move all historical reports to `Archive/` directory
   - Update any references to these files
   - Keep only if they contain actionable information still relevant

2. **Update references:**
   - Remove links to archived reports
   - Update `documentation/README.md` if it references these

**Files to Archive:**

- `DESIGN_AUDIT_REPORT.md` → `Archive/DESIGN_AUDIT_REPORT_2026-01-19.md`
- `IMPLEMENTATION_SUMMARY.md` → `Archive/IMPLEMENTATION_SUMMARY_2026-01-19.md`
- `COUNCIL_AI_MEMORY_PERSONALIZATION_REPORT_2026-01-19.md` → `Archive/`
- `PHASE4_COMPLETION_REPORT.md` → `Archive/`
- `PHASE_2_WCAG_AUDIT.md` → `Archive/`
- `COMPREHENSIVE_HARDENING_SUMMARY.md` → `Archive/`

---

### 3.2 Update Roadmap References

**Current State:**

- `ROADMAP.md` may reference completed items that should be documented
- May have outdated priorities

**Actions:**

1. **Review `ROADMAP.md`:**
   - Mark UX enhancement items as completed (January 2026)
   - Update priorities based on current state
   - Ensure completed items are reflected in documentation

2. **Update `CHANGELOG.md`:**
   - Add entry for UX enhancement implementation (January 2026)
   - Document new features (onboarding, error handling, feature discovery)

**Files to Modify:**

- `ROADMAP.md`
- `CHANGELOG.md`

---

## Phase 4: Organization & Navigation Improvements

### 4.1 Documentation Index Enhancement

**Current State:**

- `documentation/README.md` exists but may be incomplete
- Missing navigation for new documentation

**Actions:**

1. **Enhance `documentation/README.md`:**
   - Add section for new documentation (Error Handling, if created)
   - Update "Feature Guides" section with new features
   - Add clear navigation structure
   - Ensure all documentation files are listed

2. **Add cross-references:**
   - Ensure all documentation files link to related docs
   - Add "See also" sections where appropriate
   - Fix broken internal links

**Files to Modify:**

- `documentation/README.md`

---

### 4.2 README.md Structure Review

**Current State:**

- `README.md` is comprehensive but may be too long
- Some sections could be better organized

**Actions:**

1. **Review structure:**
   - Ensure logical flow (Overview → Quickstart → Features → Details)
   - Move detailed sections to appropriate documentation files
   - Keep README focused on getting started and high-level overview

2. **Add table of contents:**
   - Consider adding TOC for easier navigation
   - Link to detailed documentation throughout

**Files to Modify:**

- `README.md`

---

## Phase 5: Accuracy & Completeness

### 5.1 Update Feature Lists

**Current State:**

- Feature lists may not reflect new UX enhancements
- Missing mentions of onboarding, error handling, feature discovery

**Actions:**

1. **Update `README.md` "Key Features" section:**
   - Add: "🎯 **Onboarding Wizard** - Guided 6-step setup for first-time users"
   - Add: "🛡️ **Comprehensive Error Handling** - User-friendly error messages with recovery actions"
   - Add: "🔍 **Feature Discovery** - Interactive tours and progressive disclosure"
   - Update existing features if changed

2. **Update `WEB_APP.md` feature list:**
   - Ensure all web app features are documented
   - Add new features from UX enhancement

**Files to Modify:**

- `README.md`
- `documentation/WEB_APP.md`

---

### 5.2 Update Code Examples

**Current State:**

- Code examples may reference old APIs or patterns
- Missing examples for new features

**Actions:**

1. **Review all code examples:**
   - Ensure they work with current API
   - Update if APIs have changed
   - Add examples for new features where appropriate

2. **Test examples:**
   - Verify all code examples are executable
   - Fix any broken examples

**Files to Review:**

- `README.md`
- `documentation/API_REFERENCE.md`
- `documentation/WEB_APP.md`
- `examples/README.md`

---

### 5.3 Update Installation Instructions

**Current State:**

- Installation instructions may be outdated
- Missing information about new dependencies

**Actions:**

1. **Review installation sections:**
   - Ensure all steps are current
   - Add any new dependencies
   - Update version requirements if changed

2. **Verify setup scripts:**
   - Ensure referenced scripts exist
   - Update paths if changed

**Files to Modify:**

- `README.md`
- `SETUP_VENV.md` (if exists)
- `VENV_MANAGEMENT.md` (if exists)

---

## Phase 6: Internal Documentation Cleanup

### 6.1 Agent Documentation Review

**Current State:**

- `AGENT_KNOWLEDGE_BASE.md` - Auto-generated, should not be edited directly
- `CLAUDE.md` - May need updates for new features
- `.cursorrules` - May need updates

**Actions:**

1. **Review agent documentation:**
   - Ensure it reflects current codebase structure
   - Update if new patterns or standards were introduced
   - Note: `AGENT_KNOWLEDGE_BASE.md` is auto-generated, update source files

2. **Update `CLAUDE.md`:**
   - Add information about new UX features
   - Update architecture overview if changed
   - Update examples if needed

**Files to Review:**

- `AGENT_KNOWLEDGE_BASE.md` (check source files)
- `CLAUDE.md`
- `.cursorrules`

---

### 6.2 Consolidation Plan Review

**Current State:**

- `CONSOLIDATION_PLAN.md` exists
- May have items that are now completed or outdated

**Actions:**

1. **Review `CONSOLIDATION_PLAN.md`:**
   - Mark completed items
   - Remove outdated recommendations
   - Update with new consolidation opportunities

**Files to Modify:**

- `documentation/CONSOLIDATION_PLAN.md`

---

## Implementation Priority

### High Priority (Do First)

1. ✅ Phase 1: Critical Updates (New Features) - Document new UX features
2. ✅ Phase 2.1: Web App Documentation Consolidation - Reduce redundancy
3. ✅ Phase 3.1: Remove/Archive Historical Reports - Clean up root directory

### Medium Priority (Do Next)

4. Phase 2.2: Configuration Documentation Consolidation
5. Phase 4.1: Documentation Index Enhancement
6. Phase 5.1: Update Feature Lists

### Low Priority (Polish)

7. Phase 2.3: Quickstart Documentation Consolidation
8. Phase 4.2: README.md Structure Review
9. Phase 5.2: Update Code Examples
10. Phase 6: Internal Documentation Cleanup

---

## Success Criteria

- [ ] All new UX features are documented
- [ ] No redundant content between README.md and documentation/
- [ ] All historical reports moved to Archive/
- [ ] All documentation files listed in documentation/README.md
- [ ] All code examples are current and executable
- [ ] All internal links work correctly
- [ ] Feature lists reflect current capabilities
- [ ] Installation instructions are accurate
- [ ] Navigation is clear and logical

---

## Notes

- This plan should be implemented incrementally, with each phase completed before moving to the next
- Test all documentation changes by following instructions as a new user would
- Update CHANGELOG.md for significant documentation changes
- Consider adding screenshots or diagrams for complex features (onboarding, tours)
- Maintain consistency in tone and style across all documentation

---

**Next Steps:**

1. Review and approve this plan
2. Begin with Phase 1 (Critical Updates)
3. Test documentation changes
4. Update CHANGELOG.md
5. Commit changes incrementally
