# Troubleshooting Guide

Common issues and solutions for Council AI.

## Setup & Installation

### "ModuleNotFoundError: No module named 'council_ai'"

**Cause**: Virtual environment not activated or package not installed

**Solution**:

```bash
# Activate venv
source venv/bin/activate        # macOS/Linux
# or
venv\Scripts\activate.bat       # Windows

# Reinstall package
pip install -e ".[dev]"
```

### "Port 8000 already in use"

**Cause**: Another process is using port 8000

**Solutions**:

1. Run on a different port:

   ```bash
   python launch-council.py --web --port 8080
   ```

2. Find and stop the other process:

   ```bash
   # macOS/Linux
   lsof -i :8000
   kill -9 <PID>

   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

### Virtual Environment Won't Activate

**Issue**: PowerShell says "running scripts is disabled"

**Solution** (Windows PowerShell):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteS igned -Scope CurrentUser
# Then activate again
.\venv\Scripts\Activate.ps1
```

**Issue**: "command not found: python3" or "python not found"

**Solution**:

- Install Python 3.9+ from [python.org](https://python.org)
- Or use a package manager:

  ```bash
  # macOS
  brew install python3

  # Ubuntu/Debian
  sudo apt-get install python3 python3-venv

  # Windows
  choco install python
  ```

### "pip install" hangs or fails

**Issue**: Network issues, outdated pip, or conflicting packages

**Solutions**:

```bash
# Upgrade pip first
pip install --upgrade pip

# Try with timeout
pip install --default-timeout=1000 -e ".[dev]"

# Install from cache
pip install --no-index -f ./wheels -e .

# Last resort: use requirements.txt directly
pip install -r requirements.txt
```

---

## LLM Provider Issues

### "Invalid API key" or "Unauthorized"

**Cause**: API key missing, incorrect, or expired

**Solutions**:

1. **Check your API key**:
   - Copy exactly from provider (no extra spaces/quotes)
   - Ensure it's in `.env` or environment variable

2. **Verify provider supports the model**:
   - OpenAI: Use valid models like `gpt-4`, `gpt-3.5-turbo`
   - Anthropic: Use `claude-3-opus`, `claude-3-sonnet`, etc.
   - Gemini: Use `gemini-pro`

3. **Test the API key**:

   ```bash
   # For OpenAI
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_KEY"
   ```

### "Connection refused" or "Network error"

**Cause**:

- Internet not connected
- Firewall blocking API calls
- LLM provider API is down

**Solutions**:

- Check internet connection: `ping 8.8.8.8`
- Try a different LLM provider
- For local LLMs (Ollama, LM Studio), ensure they're running
- Check provider status page (e.g., openai.com/status)

### Local LLM (Ollama / LM Studio) Not Working

**Issue**: "Connection refused" when trying to use local LLM

**For Ollama**:

1. Ensure Ollama is running: `ollama serve`
2. Pull a model: `ollama pull llama2`
3. Verify it's working: `curl http://localhost:11434/api/tags`
4. In Council AI, set `OLLAMA_BASE_URL=http://localhost:11434` if non-standard port

**For LM Studio**:

1. Open LM Studio and start the local server
2. Set port to 1234 (default)
3. Verify: `curl http://localhost:1234/v1/models`
4. In Council AI, select "LM Studio" provider

### "Model not found" or "Invalid model"

**Cause**: Model name doesn't exist or isn't loaded

**Solutions**:

1. List available models:
   - OpenAI: Check [OpenAI docs](https://platform.openai.com/docs/models)
   - Local: `ollama list` or check LM Studio UI
2. Use a valid model name in config or CLI
3. Ensure model is downloaded (for local LLMs)

---

## Web Interface Issues

### "Cannot connect to <http://localhost:8000>"

**Cause**: Web server not running

**Solutions**:

```bash
# Start web server
python launch-council.py --web

# Check it started
curl http://localhost:8000
```

### Frontend loads but can't contact backend

**Cause**: CORS (Cross-Origin Resource Sharing) issue or backend not running

**Solutions**:

1. Verify backend is running:

   ```bash
   curl http://localhost:8000/health
   ```

2. Check console for CORS errors (F12 → Console tab)
3. Ensure you're accessing from `http://localhost:8000`, not `127.0.0.1:8000`

### "Cannot read property 'providers' of undefined"

**Cause**: Frontend trying to access data before it loaded

**Solution**: Refresh page (Ctrl+R or Cmd+R)

### Onboarding wizard won't submit

**Cause**: Validation error (usually API key issue)

**Solutions**:

1. Check browser console (F12 → Console) for error messages
2. Ensure API key is in `.env` or environment variable
3. For local LLMs, ensure they're running and accessible
4. Try skipping web search (optional feature)

---

## Configuration Issues

### "Config file not found"

**Cause**: `config.yaml` missing or in wrong location

**Solution**: Copy example config:

```bash
cp config.yaml.example config.yaml
```

### Configuration not being applied

**Cause**: Configuration precedence misunderstood

**Debug**: Check which config is being used:

```bash
# CLI
council config show

# Or check precedence order:
# 1. CLI args (--provider openai)
# 2. Environment variables (export OPENAI_API_KEY=...)
# 3. config.yaml file
# 4. Defaults
```

### "Unknown provider" or "Invalid domain"

**Cause**: Typo in provider or domain name

**Solutions**:

- Valid providers: `openai`, `anthropic`, `gemini`, `ollama`, `lmstudio`, `local`
- Valid domains: `research`, `engineering`, `business`, `writing`, `analysis`, `teaching`, and more
- List all: `council config list-domains`

---

## CLI Issues

### "Command not found: council"

**Cause**:

- Virtual environment not activated
- Package not installed

**Solution**:

```bash
source venv/bin/activate  # macOS/Linux
pip install -e .
council --help
```

### CLI command exits immediately with no output

**Cause**: Error occurred but wasn't logged properly

**Solution**: Enable debug logging:

```bash
export COUNCIL_DEBUG=1
council run
```

### "File not found" when loading context

**Cause**: Wrong file path or file doesn't exist

**Solution**:

- Use absolute paths or relative from where you run the command
- Check file exists: `ls -la /path/to/file`
- See [CONTEXT_INJECTION_GUIDE.md](documentation/CONTEXT_INJECTION_GUIDE.md)

---

## Response Quality Issues

### "Responses are generic or unhelpful"

**Cause**: Model, domain, or personas not appropriate for task

**Solutions**:

1. Try a more capable model (e.g., `gpt-4` instead of `gpt-3.5-turbo`)
2. Choose appropriate domain and personas
3. Provide more context using context injection
4. Enable web search for current information

See [COMMON_TASKS.md](documentation/COMMON_TASKS.md#improve-response-quality)

### Web search not working

**Cause**: Search provider not configured or credentials missing

**Solutions**:

1. Check search provider is configured in `.env`:

   ```bash
   TAVILY_API_KEY=...    # OR
   SERPER_API_KEY=...    # OR
   GOOGLE_API_KEY=...
   ```

2. Verify API keys are valid
3. See [WEB_SEARCH_AND_REASONING.md](documentation/WEB_SEARCH_AND_REASONING.md)

### "Response is too long" or "Response cut off"

**Cause**: Model hitting token limit

**Solutions**:

1. Ask for shorter response: "Give a 100-word summary..."
2. Narrow the scope of your question
3. Use a model with higher context limit (`gpt-4` vs `gpt-3.5-turbo`)

---

## Performance Issues

### Everything is slow

**Cause**:

- Network latency to LLM provider
- Slow hardware
- Too many tokens

**Solutions**:

1. Use a local LLM (Ollama, LM Studio) for faster responses
2. Use a faster cloud model (`gpt-3.5-turbo` vs `gpt-4`)
3. Reduce context size or token limit
4. Check network speed: `ping 8.8.8.8`

### Memory usage very high

**Cause**: Large context files or many conversations

**Solutions**:

1. Clear conversation history
2. Reduce context file size
3. Close other applications
4. Restart Council AI

---

## Platform-Specific Issues

### macOS

**Issue**: "Permission denied" when running script

**Solution**:

```bash
chmod +x launch-council.py
chmod +x bin/launch-council-web.command
```

**Issue**: "psutil" or "scipy" fails to install

**Solution**: Install system dependencies:

```bash
brew install gfortran openblas
pip install --upgrade pip
pip install -e ".[dev]"
```

### Windows

**Issue**: Long file paths break builds

**Solution**: Enable long file paths:

```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Linux

**Issue**: Permission denied for `/home/user/.cache`

**Solution**:

```bash
chmod -R u+w ~/.cache
pip install -e ".[dev]"
```

---

## Getting More Help

1. **Check documentation**: [documentation/README.md](documentation/README.md)
2. **Search GitHub issues**: [github.com/doronpers/council-ai/issues](https://github.com/doronpers/council-ai/issues)
3. **Enable debug mode**:

   ```bash
   export COUNCIL_DEBUG=1
   council run
   ```

4. **Run test suite**:

   ```bash
   pytest -v
   ```

---

## Reporting Issues

When reporting a bug, include:

- Python version: `python --version`
- Council AI version: `council --version`
- OS: (Windows/macOS/Linux)
- Steps to reproduce
- Full error message and stack trace
- Relevant `.env` values (without secrets!)

See [CONTRIBUTING.md](CONTRIBUTING.md) for full issue template.
