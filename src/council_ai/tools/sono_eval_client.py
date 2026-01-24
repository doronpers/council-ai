"""
SonoEval Client

Interact with the sono-eval assessment engine via CLI.
"""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SonoEvalClient:
    """Client for interacting with sono-eval."""

    def __init__(self, sono_eval_path: Optional[str] = None):
        """
        Initialize the client.

        Args:
            sono_eval_path: Path to sono-eval executable or directory.
                            If None, attempts to auto-discover.
        """
        self.executable = self._discover_executable(sono_eval_path)

    def _discover_executable(self, provided_path: Optional[str]) -> Optional[str]:
        """Find the sono-eval executable."""
        # 1. Use provided path
        if provided_path:
            return provided_path

        # 2. Check PATH
        in_path = shutil.which("sono-eval")
        if in_path:
            return in_path

        # 3. Check peer directory (workspace assumption)
        # Assuming we are in .../council-ai/src/council_ai/tools/
        # workspace root is 4 levels up? No, simpler to rely on CWD or known workspace structures.
        # Check standard locations
        workspace_roots = [
            Path.cwd().parent,  # If CWD is council-ai
            Path.cwd(),
            Path("../"),
            Path("../../"),
        ]

        for root in workspace_roots:
            # Check for direct executable (e.g., installed in venv)
            candidate = root / "sono-eval" / "venv" / "bin" / "sono-eval"
            if candidate.exists():
                return str(candidate)

            # Check for python execution path
            candidate_py = root / "sono-eval" / "venv" / "bin" / "python"
            if candidate_py.exists():
                return f"{candidate_py} -m sono_eval.cli.main"

        return None

    def _get_python_executable(self, root: Path) -> Optional[str]:
        """Get Python executable from venv or fallback."""
        venv_py = root / "venv" / "bin" / "python"
        if venv_py.exists():
            return str(venv_py)
        return None  # Could allow system python but safer to restrict

    def is_available(self) -> bool:
        """Check if sono-eval is available."""
        return self.executable is not None

    def assess_text(
        self,
        content: str,
        candidate_id: str = "council_qa",
        paths: list[str] = None,
    ) -> Dict:
        """
        Run assessment on text content.

        Args:
            content: Text content to assess
            candidate_id: ID for the assessment session
            paths: Specific paths to evaluate (technical, design, etc.)

        Returns:
            Review result dictionary
        """
        import os

        if not self.executable:
            raise RuntimeError("sono-eval not found. Please install it or set SONO_EVAL_PATH.")

        # Prepare Environment
        env = os.environ.copy()

        # If executable is a python module command string like ".../python -m ...",
        # parse it to set PYTHONPATH if running from source
        cmd = self.executable.split()

        # Check if we assume peer source directory structure
        if "sono-eval" in self.executable and "python" in self.executable:
            # Try to find the root of the repo to add src to PYTHONPATH
            # Assumption: executable is .../sono-eval/venv/bin/python
            # Root is .../sono-eval
            try:
                # Find path part ending in "sono-eval"
                parts = Path(cmd[0]).parts
                if "sono-eval" in parts:
                    idx = parts.index("sono-eval")
                    root_path = Path(*parts[: idx + 1])
                    src_path = root_path / "src"
                    if src_path.exists():
                        env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")
            except Exception:
                pass

            # Also add current council-ai src to PYTHONPATH if we are running from it
            # This handles the case where sono-eval depends on council-ai but isn't installed
            try:
                # Assume we are in .../council-ai/src/council_ai/tools/
                # Path(__file__) = .../council-ai/src/council_ai/tools/sono_eval_client.py
                # We want .../council-ai/src
                current_file = Path(__file__).resolve()
                # Go up 3 levels: council_ai -> tools -> sono_eval_client.py
                # src/council_ai/tools/ -> src
                council_src_path = current_file.parent.parent.parent
                if (council_src_path / "council_ai").exists():
                    env["PYTHONPATH"] = (
                        str(council_src_path) + os.pathsep + env.get("PYTHONPATH", "")
                    )

                # Also check for shared-ai-utils (council-ai dependency)
                # Assumes peer directory structure: .../Gits/council-ai -> .../Gits/shared-ai-utils
                # council_src_path is .../council-ai/src
                # council_src_path.parent is .../council-ai
                # council_src_path.parent.parent is .../Gits (Workspace root)
                workspace_root = council_src_path.parent.parent
                shared_utils_path = workspace_root / "shared-ai-utils" / "src"
                if shared_utils_path.exists():
                    env["PYTHONPATH"] = (
                        str(shared_utils_path) + os.pathsep + env.get("PYTHONPATH", "")
                    )
            except Exception:
                pass

        cmd.extend(["assess", "run"])
        cmd.extend(["--candidate-id", candidate_id])
        cmd.extend(["--content", content])
        cmd.extend(["--quiet"])

        # For reliability, we'll use a temporary output file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            output_file = tmp.name

        cmd.extend(["--output", output_file])

        if paths:
            cmd.extend(["--paths"])
            cmd.extend(paths)

        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)

            # Read result
            with open(output_file, "r") as f:
                data = json.load(f)
            return data

        except subprocess.CalledProcessError as e:
            logger.error(f"sono-eval failed: {e.stderr}")
            raise RuntimeError(f"Assessment failed: {e.stderr}\nCommand: {' '.join(cmd)}")
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse assessment results")
        finally:
            # Cleanup
            if Path(output_file).exists():
                Path(output_file).unlink()
