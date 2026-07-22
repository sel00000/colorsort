"""포터블 설정. exe·사진·기억이 한 드라이브에 담겨 통째로 이동하는 프로그램이므로
설정도 기본은 exe 옆에 둔다. 거기 못 쓰면 %APPDATA%로 물러난다."""
import json
import os
import sys
import tempfile
from pathlib import Path

_FILE = "colorsort-settings.json"

def _primary_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

def _dir_writable(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        probe = p / ".write-probe"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False

def settings_dir() -> Path:
    primary = _primary_dir()
    if _dir_writable(primary):
        return primary
    return Path(os.environ.get("APPDATA", str(Path.home()))) / "Colorsort"

def load_settings() -> dict:
    path = settings_dir() / _FILE
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def save_settings(d: dict) -> None:
    folder = settings_dir()
    folder.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, folder / _FILE)
