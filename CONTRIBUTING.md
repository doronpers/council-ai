# Contributing to Council AI

Thank you for your interest in contributing to Council AI! This document provides guidelines and instructions for contributing.

## Getting Started

### Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/doronpers/council-ai.git
cd council-ai
```

2. **Upgrade pip (recommended)**

```bash
pip install --upgrade pip
```

3. **Install in development mode**

```bash
pip install -e ".[dev]"
```

4. **Run tests**

```bash
```bash
pytest
```

> [!NOTE]
> On Windows, if tools like `black`, `ruff`, or `pytest` are not in your PATH, you can run them via the python module syntax:
>
> ```bash
> python -m black src/
> python -m ruff check src/
> python -m pytest
> ```

## Project Structure

```text
council-ai/
├── src/council_ai/          # Main package
│   ├── core/                # Core functionality
│   ├── domains/             # Domain configurations
│   ├── personas/            # Persona YAML files
│   └── providers/           # LLM provider implementations
├── tests/                   # Test suite
├── examples/                # Example scripts
└── pyproject.toml           # Package configuration
```

## How to Contribute

### 1. Adding a New Persona

Create a YAML file in `src/council_ai/personas/`:

```yaml
id: your_persona
name: Full Name
title: Brief Title
emoji: "🎭"
category: advisory  # or adversarial, creative, analytical, strategic, operational

core_question: "The fundamental question this persona asks?"
razor: "Their decision-making principle."

traits:
  - name: Trait Name
    description: What this trait means
    weight: 1.5  # 0.0-2.0, affects influence

focus_areas:
  - Area 1
  - Area 2
  - Area 3
```

### 2. Adding a New Domain

Edit `src/council_ai/domains/__init__.py` and add to the `DOMAINS` dictionary:

```python
"your_domain": Domain(
    id="your_domain",
    name="Display Name",
    description="What this domain is for",
    category=DomainCategory.BUSINESS,  # or TECHNICAL, CREATIVE, PERSONAL, GENERAL
    default_personas=["persona1", "persona2", "persona3"],
    example_queries=[
        "Example question 1",
        "Example question 2",
    ],
),
```

### 3. Adding a New LLM Provider

Create a class in `src/council_ai/providers/__init__.py`:

```python
class YourProvider(LLMProvider):
    """Your LLM provider."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.environ.get("YOUR_API_KEY"))
        if not self.api_key:
            raise ValueError("API key required")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        # Your implementation
        pass

# Register it
_PROVIDERS["your_provider"] = YourProvider
```

### 4. Writing Tests

Add tests to `tests/test_core.py` or create new test files:

```python
def test_your_feature():
    """Test description."""
    # Arrange
    council = Council(api_key="test-key")

    # Act
    result = council.some_method()

    # Assert
    assert result == expected_value
```

Run tests:

```bash
pytest -v
pytest tests/test_core.py::test_your_feature
```

## Code Style

We use:

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **Type hints** for better code clarity

Format your code:

```bash
black src/
ruff check src/
```

## Pull Request Process

1. **Fork the repository** and create a feature branch

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style

3. **Add tests** for new functionality

4. **Run tests** to ensure everything passes

   ```bash
   pytest
   ```

5. **Update documentation** if needed
   - README.md for user-facing changes
   - Docstrings for code changes

6. **Commit your changes**

   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

7. **Push and create a Pull Request**

   ```bash
   git push origin feature/your-feature-name
   ```

## Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: new feature or file`
- `Fix: bug fix`
- `Update: modify existing feature`
- `Refactor: code restructuring`
- `Docs: documentation changes`
- `Test: add or modify tests`

## Questions or Issues?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
