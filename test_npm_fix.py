#!/usr/bin/env python3
"""Quick test to verify npm command execution works."""

import importlib.util
import sys
from pathlib import Path

# Add current directory to path so we can import launch-council functions
sys.path.insert(0, str(Path(__file__).parent))

spec = importlib.util.spec_from_file_location(
    "launch_council", Path(__file__).parent / "launch-council.py"
)
launch_council = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launch_council)

# Test npm resolution and execution
print("Testing npm resolution...")
npm_exe = launch_council.resolve_executable(["npm.cmd", "npm.exe", "npm.bat", "npm"])
print(f"Resolved npm: {npm_exe}")

if npm_exe:
    print("\nTesting npm --version command...")
    rc, out, err = launch_council.run_command(
        [npm_exe, "--version"], check=False, capture_output=True
    )
    print(f"Return code: {rc}")
    if out:
        print(f"Output: {out.strip()}")
    if err:
        print(f"Error: {err.strip()}")

    if rc == 0:
        print("\n✅ SUCCESS: npm command works!")
    else:
        print("\n❌ FAILED: npm command returned error")
else:
    print("\n❌ FAILED: Could not resolve npm executable")
