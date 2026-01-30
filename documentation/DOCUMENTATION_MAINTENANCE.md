# Documentation Maintenance Guide

**Purpose**: Standardized guidelines for maintaining documentation across Council AI and related repositories.

**Last Updated**: January 25, 2026  
**Applies To**: council-ai, council-ai-personal, and all related documentation

---

## Core Principles

### 1. Root Directory is Sacred

The root level should contain ONLY user-facing materials:

- ✅ README.md (project overview)
- ✅ GETTING_STARTED.md (setup guide)
- ✅ CONTRIBUTING.md (contribution guidelines)
- ✅ SECURITY.md (security policy)
- ✅ ROADMAP.md (project roadmap)
- ✅ CHANGELOG.md (release notes)
- ✅ CODE_OF_CONDUCT.md (community standards)
- ✅ LICENSE (legal)
- ✅ AGENT_KNOWLEDGE_BASE.md (AI guidance - if substantial)
- ✅ AGENTS.md (AI agent reference - if substantial and unique)

❌ NEVER place in root:

- Planning documents
- Review/audit files
- Internal guidance (CODEX_ENV_SETUP, GEMINI notes)
- Beta-phase files
- Temporary reports

### 2. Documentation Directory Structure

```
documentation/
├── README.md                    # Navigation index
├── CONFIGURATION.md             # Config reference
├── [feature-guides]/            # Feature-specific guides
├── internal/                    # Internal/planning docs
│   ├── CODEX_*.md              # AI automation guidance
│   ├── GEMINI_NOTES.md         # Gemini-specific notes
│   ├── MERGE_INSTRUCTIONS.md   # Merge procedures
│   └── [planning-docs]/        # Planning and strategy
├── reviews/                     # Code reviews & audits
│   ├── CODE_REVIEW_*.md
│   ├── DESIGN_AUDIT_*.md
│   └── [audit-reports]/
└── Archive/                     # Historical/deprecated
    ├── QUICK_START.md          # (moved from root)
    ├── BETA_*.md               # (beta-phase files)
    └── [deprecated-guides]/
```

### 3. File Organization Rules

**User-Facing Files (in documentation/ or root)**:

- Clear, focused purpose
- Current date in metadata
- Active links to related docs
- Cross-references to internal docs are OK with context

**Internal Files (in documentation/internal/)**:

- Operational guides
- Automation instructions
- Merge procedures
- Planning documents
- AI agent guidance (CODEX, GEMINI notes)
- Session notes and investigations

**Review/Audit Files (in documentation/reviews/)**:

- Code reviews
- Design audits
- Assessment reports
- Security reviews
- Performance evaluations

**Archived Files (in documentation/Archive/)**:

- Deprecated setup guides
- Beta-phase announcements
- Historical reports (>3 months old)
- Replaced documents (keep for history)

---

## Maintenance Workflow

### When Adding Documentation

1. **Identify the category** (User-facing, Internal, Review, or Archive)
2. **Place in appropriate location** (root, documentation/, documentation/internal/, etc.)
3. **Link from README or navigation** if user-facing
4. **Add date metadata** (Last Updated: YYYY-MM-DD)
5. **Ensure cross-references** work properly

### When Updating Documentation

1. **Update the content** in place
2. **Update "Last Updated" date** if significant
3. **Check all links** still work
4. **Update documentation/README.md** if navigation changed
5. **Commit with clear message**: `docs: update [section] for [reason]`

### When Deprecating Documentation

1. **Don't delete** - move to documentation/Archive/
2. **Use git mv** to preserve history
3. **Update root README.md** to remove links
4. **Update documentation/README.md** to mark as archived
5. **Commit with clear message**: `docs: archive [file] - [reason]`

### When Consolidating Documents

1. **Identify redundant files** (similar purpose, overlapping content)
2. **Merge into single "canonical" version**
3. **Add note at top** of consolidated file listing original sources
4. **Delete source files** using `git rm` or `git mv` to Archive/
5. **Update all links** to point to consolidated version
6. **Commit with message**: `docs: consolidate [old-files] into [new-file]`

---

## Specific Guidelines by Document Type

### README.md (Root Level)

**Purpose**: Project overview, getting started, key features  
**Length**: 200-500 lines (keep it scannable)  
**Structure**:

1. Project tagline (1 line)
2. Quick overview (3-5 lines)
3. Quick start (5-10 lines with code block)
4. Core features (bulleted list)
5. Documentation index (links to detailed guides)
6. Contributing guidelines (link to CONTRIBUTING.md)
7. Security info (link to SECURITY.md)

**Anti-patterns**:

- ❌ Verbose persona listings
- ❌ Complete configuration examples
- ❌ Internal troubleshooting
- ❌ Long setup tutorials

### GETTING_STARTED.md

**Purpose**: Complete setup guide from clone to first run  
**Length**: 500-1000 lines (detailed but scannable)  
**Structure**:

1. Prerequisites
2. Step-by-step setup (all platforms)
3. Verify installation
4. Next steps (links to feature docs)
5. Quick troubleshooting

**Consolidates**: QUICK_START.md, SETUP_VENV.md, VENV_MANAGEMENT.md, WHICH_REPO.md

### documentation/README.md

**Purpose**: Navigation hub for all documentation  
**Structure**:

1. "Start Here" section (links to key guides)
2. Feature guides organized by use case
3. Reference documentation
4. Contributing/development links
5. Internal documentation note

### DOCUMENTATION_MAINTENANCE.md

**Purpose**: This file - guidelines for doc maintenance  
**Updates**: Whenever documentation structure changes  
**Applies To**: All documentation decisions across all repos

---

## Git Workflow for Documentation Changes

### Moving Files (Preserves History)

```bash
# Create new directory if needed
mkdir -p documentation/internal

# Move file using git mv
git mv CODEX_ENV_SETUP.md documentation/internal/

# Commit with clear message
git commit -m "docs: move CODEX_ENV_SETUP to internal documentation"
```

### Consolidating Files

```bash
# Create consolidated version
cat file1.md file2.md file3.md > consolidated.md

# Stage consolidation
git add consolidated.md

# Remove source files
git rm file1.md file2.md file3.md

# Move consolidated to destination
git mv consolidated.md documentation/reviews/

# Commit
git commit -m "docs: consolidate design audits into single file"
```

### Archiving Files

```bash
# Move to archive with clear naming
git mv QUICK_START.md Archive/QUICK_START.md.archived

# Or rename to mark archived
git mv BETA_NOTES.md Archive/BETA_NOTES_2026-01-15.archived.md

# Commit
git commit -m "docs: archive QUICK_START.md - content moved to GETTING_STARTED"
```

---

## Quality Checklist

Before committing documentation changes, verify:

- [ ] **Root cleanup**: No internal docs at root level
- [ ] **Organization**: Files in correct subdirectories
- [ ] **Navigation**: documentation/README.md updated if needed
- [ ] **Links**: All cross-references are valid
- [ ] **Dates**: "Last Updated" is current for significant changes
- [ ] **Consolidation**: No redundant/overlapping documents
- [ ] **Git history**: Used `git mv` when moving/reorganizing
- [ ] **Commit message**: Clear and specific about what changed
- [ ] **Archives**: Old files properly preserved, not deleted

---

## Common Patterns

### Pattern 1: Multiple Setup Guides

**Problem**:

- QUICKSTART.md, GETTING_STARTED.md, SETUP_VENV.md, SETUP_WINDOWS.md all overlap

**Solution**:

1. Create single `GETTING_STARTED.md` with all platforms
2. Move outdated guides to `Archive/`
3. Keep references in git history (via `git mv`)

### Pattern 2: Overlapping Feature Docs

**Problem**:

- WEB_SEARCH.md and WEB_SEARCH_AND_REASONING.md overlap
- Multiple "Configuration" guides

**Solution**:

1. Consolidate into single canonical version
2. Archive source files
3. Update all links to point to consolidated version

### Pattern 3: Phase-Specific Documentation

**Problem**:

- BETA_WELCOME.md, BETA_REQUIREMENTS.md, BETA_RELEASE_NOTES.md clutter root

**Solution**:

1. Archive to `documentation/Archive/` with date suffix
2. Move to `documentation/` if user-facing (e.g., RELEASE_NOTES_BETA.md)
3. Keep in `documentation/internal/` if operational

### Pattern 4: Internal AI Guidance

**Problem**:

- CODEX_ENV_SETUP.md, GEMINI.md, CLAUDE.md mixed with user docs

**Solution**:

1. Move all to `documentation/internal/`
2. Rename for clarity: `GEMINI.md` → `GEMINI_NOTES.md`
3. Update internal/README if substantial collection

---

## Documentation Workflow for Multi-Repo Environments

For repositories working together (council-ai + council-ai-personal):

1. **Main repo** (council-ai): Full framework documentation
2. **Satellite repo** (council-ai-personal): Only integration-specific docs
3. **Cross-reference**: Each includes links to the other
4. **Avoid duplication**: Don't replicate framework docs in satellite
5. **Consistent structure**: Same root/documentation/ organization in both

**Example**:

- council-ai/documentation/CONFIGURATION.md (framework)
- council-ai-personal/documentation/README.md (links to framework docs)
- council-ai-personal/personal/config/ (personal overrides only)

---

## Enforcement Points

### Pre-Commit Hooks (Recommended)

```yaml
# .pre-commit-config.yaml should include checks for:
- Documentation directory structure
- README.md exists and is reasonably sized
- No sensitive files at root level
- Markdown formatting consistency
```

### CI/CD Checks (Recommended)

- No new `.md` files at root level in PRs
- Documentation README updated when docs structure changes
- Links in documentation validated
- File organization compliance

### Manual Review

- Every documentation PR should be reviewed for:
  - Root-level cleanliness
  - Appropriate subdirectory placement
  - Narrative consistency
  - Link validity

---

## References

- **Council AI Main**: [github.com/doronpers/council-ai](https://github.com/doronpers/council-ai)
- **Personal Repository**: [github.com/doronpers/council-ai-personal](https://github.com/doronpers/council-ai-personal)
- **Related Projects**: Sono Platform, Sono-Eval, Sonotheia Examples, Website-Sonotheia

---

## Questions?

This guide is maintained in the council-ai repository. For updates or questions, see:

- **Issue**: Create an issue in the repository
- **PR**: Submit documentation improvements
- **Discussion**: Start a discussion for process questions
