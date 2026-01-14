# LLM Response Reviewer - Setup Guide

A Supreme Court-style review system for evaluating multiple LLM responses with scoring, consensus, and synthesis.

## Quick Start

```bash
# 1. Navigate to the council-ai directory
cd council-ai

# 2. Copy and configure your API keys
cp .env.example .env
# Edit .env and add your API keys (see below)

# 3. Launch the reviewer
python launch-reviewer.py
```

The reviewer will open automatically at `http://localhost:8765/reviewer`

## API Key Configuration

### Option 1: Vercel AI Gateway (Recommended)

Vercel AI Gateway provides unified access to multiple AI models through a single API endpoint.

#### Setup Steps:

1. **Create a Vercel Account** (if you don't have one)
   - Go to [vercel.com](https://vercel.com) and sign up

2. **Enable AI Gateway**
   - Navigate to your Vercel Dashboard
   - Go to Settings > AI Gateway
   - Enable the AI Gateway feature

3. **Get Your API Key**
   - In AI Gateway settings, generate a new API key
   - Copy the key (starts with `vcel_`)

4. **Configure in .env**
   ```bash
   AI_GATEWAY_API_KEY=vcel_your_key_here
   ```

5. **Configure Models** (in Vercel Dashboard)
   - Add your provider API keys (Anthropic, OpenAI, etc.) to Vercel
   - Vercel will route requests to the appropriate provider

#### Benefits:
- Single API key for multiple providers
- Automatic fallback between providers
- Usage tracking and rate limiting
- No need to manage multiple API keys locally

### Option 2: Direct Provider Keys

Add individual API keys for each provider you want to use:

```bash
# Anthropic Claude (Best for nuanced analysis)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI GPT
OPENAI_API_KEY=sk-...

# Google Gemini
GEMINI_API_KEY=AI...

# Perplexity (For research queries)
PERPLEXITY_API_KEY=pplx-...
```

### Option 3: Mixed Configuration

Use Vercel AI Gateway as default with direct keys as fallback:

```bash
# Primary: Vercel AI Gateway
AI_GATEWAY_API_KEY=vcel_...

# Fallback: Direct provider keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## Voice Synthesis (Optional)

For text-to-speech of responses:

```bash
# ElevenLabs (High quality voices)
ELEVENLABS_API_KEY=...

# OpenAI TTS (Good quality, uses OPENAI_API_KEY)
# No separate key needed if OPENAI_API_KEY is set
```

## Launching Options

### Default Launch
```bash
python launch-reviewer.py
```

### Custom Port
```bash
python launch-reviewer.py --port 9000
```

### No Auto-Browser
```bash
python launch-reviewer.py --no-browser
```

### Development Mode (Auto-reload)
```bash
python launch-reviewer.py --reload
```

### Using Council CLI
```bash
# If council-ai is installed
council review-ui
```

## Features

### 7-Justice Default Council
- **Martin Dempsey (Chair)** - Mission clarity, decisive leadership
- **Daniel Kahneman (Vice-Chair)** - Cognitive biases, System 1/2 thinking
- **Dieter Rams** - Clarity, simplicity
- **Julian Treasure** - Communication effectiveness
- **Pablos Holman** - Security/hacking perspective
- **Nassim Taleb** - Hidden risks, antifragility
- **Andy Grove** - Strategic thinking

### Sonotheia Mode (9 Justices)
Enable for topics related to:
- Deepfake audio detection
- Voice authenticity analysis
- Regulated financial institutions
- Signal processing and forensics

Adds two specialist justices:
- **Dr. Elena Vance (Signal Analyst)** - Audio forensics expert
- **Marcus Chen (Compliance Auditor)** - Regulatory compliance expert

### Evaluation Criteria
1. **Accuracy (1-10)** - Is the information correct?
2. **Factual Consistency (1-10)** - Alignment with established facts
3. **Unique Insights (1-10)** - Valuable unique perspectives
4. **Error Detection (1-10)** - Errors or hallucinations (higher = fewer)
5. **Sonotheia Relevance (1-10)** - Relevance to voice/audio security

### Output Includes
- Individual justice assessments with scores
- Group decision with majority opinion
- Dissenting opinions (if any)
- Combined best elements from all responses
- Refined final synthesis

## Troubleshooting

### "API key required" Error
- Ensure `.env` file exists with valid API keys
- Or enter an API key directly in the Advanced Settings panel

### Connection Refused
- Check if another service is using port 8765
- Try a different port: `python launch-reviewer.py --port 9000`

### Slow Responses
- The council consults multiple AI "justices" which takes time
- Each review makes multiple LLM calls
- Consider using fewer justices for faster reviews

### Module Not Found
```bash
# Install council-ai
pip install -e .
# or
pip install council-ai
```

## API Endpoints

The reviewer exposes REST endpoints for programmatic access:

```
GET  /api/reviewer/info           # Get available justices and config
POST /api/reviewer/review         # Submit review request
POST /api/reviewer/review/stream  # Stream review progress (SSE)
```

### Example API Request
```python
import requests

response = requests.post("http://localhost:8765/api/reviewer/review", json={
    "question": "What is the capital of France?",
    "responses": [
        {"id": 1, "content": "Paris is the capital.", "source": "GPT-4"},
        {"id": 2, "content": "The capital is Paris, France.", "source": "Claude"}
    ],
    "justices": ["dempsey", "kahneman", "rams"],
    "chair": "dempsey",
    "vice_chair": "kahneman"
})

result = response.json()
print(f"Winner: Response #{result['group_decision']['winner']}")
print(f"Score: {result['group_decision']['winner_score']}")
```

## Support

- Documentation: See `/docs` folder
- Issues: https://github.com/your-repo/council-ai/issues
