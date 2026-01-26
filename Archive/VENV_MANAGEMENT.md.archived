# Virtual Environment Management Guide

> **Location:** This guide is in `council-ai/VENV_MANAGEMENT.md` but applies to all projects.

## Problem: Multiple Virtual Environments

If you see `(.venv) (venv)` in your terminal prompt, you have **two virtual environments activated simultaneously**. This can cause:

- Confusion about which Python packages are installed
- Dependency conflicts
- Slower terminal performance
- Issues with package installations

## How to Identify Multiple Venvs

### Check Your Prompt

```bash
# If you see this, you have multiple venvs:
(.venv) (venv) user@hostname:~/project$
```

### Check Environment Variables

```bash
echo $VIRTUAL_ENV
# This shows the currently active venv path
```

### Check for Multiple Venv Directories

```bash
# In your project directory:
ls -la | grep venv
# Look for both 'venv' and '.venv' directories
```

## How to Fix: Remove Redundant Virtual Environment

### Step 1: Deactivate All Virtual Environments

```bash
# Deactivate multiple times if needed
deactivate
deactivate  # Run again if prompt still shows venv
```

### Step 2: Identify Which Venv to Keep

**Best Practice:** Keep `.venv` (hidden directory) as it's:

- Less likely to be accidentally committed to git
- Standard convention in many projects
- Already configured in `.gitignore`

### Step 3: Remove the Redundant Venv

```bash
# Option A: Remove 'venv' directory (if you want to keep .venv)
rm -rf venv

# Option B: Remove '.venv' directory (if you want to keep venv)
rm -rf .venv
```

### Step 4: Reactivate the Correct Venv

```bash
# If keeping .venv:
source .venv/bin/activate

# If keeping venv:
source venv/bin/activate
```

### Step 5: Verify

```bash
# Check your prompt - should show only ONE venv:
(.venv) user@hostname:~/project$

# Verify Python location:
which python3
# Should point to your venv's Python

# Check environment:
echo $VIRTUAL_ENV
# Should show path to your active venv
```

## Prevention: How to Avoid This in the Future

### 1. Always Deactivate Before Activating

```bash
# Before activating a new venv:
deactivate  # If one is already active
source .venv/bin/activate
```

### 2. Check Before Creating New Venv

```bash
# Before running: python3 -m venv .venv
# Check if one already exists:
ls -la | grep venv
```

### 3. Use Consistent Venv Name

**Recommendation:** Always use `.venv` (hidden directory)

```bash
# Create new venv:
python3 -m venv .venv

# Activate:
source .venv/bin/activate
```

### 4. Check Your Shell Configuration

Sometimes auto-activation scripts can cause double activation:

```bash
# Check ~/.zshrc or ~/.bashrc for auto-activation:
grep -i "venv\|virtualenv" ~/.zshrc ~/.bashrc

# If you find auto-activation, you may need to:
# - Remove the auto-activation script
# - Or modify it to check if venv is already active
```

### 5. Use Virtual Environment Manager

Consider using tools that prevent this:

- **pyenv-virtualenv**: Better venv management
- **direnv**: Auto-activates based on `.envrc` file
- **conda**: Alternative environment manager

## Quick Reference Commands

```bash
# Check for multiple venvs
ls -la | grep venv

# Deactivate all
deactivate; deactivate

# Remove redundant venv (keep .venv)
rm -rf venv

# Activate correct venv
source .venv/bin/activate

# Verify single venv
echo $VIRTUAL_ENV
which python3
```

## Troubleshooting

### If `deactivate` doesn't work (command not found)

This usually means the venv was activated via a custom function, not the standard activation script.

#### Solution 1: Manually unset environment variables

```bash
# Unset venv-related variables:
unset VIRTUAL_ENV
unset VIRTUAL_ENV_PROMPT

# Remove venv paths from PATH:
export PATH=$(echo $PATH | tr ':' '\n' | grep -v venv | tr '\n' ':' | sed 's/:$//')
```

#### Solution 2: Start a new shell session

```bash
# Open a new terminal window/tab
# Or:
exec zsh  # Restart zsh (or exec bash for bash)
```

**Solution 3: Check for auto-activation in shell config**

```bash
# Check for auto-activation functions:
grep -n "venv\|virtualenv" ~/.zshrc ~/.bashrc

# Common culprits:
# - Functions that auto-activate venv when entering directories
# - direnv configuration
# - Custom activation scripts
```

#### Solution 4: Disable auto-activation temporarily

```bash
# If you find an auto-activation function, comment it out:
# Edit ~/.zshrc or ~/.bashrc
# Comment out lines that auto-activate venv
# Then: source ~/.zshrc  (or source ~/.bashrc)
```

### If packages are missing after cleanup

```bash
# Reinstall dependencies:
pip install -e '.[dev]'  # Or your project's install command
```

### If you're not sure which venv to keep

```bash
# Check which one has more packages:
venv/bin/pip list | wc -l
.venv/bin/pip list | wc -l

# Check which one is newer:
ls -ld venv .venv
```

### If nvm shows "npm_config_prefix" error

This happens when a venv sets `npm_config_prefix` and conflicts with nvm.

**Immediate fix:**

```bash
unset npm_config_prefix
# Then reload nvm:
source ~/.nvm/nvm.sh
```

**Permanent fix - Update your ~/.zshrc:**
Your `.zshrc` should unset `npm_config_prefix` BEFORE loading nvm:

```bash
# In ~/.zshrc, ensure this comes BEFORE nvm loading:
unset NPM_CONFIG_PREFIX
unset npm_config_prefix

# Then load nvm:
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

**Why this happens:**

- Some venv activation scripts set `npm_config_prefix` to the venv directory
- nvm needs to control npm configuration and conflicts with this
- The fix is to unset it before nvm loads, or after venv activation

**Check if your venv sets it:**

```bash
# Check venv activation script:
grep -i "npm_config_prefix" .venv/bin/activate venv/bin/activate 2>/dev/null

# If found, you have two options:
```

#### Option A: Add post-activation fix to ~/.zshrc (Recommended)

Add this to your `~/.zshrc` AFTER the venv auto-activation function:

```bash
# Fix npm_config_prefix after venv activation
if [[ -n "$npm_config_prefix" && "$npm_config_prefix" == *"/.venv"* ]]; then
    unset npm_config_prefix
    unset NPM_CONFIG_PREFIX
fi
```

Or add it to your `auto_activate_venv()` function after the `source` command.

#### Option B: Manually unset after each activation

```bash
# After activating venv:
unset npm_config_prefix
unset NPM_CONFIG_PREFIX
```

#### Option C: Edit venv activate script (not recommended)

The activate script is auto-generated, so edits will be lost when venv is recreated:

```bash
# Edit .venv/bin/activate and comment out or remove lines 97-102:
# _OLD_NPM_CONFIG_PREFIX="${NPM_CONFIG_PREFIX:-}"
# _OLD_npm_config_prefix="${npm_config_prefix:-}"
# NPM_CONFIG_PREFIX="$NODE_VIRTUAL_ENV"
# npm_config_prefix="$NODE_VIRTUAL_ENV"
# export NPM_CONFIG_PREFIX
# export npm_config_prefix
```
