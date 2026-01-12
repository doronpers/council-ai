# GitHub Actions Workflows

This directory contains automated workflows for the Council AI project.

## TruffleHog Secrets Scan

**File:** `trufflehog-secrets-scan.yml`

### Purpose
Automatically scans the repository for accidentally committed secrets, API keys, tokens, and other sensitive data using TruffleHog.

### Features
- **Smart BASE/HEAD Detection**: Automatically detects when BASE and HEAD commits are equal
- **Graceful Skipping**: Skips the scan instead of failing when:
  - This is an initial commit (no parent)
  - BASE equals HEAD (no changes to scan)
  - BASE is the null SHA (0000000000000000000000000000000000000000)
- **Event-aware**: Works correctly for both push and pull_request events
- **Full History**: Uses `fetch-depth: 0` to ensure complete commit history is available

### How It Works

1. **Checkout Code**: Fetches the full repository history
2. **Pre-check Step**: Determines if BASE and HEAD are equal
   - For pull requests: Uses `pull_request.base.sha` and `pull_request.head.sha`
   - For pushes: Uses `event.before` and `event.after`
   - Detects initial commits and null SHAs
3. **TruffleHog Scan**: Only runs if BASE ≠ HEAD
   - Scans commit range from BASE to HEAD
   - Only reports verified secrets (`--only-verified`)
   - Fails the workflow if secrets are found (`--fail`)
4. **Notification**: Displays a notice if the scan was skipped

### Why This Matters

Without the pre-check, TruffleHog would fail with errors like:
```
fatal: ambiguous argument '[sha]~1': unknown revision or path not in the working tree
```

This makes the CI more robust and prevents false failures in edge cases like:
- Repository initialization
- Force pushes
- Single-commit branches

### Triggers

The workflow runs on:
- Pushes to `main` and `develop` branches
- Pull requests targeting `main` and `develop` branches

### Configuration

To modify the branches that trigger this workflow, edit the `on` section in the workflow file.

To adjust TruffleHog scanning parameters, modify the `extra_args` in the "TruffleHog Secret Scan" step.
