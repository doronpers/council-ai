# LLM Response Reviewer - Setup Guide

A Supreme Court-style review system for evaluating multiple LLM responses with scoring, consensus, and synthesis.

---

## Quick Start

### Prerequisites

1. **Install Council AI**
   ```bash
   # Clone the repository
   git clone https://github.com/doronpers/council-ai.git
   cd council-ai

   # Install with dependencies
   pip install -e ".[all]"
   ```

2. **Configure API Keys**

   Council AI requires at least one LLM provider API key. See the main [README.md](../README.md) for detailed configuration options.

   **Quick setup:**
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env and add your API key(s)
   # Choose one or more providers:
   ANTHROPIC_API_KEY=your-key-here
   OPENAI_API_KEY=your-key-here
   GEMINI_API_KEY=your-key-here
   ```

   See [.env.example](../.env.example) for all configuration options including Vercel AI Gateway and TTS providers.

### Launch the Reviewer

**Option 1: Using the dedicated launcher script (Recommended)**
```bash
python launch-reviewer.py
```
Opens automatically at `http://localhost:8765/reviewer`

**Option 2: Using Council CLI**
```bash
council web
```
Then navigate to `http://localhost:8000/reviewer` in your browser.

### Launch Options

```bash
# Custom port
python launch-reviewer.py --port 9000

# Don't auto-open browser
python launch-reviewer.py --no-browser

# Development mode with auto-reload
python launch-reviewer.py --reload

# Custom host
python launch-reviewer.py --host 0.0.0.0 --port 8765
```

## Features

### Review Council System

The reviewer uses a Supreme Court-style council of "justices" to evaluate multiple LLM responses. Each justice brings a unique perspective to assess the quality, accuracy, and value of responses.

**Default 7-Justice Council:**
- 🎖️ **Martin Dempsey (Chair)** - Mission clarity and decisive leadership
- 🧠 **Daniel Kahneman (Vice-Chair)** - Cognitive biases, System 1/2 thinking
- 🎨 **Dieter Rams** - Clarity and simplicity in design
- 🔊 **Julian Treasure** - Communication effectiveness
- 🔓 **Pablos Holman** - Security and hacking perspective
- 🦢 **Nassim Taleb** - Hidden risks and antifragility
- 🎯 **Andy Grove** - Strategic thinking and competition

**Sonotheia Mode (9 Justices):**

Enable this mode for specialized topics related to:
- Deepfake audio detection
- Voice authenticity analysis
- Regulated financial institutions
- Signal processing and forensics

Adds two specialist justices:
- 🔬 **Dr. Elena Vance** - Signal analysis and audio forensics
- 📋 **Marcus Chen** - Regulatory compliance and auditing

### Evaluation Process

Each justice evaluates responses across multiple dimensions:

1. **Accuracy (1-10)** - Correctness of information
2. **Factual Consistency (1-10)** - Alignment with established facts
3. **Unique Insights (1-10)** - Valuable unique perspectives offered
4. **Error Detection (1-10)** - Identification of errors or hallucinations
5. **Sonotheia Relevance (1-10)** - Relevance to voice/audio security (when applicable)

### Review Output

The reviewer provides:
- **Individual Justice Assessments** - Detailed opinions and scores from each justice
- **Group Decision** - Majority opinion identifying the best response
- **Dissenting Opinions** - Alternative views (if any)
- **Synthesized Response** - Combined best elements from all responses
- **Refined Final Output** - Polished synthesis incorporating all perspectives

---

## Troubleshooting

### Common Issues

**"API key required" Error**
- Ensure `.env` file exists in the project root with valid API keys
- Alternatively, enter an API key directly in the web UI's Advanced Settings panel
- Verify your API key is active and has sufficient credits/quota

**Connection Refused**
- Check if another service is using the default port (8765)
- Try a different port: `python launch-reviewer.py --port 9000`
- Verify firewall settings aren't blocking the connection

**Slow Responses**
- The reviewer consults multiple AI "justices" sequentially, which takes time
- Each review makes 7-9 separate LLM API calls
- Response time depends on your LLM provider's API speed
- Consider using faster models or fewer justices for quicker reviews

**Module Not Found Errors**
```bash
# Reinstall council-ai with dependencies
pip install -e ".[all]"
```

**Missing Dependencies**
```bash
# Install with web dependencies
pip install -e ".[web]"
```

---

## API Integration

The reviewer exposes REST API endpoints for programmatic access:

### Available Endpoints

```
GET  /api/reviewer/info           # Get available justices and configuration
POST /api/reviewer/review         # Submit review request (blocking)
POST /api/reviewer/review/stream  # Stream review progress (Server-Sent Events)
```

### Example Usage

**Python:**
```python
import requests

response = requests.post("http://localhost:8765/api/reviewer/review", json={
    "question": "What is the capital of France?",
    "responses": [
        {"id": 1, "content": "Paris is the capital of France.", "source": "GPT-4"},
        {"id": 2, "content": "The capital is Paris.", "source": "Claude"}
    ],
    "justices": ["dempsey", "kahneman", "rams"],
    "chair": "dempsey",
    "vice_chair": "kahneman",
    "api_key": "your-api-key"  # Optional if set in .env
})

result = response.json()
print(f"Winner: Response #{result['group_decision']['winner']}")
print(f"Score: {result['group_decision']['winner_score']:.2f}")
print(f"Reasoning: {result['group_decision']['majority_opinion']}")
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8765/api/reviewer/review', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "What is the capital of France?",
    responses: [
      { id: 1, content: "Paris is the capital of France.", source: "GPT-4" },
      { id: 2, content: "The capital is Paris.", source: "Claude" }
    ],
    justices: ["dempsey", "kahneman", "rams"]
  })
});

const result = await response.json();
console.log(`Winner: Response #${result.group_decision.winner}`);
```

**cURL:**
```bash
curl -X POST http://localhost:8765/api/reviewer/review \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the capital of France?",
    "responses": [
      {"id": 1, "content": "Paris is the capital.", "source": "GPT-4"}
    ]
  }'
```

### Streaming Reviews

For real-time progress updates, use the streaming endpoint:

```python
import requests

response = requests.post(
    "http://localhost:8765/api/reviewer/review/stream",
    json={...},  # Same payload as above
    stream=True
)

for line in response.iter_lines():
    if line:
        # Parse Server-Sent Events
        if line.startswith(b'data: '):
            data = json.loads(line[6:])
            print(f"Progress: {data}")
```

---

## Related Documentation

- **[Main README](../README.md)** - Complete Council AI documentation
- **[API Configuration](../.env.example)** - All API key options
- **[Contributing](../CONTRIBUTING.md)** - Development guidelines
- **[Agent Knowledge Base](../AGENT_KNOWLEDGE_BASE.md)** - System architecture and patterns

---

## Support

For issues, questions, or feature requests:
- **Issues**: [GitHub Issues](https://github.com/doronpers/council-ai/issues)
- **Documentation**: Review the main [README.md](../README.md) for comprehensive guides
- **Examples**: Check the [examples/](../examples/) directory for more use cases
