"""Personal integration module for council-ai-personal.

This module handles detection, integration, and verification of council-ai-personal
repository integration.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PersonalIntegration:
    """Manages integration with council-ai-personal repository."""

    def __init__(self):
        """Initialize personal integration manager."""
        from ..utils.paths import get_workspace_config_dir

        self._repo_path: Optional[Path] = None
        # Use workspace-relative config directory
        config_dir_env = os.environ.get("COUNCIL_CONFIG_DIR")
        if config_dir_env:
            self._config_dir = Path(config_dir_env)
        else:
            self._config_dir = get_workspace_config_dir("council-ai")

    @staticmethod
    def detect_repo() -> Optional[Path]:
        """
        Detect council-ai-personal repository in common locations.

        Checks:
        1. Environment variable COUNCIL_AI_PERSONAL_PATH
        2. Sibling directory ../council-ai-personal
        3. User home ~/council-ai-personal
        4. Current working directory parent

        Returns:
            Path to council-ai-personal if found, None otherwise
        """
        # Check environment variable first
        env_path = os.environ.get("COUNCIL_AI_PERSONAL_PATH")
        if env_path:
            path = Path(env_path).expanduser().resolve()
            if path.exists() and path.is_dir():
                # Verify it looks like council-ai-personal
                if (path / "personal").exists() or (path / "setup.sh").exists():
                    return path

        # Check sibling directory (common development setup)
        try:
            # Try to find from council-ai installation
            council_ai_path = Path(__file__).parent.parent.parent.parent
            sibling_path = council_ai_path.parent / "council-ai-personal"
            if sibling_path.exists() and sibling_path.is_dir():
                if (sibling_path / "personal").exists() or (sibling_path / "setup.sh").exists():
                    return sibling_path
        except Exception:
            pass

        # Check user home
        home_path = Path.home() / "council-ai-personal"
        if home_path.exists() and home_path.is_dir():
            if (home_path / "personal").exists() or (home_path / "setup.sh").exists():
                return home_path

        # Check current working directory parent
        try:
            cwd_parent = Path.cwd().parent / "council-ai-personal"
            if cwd_parent.exists() and cwd_parent.is_dir():
                if (cwd_parent / "personal").exists() or (cwd_parent / "setup.sh").exists():
                    return cwd_parent
        except Exception:
            pass

        return None

    def is_configured(self) -> bool:
        """
        Check if personal configs are already integrated.

        Returns:
            True if personal configs appear to be loaded
        """
        # Check for personal config marker
        marker_file = self._config_dir / ".personal_integrated"
        if marker_file.exists():
            return True

        # Check if personal configs exist in config directory
        personal_config = self._config_dir / "config.yaml"
        if personal_config.exists():
            # Check if it has personal-specific markers
            try:
                with open(personal_config, encoding="utf-8") as f:
                    content = f.read()
                    if "personal" in content.lower() or "consultation_analytics" in content:
                        return True
            except Exception:
                pass

        # Check for personal personas directory
        personal_personas = self._config_dir / "personas"
        if personal_personas.exists() and any(personal_personas.glob("*.yaml")):
            # Check if any persona files look like they're from personal repo
            return True

        return False

    def integrate(self, repo_path: Optional[Path] = None, use_setup_script: bool = True) -> bool:
        """
        Integrate council-ai-personal by copying configs.

        Args:
            repo_path: Path to council-ai-personal repo. If None, auto-detect.
            use_setup_script: If True, use setup.sh script. Otherwise, copy manually.

        Returns:
            True if integration succeeded, False otherwise
        """
        if repo_path is None:
            repo_path = self.detect_repo()
            if repo_path is None:
                logger.error("Could not detect council-ai-personal repository")
                return False

        self._repo_path = repo_path

        # Ensure config directory exists
        self._config_dir.mkdir(parents=True, exist_ok=True)

        if use_setup_script:
            # Try to use setup.sh script
            setup_script = repo_path / "setup.sh"
            if setup_script.exists() and setup_script.is_file():
                try:
                    # Make script executable
                    os.chmod(setup_script, 0o755)
                    # Run setup script
                    result = subprocess.run(
                        [str(setup_script)],
                        cwd=str(repo_path),
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if result.returncode == 0:
                        # Create marker file
                        marker_file = self._config_dir / ".personal_integrated"
                        marker_file.touch()
                        logger.info("Personal integration completed via setup.sh")
                        return True
                    else:
                        logger.warning(f"setup.sh returned non-zero exit code: {result.stderr}")
                except Exception as e:
                    logger.warning(f"Failed to run setup.sh: {e}")

        # Manual integration (copy files)
        return self._integrate_manual(repo_path)

    def _integrate_manual(self, repo_path: Path) -> bool:
        """Manually copy personal configs to config directory."""
        try:
            personal_dir = repo_path / "personal"
            if not personal_dir.exists():
                logger.error(f"Personal directory not found at {personal_dir}")
                return False

            # Copy config files
            config_source = personal_dir / "config"
            if config_source.exists():
                for item in config_source.iterdir():
                    if item.is_file():
                        dest = self._config_dir / item.name
                        shutil.copy2(item, dest)
                        logger.debug(f"Copied {item.name} to {dest}")

            # Copy personas
            personas_source = personal_dir / "personas"
            if personas_source.exists():
                personas_dest = self._config_dir / "personas"
                personas_dest.mkdir(parents=True, exist_ok=True)
                for yaml_file in personas_source.glob("*.yaml"):
                    dest = personas_dest / yaml_file.name
                    shutil.copy2(yaml_file, dest)
                    logger.debug(f"Copied persona {yaml_file.name}")

            # Copy scripts if they exist
            scripts_source = personal_dir / "scripts"
            if scripts_source.exists():
                scripts_dest = self._config_dir / "scripts"
                scripts_dest.mkdir(parents=True, exist_ok=True)
                for script_file in scripts_source.iterdir():
                    if script_file.is_file():
                        dest = scripts_dest / script_file.name
                        shutil.copy2(script_file, dest)
                        # Make scripts executable
                        if script_file.suffix in (".sh", ".py"):
                            os.chmod(dest, 0o755)  # nosec B103
                        logger.debug(f"Copied script {script_file.name}")

            # Create marker file
            marker_file = self._config_dir / ".personal_integrated"
            marker_file.write_text(f"Integrated from: {repo_path}\n", encoding="utf-8")

            logger.info("Personal integration completed manually")
            return True

        except Exception as e:
            logger.error(f"Failed to integrate manually: {e}")
            return False

    def load_configs(self, repo_path: Optional[Path] = None) -> Dict:
        """
        Load personal configs without copying (seamless mode).

        Args:
            repo_path: Path to council-ai-personal repo. If None, auto-detect.

        Returns:
            Dictionary of loaded configs
        """
        if repo_path is None:
            repo_path = self.detect_repo()
            if repo_path is None:
                return {}

        self._repo_path = repo_path
        configs: Dict[str, Any] = {}

        try:
            personal_dir = repo_path / "personal"
            if not personal_dir.exists():
                return configs

            # Load config.yaml if exists
            config_file = personal_dir / "config" / "config.yaml"
            if config_file.exists():
                import yaml

                with open(config_file, encoding="utf-8") as f:
                    configs["config"] = yaml.safe_load(f) or {}

            # List personas
            personas_dir = personal_dir / "personas"
            if personas_dir.exists():
                configs["personas"] = [f.name for f in personas_dir.glob("*.yaml")]

            # List scripts
            scripts_dir = personal_dir / "scripts"
            if scripts_dir.exists():
                configs["scripts"] = [f.name for f in scripts_dir.iterdir() if f.is_file()]

        except Exception as e:
            logger.warning(f"Failed to load personal configs: {e}")

        return configs

    def verify(self) -> Dict[str, Any]:
        """
        Verify that personal integration is working.

        Returns:
            Dictionary with verification results
        """
        result: Dict[str, Any] = {
            "detected": False,
            "configured": False,
            "repo_path": None,
            "configs_loaded": False,
            "personas_available": False,
            "issues": [],
        }

        # Check if repo is detected
        repo_path = self.detect_repo()
        result["detected"] = repo_path is not None
        result["repo_path"] = str(repo_path) if repo_path else None

        # Check if configured
        result["configured"] = self.is_configured()

        # Check if configs are accessible
        if result["configured"]:
            config_file = self._config_dir / "config.yaml"
            if config_file.exists():
                result["configs_loaded"] = True
            else:
                result["issues"].append("Config file not found in config directory")

            # Check personas
            personas_dir = self._config_dir / "personas"
            if personas_dir.exists():
                persona_files = list(personas_dir.glob("*.yaml"))
                if persona_files:
                    result["personas_available"] = True
                    result["persona_count"] = len(persona_files)
                else:
                    result["issues"].append("No persona files found in personas directory")
            else:
                result["issues"].append("Personas directory not found")

        elif result["detected"]:
            result["issues"].append("Repository detected but not integrated")

        if not result["detected"]:
            result["issues"].append("council-ai-personal repository not detected")

        return result

    def get_status(self) -> Dict[str, Any]:
        """
        Get current integration status.

        Returns:
            Dictionary with status information
        """
        repo_path = self.detect_repo()
        configured = self.is_configured()

        status: Dict[str, Any] = {
            "detected": repo_path is not None,
            "configured": configured,
            "repo_path": str(repo_path) if repo_path else None,
            "config_dir": str(self._config_dir),
        }

        if repo_path:
            # Check what's available in the repo
            personal_dir = repo_path / "personal"
            if personal_dir.exists():
                available: Dict[str, Any] = {}
                if (personal_dir / "config").exists():
                    available["configs"] = True
                if (personal_dir / "personas").exists():
                    persona_count = len(list((personal_dir / "personas").glob("*.yaml")))
                    available["personas"] = str(persona_count)
                if (personal_dir / "scripts").exists():
                    script_count = len(
                        [f for f in (personal_dir / "scripts").iterdir() if f.is_file()]
                    )
                    available["scripts"] = str(script_count)
                status["available"] = available

        return status


# Convenience functions
def detect_personal_repo() -> Optional[Path]:
    """Detect council-ai-personal repository."""
    integration = PersonalIntegration()
    return integration.detect_repo()


def is_personal_configured() -> bool:
    """Check if personal configs are configured."""
    integration = PersonalIntegration()
    return integration.is_configured()


def integrate_personal(repo_path: Optional[Path] = None) -> bool:
    """Integrate council-ai-personal."""
    integration = PersonalIntegration()
    return integration.integrate(repo_path)


def verify_personal_integration() -> Dict[str, Any]:
    """Verify personal integration."""
    integration = PersonalIntegration()
    return integration.verify()


def get_personal_status() -> Dict[str, Any]:
    """Get personal integration status."""
    integration = PersonalIntegration()
    return integration.get_status()
