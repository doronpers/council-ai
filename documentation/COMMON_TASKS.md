# Common Tasks

Quick how-to guides for frequent operations in Council AI.

## Getting Started

### Set Up Council AI (5 minutes)

See [GETTING_STARTED.md](../GETTING_STARTED.md) for detailed instructions.

Quick version:

```bash
git clone https://github.com/doronpers/council-ai.git
cd council-ai
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
python launch-council.py --web  # Open browser to http://localhost:8000
```

---

## Configuration

### Add an API Key

1. **Get key from provider**:
   - OpenAI: [platform.openai.com](https://platform.openai.com/account/api-keys)
   - Anthropic: [console.anthropic.com](https://console.anthropic.com)
   - Google Gemini: [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

2. **Add to `.env`**:

   ```bash
   # In repository root
   cp .env.example .env
   # Edit .env with your favorite editor
   export OPENAI_API_KEY=sk-...
   ```

3. **Or set as environment variable**:

   ```bash
   export OPENAI_API_KEY=sk-...
   python launch-council.py --web
   ```

### Set Up Local LLM (Ollama or LM Studio)

**Using Ollama**:

1. Install [Ollama](https://ollama.ai)
2. Run `ollama serve` in a terminal
3. In another terminal: `ollama pull llama2`
4. In Council AI: Select "Ollama" as provider
5. No API key needed!

**Using LM Studio**:

1. Install [LM Studio](https://lmstudio.ai)
2. Open app and select a model
3. Click "Start Server" (localhost:1234)
4. In Council AI: Select "LM Studio" as provider
5. No API key needed!

### Create a Custom config.yaml

Create `config.yaml` in repository root:

```yaml
# LLM Configuration
provider: openai # or: anthropic, gemini, ollama, lmstudio
model: gpt-4 # Model name

# Behavior
temperature: 0.7 # 0 = focused, 1 = creative
max_tokens: 2000

# Interface
domain: research # Predefined context domain
web_search_enabled: true

# LLM-Specific (optional)
# For Anthropic:
anthropic_model: claude-3-opus
# For Ollama:
ollama_base_url: http://localhost:11434
# For LM Studio:
lmstudio_base_url: http://localhost:1234/v1
```

Then use it:

```bash
council run --config config.yaml
```

For all options, see [CONFIGURATION.md](CONFIGURATION.md).

---

## Personas & Domains

### Use a Specific Domain

Domains provide context and guidance for different use cases.

Available domains: `research`, `engineering`, `business`, `writing`, `analysis`, `teaching`, `creative`, `legal`, `medical`, `financial`, `technical`, `academic`, `journalistic`, `scientific`, `consulting`

**Web UI**:

1. Open <http://localhost:8000>
2. Step 1 of onboarding: Select "Domain"
3. Choose domain
4. Complete setup

**CLI**:

```bash
council run --domain research
```

**Config file**:

```yaml
domain: research
```

### Add Custom Personas to a Consultation

Personas are AI team members that help answer your question.

**Web UI**:

1. In the consultation bar, click "Add Team Member"
2. Browse or search for personas
3. Click to add (shows ✓)
4. See persona details by clicking ℹ️ icon
5. Submit your question

**CLI**:
Personas are selected during initialization. See [CONTRIBUTING.md](../CONTRIBUTING.md) for adding custom personas.

### View All Built-In Personas

**Web UI**:

1. Open <http://localhost:8000>
2. Start consultation, click "Add Team Member"
3. Browse all available personas

**CLI**:

```bash
council config list-personas
```

**Reference**: [PERSONAS_AND_DOMAINS.md](PERSONAS_AND_DOMAINS.md)

### Create a Custom Persona

See [CONTRIBUTING.md](../CONTRIBUTING.md#adding-custom-personas) for detailed instructions.

Quick version:

1. Create `src/council_ai/personas/my_persona.py`
2. Define class inheriting from `BasePersona`
3. Add to `personas/__init__.py`
4. Register in config

For full code example, see [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Web Search & Reasoning

### Enable Web Search

Council AI can search the web for real-time information.

**Requirements**:

- One search provider API key (Tavily, Serper, or Google)

**Setup**:

1. **Get API key**:
   - [Tavily API](https://tavily.com) (recommended, free tier)
   - [Serper API](https://serper.dev) (free tier available)
   - [Google Custom Search](https://programmablesearchengine.google.com) (requires setup)

2. **Add to `.env`**:

   ```bash
   TAVILY_API_KEY=YOUR_KEY
   ```

3. **Enable in config**:

   ```yaml
   web_search_enabled: true
   ```

4. **Use it**:
   - Web UI: Just ask! Search happens automatically when helpful
   - CLI: `council run --web-search`

See [WEB_SEARCH_AND_REASONING.md](WEB_SEARCH_AND_REASONING.md) for details.

### Use Reasoning Mode

Reasoning mode (slow, deep thinking):

- Makes the LLM "think harder" about complex problems
- Slower but more accurate for hard problems
- Requires OpenAI API access (GPT-4 with reasoning)

**CLI**:

```bash
council run --reasoning
```

**Web UI**: In onboarding, enable "Reasoning Mode"

See [WEB_SEARCH_AND_REASONING.md](WEB_SEARCH_AND_REASONING.md#reasoning-mode) for details.

---

## Using Context

### Load Context from Files

Context is background information you provide to shape responses.

**Web UI**:

1. Click "Configuration"
2. Scroll to "Context"
3. Upload or paste context text
4. Submit question

**CLI**:

```bash
council run --context file.txt
# or
council run --context "Background: The company is focused on AI research..."
```

**Programmatically** (Python):

```python
from council_ai import ConsultationEngine

engine = ConsultationEngine()
result = engine.consult(
    question="What should we do?",
    context="Our company is focused on AI research...",
    domain="business"
)
print(result.response)
```

For advanced context loading, see [CONTEXT_INJECTION_GUIDE.md](CONTEXT_INJECTION_GUIDE.md).

### Use LLM Response Reviewer

Review and critique LLM responses using domain-expert personas.

**CLI**:

```bash
# 1. Run normal consultation
council run

# 2. Review the response
council review "Is this response accurate for our research domain?"
```

**Web UI**:

1. Get a response
2. Click "Review Response"
3. See detailed analysis from reviewer personas

See [REVIEWER_SETUP.md](REVIEWER_SETUP.md) for full guide.

---

## Web UI

### Complete the Onboarding Wizard

First time using Council AI? Complete the 6-step wizard:

1. **Select Domain** - Choose context (research, business, etc.)
2. **Select LLM Provider** - Choose where to run (OpenAI, local, etc.)
3. **API Configuration** - Add API keys or local setup
4. **Team Members** - Add AI personas to help
5. **Enable Web Search** - (Optional) Turn on live search
6. **Reasoning Mode** - (Optional) Enable deep thinking

After onboarding, you can change settings anytime in Configuration panel.

### Submit a Consultation

1. Type your question in the "Ask something..." field
2. (Optional) Add team members using "Add Team Member" button
3. Click "Submit" or press Cmd+Enter / Ctrl+Enter
4. View response with reasoning breakdown

### Change Configuration During Session

1. Click "Configuration" panel (gear icon)
2. Change:
   - LLM Provider
   - Model
   - Temperature / Max Tokens
   - Enable/disable web search
3. Changes apply to next submission

See [WEB_APP.md](WEB_APP.md) for full walkthrough.

---

## CLI Usage

### Run Interactive Session

```bash
council run
```

Starts interactive CLI where you can:

- Ask questions
- Get responses with reasoning
- Optionally search the web
- Switch domains/providers mid-session

### Run One Query and Exit

```bash
council run --query "What is machine learning?"
```

### Use Specific Configuration

```bash
council run \
  --domain research \
  --provider openai \
  --model gpt-4 \
  --web-search \
  --temperature 0.7
```

### See All CLI Options

```bash
council --help
council run --help
```

See [CLI reference](../documentation/README.md) for all commands.

---

## Improve Response Quality

### Problem: Responses are too generic

**Solutions**:

1. **Use web search**: Enables current information

   ```bash
   council run --web-search
   ```

2. **Add context**: Provide background information

   ```bash
   council run --context "Our research focuses on neural networks..."
   ```

3. **Choose better domain**: Pick most relevant domain

   ```bash
   council run --domain research
   ```

4. **Add specific personas**: Include domain experts
   - Web UI: Click "Add Team Member" and select specific personas
   - CLI: Edit `config.yaml` to include personas

5. **Use better model**: More capable models give better results

   ```bash
   council run --model gpt-4
   ```

### Problem: Response is wrong or hallucinated

**Solutions**:

1. **Enable reasoning mode** (slow but more accurate):

   ```bash
   council run --reasoning
   ```

2. **Enable web search** (gets real information):

   ```bash
   council run --web-search
   ```

3. **Add context**: Provide facts to base response on

   ```bash
   council run --context "Key fact: This was invented in 1995..."
   ```

4. **Lower temperature**: Makes model more focused/conservative

   ```yaml
   # in config.yaml
   temperature: 0.3 # Lower = more focused
   ```

5. **Use review mode**: Have expert personas critique response
   - CLI: `council review "Is this accurate?"`
   - Web UI: Click "Review Response"

---

## Contributing

### Run Tests

```bash
pytest                  # Run all tests
pytest -v             # Verbose output
pytest tests/unit/    # Just unit tests
```

### Format and Lint Code

```bash
black .               # Auto-format code
isort .               # Organize imports
flake8 .              # Check for issues
mypy .                # Type check
```

### Add a New Persona

1. Create `src/council_ai/personas/my_persona.py`:

```python
from council_ai.personas.base import BasePersona

class MyPersona(BasePersona):
    def __init__(self):
        super().__init__(
            name="My Expert",
            description="Does X, Y, Z",
            system_prompt="You are an expert in..."
        )
```

1. Add to `src/council_ai/personas/__init__.py`:

```python
from .my_persona import MyPersona

__all__ = [..., "MyPersona"]
```

1. Register in config and test

See [CONTRIBUTING.md](../CONTRIBUTING.md#adding-custom-personas) for full guide.

### Submit a Pull Request

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test
3. Format code: `black . && isort .`
4. Commit: `git commit -m "feat: add my feature"`
5. Push: `git push origin feature/my-feature`
6. Open PR on GitHub

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guidelines.

---

## Troubleshooting

If something isn't working, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

Common issues:

- **Setup**: See [GETTING_STARTED.md](../GETTING_STARTED.md)
- **Configuration**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Web search**: See [WEB_SEARCH_AND_REASONING.md](WEB_SEARCH_AND_REASONING.md)
- **Errors**: See [ERROR_HANDLING.md](ERROR_HANDLING.md)

---

## Getting Help

- **Documentation**: [documentation/README.md](README.md)
- **Issues**: [github.com/doronpers/council-ai/issues](https://github.com/doronpers/council-ai/issues)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
