import os
import stat
import sys
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path


def _make_executable(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("echo test\n", encoding="utf-8")
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR)
    except Exception:
        # On Windows this may be a no-op; shutil.which uses PATHEXT.
        pass


def test_resolve_executable_prefers_first_match(monkeypatch, tmp_path):
    # `launch-council.py` is not importable as a normal module; load it directly.
    script_path = Path(__file__).resolve().parents[1] / "launch-council.py"
    loader = SourceFileLoader("launch_council_script", str(script_path))
    spec = spec_from_loader("launch_council_script", loader)
    assert spec is not None
    module = module_from_spec(spec)
    sys.modules["launch_council_script"] = module
    loader.exec_module(module)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()

    if os.name == "nt":
        first = bin_dir / "npm.cmd"
        second = bin_dir / "npm.bat"
        _make_executable(first)
        _make_executable(second)
        monkeypatch.setenv("PATHEXT", ".COM;.EXE;.BAT;.CMD")
        monkeypatch.setenv("PATH", str(bin_dir))
        resolved = module.resolve_executable(["npm.cmd", "npm.bat", "npm"])
        assert resolved is not None
        assert resolved.lower().endswith("npm.cmd")
    else:
        first = bin_dir / "npm"
        second = bin_dir / "npm2"
        _make_executable(first)
        _make_executable(second)
        monkeypatch.setenv("PATH", str(bin_dir))
        resolved = module.resolve_executable(["npm", "npm2"])
        assert resolved is not None
        assert resolved.endswith("npm")

