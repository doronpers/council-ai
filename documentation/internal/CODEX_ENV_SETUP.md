# Codex Environment Setup for council-ai

This document provides the complete configuration for setting up a Codex development environment for `council-ai`.

## 1. Name & Description

- **Name**: `council-ai / dev + tests`
- **Description**: `Full council-ai dev env with dependencies, pytest, linting, and API access.`

## 2. Container Image & Workspace

- **Container image**: `universal` (Ubuntu 24.04 - perfect for Python/AI/agents stack)
- **Workspace directory**: `/workspace/council-ai` (default - no change needed)

## 3. Setup Script & Caching

### Setup Script

- **Mode**: `Manual`
- **Script path**: `/workspace/council-ai/scripts/codex-setup.sh`

The setup script (`scripts/codex-setup.sh`) will:

- Upgrade pip
- Install council-ai in editable mode with dev dependencies: `pip install -e ".[dev]"`
- Install pre-commit hooks
- Verify installation
- Run quick sanity check (test discovery)

### Container Caching

- **Container Caching**: `On`
- This significantly reduces startup time after the first run

## 4. Environment Variables & Secrets

### Environment Variables (Non-sensitive configuration)

Add these environment variables for Codex-specific behavior:

```
COUNCIL_ENV=codex
COUNCIL_LOG_LEVEL=INFO
COUNCIL_TEST_MODE=true
PYTHONUNBUFFERED=1
PYTHONUTF8=1
```

**Explanation:**

- `COUNCIL_ENV=codex` - Identifies Codex environment for conditional logic
- `COUNCIL_LOG_LEVEL=INFO` - Sets appropriate log level for development
- `COUNCIL_TEST_MODE=true` - Enables test-friendly behavior
- `PYTHONUNBUFFERED=1` - Ensures clear, real-time logs
- `PYTHONUTF8=1` - Handles Unicode properly

### Secrets (API Keys)

Add these secrets for full functionality:

**Required for LLM functionality:**

- `OPENAI_API_KEY` - For OpenAI GPT models
- `ANTHROPIC_API_KEY` - For Anthropic Claude models
- `GEMINI_API_KEY` - For Google Gemini models

**Optional but recommended:**

- `AI_GATEWAY_API_KEY` - For Vercel AI Gateway (unified access)
- `ELEVENLABS_API_KEY` - For text-to-speech functionality
- `TAVILY_API_KEY` - For web search integration
- `PERPLEXITY_API_KEY` - For research-oriented queries

**Best Practices:**

- Use project-scoped or org-scoped keys, not personal keys
- Only add secrets actually needed for your testing scenarios
- Rotate keys regularly

## 5. Agent Internet Access & Domain Allowlist

### Internet Access

- **Agent internet access**: `On`
- Required for meaningful testing with real LLM API calls

### Domain Allowlist

**Start with**: `Common dependencies` (Codex default)

**Then add these specific domains:**

```
api.openai.com
api.anthropic.com
generativelanguage.googleapis.com
gateway.ai.vercel.app
api.elevenlabs.io
api.tavily.com
api.perplexity.ai
pypi.org
files.pythonhosted.org
github.com
raw.githubusercontent.com
```

**Explanation:**

- `api.openai.com` - OpenAI API
- `api.anthropic.com` - Anthropic API
- `generativelanguage.googleapis.com` - Google Gemini API
- `gateway.ai.vercel.app` - Vercel AI Gateway
- `api.elevenlabs.io` - ElevenLabs TTS
- `api.tavily.com` - Tavily web search
- `api.perplexity.ai` - Perplexity API
- `pypi.org`, `files.pythonhosted.org` - Python package installation
- `github.com`, `raw.githubusercontent.com` - For shared-ai-utils dependency

### Allowed HTTP Methods

- **Allowed HTTP Methods**: `All methods`
- Required for full functionality (POST for API calls, GET for package downloads)

## 6. Usage Examples

Once the environment is set up, you can use Codex tasks for:

### Running Tests

```bash
# Run all tests
pytest

# Run fast tests only (excludes slow/integration tests)
pytest -m "not slow and not integration"

# Run specific test file
pytest tests/test_core.py

# Run with coverage
pytest --cov=src/council_ai --cov-report=html
```

### Code Quality Checks

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Development Workflow

```bash
# Install new dependencies
pip install -e ".[dev,web,anthropic]"

# Run council CLI
council consult "Your question here"

# Start web app
council web
```

## 7. Maintenance

When council-ai's dev workflow changes:

1. **Update `scripts/codex-setup.sh`** if:
   - New dev dependencies are added
   - Setup process changes
   - New tools need installation

2. **Update environment variables/secrets** in Codex if:
   - New API keys are needed
   - Environment variable names change
   - New services are integrated

3. **Update domain allowlist** if:
   - New external APIs are used
   - New package repositories are needed

## 8. Troubleshooting

### Setup script fails

- Check Codex logs for specific error messages
- Verify Python 3.11+ is available
- Ensure network access is enabled during setup

### Tests fail with API errors

- Verify API keys are set correctly in Secrets
- Check domain allowlist includes required APIs
- Ensure Agent internet access is On

### Import errors

- Verify `pip install -e ".[dev]"` completed successfully
- Check that shared-ai-utils dependency installed (from GitHub)
- Run `pip list | grep council-ai` to verify installation

### Pre-commit hooks fail

- This is non-critical - setup script continues even if pre-commit install fails
- You can manually run `pre-commit install` if needed
- Or skip pre-commit hooks: `pre-commit run --all-files --hook-stage manual`

## Notes

- The setup script uses `--quiet` flags to reduce noise in logs
- Test discovery check doesn't fail setup if tests have issues (intentional)
- Container caching means subsequent runs will be much faster
- Workspace config is stored in `.workspace-config/council-ai/` (not `~/.config/`)

## 9. LM Studio (Local LLM) Configuration

### Overview

LM Studio runs locally on your machine and provides a local, cost-free LLM server. Council-ai can automatically detect and use LM Studio if it's running.

### Default Configuration

By default, council-ai looks for LM Studio at:

- **Default URL**: `http://localhost:1234/v1`
- **Provider**: `lmstudio`
- **No API key required** (LM Studio doesn't use authentication)

### Configuration Options

You can configure LM Studio in two ways:

#### Option 1: Via Config File (Recommended)

Create or edit `.workspace-config/council-ai/config.yaml`:

```yaml
api:
  provider: lmstudio
  base_url: http://localhost:1234/v1
  # Optional: specify model name
  model: your-model-name
```

#### Option 2: Via Environment Variables

Add these to your Codex **Environment Variables**:

```
COUNCIL_CONFIG_DIR=/workspace/council-ai/.workspace-config/council-ai
```

Or use the config path format:

```
COUNCIL_CONFIG_DIR=/workspace/council-ai/.workspace-config/council-ai
```

Then create the config file at that location.

### Important: Container Networking Limitation

⚠️ **Note**: Codex runs in a container, and `localhost:1234` inside the container refers to the container itself, not your host machine where LM Studio is running.

**Solutions:**

1. **Use host.docker.internal** (if Codex containers support it):

   ```yaml
   api:
     base_url: http://host.docker.internal:1234/v1
   ```

2. **Use your machine's IP address**:

   ```yaml
   api:
     base_url: http://192.168.1.XXX:1234/v1 # Replace with your actual IP
   ```

3. **Test with cloud APIs first**: For Codex testing, you may want to use cloud APIs (OpenAI, Anthropic) instead, and reserve LM Studio for local development.

### Verification

To verify LM Studio is accessible from the Codex container:

```bash
# Check if LM Studio is reachable
curl http://localhost:1234/v1/models

# Or with host.docker.internal
curl http://host.docker.internal:1234/v1/models
```

### Using LM Studio as Default

If you want LM Studio to be the default provider when available:

1. Configure it in `config.yaml` as shown above (recommended)
2. Or set `COUNCIL_CONFIG_DIR` environment variable to point to your config directory
3. Council-ai will automatically detect if LM Studio is running and use it

### Fallback Behavior

If LM Studio is configured but not available, council-ai will:

- Log a warning
- Fall back to other configured providers (Anthropic, OpenAI, etc.) if available
- Or fail gracefully if no other providers are configured
