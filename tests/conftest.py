"""Test configuration for pytest."""

import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest

@pytest.fixture
def anyio_backend():
    return "asyncio"
