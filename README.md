# 🏛️ Council AI

**Intelligent Advisory Council System** - Get advice from a council of AI-powered personas with diverse perspectives and expertise.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/doronpers/council-ai)

---

## ☁️ Open in Codespaces

Get up and running immediately with a fully configured development environment in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/doronpers/council-ai)

## 🚀 Quickstart (Zero Cost, No API Key Required)

The best way to experience Council AI is by using **LM Studio** for local, private, and cost-free consulting.

1. **Download LM Studio**: [lmstudio.ai](https://lmstudio.ai/)
2. **Load a Model**: Mistral, Llama 3, or any GGUF model
3. **Start Server**: Turn on the "Local Server" inside LM Studio
4. **Run Council**:

   ```bash
   # Run the interactive setup (detects LM Studio automatically)
   council init
   
   # Consult the council (uses your local model by default)
   council consult "Should we redesign our API?"
   ```

### First-Time Setup

For users without local LLMs, we support all major cloud providers:

```bash
# Run the interactive setup wizard
council init
```

This will guide you through:

- Detecting **LM Studio** (cost-free, local)
- Configuring **Anthropic**, **OpenAI**, or **Gemini** (cloud fallback)
- Setting your default domain
- Understanding next steps

To use cloud providers (requires API key):

```bash
# Install with a provider (choose one)
pip install -e ".[anthropic]"   # For Anthropic Claude
pip install -e ".[openai]"      # For OpenAI GPT
pip install -e ".[gemini]"      # For Google Gemini

# Set your API key (choose one)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# Try a simple consultation
python examples/simple_example.py
```

---

## Overview

Council AI provides a framework for consulting multiple AI "personas" - each with distinct expertise, perspectives, and decision-making approaches. Whether you're making business decisions, reviewing code, planning strategy, or working on creative projects, the council provides comprehensive, multi-perspective advice.

**Key Features:**

- 🎭 **14 Built-in Personas** - Advisory Council (build it right) + Red Team (break & survive) + Specialists
- 🌐 **15 Domain Presets** - Coding, business, startup, creative, career, and more
- 🔧 **Fully Customizable** - Create your own personas, adjust weights, modify traits
- 🤖 **Multi-Provider Support** - Anthropic, OpenAI, Google Gemini, or custom endpoints. Personas can use various LLM providers simultaneously.
- 💬 **Multiple Modes** - Individual, synthesis, debate, vote, or sequential
- 🔍 **Web Search Integration** - Connect to live web data via Tavily, Serper, or Google Custom Search
- 🧠 **Reasoning Modes** - Extended thinking for complex analysis
- 📝 **Session & History Management** - Track, resume, search, and export consultations
- 🧭 **Standalone Web App** - Modern React/TypeScript UI with Dieter Rams-inspired design
- 🔊 **Text-to-Speech** - Voice responses via ElevenLabs and OpenAI TTS
- 📦 **Portable Package** - pip-installable, use in any project
- 📖 **[Full API Documentation](documentation/API_REFERENCE.md)** - Complete Python API reference

---

## 📁 Repository Structure

**Important**: If you have both `council-ai` and `council-ai-personal` repositories:

- **`council-ai`** = Main repository (use this for running the app)
- **`council-ai-personal`** = Your personal customizations (personas, configs)

**Always run Council AI from the `council-ai` directory.** It will automatically detect and use your personal configs from `council-ai-personal` if it exists as a sibling directory.

See [WHICH_REPO.md](WHICH_REPO.md](WHICH_REPO.md) for more details.

## Installation

**From PyPI (when published):**

```bash
# Basic installation
pip install council-ai

# With Anthropic Claude support
pip install "council-ai[anthropic]"

# With OpenAI GPT support
pip install "council-ai[openai]"

# With Google Gemini support
pip install "council-ai[gemini]"

# Full installation (all providers)
pip install "council-ai[all]"
```

**Development Installation (from this repo):**

### Quick Setup with Virtual Environment (Recommended)

The easiest way to get started is using the setup script that creates a virtual environment and configures your API keys:

**Windows (PowerShell):**

```powershell
.\setup-venv.ps1
```

**Windows (Command Prompt):**

```cmd
setup-venv.bat
```

**macOS/Linux:**

```bash
chmod +x setup-venv.sh
./setup-venv.sh
```

This will:

- Create a virtual environment (`venv/`)
- Install all dependencies
- Create a `.env` file template for your API keys
- Set up activation scripts that automatically load your secrets

After setup, activate the environment:

- **Windows**: `.\venv\Scripts\activate-env.ps1` or `venv\Scripts\activate-env.bat`
- **macOS/Linux**: `source venv/bin/activate-env`

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/doronpers/council-ai.git
cd council-ai

# Upgrade pip (recommended)
pip install --upgrade pip

# Install with a specific provider (e.g., anthropic)
pip install -e ".[anthropic]"

# Or with all providers
pip install -e ".[all]"

# Or for development (includes testing tools)
pip install -e ".[dev]"
```

### Code Quality & Security Audit

The codebase is regularly audited for quality, security, and type safety. You can run the latest audit suite using:

```bash
# Run the automated audit script (ruff, mypy, bandit, pytest)
./scripts/audit_recent.sh
```

This script ensures that the latest changes adhere to our coding standards and security best practices.

> [!NOTE]
> **Windows Users:** If you encounter "command not found" errors, ensure your Python `Scripts` directory is in your PATH. Alternatively, you can run commands using the `python -m` syntax (e.g., `python -m pytest`, `python -m black src/`).

### Set Your API Key

**Option 1: Using a `.env` file (Recommended)**

If you used the `setup-venv` script, a `.env` file was already created. Just edit it and add your API keys:

```bash
# Edit .env and add your API keys
ANTHROPIC_API_KEY=your-anthropic-key-here
OPENAI_API_KEY=your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
```

Or create it manually:

```bash
# Copy the example file (if available)
cp .env.example .env

# Edit .env and add your API keys
```

The `.env` file is automatically loaded when you:

- Use the `launch-council.py` script
- Activate the virtual environment with `activate-env` (created by setup script)
- Import `council_ai` (it uses `python-dotenv`)

The `.env` file is already in `.gitignore`, so it won't be committed.

### Option 2: Environment Variables

```bash
# Choose your provider
export ANTHROPIC_API_KEY="your-key"    # For Claude
export OPENAI_API_KEY="your-key"       # For GPT-4
export GEMINI_API_KEY="your-key"       # For Gemini
```

### Option 3: Config File

```bash
council config set api.api_key your-key
```

### Option 4: Setup Wizard (Recommended for First-Time Users)

```bash
council init
```

**Priority Order:**

1. CLI flags (`--api-key`)
2. Environment variables
3. `.env` file (auto-loaded)
4. Config file (`~/.config/council-ai/config.yaml`)

### CLI Usage

```bash
# First time? Run the setup wizard
council init

# Explore features without an API key
council quickstart

# Simple consultation
council consult "Should I take this job offer?"

# With a specific domain
council consult --domain startup "Should we pivot?"

# With specific personas
council consult --members grove --members taleb "What's our biggest risk?"

# With a specific mode
council consult --mode sequential "Walk through this step-by-step"

# Interactive mode (with session tracking)
council interactive

# Session & History Management
council history sessions          # List recent sessions
council history resume SESSION_ID # Resume a previous session
council history list              # List all consultations
council history search "keyword"  # Search history
council history export CONSULT_ID # Export to markdown/JSON

# Web app (for user testing)
council web --reload

# Repository review (code/design/security)
council review . --focus all --output review.md

# Manage personas
council persona list
council persona show rams
council persona create --interactive

# Manage domains
council domain list
council domain show coding

# Manage configuration
council config show
council config set api.provider openai
```

### Python API

```python
from council_ai import Council

# Create a council for a domain
council = Council.for_domain("business")

# Consult the council
result = council.consult("Should we enter the European market?")

# Print the synthesis
print(result.synthesis)

# Print individual responses
for response in result.responses:
    print(f"{response.persona.emoji} {response.persona.name}:")
    print(response.content)
    print()
```

---

## Built-in Personas

### Advisory Council (Build It Right)

| Persona (ID)                        | Focus                     | Core Question                                 |
| ----------------------------------- | ------------------------- | --------------------------------------------- |
| 🎨 **Dieter Rams** (`DR`)         | Simplification, Design    | "Is this as simple as possible?"              |
| 🎖️ **Martin Dempsey** (`MD`)   | Mission Clarity, Autonomy | "Can this operate without asking permission?" |
| 🧠 **Daniel Kahneman** (`DK`) | Cognitive Load, UX        | "Does this work with human cognition?"        |
| 🔊 **Julian Treasure** (`JT`) | Communication, Listening  | "Are we listening with integrity?"            |

### Red Team Council (Break & Survive)

| Persona (ID)                                       | Focus                   | Core Question                                       |
| -------------------------------------------------- | ----------------------- | --------------------------------------------------- |
| 🔓 **Pablos Holman** (`PH`)                    | Security, Exploits      | "How would I break this?"                           |
| 🦢 **Nassim Taleb** (`NT`)                      | Risk, Antifragility     | "What's the hidden risk?"                           |
| 🎯 **Andy Grove** (`AG`)                        | Strategy, Competition   | "What 10X force could make us irrelevant?"          |
| 🔍 **Detective Ray Castellano** (`fraud_examiner`) | Fraud tactics, evidence | "How would a sophisticated fraudster exploit this?" |

### Specialist Council (Deep Domain Expertise)

#### Security & Compliance

| Persona (ID)                              | Focus                               | Core Question                                                        |
| ----------------------------------------- | ----------------------------------- | -------------------------------------------------------------------- |
| 🔬 **Dr. Elena Vance** (`signal_analyst`) | Audio forensics, deepfake detection | "What does the physics tell us that perception might miss?"          |
| ⚖️ **Marcus Chen** (`compliance_auditor`) | Regulations, fintech                | "Will this withstand examiner scrutiny and protect the institution?" |

#### Audio & Post-Production

| Persona (ID)                             | Focus                           | Core Question                                                                       |
| ---------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------- |
| 🎭 **James Mitchell** (`adr_supervisor`) | ADR performance & sync          | "Can we match the original performance while fixing technical issues?"              |
| 🎙️ **Sarah Kimura** (`dialogue_editor`)  | Dialogue clarity & continuity   | "Does every word serve the story, and can the audience understand it effortlessly?" |
| 🎚️ **Marcus Webb** (`rerecording_mixer`) | Mix translation & dynamics      | "Does this mix serve the director's vision while meeting delivery requirements?"    |
| 🎬 **Alex Rivera** (`sound_designer`)    | Narrative impact & sound design | "What sounds will make this moment unforgettable and emotionally resonant?"         |

---

## Domain Presets

```bash
# List all domains
council domain list
```

| Domain       | Description             | Default Personas                                                   |
| ------------ | ----------------------- | ------------------------------------------------------------------ |
| `coding`     | Software development    | DR, DK, PH, NT                                      |
| `business`   | Business strategy       | AG, NT, MD, DK                                    |
| `startup`    | Early-stage decisions   | AG, NT, DK, DR                                       |
| `product`    | Product management      | DK, DR, JT, AG                                    |
| `leadership` | Team & org leadership   | MD, DK, AG                                           |
| `creative`   | Creative projects       | JT, DR, DK                                           |
| `writing`    | Written content         | JT, DK, DR                                           |
| `audio_post` | Audio post-production   | dialogue_editor, rerecording_mixer, sound_designer, adr_supervisor |
| `career`     | Career decisions        | AG, DK, MD, NT                                    |
| `decisions`  | Major life decisions    | DK, NT, MD                                           |
| `devops`     | Infrastructure & ops    | MD, PH, NT, AG                                      |
| `data`       | Data science            | DK, NT, DR                                              |
| `general`    | General purpose         | DK, NT, AG, DR                                       |
| `llm_review` | High-quality LLM review | MD, DK, DR, JT                                  |
| `sonotheia`  | Audio defense & fintech | signal_analyst, compliance_auditor, PH, NT                  |

---

## Customization

### Create Custom Personas

**Via YAML:**

Create a YAML file in `~/.config/council-ai/personas/` or a custom directory specified in your config file.

```yaml
# ~/.config/council-ai/personas/my_advisor.yaml
id: my_advisor
name: My Custom Advisor
title: Domain Expert
emoji: '🔮'
category: custom

core_question: 'What would a domain expert ask?'
razor: 'The key principle for decisions.'

traits:
  - name: Expertise
    description: Deep knowledge in the domain
    weight: 1.5
  - name: Practicality
    description: Focuses on actionable advice
    weight: 1.2

focus_areas:
  - Area 1
  - Area 2
  - Area 3
```

**Via CLI:**

```bash
council persona create --from-file my_advisor.yaml
```

**Via Python:**

```python
from council_ai import Council
from council_ai.core.persona import Persona

# Create a custom persona from a YAML file
persona = Persona.from_yaml_file("my_advisor.yaml")

# Add to council
council = Council()
council.add_member(persona)
```

### Modify Persona Weights

```python
council = Council.for_domain("business", api_key="your-key")

# Increase Grove's influence (strategy focus)
council.set_member_weight("AG", 1.5)

# Decrease Kahneman's influence
council.set_member_weight("DK", 0.8)
```

### Add/Remove Traits

```python
from council_ai import get_persona

persona = get_persona("DR")

# Add a trait
persona.add_trait(
    name="Sustainability Focus",
    description="Considers environmental impact",
    weight=1.2
)

# Remove a trait
persona.remove_trait("Minimalism")

# Update a trait's weight
persona.update_trait("Simplification Obsession", weight=1.8)
```

---

## Consultation Modes

```python
from council_ai import Council
from council_ai.core.council import ConsultationMode

council = Council.for_domain("business", api_key="your-key")

# Individual: Each member responds separately
result = council.consult(query, mode=ConsultationMode.INDIVIDUAL)

# Synthesis: Individual responses + synthesized summary (default)
result = council.consult(query, mode=ConsultationMode.SYNTHESIS)

# Sequential: Members respond in order, seeing previous responses
result = council.consult(query, mode=ConsultationMode.SEQUENTIAL)

# Debate: Multiple rounds of discussion
result = council.consult(query, mode=ConsultationMode.DEBATE)

# Vote: Members vote on a decision
result = council.consult(query, mode=ConsultationMode.VOTE)
```

---

## Web Search & Reasoning Modes

### Web Search Integration

Council AI can search the web for current information during consultations. Useful for up-to-date facts, news, research, and current events.

**Supported Providers:**

- **Tavily** (Recommended) - Fast, AI-powered search
- **Serper.dev** - Google search API
- **Google Custom Search** - Official Google API

**Setup:**

```bash
# Add to your .env file
TAVILY_API_KEY=your-tavily-key      # Or
SERPER_API_KEY=your-serper-key      # Or
GOOGLE_API_KEY=your-key
GOOGLE_CSE_ID=your-cse-id
```

**Usage:**

```python
from council_ai import Council, CouncilConfig

# Enable web search
config = CouncilConfig(enable_web_search=True)
council = Council(api_key="key", config=config)

result = council.consult("What are the latest AI developments in 2026?")
```

### Reasoning Modes

Enable deeper analysis with extended thinking for complex queries:

```python
config = CouncilConfig(
    reasoning_mode="analytical"  # chain_of_thought, tree_of_thought, reflective, creative
)
council = Council(api_key="key", config=config)

result = council.consult("Analyze the trade-offs of our scaling strategy")
```

**📖 Full Guide:** [Web Search and Reasoning Documentation](documentation/WEB_SEARCH_AND_REASONING.md)

---

## Context Injection

Inject external context (documents, code, data) into consultations:

```python
context = """
Company: TechStartup Inc.
Revenue: $2M ARR
Team: 15 people
Challenge: Scaling infrastructure
"""

result = council.consult(
    "Should we migrate to Kubernetes?",
    context=context
)
```

**📖 Full Guide:** [Context Injection Guide](documentation/CONTEXT_INJECTION_GUIDE.md)

---

## Structured Synthesis, Weighting, and Failure Behavior

Council AI can optionally request a structured, JSON-schema-backed synthesis. When enabled,
the council first attempts structured synthesis; if that step raises an exception, it falls
back to the normal free-form synthesis. If the structured call returns no data (or returns
`None`), the formatted synthesis text will be empty. Streaming mode always uses free-form
synthesis, even when structured output is enabled, and will still emit synthesis events even
if the synthesis content is empty. Individual member failures are surfaced in their response
content, and only successful responses are included in the synthesis prompt, so if every
member fails you will see only error responses and an empty/low-signal synthesis.

Persona weights are stored on each persona (0.0–2.0) and can be adjusted per council member.
The synthesis prompt explicitly asks the model to weight advisor input by expertise relevance,
so weights act as guidance metadata you can use directly (or via custom hooks) rather than
changing generation parameters by default.

```python
from council_ai import Council, CouncilConfig

config = CouncilConfig()
config.use_structured_output = True  # Enable structured synthesis output

council = Council.for_domain("business", api_key="your-key", config=config)

# Adjust persona influence weights (0.0–2.0)
council.set_member_weight("AG", 1.5)
council.set_member_weight("DK", 0.8)

result = council.consult("Should we expand into Europe?")
print(result.structured_synthesis)  # Structured schema (if available)
print(result.synthesis)             # Markdown-formatted synthesis text
```

---

## Configuration

### Config File

Council AI stores configuration in `~/.config/council-ai/config.yaml`.
Override the location with `COUNCIL_CONFIG_PATH`.

```yaml
api:
  provider: openai
  api_key: null # Use environment variable instead
  model: gpt-4-turbo-preview # or your preferred model
  base_url: null # Optional for OpenAI-compatible endpoints

default_mode: synthesis
default_domain: general
temperature: 0.7
max_tokens_per_response: 1000
synthesis_provider: null # Optional: set to use a separate provider for synthesis
synthesis_model: null # Optional: set to use a different model for synthesis
synthesis_max_tokens: null # Optional: override max tokens for synthesis

presets:
  my_team:
    domain: coding
    members: [rams, holman, grove]
    mode: synthesis
```

### CLI Configuration

```bash
# Set provider
council config set api.provider openai

# Set default domain
council config set default_domain startup

# Set temperature
council config set temperature 0.8

# View config
council config show
```

### Configuration Presets

Save commonly-used configurations as presets for quick access:

```bash
# Save a preset
council config preset-save my-review-team --domain coding --members rams,holman,kahneman --mode synthesis

# List all presets
council config preset-list

# Use a preset in consultation
council consult --preset my-review-team "Review this code"

# Delete a preset
council config preset-delete my-review-team
```

**Presets are perfect for:**

- Different project types (frontend, backend, devops)
- Different consultation styles (quick reviews vs deep analysis)
- Team-specific member combinations

### Set temperature

```bash
council config set temperature 0.8
```

### View config

```bash
council config show
```

---

## Provider Support

### Anthropic (Claude)

```python
council = Council(
    api_key="your-anthropic-key",
    provider="anthropic"
)
```

### OpenAI (GPT-4)

```python
council = Council(
    api_key="your-openai-key",
    provider="openai",
    model="gpt-4-turbo-preview",  # or "gpt-4", "gpt-3.5-turbo", etc.
    base_url="https://api.openai.com/v1"
)
```

### Google Gemini

```python
council = Council(
    api_key="your-gemini-key",
    provider="gemini"
)
```

### Custom HTTP Endpoint

```python
from council_ai.providers import HTTPProvider, register_provider

# Register a custom provider
register_provider("my_llm", HTTPProvider)

# Use it
council = Council(
    api_key="your-key",
    provider="http",
    base_url="http://localhost:8000/v1/completions"
)
```

You can also set the endpoint via `LLM_ENDPOINT` and pass an optional API key via
`HTTP_API_KEY` or `COUNCIL_API_KEY`.

You can set provider defaults via the config file (model, base URL) and override them
per council instance when needed.

---

## Web App (Standalone)

The web app is the primary user-testing surface. It features a modern, Dieter Rams-inspired UI built with **React 18** and **TypeScript**. The frontend architecture was migrated from vanilla JavaScript to a fully modular component-based system with 25+ React components, Context API for state management, and optimized build output.

### 1-Click Launchers

For the easiest experience, we provide specialized 1-click launchers in the project root. **Double-click** any of these to start:

- 🚀 **`launch-council-web.command` (Mac)** / **`launch-council.bat` (Windows)**: Standard 1-click launch. Handles setup and opens in your browser. **Requires Node.js for web interface.**
- 💻 **`launch-council-cli.bat` (Windows)**: **CLI Mode** - No Node.js required! Perfect if you just want to use the command-line interface (`council consult`, `council interactive`, etc.)
- 🌐 **`launch-council-lan.command` (Mac)** / **`launch-council-lan.bat` (Windows)**: **Network Access Mode**. Use this if you want to access the UI from another PC, phone, or tablet on your network. It displays a local IP (e.g., `http://192.168.1.15:8000`) for remote access.
- 🔄 **`launch-council-persistent.command` (Mac)** / **`launch-council-persistent.bat` (Windows)**: **"Always Up" Mode**. Optimizes for personal use by automatically restarting the server if it crashes or encounters a network error.

> [!TIP]
> **Don't have Node.js installed?** Use `launch-council-cli.bat` for CLI mode, or run `install-nodejs.bat` to get installation help.

### 💻 Satellite Access (From Other Devices)

If you are hosting Council AI on one machine (e.g., your Mac) and want to access it from another (e.g., a PC), use these "Connect" shortcuts to jump straight to the UI:

- **Windows PC**: Double-click **`connect-to-council.bat`**. (The first time you run it, it will ask for the Mac's IP/Hostname).
- **Other Devices**: Simply open the browser to `http://[HOST_IP]:8000`.

> [!TIP]
> To find your host's IP, run **`launch-council-lan.command`** on the host machine. It will display the correct network URL in the terminal.

**Command Line equivalents:**

```bash
# Standard
./launch-council.py --open

# Network Access (LAN)
./launch-council.py --network

# Persistent (Auto-restart)
./launch-council.py --retry
```

### Manual Launch

If you prefer to run manually or different parts separately:

```bash
# 1. Install Python dependencies
pip install -e ".[web]"

# 2. Build the React frontend (requires Node.js & npm)
npm install
npm run build

# 3. Run the web server
council web --reload
```

Then open <http://127.0.0.1:8000>.

### Development Mode

For frontend development with hot-reloading:

1. Start the backend API:

   ```bash
   council web --reload
   ```

2. In a separate terminal, start the React dev server:

   ```bash
   npm run dev
   ```

   Access the app at <http://localhost:5173>.

### Text-to-Speech (TTS) Integration 🔊

The web UI supports voice/audio responses powered by ElevenLabs (primary) and OpenAI TTS (fallback).

**Setup:**

1. **Add API Keys** - Add to your `.env` file:

```bash
ELEVENLABS_API_KEY=your-elevenlabs-key-here
OPENAI_API_KEY=your-openai-key-here  # Fallback
```

1. **Enable TTS** - In the web UI, go to Advanced Settings and toggle "Enable voice responses"

2. **Select Voice** (Optional) - Choose from available voices in the dropdown

**Configuration:**

Create or edit `~/.config/council-ai/config.yaml`:

```yaml
tts:
  enabled: false # Set to true to enable by default
  provider: 'elevenlabs' # Primary provider
  voice: 'EXAVITQu4vr4xnSDxMaL' # Optional: specific voice ID
  fallback_provider: 'openai' # Fallback provider
  fallback_voice: 'alloy' # Optional: fallback voice
```

See `config.yaml.example` for full configuration options.

**Features:**

- 🎙️ **High-Quality Voices** - ElevenLabs provides natural, human-like voices
- 🔄 **Automatic Fallback** - Falls back to OpenAI TTS if ElevenLabs fails
- 🎚️ **Voice Selection** - Choose from multiple voices per provider
- 🔇 **Optional** - TTS is disabled by default, enable per-session or globally
- 📱 **Browser-Native** - Uses HTML5 audio player for compatibility

**Supported Providers:**

| Provider       | Quality    | Speed     | Voices | Cost |
| :------------- | :--------- | :-------- | :----- | :--- |
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | Fast      | 50+    | $$   |
| **OpenAI TTS** | ⭐⭐⭐⭐   | Very Fast | 6      | $    |

### Web App Features

- **Auto-Save Settings**: Provider, domain, mode, model, and base URL are automatically saved to browser localStorage
- **Clear Persistence Indicators**: Each field shows whether it's saved to browser or session-only
- **Manual Save/Reset**: Use the "💾 Save Settings" and "🔄 Reset to Defaults" buttons in Advanced Settings
- **Security**: API keys are never stored - only used for the current session
- **History**: Recent consultations are automatically saved and displayed

**Settings Persistence:**

- ✅ Saved to browser: Provider, Model, Base URL, Domain, Mode
- ❌ Session only: Custom Members, API Key

---

## Quality & Testing Policy

See [CONTRIBUTING.md](CONTRIBUTING.md) for the testing, linting, and formatting policy.

---

## Python API Reference

**📖 [Complete API Documentation](documentation/API_REFERENCE.md)**

For comprehensive API documentation including all classes, methods, parameters, and examples, see the [API Reference Guide](documentation/API_REFERENCE.md).

### Quick Reference

Below is a quick reference for common API usage. For detailed documentation, see the [full API reference](documentation/API_REFERENCE.md).

### Council

```python
from council_ai import Council

# Create
council = Council(api_key="key", provider="anthropic")
council = Council.for_domain("business", api_key="key")

# Members
council.add_member("DR")
council.add_member(custom_persona)
council.remove_member("DR")
council.set_member_weight("AG", 1.5)
council.enable_member("PH")
council.disable_member("PH")
council.list_members()
council.clear_members()

# Consult
result = council.consult("query")
result = council.consult("query", context="additional context")
result = council.consult("query", mode=ConsultationMode.DEBATE)
result = council.consult("query", members=["DR", "AG"])

# Async
result = await council.consult_async("query")
```

### ConsultationResult

```python
result = council.consult("query")

# Access
result.query          # Original query
result.synthesis      # Synthesized response
result.responses      # List of MemberResponse
result.mode           # Consultation mode used
result.timestamp      # When consulted

# Export
result.to_markdown()  # Markdown format
result.to_dict()      # Dictionary format

# Individual responses
for response in result.responses:
    response.persona      # Persona object
    response.content      # Response text
    response.error        # Error if any
```

### Persona

```python
from council_ai import get_persona, list_personas
from council_ai.core.persona import Persona, PersonaManager

# Get built-in
persona = get_persona("DR")
all_personas = list_personas()

# Create
persona = Persona(
    id="custom",
    name="Custom",
    title="Title",
    core_question="Question?",
    razor="Principle.",
)

# Modify
persona.add_trait("name", "description", weight=1.2)
persona.remove_trait("name")
persona.update_trait("name", weight=1.5)

# Export
persona.to_yaml()
persona.save_to_yaml("path.yaml")

# Clone with modifications
new_persona = persona.clone(new_id="custom_v2", weight=1.5)
```

---

## Examples

### Code Review

```python
council = Council.for_domain("coding", api_key=key)
result = council.consult("""
Review this API design:

POST /users
- Creates a new user
- Accepts: {email, password, name}
- Returns: {id, email, name, created_at}

What issues do you see?
""")
```

### Business Strategy

```python
council = Council.for_domain("business", api_key=key)
result = council.consult("""
We're a B2B SaaS company with $2M ARR.
A competitor just raised $50M.
Should we:
A) Raise funding to compete
B) Focus on profitability and niche down
C) Seek acquisition

What do you advise?
""")
```

### Career Decision

```python
council = Council.for_domain("career", api_key=key)
result = council.consult("""
I'm a senior engineer at a stable company.
I've been offered a CTO role at an early-stage startup.

Pros:
- 3x equity, 20% salary cut
- Full technical ownership
- High growth potential

Cons:
- Startup has 18 months runway
- Would leave a team I built
- More stress, less stability

How should I think about this?
""")
```

### Creative Project

```python
council = Council.for_domain("creative", api_key=key)
council.add_member("JT")  # Add sonic lens

result = council.consult("""
I'm designing a podcast intro.
It needs to:
- Grab attention in 5 seconds
- Convey "thoughtful tech commentary"
- Be memorable but not annoying

What elements should I include?
""")
```

### Repository Review

```python
# Review your repository's code, design, and functionality
# See examples/review_repository.py for full implementation
council = Council(api_key=key)

# Code quality review
council.add_member("DR")      # Design & Simplicity
council.add_member("PH")    # Security
council.add_member("DK")  # Cognitive Load

result = council.consult("Review code quality and architecture...")

# Also review design/UX and functionality/robustness
# with different persona combinations
```

### LLM Response Reviewer

Council AI includes a specialized "Supreme Court-style" reviewer for evaluating multiple LLM responses. See the [LLM Response Reviewer Setup Guide](documentation/REVIEWER_SETUP.md) for details.

---

## Contributing

Contributions welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

```bash
# Development setup
git clone https://github.com/doronpers/council-ai
cd council-ai

# Upgrade pip (recommended)
pip install --upgrade pip

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=council_ai

# Format code
black src/
ruff check src/

# Try the quickstart demo (no API key needed)
python examples/quickstart.py
```

### Adding New Personas

Create a YAML file in `src/council_ai/personas/`:

```yaml
id: your_persona
name: Full Name
title: Brief Title
emoji: '🎭'
category: advisory

core_question: 'The key question?'
razor: 'The decision principle.'

traits:
  - name: Trait Name
    description: What it means
    weight: 1.5

focus_areas:
  - Area 1
  - Area 2
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on adding domains, providers, and more.

---

## License

MIT License - see LICENSE file.

---

## 📋 Roadmap & TODOs

For a complete list of planned features, improvements, and TODOs, see [ROADMAP.md](./ROADMAP.md).

---

## Credits

Inspired by the decision-making frameworks of:

- **Dieter Rams** - Industrial design principles
- **Martin Dempsey** - Mission command leadership
- **Daniel Kahneman** - Behavioral economics
- **Julian Treasure** - Sound and communication
- **Pablos Holman** - Hacker mindset
- **Nassim Nicholas Taleb** - Antifragility and risk
- **Andy Grove** - Strategic management

---

Built with ❤️ for better decisions.
