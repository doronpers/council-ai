# Getting Started with Council AI

Welcome! This guide walks you through setup in 5-10 minutes.

## System Requirements

- **Python**: 3.9 or higher
- **Node.js**: 18+ (for web UI)
- **Internet**: For LLM provider API keys (optional for local LLMs)

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
git clone https://github.com/doronpers/council-ai.git
cd council-ai
```

### 2. Set Up Python Virtual Environment

Choose your operating system:

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

**Windows (Command Prompt):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Configure Your First LLM

Create a `.env` file in the repository root:

```bash
cp .env.example .env
```

Then edit `.env` and add your LLM provider details. See **Configuration** section below.

### 4. Launch Council

**Web interface (recommended):**

```bash
python launch-council.py --web
```

Then open <http://localhost:8000> in your browser.

**CLI interface:**

```bash
council --help
```

That's it! 🎉

---

## Configuration

### Environment Variables

Create a `.env` file with your LLM provider credentials:

```bash
# OpenAI (cloud)
OPENAI_API_KEY=sk-...

# Anthropic (cloud)
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini (cloud)
GEMINI_API_KEY=AIzaSy...

# LM Studio / Ollama (local)
# No API key needed; just set the provider in the web UI
```

### Configuration Precedence

Council AI checks settings in this order (first match wins):

1. **Command-line arguments** (e.g., `council --provider openai`)
2. **Environment variables** (e.g., `OPENAI_API_KEY`)
3. **Config file** (`config.yaml`)
4. **Defaults** (built-in values)

### Configuration File

For persistent settings, create `config.yaml` in the repository root:

```yaml
# Example config.yaml
provider: openai
model: gpt-4
domain: research
temperature: 0.7
web_search_enabled: true
```

For full configuration options, see [CONFIGURATION.md](documentation/CONFIGURATION.md).

---

## Using Council AI

### Web Interface

1. Open <http://localhost:8000>
2. Complete the onboarding wizard (first time only)
3. Type your question in the consultation bar
4. Add team members (personas) to help
5. Click **Submit** to get a response

### CLI Interface

```bash
# Start interactive session
council run

# Analyze with a specific domain
council run --domain research

# Use a specific LLM provider
council run --provider openai --model gpt-4

# See all options
council --help
```

### Using Local LLMs

**With LM Studio:**

1. Download [LM Studio](https://lmstudio.ai)
2. Start the LM Studio local server
3. In Council AI: Select "LM Studio" as provider
4. No API key needed

**With Ollama:**

1. Install [Ollama](https://ollama.ai)
2. Pull a model: `ollama pull llama2`
3. In Council AI: Select "Ollama" as provider
4. No API key needed

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'council_ai'"

Your virtual environment isn't activated. Run:

```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

Then reinstall:

```bash
pip install -e ".[dev]"
```

### "Port 8000 already in use"

Another process is using port 8000. Either:

- Stop the other process
- Run on a different port: `python launch-council.py --web --port 8080`

### Virtual Environment Activation Issues

**Issue**: Venv activation fails with script error

**Solution**:

- Ensure you're using `python3` (not `python`) to create the venv
- Delete the venv and recreate: `rm -rf venv && python3 -m venv venv`
- Activate again: `source venv/bin/activate`

**Windows-specific**:

- If PowerShell says "cannot be loaded because running scripts is disabled":

  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteS igned -Scope CurrentUser
  ```

  Then try activating again

### "LLM provider not responding"

1. Verify your API key in `.env` is correct
2. Check internet connection
3. Test with a known-working provider (e.g., swap to local Ollama)
4. See [TROUBLESHOOTING.md](documentation/TROUBLESHOOTING.md) for provider-specific issues

### Other Issues?

See [TROUBLESHOOTING.md](documentation/TROUBLESHOOTING.md) for common issues and solutions.

---

## Next Steps

- **Learn features**: [WEB_APP.md](documentation/WEB_APP.md) for web UI guide
- **Set up web search**: [WEB_SEARCH_AND_REASONING.md](documentation/WEB_SEARCH_AND_REASONING.md)
- **Add custom personas**: [CONTRIBUTING.md](CONTRIBUTING.md#adding-custom-personas)
- **Reference**: [QUICK_REFERENCE.md](documentation/QUICK_REFERENCE.md) for code examples

---

## Which Repository?

Are you using the right one?

- **council-ai**: The main open-source framework
- **council-ai-personal**: Personal agent templates for individual use

See [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) for details on which to use.

---

## Getting Help

- **Docs**: Start with [README.md](README.md)
- **Questions**: Check [documentation/](documentation/README.md)
- **Issues**: See [TROUBLESHOOTING.md](documentation/TROUBLESHOOTING.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

Happy researching! 🚀
