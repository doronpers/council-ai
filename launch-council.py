#!/usr/bin/env python3
"""Lightweight shim for tests that expect `launch-council.py` at repo root.
Provides a minimal `resolve_executable` function used by tests.
"""
import shutil
from typing import List, Optional


def resolve_executable(candidates: List[str]) -> Optional[str]:
    """Resolve the first candidate that exists on PATH using shutil.which."""
    for c in candidates:
        path = shutil.which(c)
        if path:
            return path
    return None


if __name__ == "__main__":
    print("This shim exists to satisfy tests that import launch-council.py")
