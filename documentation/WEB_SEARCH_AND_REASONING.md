# Web Search and Reasoning Modes Guide

This guide explains how to enable web search and deeper reasoning modes in Council AI consultations.

## Table of Contents

1. [Web Search](#web-search)
2. [Reasoning Modes](#reasoning-modes)
3. [Configuration](#configuration)
4. [Examples](#examples)

---

## Web Search

Council AI can automatically search the web for current information during consultations. This is useful when you need up-to-date facts, news, research, or information that may not be in the LLM's training data.

### Supported Providers

1. **Tavily** (Recommended) - Fast, AI-powered search
   - Sign up at https://tavily.com
   - Set `TAVILY_API_KEY` environment variable

2. **Serper.dev** - Google search API
   - Sign up at https://serper.dev
   - Set `SERPER_API_KEY` environment variable

3. **Google Custom Search** - Official Google API
   - Requires Google API key and Custom Search Engine ID
   - Set `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` environment variables

### Enabling Web Search

#### Council-Level (All Members)

```python
from council_ai import Council, CouncilConfig

# Enable web search for all consultations
config = CouncilConfig(
    enable_web_search=True,
    web_search_provider="tavily"  # Optional: auto-detects from env vars
)

council = Council(
    api_key="your-key",
    provider="anthropic",
    config=config
)
council.add_member("rams")

result = council.consult(
    "What are the latest trends in API design in 2024?",
    # Web search will automatically be used
)
```

#### Persona-Level (Specific Members)

```python
from council_ai import Council
from council_ai.core.persona import get_persona

council = Council(api_key="your-key", provider="anthropic")

# Enable web search for a specific persona
persona = get_persona("rams").clone(
    new_id="rams_with_search",
    enable_web_search=True
)
council.add_member(persona)

result = council.consult(
    "What are current best practices for REST API design?",
    # Only rams will use web search
)
```

### How It Works

1. When a consultation is made, Council AI checks if web search is enabled
2. If enabled, it performs a web search using the query
3. Search results are automatically added to the context
4. LLMs receive both your original context and web search results
5. Responses incorporate information from web search

### Example Output

```
Web Search Results for: What are the latest trends in API design in 2024?

1. API Design Trends 2024
   URL: https://example.com/api-trends
   GraphQL adoption is increasing, REST remains dominant...

2. Modern API Design Patterns
   URL: https://example.com/patterns
   OpenAPI 3.1, async-first designs, and event-driven architectures...
```

---

## Reasoning Modes

Reasoning modes enable deeper thinking and more structured analysis. Different modes use different cognitive strategies.

### Available Modes

1. **Standard** (default) - Normal reasoning, no special instructions

2. **Chain-of-Thought** - Step-by-step reasoning
   - Breaks down problems into clear steps
   - Shows explicit reasoning process
   - Best for: Complex problems requiring logical progression

3. **Tree-of-Thought** - Multiple reasoning paths
   - Explores 2-3 different approaches
   - Compares and contrasts paths
   - Best for: Problems with multiple valid solutions

4. **Reflective** - Think, reflect, refine
   - Initial analysis → Reflection → Refinement → Final synthesis
   - Best for: Important decisions requiring careful consideration

5. **Analytical** - Deep analysis with evidence
   - Thesis → Evidence → Counterarguments → Conclusions
   - Best for: Research, analysis, evidence-based decisions

6. **Creative** - Divergent thinking
   - Multiple perspectives → Connections → Novel insights
   - Best for: Innovation, brainstorming, creative solutions

### Enabling Reasoning Modes

#### Council-Level

```python
from council_ai import Council, CouncilConfig

config = CouncilConfig(
    reasoning_mode="chain_of_thought"  # All members use this mode
)

council = Council(
    api_key="your-key",
    provider="anthropic",
    config=config
)
council.add_member("rams")
council.add_member("kahneman")

result = council.consult(
    "Should we migrate from REST to GraphQL?",
    # All members will use chain-of-thought reasoning
)
```

#### Persona-Level

```python
from council_ai import Council
from council_ai.core.persona import get_persona

council = Council(api_key="your-key", provider="anthropic")

# Different reasoning modes for different personas
rams = get_persona("rams").clone(
    new_id="rams_analytical",
    reasoning_mode="analytical"
)

kahneman = get_persona("kahneman").clone(
    new_id="kahneman_reflective",
    reasoning_mode="reflective"
)

council.add_member(rams)
council.add_member(kahneman)

result = council.consult(
    "Review our API design for cognitive load",
    # rams uses analytical, kahneman uses reflective
)
```

### Reasoning Mode Examples

#### Chain-of-Thought Output

```
Step 1: Identify the key question
The question is whether to migrate from REST to GraphQL.

Step 2: Analyze REST advantages
- Simple, well-understood
- Caching is straightforward
- Wide tooling support

Step 3: Analyze GraphQL advantages
- Single endpoint reduces complexity
- Client specifies exact data needs
- Strong typing with schema

Step 4: Consider migration costs
- Team learning curve
- Infrastructure changes
- Client updates required

Step 5: Synthesize conclusion
Based on the analysis, I recommend...
```

#### Tree-of-Thought Output

```
Approach 1: Technical Perspective
- Performance considerations
- Scalability implications
- Developer experience

Approach 2: Business Perspective
- Time to market
- Resource requirements
- Risk assessment

Approach 3: User Experience Perspective
- API usability
- Client integration complexity
- Long-term maintainability

Synthesis: Comparing all three approaches, the optimal solution...
```

---

## Configuration

### Environment Variables

```bash
# Web Search (choose one)
export TAVILY_API_KEY="your-tavily-key"
# OR
export SERPER_API_KEY="your-serper-key"
# OR
export GOOGLE_API_KEY="your-google-key"
export GOOGLE_CSE_ID="your-search-engine-id"

# LLM Provider
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Programmatic Configuration

```python
from council_ai import Council, CouncilConfig
from council_ai.core.persona import get_persona

# Council-level configuration
config = CouncilConfig(
    enable_web_search=True,
    web_search_provider="tavily",  # Optional
    reasoning_mode="chain_of_thought"
)

council = Council(
    api_key="your-key",
    provider="anthropic",
    config=config
)

# Persona-level overrides
persona = get_persona("rams").clone(
    enable_web_search=True,  # Override council setting
    reasoning_mode="analytical"  # Override council setting
)
council.add_member(persona)
```

---

## Examples

### Example 1: Web Search for Current Information

```python
from council_ai import Council, CouncilConfig

config = CouncilConfig(enable_web_search=True)
council = Council(api_key="your-key", provider="anthropic", config=config)
council.add_member("rams")
council.add_member("kahneman")

result = council.consult(
    "What are the latest security best practices for REST APIs in 2024?",
    # Automatically searches web for current information
)

print(result.synthesis)
```

### Example 2: Chain-of-Thought Reasoning

```python
from council_ai import Council, CouncilConfig

config = CouncilConfig(reasoning_mode="chain_of_thought")
council = Council(api_key="your-key", provider="anthropic", config=config)
council.add_member("rams")

result = council.consult(
    "Should we implement rate limiting at the API gateway or application level?",
    # Uses step-by-step reasoning
)

for response in result.responses:
    print(f"{response.persona.name}:")
    print(response.content)
    print()
```

### Example 3: Combined Web Search + Reasoning

```python
from council_ai import Council, CouncilConfig
from council_ai.core.persona import get_persona

config = CouncilConfig(
    enable_web_search=True,
    reasoning_mode="analytical"
)

council = Council(api_key="your-key", provider="anthropic", config=config)

# Different personas with different capabilities
rams = get_persona("rams").clone(
    reasoning_mode="analytical",
    enable_web_search=True
)

kahneman = get_persona("kahneman").clone(
    reasoning_mode="reflective",
    enable_web_search=False  # This persona doesn't need web search
)

council.add_member(rams)
council.add_member(kahneman)

result = council.consult(
    "What are the current best practices for API rate limiting, "
    "and how should we implement it considering cognitive load?",
    # rams: web search + analytical reasoning
    # kahneman: reflective reasoning only
)
```

### Example 4: Persona-Specific Configuration

```python
from council_ai import Council
from council_ai.core.persona import get_persona

council = Council(api_key="your-key", provider="anthropic")

# Research-focused persona with web search
researcher = get_persona("rams").clone(
    new_id="researcher",
    enable_web_search=True,
    reasoning_mode="analytical",
    prompt_prefix="You are a research-focused advisor. Always verify facts with current sources."
)

# Strategic persona with reflective reasoning
strategist = get_persona("kahneman").clone(
    new_id="strategist",
    enable_web_search=False,
    reasoning_mode="reflective",
    prompt_prefix="You are a strategic advisor. Think deeply before responding."
)

council.add_member(researcher)
council.add_member(strategist)

result = council.consult(
    "Should we adopt microservices architecture?",
    # researcher: web search + analytical
    # strategist: reflective only
)
```

---

## Best Practices

### When to Use Web Search

✅ **Use web search when:**
- You need current information (news, trends, recent research)
- Facts may have changed since model training
- You want to verify information
- You need specific technical documentation

❌ **Don't use web search when:**
- Question is about general principles or philosophy
- You already have all necessary context
- You want faster responses (web search adds latency)
- Question is about your specific codebase/context

### When to Use Reasoning Modes

✅ **Chain-of-Thought:**
- Complex technical decisions
- Problems with clear logical steps
- When you want to see the reasoning process

✅ **Tree-of-Thought:**
- Problems with multiple valid solutions
- When you want to explore alternatives
- Design decisions with trade-offs

✅ **Reflective:**
- Important strategic decisions
- When you want careful consideration
- High-stakes choices

✅ **Analytical:**
- Research questions
- Evidence-based decisions
- When you need thorough analysis

✅ **Creative:**
- Brainstorming sessions
- Innovation challenges
- When you need novel perspectives

### Performance Considerations

- **Web Search:** Adds ~1-3 seconds per consultation
- **Reasoning Modes:** May increase token usage by 20-50%
- **Combined:** Can significantly increase response time and cost

### Cost Optimization

- Only enable web search for personas that need it
- Use reasoning modes selectively (not for simple questions)
- Consider using reasoning modes only for synthesis phase

---

## Troubleshooting

### Web Search Not Working

1. **Check API keys:**
   ```bash
   echo $TAVILY_API_KEY  # or SERPER_API_KEY, GOOGLE_API_KEY
   ```

2. **Verify provider:**
   ```python
   from council_ai.tools.web_search import WebSearchTool
   tool = WebSearchTool()
   # Should not raise ValueError
   ```

3. **Check logs:**
   - Web search failures are logged as warnings
   - Consultations continue even if web search fails

### Reasoning Mode Not Applied

1. **Check configuration:**
   ```python
   print(council.config.reasoning_mode)
   print(persona.reasoning_mode)
   ```

2. **Verify mode name:**
   - Must be one of: `chain_of_thought`, `tree_of_thought`, `reflective`, `analytical`, `creative`
   - Case-insensitive, but use underscores

---

## Summary

- **Web Search:** Enable with `enable_web_search=True` (council or persona level)
- **Reasoning Modes:** Set `reasoning_mode` to desired mode (council or persona level)
- **Combined:** Use both for comprehensive, well-researched, deeply-reasoned responses
- **Selective:** Enable per-persona for different capabilities per council member

For more examples, see `examples/web_search_reasoning_example.py`.
