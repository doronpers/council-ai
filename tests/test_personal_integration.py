"""Tests for personal integration detection and operations."""

import os
import stat
from pathlib import Path

from council_ai.core.personal_integration import PersonalIntegration, detect_personal_repo


def make_personal_repo(base: Path):
    personal = base / "personal"
    config = personal / "config"
    personas = personal / "personas"
    scripts = personal / "scripts"
    config.mkdir(parents=True)
    personas.mkdir(parents=True)
    scripts.mkdir(parents=True)

    # create files
    (config / "config.yaml").write_text("key: value\n")
    (personas / "p1.yaml").write_text("name: p1\n")
    (scripts / "setup.sh").write_text("#!/bin/sh\necho ok\n")
    os.chmod(str(scripts / "setup.sh"), stat.S_IRWXU)
    return base


def test_detect_repo_via_env(tmp_path, monkeypatch):
    repo = tmp_path / "council-ai-personal"
    repo.mkdir()
    make_personal_repo(repo)
    monkeypatch.setenv("COUNCIL_AI_PERSONAL_PATH", str(repo))

    detected = detect_personal_repo()
    assert detected is not None
    assert str(repo) == str(detected)


def test_is_configured_marker_and_config(tmp_path, monkeypatch):
    # set config dir
    config_dir = tmp_path / "configdir"
    monkeypatch.setenv("COUNCIL_CONFIG_DIR", str(config_dir))
    pi = PersonalIntegration()

    # Initially not configured
    assert not pi.is_configured()

    # Create marker file
    (config_dir).mkdir(parents=True, exist_ok=True)
    (config_dir / ".personal_integrated").write_text("marker\n")
    assert pi.is_configured()

    # Write config with personal marker
    (config_dir / "config.yaml").write_text("personal: true\n")
    assert pi.is_configured()


def test_integrate_manual_and_load_configs(tmp_path, monkeypatch):
    repo = tmp_path / "council-ai-personal"
    repo.mkdir()
    make_personal_repo(repo)

    # Set config dir
    config_dir = tmp_path / "configdir"
    monkeypatch.setenv("COUNCIL_CONFIG_DIR", str(config_dir))

    pi = PersonalIntegration()
    success = pi.integrate(repo_path=repo, use_setup_script=False)
    assert success

    # marker file exists
    assert (config_dir / ".personal_integrated").exists()

    # load_configs should return data
    configs = pi.load_configs(repo)
    assert "config" in configs
    assert "personas" in configs
    assert "scripts" in configs


def test_verify_and_status(tmp_path, monkeypatch):
    repo = tmp_path / "council-ai-personal"
    repo.mkdir()
    make_personal_repo(repo)

    monkeypatch.setenv("COUNCIL_AI_PERSONAL_PATH", str(repo))
    config_dir = tmp_path / "configdir"
    monkeypatch.setenv("COUNCIL_CONFIG_DIR", str(config_dir))

    pi = PersonalIntegration()
    status = pi.get_status()
    assert status["detected"]
    assert status["repo_path"] is not None

    # Not configured yet
    assert not status["configured"]

    verify = pi.verify()
    assert verify["detected"]
    assert not verify["configured"]
    assert "Repository detected but not integrated" in verify["issues"]

    # Now integrate and check verify again
    pi.integrate(repo, use_setup_script=False)
    verify2 = pi.verify()
    assert verify2["configured"]
    assert verify2["configs_loaded"]
    assert verify2["personas_available"]
