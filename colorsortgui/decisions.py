"""사람이 버튼으로 확정한 결정. 지문이 열쇠라서 재실행·개명·드라이브 이동에서 살아남는다."""
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

_LABELS = {"BLUE", "GREEN"}

class DecisionStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._d: dict[str, dict] = {}
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                self._d = dict(raw.get("decisions", {}))
            except (json.JSONDecodeError, OSError, AttributeError):
                # 깨진 파일은 증거로 옆에 치워 두고 빈 상태로 연다. 조용히 지우지 않는다.
                bad = self.path.with_suffix(self.path.suffix + ".bad")
                try:
                    os.replace(self.path, bad)
                except OSError:
                    pass

    def get(self, fp: str) -> str | None:
        rec = self._d.get(fp)
        return rec["label"] if rec else None

    def set(self, fp: str, label: str, name: str) -> None:
        if label not in _LABELS:
            raise ValueError(f"unknown label: {label}")
        self._d[fp] = {"label": label, "name": name,
                       "decided_at": datetime.now().isoformat(timespec="seconds")}
        self._save()

    def remove(self, fp: str) -> None:
        self._d.pop(fp, None)
        self._save()

    @property
    def count(self) -> int:
        return len(self._d)

    def _save(self) -> None:
        # USB가 도중에 뽑혀도 기존 파일이 깨지지 않도록: 같은 폴더에 임시 파일 → 교체.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"version": 1, "decisions": self._d},
                             ensure_ascii=False, indent=1)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)
            os.replace(tmp, self.path)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
