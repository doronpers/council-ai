# Virtual Environment Setup Guide

This guide explains how to set up a virtual environment for Council AI with your API keys automatically loaded.

## Quick Start

### Windows (PowerShell)
```powershell
.\setup-venv.ps1
.\venv\Scripts\activate-env.ps1
.\launch-council.bat
```

### Windows (Command Prompt)
```cmd
setup-venv.bat
venv\Scripts\activate-env.bat
launch-council.bat
```

### macOS/Linux
```bash
chmod +x setup-venv.sh
./setup-venv.sh
source venv/bin/activate-env
./launch-council.py --open
```

## What the Setup Script Does

1. **Creates a virtual environment** (`venv/`) to isolate dependencies
2. **Installs Council AI** with all web dependencies
3. **Creates a `.env` file** template for your API keys
4. **Creates enhanced activation scripts** that automatically load your `.env` file

## Environment Variables

After running the setup script, edit `.env` and add your API keys:

```bash
# Required: At least one LLM provider
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Optional: Web search
TAVILY_API_KEY=...
SERPER_API_KEY=...

# Optional: Text-to-speech
ELEVENLABS_API_KEY=...
```

## Activation Scripts

The setup creates enhanced activation scripts that automatically load your `.env` file:

- **Windows**: `venv\Scripts\activate-env.bat` or `venv\Scripts\activate-env.ps1`
- **Unix/macOS**: `venv/bin/activate-env`

These scripts:
1. Activate the virtual environment
2. Load environment variables from `.env`
3. Skip placeholder values (containing "your-...-here")

## Manual .env Loading

The `launch-council.py` script automatically loads `.env` if it exists in the project root, so you don't need to manually activate the venv if you're just launching the web app.

## Troubleshooting

### PowerShell Execution Policy
If you get an execution policy error on Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### .env Not Loading
- Ensure `.env` is in the project root (same directory as `launch-council.py`)
- Check that your API keys don't contain placeholder text like "your-key-here"
- Verify the `.env` file uses `KEY=value` format (no spaces around `=`)

### Virtual Environment Issues
- Delete `venv/` and run the setup script again
- Ensure Python 3.11+ is installed and in your PATH
