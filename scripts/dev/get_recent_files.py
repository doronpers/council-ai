#!/usr/bin/env python3
import datetime
import os
from pathlib import Path

# Get the list of files from the glob output
files = [
    ".pre-commit-config.yaml",
    ".secrets.baseline",
    "src/council_ai/cli.py",
    "test_improvements.py",
    "src/council_ai/tools/web_search.py",
    "src/council_ai/domains/__init__.py",
    "src/council_ai/core/persona.py",
    "examples/web_search_reasoning_example.py",
    "src/council_ai/core/history.py",
    "src/council_ai/__init__.py",
    "src/council_ai/core/council.py",
    "src/council_ai/utils/__init__.py",
    "src/council_ai/utils/context.py",
    "src/council_ai/tools/reviewer.py",
    "src/council_ai/tools/__init__.py",
    "src/council_ai/core/diagnostics.py",
    "examples/context_injection_example.py",
    "documentation/CONTEXT_INJECTION_GUIDE.md",
    "AGENT_KNOWLEDGE_BASE.md",
    ".cursorrules",
    "src/council_ai/core/__init__.py",
    "documentation/QUICK_REFERENCE.md",
    "documentation/WEB_SEARCH_AND_REASONING.md",
    "src/council_ai/core/reasoning.py",
    "src/council_ai/webapp/reviewer.py",
    "src/council_ai/providers/__init__.py",
    "src/council_ai/core/config.py",
    ".agent/workflows/pre-task.md",
    ".github/workflows/README.md",
    "examples/README.md",
    "planning/integration-plan.md",
    "tests/README.md",
    "config/superset/README.md",
    "documentation/REVIEWER_SETUP.md",
    "documentation/API_REFERENCE.md",
    "documentation/INTEGRATION_ASSESSMENT.md",
    "SECURITY.md",
    "PERSONA_MODEL_SETTINGS.md",
    "TODOS_REPORT.md",
    "GEMINI.md",
    "CONTRIBUTING.md",
    "ROADMAP.md",
    "README.md",
    "IMPROVEMENTS_SUMMARY.md",
    "CHANGELOG.md",
    "src/council_ai/webapp/app.py",
    "launch-council-web.command",
    "pyproject.toml",
    "launch-council.py",
    ".devcontainer/devcontainer.json",
    "tests/test_multi_model_utility.py",
    "tests/conftest.py",
    "launch-council.bat",
    "launch-council-mac.sh",
    "src/council_ai/webapp/assets/css/main.css",
    "package.json",
]

# Get the current time
now = datetime.datetime.now()
base_path = Path(__file__).parent.resolve()

# Iterate over the files
for rel_path in files:
    file_path = base_path / rel_path
    try:
        # Get the modification time of the file
        if not file_path.exists():
            continue

        mtime = os.path.getmtime(file_path)
        mtime_dt = datetime.datetime.fromtimestamp(mtime)

        # Calculate the difference between the current time and the modification time
        diff = now - mtime_dt

        # Check if the file was modified in the last 4 hours
        if diff.total_seconds() <= 4 * 60 * 60:
            print(rel_path)
    except Exception as e:
        print(f"Error processing {rel_path}: {e}")
