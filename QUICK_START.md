# Quick Start Guide

## Which Directory Should I Use?

**Short answer: Always work in `council-ai`**

### The Two Repositories

1. **`council-ai`** (Main)
   - Contains all the core code
   - This is where you run the web server
   - This is where you run CLI commands
   - **Use this for everything**

2. **`council-ai-personal`** (Your Customizations)
   - Contains your personal personas and configs
   - Automatically detected by `council-ai`
   - You edit files here, but run from `council-ai`

## Getting Started

### Step 1: Navigate to the main repository
```bash
cd council-ai
```

### Step 2: Activate virtual environment
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Or use the activation script
.\activate-venv.ps1
```

### Step 3: Start the web server
```bash
python launch-council.py
```

Or use the batch file:
```bash
# Windows
launch-council.bat

# For personal mode (auto-detects council-ai-personal)
launch-council-personal.bat
```

### Step 4: Open your browser
Go to: `http://localhost:8000`

## Personal Customizations

If you have a `council-ai-personal` repository:

1. **Edit your customizations** in `council-ai-personal/personal/`
2. **Run the app** from `council-ai` (it auto-detects personal configs)
3. **To sync changes**: Run `council personal integrate` from `council-ai`

## Troubleshooting

**"Connection refused" error?**
- Make sure the server is running in a terminal window
- Keep that terminal window open while using the web app
- Check that you activated the virtual environment

**Can't find the server?**
- Make sure you're in the `council-ai` directory
- Make sure the virtual environment is activated
- Check the terminal for error messages

## Summary

- **Work in**: `council-ai` 
- **Store customizations in**: `council-ai-personal`
- **Run from**: `council-ai`
- **Personal configs**: Automatically detected if `council-ai-personal` exists
