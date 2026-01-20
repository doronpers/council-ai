# Conflict Resolution Guide

## Current Status

- **12 files with conflicts** in the webapp frontend
- All files are TypeScript/React components and utilities

## Files with Conflicts

1. `src/council_ai/webapp/src/components/Configuration/ConfigPanel.tsx`
2. `src/council_ai/webapp/src/components/Consultation/SubmitButton.tsx`
3. `src/council_ai/webapp/src/components/History/HistoryFilters.tsx`
4. `src/council_ai/webapp/src/components/History/HistoryItem.tsx`
5. `src/council_ai/webapp/src/components/History/HistoryPanel.tsx`
6. `src/council_ai/webapp/src/components/History/HistorySearch.tsx`
7. `src/council_ai/webapp/src/components/Layout/Modal.tsx`
8. `src/council_ai/webapp/src/components/Members/MemberSelectionGrid.tsx`
9. `src/council_ai/webapp/src/components/Onboarding/OnboardingWizard.tsx`
10. `src/council_ai/webapp/src/utils/export.ts`
11. `src/council_ai/webapp/src/utils/helpers.ts`
12. `src/council_ai/webapp/src/utils/reviewerApi.ts`

## Resolution Strategy

### Step 1: Identify the Source Branch

From the GitHub PR page, identify which branch is being merged. Common patterns:

- `origin/copilot/*`
- `origin/codex/*`
- A feature branch name

### Step 2: Attempt the Merge

```bash
# Make sure you're on main and it's up to date
git checkout main
git pull origin main

# Attempt the merge (replace BRANCH_NAME with actual branch)
git merge origin/BRANCH_NAME
```

### Step 3: Resolve Conflicts Systematically

For each conflicted file:

1. Open the file and locate conflict markers:
   - `<<<<<<< HEAD` (current branch - main)
   - `=======` (separator)
   - `>>>>>>> BRANCH_NAME` (incoming changes)

2. Review both versions:
   - Understand what each side is trying to do
   - Look for:
     - Type safety improvements
     - Bug fixes
     - New features
     - Code style consistency

3. Resolve by:
   - Keeping both changes if compatible
   - Choosing the better implementation
   - Merging logic when both add value
   - Ensuring TypeScript types are correct
   - Maintaining React best practices

4. Remove conflict markers after resolution

5. Test the resolved code:

   ```bash
   # Check for TypeScript errors
   cd src/council_ai/webapp
   npm run type-check  # or tsc --noEmit

   # Check for linting issues
   npm run lint
   ```

### Step 4: Commit the Resolution

```bash
# Stage all resolved files
git add src/council_ai/webapp/src/components/Configuration/ConfigPanel.tsx
git add src/council_ai/webapp/src/components/Consultation/SubmitButton.tsx
# ... add all 12 files

# Complete the merge
git commit
```

## Common Conflict Patterns

### Import Statements

- Usually safe to merge both sets of imports
- Remove duplicates
- Keep imports alphabetically sorted

### Type Definitions

- Prefer more specific types
- Keep type safety improvements
- Merge interface extensions

### Component Props

- Merge prop interfaces
- Keep all useful props from both sides

### Function Logic

- Review both implementations
- Choose the more robust version
- Merge if both add value

## Best Practices

1. **Preserve Type Safety**: Always keep TypeScript types correct
2. **Maintain React Patterns**: Follow React hooks rules and best practices
3. **Keep Error Handling**: Preserve error handling from both sides
4. **Test After Each File**: Resolve one file, test, then move to next
5. **Document Decisions**: Add comments if merge logic is complex

## Verification Checklist

After resolving all conflicts:

- [ ] All 12 files resolved
- [ ] No conflict markers remain (`<<<<<<<`, `=======`, `>>>>>>>`)
- [ ] TypeScript compiles without errors
- [ ] Linter passes
- [ ] Code follows project style guide
- [ ] All imports are valid
- [ ] No console errors in browser
