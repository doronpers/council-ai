# Merge Conflict Resolution Instructions

## Quick Start

Based on the PR "Strengthen the types #3" with branch `claude/strengthen-types-mkjzqv9pv3m0q3ny-HqsR1`:

### Step 1: Get the Branch Locally

**Option A: Using GitHub CLI (if PR is accessible)**

```bash
gh pr checkout <PR_NUMBER>
```

**Option B: Fetch the branch directly**

```bash
git fetch origin claude/strengthen-types-mkjzqv9pv3m0q3ny-HqsR1:claude/strengthen-types-mkjzqv9pv3m0q3ny-HqsR1
```

**Option C: If branch is in a fork, add the fork as remote**

```bash
git remote add fork https://github.com/<fork-owner>/council-ai.git
git fetch fork claude/strengthen-types-mkjzqv9pv3m0q3ny-HqsR1:claude/strengthen-types-mkjzqv9pv3m0q3ny-HqsR1
```

### Step 2: Attempt the Merge

```bash
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Attempt the merge
git merge claude/strengthen-types-mkjzqv9pv3m0q3ny-HqsR1 --no-commit --no-ff
```

### Step 3: Resolve Conflicts

The 12 files with conflicts are:

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

### Step 4: Resolution Strategy

Since this PR is about **strengthening TypeScript types**, prioritize:

1. **Type Safety**: Keep all type improvements from the PR
2. **Explicit Types**: Prefer explicit return types and parameter types
3. **Interface Definitions**: Keep new interfaces like `FilterValues`, `HistoryFilters`, `WizardStepData`, `ConfigStatus`
4. **Generic Functions**: Keep the generic `parseSSELine` implementation
5. **Error Handling**: Merge improved error handling from both sides

### Step 5: After Resolving Each File

```bash
# Stage the resolved file
git add <file-path>

# Verify TypeScript compiles
cd src/council_ai/webapp
npm run type-check  # or tsc --noEmit
```

### Step 6: Complete the Merge

```bash
# After all files are resolved and staged
git commit
```

## What to Look For

The PR description mentions these specific changes:

- **SSE parsing**: Generic `parseSSELine` - keep the generic version
- **Explicit types**: Return types on handlers/callbacks - keep these
- **Interfaces**: New interfaces instead of inline types - keep the interfaces
- **Utils**: `MimeType` alias and tighter parameter types - keep these improvements
- **API typing**: Improved error handling in `reviewerApi` - keep the typed versions

## Need Help?

Once you have the branch locally and attempt the merge, I can help resolve each conflict file by file. Just let me know when you're ready!
